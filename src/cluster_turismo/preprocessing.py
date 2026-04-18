"""Funciones de preprocesamiento y validación de datos."""

from typing import List, Optional

import matplotlib
import numpy as np
import pandas as pd


def filter_permanent_attractions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra atractivos temporales y conserva solo los permanentes.

    Elimina todos los registros con CATEGORIA == 'ACONTECIMIENTOS PROGRAMADOS'
    (eventos programados que no son atractivos permanentes).

    Parámetros
    ----------
    df : pd.DataFrame
        Dataframe de atractivos sin procesar

    Retorna
    -------
    pd.DataFrame
        Dataframe filtrado con solo atractivos permanentes
    """
    df_filtered = df[df["CATEGORIA"] != "ACONTECIMIENTOS PROGRAMADOS"].copy()
    return df_filtered


def validate_coordinates(
    df: pd.DataFrame, lat_col: str = "POINT_Y", lon_col: str = "POINT_X"
) -> pd.DataFrame:
    """
    Valida y filtra coordenadas dentro de los límites continentales de Chile.

    Límites continentales de Chile (aproximadamente):
    - Latitud: -17° a -56°
    - Longitud: -66° a -75°

    Parámetros
    ----------
    df : pd.DataFrame
        Dataframe con columnas de coordenadas
    lat_col : str
        Nombre de la columna de latitud (por defecto: 'POINT_Y')
    lon_col : str
        Nombre de la columna de longitud (por defecto: 'POINT_X')

    Retorna
    -------
    pd.DataFrame
        Dataframe con solo filas de coordenadas válidas
    """
    # Límites continentales de Chile
    lat_min, lat_max = -56, -17
    lon_min, lon_max = -75, -66

    mask = (
        (df[lat_col] >= lat_min)
        & (df[lat_col] <= lat_max)
        & (df[lon_col] >= lon_min)
        & (df[lon_col] <= lon_max)
    )

    df_valid = df[mask].copy()
    n_removed = len(df) - len(df_valid)
    if n_removed > 0:
        print(f"Se eliminaron {n_removed} registros con coordenadas inválidas")

    return df_valid


def normalize_commune_codes(df: pd.DataFrame, col: str = "COD_COM") -> pd.DataFrame:
    """
    Normaliza códigos de comuna eliminando espacios en blanco.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataframe con columna de código de comuna
    col : str
        Nombre de la columna de código de comuna (por defecto: 'COD_COM')

    Retorna
    -------
    pd.DataFrame
        Dataframe con códigos normalizados
    """
    df_normalized = df.copy()
    df_normalized[col] = df_normalized[col].astype(str).str.strip()
    return df_normalized


def merge_attractions_destinations(
    df_attractions: pd.DataFrame,
    df_destinations: pd.DataFrame,
    attr_code_col: str = "COD_COM",
    dest_code_col: str = "codigo",
) -> pd.DataFrame:
    """
    Combina atractivos con destinos oficiales por código de comuna.

    Parámetros
    ----------
    df_attractions : pd.DataFrame
        Dataframe de atractivos con columna de código de comuna
    df_destinations : pd.DataFrame
        Dataframe de destinos con columna de código
    attr_code_col : str
        Columna de código de comuna en atractivos (por defecto: 'COD_COM')
    dest_code_col : str
        Columna de código en destinos (por defecto: 'codigo')

    Retorna
    -------
    pd.DataFrame
        Dataframe combinado con información de atractivo + destino
    """
    df_merged = df_attractions.merge(
        df_destinations, left_on=attr_code_col, right_on=dest_code_col, how="left"
    )

    n_with_dest = df_merged["nombre"].notna().sum()
    n_without_dest = df_merged["nombre"].isna().sum()
    print(f"Atractivos coincidentes: {n_with_dest} / Sin coincidencia: {n_without_dest}")

    return df_merged


def get_hierarchy_color_map() -> dict:
    """
    Obtiene el mapa de colores para niveles de jerarquía de atractivos.

    Retorna
    -------
    dict
        Mapeo de nivel de jerarquía a triplete de color RGB
    """
    return {
        "LOCAL": [180, 180, 180],
        "REGIONAL": [130, 170, 210],
        "NACIONAL": [70, 130, 180],
        "INTERNACIONAL": [220, 30, 120],
    }


def get_hierarchy_radius_map() -> dict:
    """
    Obtiene el mapa de radio (tamaño) para niveles de jerarquía de atractivos.

    Retorna
    -------
    dict
        Mapeo de nivel de jerarquía a valor de radio
    """
    return {
        "LOCAL": 1,
        "REGIONAL": 1.5,
        "NACIONAL": 2,
        "INTERNACIONAL": 3,
    }


def assign_hierarchy_styling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Asigna color y radio según el nivel de jerarquía del atractivo.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataframe con columna JERARQUÍA

    Retorna
    -------
    pd.DataFrame
        Dataframe con columnas 'color' y 'radius' agregadas
    """
    df_styled = df.copy()

    color_map = get_hierarchy_color_map()
    radius_map = get_hierarchy_radius_map()

    hierarchy_col = "JERARQUIA" if "JERARQUIA" in df_styled.columns else "JERARQUÍA"
    df_styled["color"] = df_styled[hierarchy_col].map(color_map)
    df_styled["radius"] = df_styled[hierarchy_col].map(radius_map)

    return df_styled


def get_cluster_color_palette(n_clusters: int) -> dict:
    """
    Genera colores distintos para visualización de clústeres.

    Usa los mapas de colores tab20 y tab20b de matplotlib para obtener hasta 40 colores distintos.

    Parámetros
    ----------
    n_clusters : int
        Número de clústeres a los que asignar colores

    Retorna
    -------
    dict
        Mapeo de ID de clúster a triplete de color RGB
    """
    colors = {}

    # Usar tab20 (20 colores) y tab20b (20 colores) para hasta 40 clústeres
    cmap_a = matplotlib.colormaps.get_cmap("tab20")
    cmap_b = matplotlib.colormaps.get_cmap("tab20b")

    for i in range(n_clusters):
        if i < 20:
            rgba = cmap_a(i)
        else:
            rgba = cmap_b(i - 20)

        # Convertir RGBA a RGB en rango 0-255
        rgb = [int(rgba[j] * 255) for j in range(3)]
        colors[i] = rgb

    # Los puntos de ruido (clúster -1) obtienen gris con transparencia
    colors[-1] = [150, 150, 150]

    return colors


def assign_cluster_colors(df: pd.DataFrame, n_clusters: int) -> pd.DataFrame:
    """
    Asigna colores a las filas del dataframe según la asignación de clúster.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataframe con columna 'CLUSTER'
    n_clusters : int
        Número de clústeres

    Retorna
    -------
    pd.DataFrame
        Dataframe con columna 'cluster_color' agregada
    """
    df_colored = df.copy()

    color_map = get_cluster_color_palette(n_clusters)
    df_colored["cluster_color"] = df_colored["CLUSTER"].map(color_map)

    return df_colored


def get_anchor_color_map() -> dict:
    """
    Obtiene el mapa de colores para clasificación de ancla.

    Retorna
    -------
    dict
        Mapeo de estado de ancla a valores RGB
    """
    return {
        "Con ancla internacional": [46, 204, 113],  # Verde
        "Solo ancla nacional": [243, 156, 18],  # Naranja
        "Sin ancla": [231, 76, 60],  # Rojo
        "Ruido": [150, 150, 150],  # Gris
    }
