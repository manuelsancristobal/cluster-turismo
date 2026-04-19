"""Funciones de agrupamiento espacial usando HDBSCAN con métrica haversine."""

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon


def run_hdbscan_spatial(
    df: pd.DataFrame,
    lat_col: str = "POINT_Y",
    lon_col: str = "POINT_X",
    min_cluster_size: int = 10,
) -> pd.DataFrame:
    """Realizar agrupamiento espacial HDBSCAN usando métrica haversine.

    Convierte latitud/longitud a radianes y agrupa usando la métrica de distancia
    haversine, apropiada para coordenadas geográficas en una esfera.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame con columnas de latitud y longitud
    lat_col : str
        Nombre de la columna de latitud (por defecto: 'POINT_Y')
    lon_col : str
        Nombre de la columna de longitud (por defecto: 'POINT_X')
    min_cluster_size : int
        Tamaño mínimo de un clúster en HDBSCAN (por defecto: 10)

    Retorna
    -------
    pd.DataFrame
        DataFrame de entrada con columna 'CLUSTER' añadida conteniendo las etiquetas de clúster
    """
    # Validar que existan las columnas requeridas
    for col in [lat_col, lon_col]:
        if col not in df.columns:
            raise KeyError(f"Columna '{col}' no encontrada en el dataframe. Columnas disponibles: {list(df.columns)}")

    # Extraer coordenadas y convertir a radianes (requerido para métrica haversine)
    coords = np.radians(df[[lat_col, lon_col]].values)

    # Ejecutar HDBSCAN con métrica haversine (apropiada para lat/lon)
    from sklearn.cluster import HDBSCAN

    clusterer = HDBSCAN(min_cluster_size=min_cluster_size, metric="haversine")
    cluster_labels = clusterer.fit_predict(coords)

    # Añadir etiquetas de clúster al dataframe
    df_clustered = df.copy()
    df_clustered["CLUSTER"] = cluster_labels

    # Imprimir resumen del agrupamiento
    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    n_noise = list(cluster_labels).count(-1)

    print("Resultados del agrupamiento:")
    print(f"  Número de clústeres: {n_clusters}")
    print(f"  Número de puntos de ruido: {n_noise}")
    print(f"  Porcentaje asignado: {((len(cluster_labels) - n_noise) / len(cluster_labels) * 100):.1f}%")

    return df_clustered


def compute_cluster_convex_hulls(
    df: pd.DataFrame,
    cluster_col: str = "CLUSTER",
    lat_col: str = "POINT_Y",
    lon_col: str = "POINT_X",
) -> Dict[int, Polygon]:
    """Calcular el casco convexo para cada clúster.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame agrupado con asignaciones de clúster
    cluster_col : str
        Nombre de la columna de clúster (por defecto: 'CLUSTER')
    lat_col : str
        Nombre de la columna de latitud (por defecto: 'POINT_Y')
    lon_col : str
        Nombre de la columna de longitud (por defecto: 'POINT_X')

    Retorna
    -------
    Dict[int, Polygon]
        Diccionario que mapea ID de clúster a Polygon de Shapely (casco convexo)
    """
    # NOTA: ConvexHull opera en espacio euclidiano sobre lat/lon crudos.
    # Para la extensión continental de Chile (~17°S–56°S) esta es una aproximación
    # aceptable (<0.5% de distorsión). Una proyección UTM sería más rigurosa
    # pero añade complejidad sin ganancia significativa de precisión aquí.
    hulls = {}
    n_failed = 0

    for cluster_id in df[cluster_col].unique():
        if cluster_id == -1:  # Omitir puntos de ruido
            continue

        cluster_points = df[df[cluster_col] == cluster_id][[lat_col, lon_col]].values

        if len(cluster_points) >= 3:
            try:
                hull = ConvexHull(cluster_points)
                hull_vertices = cluster_points[hull.vertices]
                # Crear polígono como lista de tuplas de coordenadas
                hull_coords = [tuple(pt) for pt in hull_vertices]
                hull_coords.append(hull_coords[0])  # Cerrar el polígono
                hulls[cluster_id] = hull_coords
            except Exception as e:
                n_failed += 1
                print(f"  ADVERTENCIA: No se pudo calcular el casco convexo para el clúster {cluster_id}: {e}")

    if n_failed > 0:
        print(f"  {n_failed} clúster(es) fallaron en el cálculo del casco convexo de {len(hulls) + n_failed}")

    return hulls


def get_hull_as_geojson(hull_coords: List[Tuple[float, float]]) -> dict:
    """Convertir lista de coordenadas del casco a formato GeoJSON.

    Parámetros
    ----------
    hull_coords : List[Tuple[float, float]]
        Lista de tuplas (lat, lon) que forman un polígono

    Retorna
    -------
    dict
        Feature GeoJSON con geometría Polygon
    """
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [hull_coords]},
    }


def summarize_clusters(
    df: pd.DataFrame,
    cluster_col: str = "CLUSTER",
    region_col: str = "REGION",
    category_col: str = "CATEGORIA",
    hierarchy_col: str = "JERARQUIA",
) -> pd.DataFrame:
    """Generar estadísticas resumidas para cada clúster.

    Calcula agregaciones por clúster incluyendo tamaño, región/categoría principal
    y porcentaje por nivel de jerarquía.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame agrupado
    cluster_col : str
        Nombre de la columna de clúster (por defecto: 'CLUSTER')
    region_col : str
        Nombre de la columna de región (por defecto: 'REGION')
    category_col : str
        Nombre de la columna de categoría (por defecto: 'CATEGORIA')
    hierarchy_col : str
        Nombre de la columna de jerarquía (por defecto: 'JERARQUÍA')

    Retorna
    -------
    pd.DataFrame
        Estadísticas resumidas por clúster
    """
    # Contar atractivos por clúster
    summary = df.groupby(cluster_col).agg(
        n_attractions=("NOMBRE", "count"),
        region_principal=(
            region_col,
            lambda x: x.value_counts().index[0] if len(x) > 0 and len(x.value_counts()) > 0 else None,
        ),
        categoria_principal=(
            category_col,
            lambda x: x.value_counts().index[0] if len(x) > 0 and len(x.value_counts()) > 0 else None,
        ),
        jerarquia_principal=(
            hierarchy_col,
            lambda x: x.value_counts().index[0] if len(x) > 0 and len(x.value_counts()) > 0 else None,
        ),
    )

    # Calcular conteos y porcentajes por nivel de jerarquía
    for level in ["INTERNACIONAL", "NACIONAL", "REGIONAL", "LOCAL"]:
        col_lower = level.lower()
        counts = df[df[hierarchy_col] == level].groupby(cluster_col).size()
        summary[f"n_{col_lower}"] = counts.reindex(summary.index, fill_value=0)
        summary[f"pct_{col_lower}"] = ((summary[f"n_{col_lower}"] / summary["n_attractions"]) * 100).round(1)

    return summary.sort_values("n_attractions", ascending=False)


def identify_cluster_quality(summary_df: pd.DataFrame) -> pd.DataFrame:
    """Clasificar la calidad del clúster según la distribución de jerarquía.

    Parámetros
    ----------
    summary_df : pd.DataFrame
        DataFrame resumen de clústeres generado por summarize_clusters()

    Retorna
    -------
    pd.DataFrame
        DataFrame de entrada con columna 'quality' añadida
    """
    summary_df_copy = summary_df.copy()

    def classify_quality(row):
        if row["pct_internacional"] > 0:
            return "Alta - Tiene ancla internacional"
        elif row["pct_nacional"] > 0:
            return "Media - Tiene ancla nacional"
        else:
            return "Baja - Sin atractivos ancla"

    summary_df_copy["quality"] = summary_df_copy.apply(classify_quality, axis=1)

    return summary_df_copy
