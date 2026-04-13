"""Data preprocessing and validation functions."""

from typing import List, Optional

import matplotlib
import numpy as np
import pandas as pd


def filter_permanent_attractions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter out temporary attractions and keep only permanent ones.

    Removes all records with CATEGORIA == 'ACONTECIMIENTOS PROGRAMADOS'
    (scheduled events that are not permanent attractions).

    Parameters
    ----------
    df : pd.DataFrame
        Raw attractions dataframe

    Returns
    -------
    pd.DataFrame
        Filtered dataframe with only permanent attractions
    """
    df_filtered = df[df["CATEGORIA"] != "ACONTECIMIENTOS PROGRAMADOS"].copy()
    return df_filtered


def validate_coordinates(
    df: pd.DataFrame, lat_col: str = "POINT_Y", lon_col: str = "POINT_X"
) -> pd.DataFrame:
    """
    Validate and filter coordinates within Chilean continental bounds.

    Chile continental bounds (approximately):
    - Latitude: -17° to -56°
    - Longitude: -66° to -75°

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with coordinate columns
    lat_col : str
        Name of latitude column (default: 'POINT_Y')
    lon_col : str
        Name of longitude column (default: 'POINT_X')

    Returns
    -------
    pd.DataFrame
        Dataframe with only valid coordinate rows
    """
    # Chilean continental bounds
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
        print(f"Removed {n_removed} records with invalid coordinates")

    return df_valid


def normalize_commune_codes(df: pd.DataFrame, col: str = "COD_COM") -> pd.DataFrame:
    """
    Normalize commune codes by removing whitespace.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with commune code column
    col : str
        Name of commune code column (default: 'COD_COM')

    Returns
    -------
    pd.DataFrame
        Dataframe with normalized codes
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
    Merge attractions with official destinations by commune code.

    Parameters
    ----------
    df_attractions : pd.DataFrame
        Attractions dataframe with commune code column
    df_destinations : pd.DataFrame
        Destinations dataframe with code column
    attr_code_col : str
        Commune code column in attractions (default: 'COD_COM')
    dest_code_col : str
        Code column in destinations (default: 'codigo')

    Returns
    -------
    pd.DataFrame
        Merged dataframe with attraction + destination info
    """
    df_merged = df_attractions.merge(
        df_destinations, left_on=attr_code_col, right_on=dest_code_col, how="left"
    )

    n_with_dest = df_merged["nombre"].notna().sum()
    n_without_dest = df_merged["nombre"].isna().sum()
    print(f"Matched attractions: {n_with_dest} / Unmatched: {n_without_dest}")

    return df_merged


def get_hierarchy_color_map() -> dict:
    """
    Get color map for attraction hierarchy levels.

    Returns
    -------
    dict
        Mapping of hierarchy level to RGB color triplet
    """
    return {
        "LOCAL": [180, 180, 180],
        "REGIONAL": [130, 170, 210],
        "NACIONAL": [70, 130, 180],
        "INTERNACIONAL": [220, 30, 120],
    }


def get_hierarchy_radius_map() -> dict:
    """
    Get radius (size) map for attraction hierarchy levels.

    Returns
    -------
    dict
        Mapping of hierarchy level to radius value
    """
    return {
        "LOCAL": 1,
        "REGIONAL": 1.5,
        "NACIONAL": 2,
        "INTERNACIONAL": 3,
    }


def assign_hierarchy_styling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign color and radius based on attraction hierarchy level.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with JERARQUÍA column

    Returns
    -------
    pd.DataFrame
        Dataframe with added 'color' and 'radius' columns
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
    Generate distinct colors for cluster visualization.

    Uses matplotlib's tab20 and tab20b colormaps to get up to 40 distinct colors.

    Parameters
    ----------
    n_clusters : int
        Number of clusters to assign colors

    Returns
    -------
    dict
        Mapping of cluster ID to RGB color triplet
    """
    colors = {}

    # Use tab20 (20 colors) and tab20b (20 colors) for up to 40 clusters
    cmap_a = matplotlib.colormaps.get_cmap("tab20")
    cmap_b = matplotlib.colormaps.get_cmap("tab20b")

    for i in range(n_clusters):
        if i < 20:
            rgba = cmap_a(i)
        else:
            rgba = cmap_b(i - 20)

        # Convert RGBA to RGB in 0-255 range
        rgb = [int(rgba[j] * 255) for j in range(3)]
        colors[i] = rgb

    # Noise points (-1 cluster) get gray with transparency
    colors[-1] = [150, 150, 150]

    return colors


def assign_cluster_colors(df: pd.DataFrame, n_clusters: int) -> pd.DataFrame:
    """
    Assign colors to dataframe rows based on cluster assignment.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with 'CLUSTER' column
    n_clusters : int
        Number of clusters

    Returns
    -------
    pd.DataFrame
        Dataframe with added 'cluster_color' column
    """
    df_colored = df.copy()

    color_map = get_cluster_color_palette(n_clusters)
    df_colored["cluster_color"] = df_colored["CLUSTER"].map(color_map)

    return df_colored


def get_anchor_color_map() -> dict:
    """
    Get color map for anchor classification.

    Returns
    -------
    dict
        Mapping of anchor status to RGB values
    """
    return {
        "Con ancla internacional": [46, 204, 113],  # Green
        "Solo ancla nacional": [243, 156, 18],  # Orange
        "Sin ancla": [231, 76, 60],  # Red
        "Ruido": [150, 150, 150],  # Gray
    }
