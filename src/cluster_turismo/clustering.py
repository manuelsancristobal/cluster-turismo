"""Spatial clustering functions using HDBSCAN with haversine metric."""

from typing import Dict, List, Tuple

import hdbscan
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
    """
    Perform HDBSCAN spatial clustering using haversine metric.

    Converts latitude/longitude to radians and clusters using the haversine distance
    metric, which is appropriate for geographic coordinates on a sphere.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with latitude and longitude columns
    lat_col : str
        Column name for latitude (default: 'POINT_Y')
    lon_col : str
        Column name for longitude (default: 'POINT_X')
    min_cluster_size : int
        Minimum size for a cluster in HDBSCAN (default: 10)

    Returns
    -------
    pd.DataFrame
        Input dataframe with added 'CLUSTER' column containing cluster labels
    """
    # Validate required columns exist
    for col in [lat_col, lon_col]:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found in dataframe. Available columns: {list(df.columns)}")

    # Extract coordinates and convert to radians (required for haversine metric)
    coords = np.radians(df[[lat_col, lon_col]].values)

    # Run HDBSCAN with haversine metric (appropriate for lat/lon)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric="haversine")
    cluster_labels = clusterer.fit_predict(coords)

    # Add cluster labels to dataframe
    df_clustered = df.copy()
    df_clustered["CLUSTER"] = cluster_labels

    # Print clustering summary
    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    n_noise = list(cluster_labels).count(-1)

    print(f"Clustering Results:")
    print(f"  Number of clusters: {n_clusters}")
    print(f"  Number of noise points: {n_noise}")
    print(f"  Percentage assigned: {((len(cluster_labels) - n_noise) / len(cluster_labels) * 100):.1f}%")

    return df_clustered


def compute_cluster_convex_hulls(
    df: pd.DataFrame,
    cluster_col: str = "CLUSTER",
    lat_col: str = "POINT_Y",
    lon_col: str = "POINT_X",
) -> Dict[int, Polygon]:
    """
    Compute convex hull for each cluster.

    Parameters
    ----------
    df : pd.DataFrame
        Clustered dataframe with cluster assignments
    cluster_col : str
        Name of cluster column (default: 'CLUSTER')
    lat_col : str
        Latitude column name (default: 'POINT_Y')
    lon_col : str
        Longitude column name (default: 'POINT_X')

    Returns
    -------
    Dict[int, Polygon]
        Dictionary mapping cluster ID to Shapely Polygon (convex hull)
    """
    # NOTE: ConvexHull operates in Euclidean space on raw lat/lon.
    # For Chile's continental extent (~17°S–56°S) this is an acceptable
    # approximation (<0.5% distortion). A UTM projection would be more
    # rigorous but adds complexity without meaningful accuracy gain here.
    hulls = {}
    n_failed = 0

    for cluster_id in df[cluster_col].unique():
        if cluster_id == -1:  # Skip noise points
            continue

        cluster_points = df[df[cluster_col] == cluster_id][[lat_col, lon_col]].values

        if len(cluster_points) >= 3:
            try:
                hull = ConvexHull(cluster_points)
                hull_vertices = cluster_points[hull.vertices]
                # Create polygon as list of coordinate tuples
                hull_coords = [tuple(pt) for pt in hull_vertices]
                hull_coords.append(hull_coords[0])  # Close the polygon
                hulls[cluster_id] = hull_coords
            except Exception as e:
                n_failed += 1
                print(f"  WARNING: Could not compute hull for cluster {cluster_id}: {e}")

    if n_failed > 0:
        print(f"  {n_failed} cluster(s) failed hull computation out of {len(hulls) + n_failed}")

    return hulls


def get_hull_as_geojson(hull_coords: List[Tuple[float, float]]) -> dict:
    """
    Convert hull coordinate list to GeoJSON format.

    Parameters
    ----------
    hull_coords : List[Tuple[float, float]]
        List of (lat, lon) tuples forming a polygon

    Returns
    -------
    dict
        GeoJSON Feature with Polygon geometry
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
    """
    Generate summary statistics for each cluster.

    Computes per-cluster aggregations including size, primary region/category,
    and percentage by hierarchy level.

    Parameters
    ----------
    df : pd.DataFrame
        Clustered dataframe
    cluster_col : str
        Cluster column name (default: 'CLUSTER')
    region_col : str
        Region column name (default: 'REGION')
    category_col : str
        Category column name (default: 'CATEGORIA')
    hierarchy_col : str
        Hierarchy column name (default: 'JERARQUÍA')

    Returns
    -------
    pd.DataFrame
        Summary statistics per cluster
    """
    # Count attractions per cluster
    summary = df.groupby(cluster_col).agg(
        n_attractions=("NOMBRE", "count"),
        region_principal=(region_col, lambda x: x.value_counts().index[0] if len(x) > 0 and len(x.value_counts()) > 0 else None),
        categoria_principal=(category_col, lambda x: x.value_counts().index[0] if len(x) > 0 and len(x.value_counts()) > 0 else None),
        jerarquia_principal=(hierarchy_col, lambda x: x.value_counts().index[0] if len(x) > 0 and len(x.value_counts()) > 0 else None),
    )

    # Calculate counts and percentages by hierarchy level
    for level in ["INTERNACIONAL", "NACIONAL", "REGIONAL", "LOCAL"]:
        col_lower = level.lower()
        counts = df[df[hierarchy_col] == level].groupby(cluster_col).size()
        summary[f"n_{col_lower}"] = counts.reindex(summary.index, fill_value=0)
        summary[f"pct_{col_lower}"] = (
            (summary[f"n_{col_lower}"] / summary["n_attractions"]) * 100
        ).round(1)

    return summary.sort_values("n_attractions", ascending=False)


def identify_cluster_quality(summary_df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify cluster quality based on hierarchy distribution.

    Parameters
    ----------
    summary_df : pd.DataFrame
        Cluster summary dataframe from summarize_clusters()

    Returns
    -------
    pd.DataFrame
        Input dataframe with added 'quality' column
    """
    summary_df_copy = summary_df.copy()

    def classify_quality(row):
        if row["pct_internacional"] > 0:
            return "High - Has international anchor"
        elif row["pct_nacional"] > 0:
            return "Medium - Has national anchor"
        else:
            return "Low - No anchor attractions"

    summary_df_copy["quality"] = summary_df_copy.apply(classify_quality, axis=1)

    return summary_df_copy
