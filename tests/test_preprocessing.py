"""Tests para el módulo de preprocesamiento."""

import os

import pandas as pd
import pytest

from cluster_turismo import preprocessing


@pytest.fixture
def sample_data():
    """Cargar CSV de atractivos de ejemplo."""
    fixtures_dir = os.path.dirname(__file__)
    return pd.read_csv(os.path.join(fixtures_dir, "fixtures/sample_attractions.csv"))


def test_filter_permanent_attractions(sample_data):
    """Verificar que los eventos se filtren."""
    df = preprocessing.filter_permanent_attractions(sample_data)

    # Debe eliminar la fila "ACONTECIMIENTOS PROGRAMADOS"
    assert len(df) < len(sample_data)
    assert (df["CATEGORIA"] == "ACONTECIMIENTOS PROGRAMADOS").sum() == 0

    # Debe mantener todos los demás atractivos
    assert len(df) == len(sample_data) - 1


def test_validate_coordinates(sample_data):
    """Verificar validación de coordenadas dentro de límites chilenos."""
    df = preprocessing.validate_coordinates(sample_data)

    # Todas las coordenadas deben estar dentro de los límites de Chile
    assert (df["POINT_Y"] >= -56).all()
    assert (df["POINT_Y"] <= -17).all()
    assert (df["POINT_X"] >= -75).all()
    assert (df["POINT_X"] <= -66).all()


def test_validate_coordinates_removes_outliers():
    """Verificar que las coordenadas inválidas se eliminen."""
    data = {
        "NOMBRE": ["Valid1", "Invalid1", "Valid2", "Invalid2"],
        "POINT_Y": [-33.0, -60.0, -35.0, -10.0],  # -60 y -10 están fuera de rango
        "POINT_X": [-70.0, -70.0, -71.0, -71.0],
    }
    df = pd.DataFrame(data)
    df_valid = preprocessing.validate_coordinates(df)

    assert len(df_valid) == 2
    assert "Valid1" in df_valid["NOMBRE"].values
    assert "Valid2" in df_valid["NOMBRE"].values


def test_normalize_commune_codes():
    """Verificar que los códigos de comuna se normalicen."""
    data = {
        "COD_COM": ["  01001  ", "02001", " 03001"],
        "NOMBRE": ["A", "B", "C"],
    }
    df = pd.DataFrame(data)
    df_norm = preprocessing.normalize_commune_codes(df)

    expected = ["01001", "02001", "03001"]
    assert df_norm["COD_COM"].tolist() == expected


def test_get_hierarchy_color_map():
    """Verificar mapeo de colores por jerarquía."""
    colors = preprocessing.get_hierarchy_color_map()

    assert "INTERNACIONAL" in colors
    assert "NACIONAL" in colors
    assert "REGIONAL" in colors
    assert "LOCAL" in colors

    # Verificar formato (lista RGB)
    for color in colors.values():
        assert len(color) == 3
        assert all(isinstance(c, int) for c in color)


def test_get_hierarchy_radius_map():
    """Verificar mapeo de radios por jerarquía."""
    radii = preprocessing.get_hierarchy_radius_map()

    assert radii["INTERNACIONAL"] > radii["LOCAL"]
    assert radii["NACIONAL"] > radii["REGIONAL"]


def test_assign_hierarchy_styling(sample_data):
    """Verificar que se agreguen las columnas de estilo."""
    df = preprocessing.assign_hierarchy_styling(sample_data)

    assert "color" in df.columns
    assert "radius" in df.columns
    assert len(df) == len(sample_data)

    # Verificar que los colores se mapearon correctamente
    assert df[df["JERARQUÍA"] == "INTERNACIONAL"]["color"].notna().all()


def test_get_cluster_color_palette():
    """Verificar generación de colores de clúster."""
    colors = preprocessing.get_cluster_color_palette(30)

    # 30 clústeres + 1 entrada de ruido (-1)
    assert len(colors) == 31
    assert -1 in colors
    # Verificar formato
    for cluster_id, color in colors.items():
        assert len(color) == 3


def test_assign_cluster_colors(sample_data):
    """Verificar asignación de colores por clúster."""
    # Agregar columna de clúster dummy
    sample_data["CLUSTER"] = [0, 0, 1, 1, 0, 1, 2, 2, 1, 2, 0, 0, -1, 1, 2, 0]

    df = preprocessing.assign_cluster_colors(sample_data, n_clusters=3)

    assert "cluster_color" in df.columns
    assert len(df) == len(sample_data)


def test_merge_attractions_destinations():
    """Verificar la unión de atractivos con destinos."""
    attractions = pd.DataFrame(
        {
            "NOMBRE": ["A", "B", "C"],
            "COD_COM": ["01", "02", "03"],
        }
    )
    destinations = pd.DataFrame(
        {
            "nombre": ["Dest1", "Dest2"],
            "codigo": ["01", "02"],
        }
    )
    result = preprocessing.merge_attractions_destinations(attractions, destinations)
    assert len(result) == 3
    assert result.iloc[0]["nombre"] == "Dest1"
    assert result.iloc[1]["nombre"] == "Dest2"
    assert pd.isna(result.iloc[2]["nombre"])


def test_get_anchor_color_map():
    """Verificar mapeo de colores por estado de ancla."""
    colors = preprocessing.get_anchor_color_map()

    assert "Con ancla internacional" in colors
    assert "Solo ancla nacional" in colors
    assert "Sin ancla" in colors
    assert "Ruido" in colors

    # Verificar que los colores sean distintos
    unique_colors = set(str(c) for c in colors.values())
    assert len(unique_colors) == 4
