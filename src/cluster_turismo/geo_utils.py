"""Geospatial utility functions using Shapely."""

from typing import Dict, List, Tuple

import pandas as pd
from shapely.geometry import Point, Polygon


def build_shapely_polygons(df: pd.DataFrame, coords_col: str = "coordinates") -> Dict[str, Polygon]:
    """
    Build Shapely Polygon objects from coordinate data.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with coordinate information (typically from data_loader.load_kmz_destinations)
    coords_col : str
        Column name containing coordinate list (default: 'coordinates')

    Returns
    -------
    Dict[str, Polygon]
        Dictionary mapping destination names to Shapely Polygon objects
    """
    polygons = {}

    for idx, row in df.iterrows():
        name = row.get("nombre")
        coords = row.get(coords_col)

        if name and coords and len(coords) >= 3:
            try:
                polygon = Polygon(coords)
                if polygon.is_valid:
                    polygons[name] = polygon
            except Exception as e:
                print(f"Could not create polygon for {name}: {e}")

    return polygons


def point_in_polygon_check(
    df_points: pd.DataFrame,
    df_polygons: pd.DataFrame,
    lat_col: str = "POINT_Y",
    lon_col: str = "POINT_X",
) -> pd.DataFrame:
    """
    Determine if each attraction point falls within any destination polygon.

    Parameters
    ----------
    df_points : pd.DataFrame
        Attractions dataframe with coordinates
    df_polygons : pd.DataFrame
        Destinations dataframe with polygon coordinates
    lat_col : str
        Latitude column in points (default: 'POINT_Y')
    lon_col : str
        Longitude column in points (default: 'POINT_X')

    Returns
    -------
    pd.DataFrame
        Input points dataframe with added 'in_destination' and 'destination_name' columns
    """
    # Build polygons from destinations
    polygons = build_shapely_polygons(df_polygons)

    # Check each attraction
    in_destination_list = []
    destination_names = []

    for idx, row in df_points.iterrows():
        point = Point(row[lon_col], row[lat_col])

        found_dest = None
        for dest_name, polygon in polygons.items():
            if polygon.contains(point):
                found_dest = dest_name
                break

        in_destination_list.append(found_dest is not None)
        destination_names.append(found_dest)

    df_result = df_points.copy()
    df_result["in_destination"] = in_destination_list
    df_result["destination_name"] = destination_names

    return df_result


def compute_cluster_centroid(
    df: pd.DataFrame, lat_col: str = "POINT_Y", lon_col: str = "POINT_X"
) -> Tuple[float, float]:
    """
    Compute centroid (center) of cluster points.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with coordinate columns
    lat_col : str
        Latitude column (default: 'POINT_Y')
    lon_col : str
        Longitude column (default: 'POINT_X')

    Returns
    -------
    Tuple[float, float]
        (latitude, longitude) of cluster centroid
    """
    lat = df[lat_col].mean()
    lon = df[lon_col].mean()
    return lat, lon


def compute_geographic_bounds(
    df: pd.DataFrame, lat_col: str = "POINT_Y", lon_col: str = "POINT_X"
) -> dict:
    """
    Compute geographic bounding box of points.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with coordinates
    lat_col : str
        Latitude column (default: 'POINT_Y')
    lon_col : str
        Longitude column (default: 'POINT_X')

    Returns
    -------
    dict
        Dictionary with 'north', 'south', 'east', 'west' bounds
    """
    return {
        "north": df[lat_col].max(),
        "south": df[lat_col].min(),
        "east": df[lon_col].max(),
        "west": df[lon_col].min(),
    }


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate haversine distance between two coordinate pairs.

    Parameters
    ----------
    lat1, lon1 : float
        First coordinate pair in degrees
    lat2, lon2 : float
        Second coordinate pair in degrees

    Returns
    -------
    float
        Distance in kilometers
    """
    from math import asin, cos, radians, sin, sqrt

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r
