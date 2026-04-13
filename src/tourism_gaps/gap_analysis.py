"""Gap analysis and opportunity identification functions."""

from typing import Optional

import pandas as pd
from shapely.geometry import Polygon


def classify_anchor_status(df: pd.DataFrame, n_int_col: str = "n_internacional", n_nat_col: str = "n_nacional") -> pd.DataFrame:
    """
    Classify clusters by anchor attraction status.

    Classification logic:
    - 'Con ancla internacional': Has 1+ international-level attractions
    - 'Solo ancla nacional': Has national-level attractions but no international
    - 'Sin ancla': Has no anchor attractions (investment opportunity)

    Parameters
    ----------
    df : pd.DataFrame
        Cluster summary dataframe with counts by hierarchy
    n_int_col : str
        Column name for international attraction count
    n_nat_col : str
        Column name for national attraction count

    Returns
    -------
    pd.DataFrame
        Input dataframe with added 'anchor_status' column
    """

    def classify(row):
        if row[n_int_col] > 0:
            return "Con ancla internacional"
        elif row[n_nat_col] > 0:
            return "Solo ancla nacional"
        else:
            return "Sin ancla"

    df_classified = df.copy()
    df_classified["anchor_status"] = df_classified.apply(classify, axis=1)

    # Print distribution
    print("\nAnchor Status Distribution:")
    print(df_classified["anchor_status"].value_counts())

    return df_classified


def identify_investment_opportunities(df: pd.DataFrame, cluster_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Identify clusters with investment/development opportunities.

    Priority 1 (Highest): Sin ancla - No anchor attractions
    Priority 2 (High): Solo ancla nacional - Only national-level anchors
    Priority 3 (Medium): Con ancla internacional - Full development potential

    Parameters
    ----------
    df : pd.DataFrame
        Full attraction dataframe with cluster assignments
    cluster_summary : pd.DataFrame
        Cluster summary with anchor classifications

    Returns
    -------
    pd.DataFrame
        Opportunities dataframe sorted by priority
    """
    opportunities = cluster_summary[cluster_summary["anchor_status"] != "Con ancla internacional"].copy()

    # Add additional context from full dataframe
    opportunities["communes"] = opportunities.index.map(
        lambda cluster_id: df[df["CLUSTER"] == cluster_id]["COMUNA"].unique()
    )

    opportunities["commune_names"] = opportunities["communes"].apply(
        lambda x: " - ".join(sorted(x.astype(str).unique())) if len(x) > 0 else ""
    )

    # Calculate category diversity
    opportunities["category_diversity"] = opportunities.index.map(
        lambda cluster_id: df[df["CLUSTER"] == cluster_id]["CATEGORIA"].nunique()
    )

    # Assign priority
    def get_priority(row):
        if row["anchor_status"] == "Sin ancla":
            return 1
        elif row["anchor_status"] == "Solo ancla nacional":
            return 2
        else:
            return 3

    opportunities["priority"] = opportunities.apply(get_priority, axis=1)

    return opportunities.sort_values("priority")


def compute_lagging_overlap_type(lagging_poly: Polygon, official_poly: Polygon) -> str:
    """
    Classify how a lagging attraction cluster overlaps with official destinations.

    Classification:
    - 'Contenido': >90% inside official destination
    - 'Parcialmente superpuesto': 10-90% overlap
    - 'Genuinamente rezagado': <10% overlap (independent cluster)

    Parameters
    ----------
    lagging_poly : Polygon
        Polygon of lagging attraction cluster
    official_poly : Polygon
        Polygon of official destination

    Returns
    -------
    str
        Classification of overlap type
    """
    if not lagging_poly.intersects(official_poly):
        return "Separado"

    intersection = lagging_poly.intersection(official_poly)
    overlap_pct = intersection.area / lagging_poly.area if lagging_poly.area > 0 else 0

    if overlap_pct > 0.9:
        return "Contenido"
    elif overlap_pct > 0.1:
        return "Parcialmente superpuesto"
    else:
        return "Genuinamente rezagado"


def compute_cluster_overlap_analysis(
    df_attractions: pd.DataFrame,
    df_cluster_hulls: dict,
    df_destinations: pd.DataFrame,
    dest_polygons: dict,
) -> pd.DataFrame:
    """
    Analyze how lagging clusters overlap with official destinations.

    Parameters
    ----------
    df_attractions : pd.DataFrame
        Full attractions dataframe with cluster assignments
    df_cluster_hulls : dict
        Mapping of cluster ID to hull polygons
    df_destinations : pd.DataFrame
        Destinations dataframe
    dest_polygons : dict
        Mapping of destination ID to Shapely Polygon

    Returns
    -------
    pd.DataFrame
        Analysis results with overlap classifications and recommendations
    """
    results = []

    # Identify lagging clusters (those with attractions outside official destinations)
    lagging_clusters = df_attractions[df_attractions["nombre"].isna()]["CLUSTER"].unique()

    for cluster_id in lagging_clusters:
        if cluster_id == -1:  # Skip noise
            continue

        cluster_data = df_attractions[df_attractions["CLUSTER"] == cluster_id]

        if cluster_id not in df_cluster_hulls:
            continue

        lagging_poly = Polygon(df_cluster_hulls[cluster_id])

        # Check overlap with each official destination
        best_overlap = None
        best_overlap_type = None

        for dest_name, dest_poly in dest_polygons.items():
            overlap_type = compute_lagging_overlap_type(lagging_poly, dest_poly)
            if best_overlap is None:
                best_overlap = dest_name
                best_overlap_type = overlap_type

        results.append(
            {
                "cluster_id": cluster_id,
                "n_attractions": len(cluster_data),
                "main_region": cluster_data["REGION"].value_counts().index[0] if len(cluster_data) > 0 else None,
                "overlap_type": best_overlap_type,
                "nearest_destination": best_overlap,
                "n_internacional": (cluster_data["JERARQUÍA"] == "INTERNACIONAL").sum(),
                "n_nacional": (cluster_data["JERARQUÍA"] == "NACIONAL").sum(),
            }
        )

    return pd.DataFrame(results)


def generate_opportunity_report(
    opportunities: pd.DataFrame, region_col: str = "region_principal"
) -> pd.DataFrame:
    """
    Generate executive summary of opportunities by region.

    Parameters
    ----------
    opportunities : pd.DataFrame
        Opportunities dataframe from identify_investment_opportunities()
    region_col : str
        Column name for region (default: 'region_principal')

    Returns
    -------
    pd.DataFrame
        Summary statistics by region
    """
    report = opportunities.groupby(region_col).agg(
        n_opportunity_clusters=("anchor_status", "count"),
        total_attractions=("n_attractions", "sum"),
        avg_attractions_per_cluster=("n_attractions", "mean"),
        n_sin_ancla=("anchor_status", lambda x: (x == "Sin ancla").sum()),
        n_solo_nacional=("anchor_status", lambda x: (x == "Solo ancla nacional").sum()),
    )

    report = report.round(1).sort_values("n_opportunity_clusters", ascending=False)

    return report
