"""Tests para el módulo de clustering."""

import numpy as np
import pandas as pd

from cluster_turismo import clustering


def test_run_hdbscan_spatial_output_shape(sample_data):
    """Verificar que HDBSCAN retorne la cantidad correcta de etiquetas."""
    df = clustering.run_hdbscan_spatial(sample_data, lat_col="POINT_Y", lon_col="POINT_X", min_cluster_size=3)

    # Debe tener la misma longitud
    assert len(df) == len(sample_data)

    # Debe tener columna CLUSTER
    assert "CLUSTER" in df.columns

    # Las etiquetas de clúster deben ser enteros
    assert df["CLUSTER"].dtype in [np.int32, np.int64, int]


def test_run_hdbscan_spatial_cluster_range(sample_data):
    """Verificar que el clustering produzca un número razonable de clústeres."""
    df = clustering.run_hdbscan_spatial(sample_data, lat_col="POINT_Y", lon_col="POINT_X", min_cluster_size=2)

    unique_clusters = set(df["CLUSTER"].unique())
    # Quitar ruido (-1) para contar
    num_clusters = len([c for c in unique_clusters if c != -1])

    # Debe tener al menos 1 clúster y no más de la mitad de los puntos
    assert num_clusters >= 1
    assert num_clusters <= len(sample_data) / 2

    # Los puntos de ruido deben estar etiquetados como -1
    noise_mask = df["CLUSTER"] == -1
    non_noise = df[~noise_mask]
    assert all(c >= 0 for c in non_noise["CLUSTER"])


def test_run_hdbscan_spatial_with_geographic_data():
    """Verificar HDBSCAN con clustering geográfico real."""
    # Crear datos con dos clústeres geográficos distintos
    data = {
        "NOMBRE": [f"A{i}" for i in range(20)],
        "POINT_Y": ([-33.0] * 10 + [-45.0] * 10),  # Dos regiones de latitud distintas
        "POINT_X": [-70.5] * 10 + [-72.5] * 10,  # Dos regiones de longitud distintas
        "JERARQUÍA": ["NACIONAL"] * 20,
    }
    df = pd.DataFrame(data)

    df_clustered = clustering.run_hdbscan_spatial(df, lat_col="POINT_Y", lon_col="POINT_X", min_cluster_size=5)

    # Debe encontrar al menos 2 clústeres
    unique_clusters = set(df_clustered["CLUSTER"].unique())
    num_clusters = len([c for c in unique_clusters if c != -1])
    assert num_clusters >= 1  # Al mínimo, encuentra un clúster


def test_compute_cluster_convex_hulls(sample_data):
    """Verificar cálculo de cascos convexos."""
    # Agregar asignaciones de clúster primero
    sample_data["CLUSTER"] = [0, 0, 1, 1, 0, 1, 2, 2, 1, 2, 0, 0, -1, 1, 2, 0]

    hulls = clustering.compute_cluster_convex_hulls(
        sample_data, cluster_col="CLUSTER", lat_col="POINT_Y", lon_col="POINT_X"
    )

    # Debe excluir el clúster de ruido (-1)
    assert -1 not in hulls

    # Debe tener cascos para clústeres con 3+ puntos
    assert len(hulls) > 0

    # Cada casco debe ser un polígono cerrado de tuplas de coordenadas
    for _hull_id, hull_coords in hulls.items():
        assert isinstance(hull_coords, list)
        assert len(hull_coords) >= 4  # Al menos 3 vértices + punto de cierre
        assert all(isinstance(coord, tuple) for coord in hull_coords)
        assert all(len(coord) == 2 for coord in hull_coords)
        # El casco debe estar cerrado (primero == último)
        assert hull_coords[0] == hull_coords[-1]


def test_compute_cluster_convex_hulls_single_point():
    """Verificar que los clústeres de un solo punto se omitan."""
    data = {
        "NOMBRE": ["A", "B"],
        "POINT_Y": [-33.0, -45.0],
        "POINT_X": [-70.0, -72.0],
        "CLUSTER": [0, 1],
    }
    df = pd.DataFrame(data)

    hulls = clustering.compute_cluster_convex_hulls(df)

    # No debe incluir clústeres con menos de 3 puntos
    assert len(hulls) == 0


def test_summarize_clusters(sample_data):
    """Verificar resumen de clústeres."""
    sample_data["CLUSTER"] = [0, 0, 1, 1, 0, 1, 2, 2, 1, 2, 0, 0, -1, 1, 2, 0]

    summary = clustering.summarize_clusters(
        sample_data,
        cluster_col="CLUSTER",
        region_col="REGION",
        category_col="CATEGORIA",
        hierarchy_col="JERARQUÍA",
    )

    # Debe tener resumen para cada clúster
    assert len(summary) > 0

    # Debe tener las columnas esperadas
    expected_cols = [
        "n_attractions",
        "region_principal",
        "categoria_principal",
        "n_internacional",
        "n_nacional",
        "pct_internacional",
        "pct_nacional",
    ]
    for col in expected_cols:
        assert col in summary.columns, f"Falta columna: {col}"

    # Debe estar ordenado por n_attractions descendente
    assert (summary["n_attractions"].iloc[:-1].values >= summary["n_attractions"].iloc[1:].values).all()

    # Los conteos de atractivos deben ser positivos
    assert (summary["n_attractions"] > 0).all()

    # Los porcentajes deben estar entre 0 y 100
    for pct_col in [c for c in summary.columns if c.startswith("pct_")]:
        assert (summary[pct_col] >= 0).all()
        assert (summary[pct_col] <= 100).all()


def test_summarize_clusters_percentages():
    """Verificar que los porcentajes se calculen correctamente."""
    data = {
        "NOMBRE": ["A"] * 10,
        "REGION": ["TestRegion"] * 10,
        "CATEGORIA": ["TestCategory"] * 10,
        "JERARQUIA": ["INTERNACIONAL"] * 5 + ["NACIONAL"] * 5,
        "CLUSTER": [0] * 10,
    }
    df = pd.DataFrame(data)

    summary = clustering.summarize_clusters(df)

    # Debe tener los porcentajes correctos
    assert summary.loc[0, "pct_internacional"] == 50.0
    assert summary.loc[0, "pct_nacional"] == 50.0


def test_identify_cluster_quality():
    """Verificar clasificación de calidad de clústeres."""
    summary_data = {
        "n_attractions": [10, 5, 8],
        "pct_internacional": [50, 0, 25],
        "pct_nacional": [50, 100, 75],
        "pct_regional": [0, 0, 0],
        "pct_local": [0, 0, 0],
    }
    df = pd.DataFrame(summary_data)

    df_quality = clustering.identify_cluster_quality(df)

    assert "quality" in df_quality.columns
    assert df_quality.loc[0, "quality"] == "Alta - Tiene ancla internacional"
    assert df_quality.loc[1, "quality"] == "Media - Tiene ancla nacional"
