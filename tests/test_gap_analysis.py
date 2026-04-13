"""Tests for gap_analysis module."""

import pandas as pd
import pytest
from shapely.geometry import Polygon

from tourism_gaps import gap_analysis


@pytest.fixture
def cluster_summary():
    """Create sample cluster summary data."""
    return pd.DataFrame(
        {
            "n_internacional": [2, 0, 1, 0],
            "n_nacional": [5, 3, 0, 0],
            "n_attractions": [10, 5, 8, 3],
            "region_principal": ["Región A", "Región B", "Región C", "Región D"],
        },
        index=[0, 1, 2, 3],
    )


def test_classify_anchor_status_with_internacional(cluster_summary):
    """Test classification of cluster with international anchor."""
    df = gap_analysis.classify_anchor_status(cluster_summary)

    assert df.loc[0, "anchor_status"] == "Con ancla internacional"


def test_classify_anchor_status_solo_nacional(cluster_summary):
    """Test classification of cluster with only national anchor."""
    df = gap_analysis.classify_anchor_status(cluster_summary)

    assert df.loc[1, "anchor_status"] == "Solo ancla nacional"
    # Cluster 2 has n_internacional=1, so it's "Con ancla internacional"
    assert df.loc[2, "anchor_status"] == "Con ancla internacional"


def test_classify_anchor_status_sin_ancla(cluster_summary):
    """Test classification of cluster with no anchor."""
    df = gap_analysis.classify_anchor_status(cluster_summary)

    assert df.loc[3, "anchor_status"] == "Sin ancla"


def test_classify_anchor_status_all_have_status(cluster_summary):
    """Test that all clusters get classified."""
    df = gap_analysis.classify_anchor_status(cluster_summary)

    assert df["anchor_status"].notna().all()
    assert len(df) == len(cluster_summary)


def test_identify_investment_opportunities(cluster_summary):
    """Test opportunity identification."""
    attractions_data = {
        "NOMBRE": [f"Atr{i}" for i in range(20)],
        "CLUSTER": [0] * 10 + [1] * 5 + [2] * 3 + [3] * 2,
        "CATEGORIA": ["Naturaleza"] * 20,
        "COMUNA": ["Comuna A"] * 10 + ["Comuna B"] * 5 + ["Comuna C"] * 3 + ["Comuna D"] * 2,
        "JERARQUÍA": ["NACIONAL"] * 20,
    }
    df_attr = pd.DataFrame(attractions_data)

    df_class = gap_analysis.classify_anchor_status(cluster_summary)
    opportunities = gap_analysis.identify_investment_opportunities(df_attr, df_class)

    # Should exclude clusters with international anchor (0 and 2)
    assert 0 not in opportunities.index
    assert 2 not in opportunities.index

    # Should include clusters without international anchor
    assert 1 in opportunities.index or 3 in opportunities.index

    # Should have priority column
    assert "priority" in opportunities.columns


def test_identify_investment_opportunities_priority():
    """Test that opportunities are prioritized correctly."""
    summary_data = {
        "n_internacional": [0, 0, 0],
        "n_nacional": [0, 5, 0],
        "n_attractions": [5, 8, 10],
        "region_principal": ["A", "B", "C"],
    }
    summary_df = pd.DataFrame(summary_data, index=[1, 2, 3])

    attractions_data = {
        "NOMBRE": [f"Atr{i}" for i in range(23)],
        "CLUSTER": [1] * 5 + [2] * 8 + [3] * 10,
        "CATEGORIA": ["Test"] * 23,
        "COMUNA": ["C"] * 23,
        "JERARQUÍA": ["LOCAL"] * 23,
    }
    df_attr = pd.DataFrame(attractions_data)

    df_class = gap_analysis.classify_anchor_status(summary_df)
    opp = gap_analysis.identify_investment_opportunities(df_attr, df_class)

    # Priority 1 (Sin ancla) should come first
    assert opp.iloc[0]["anchor_status"] == "Sin ancla"
    # Priority 2 (Solo nacional) should come last (there are 2 Sin ancla clusters)
    assert opp.iloc[-1]["anchor_status"] == "Solo ancla nacional"


def test_compute_lagging_overlap_type_contained():
    """Test overlap classification for fully contained cluster."""
    # Small polygon inside large polygon
    lagging = Polygon([(-70.0, -33.0), (-70.1, -33.0), (-70.1, -33.1), (-70.0, -33.1)])
    official = Polygon(
        [(-71.0, -32.0), (-69.0, -32.0), (-69.0, -34.0), (-71.0, -34.0)]
    )

    result = gap_analysis.compute_lagging_overlap_type(lagging, official)
    assert result == "Contenido"


def test_compute_lagging_overlap_type_partial():
    """Test overlap classification for partially overlapping clusters."""
    lagging = Polygon([(-70.0, -33.0), (-70.3, -33.0), (-70.3, -33.3), (-70.0, -33.3)])
    official = Polygon(
        [(-70.2, -33.0), (-70.5, -33.0), (-70.5, -33.3), (-70.2, -33.3)]
    )

    result = gap_analysis.compute_lagging_overlap_type(lagging, official)
    assert result == "Parcialmente superpuesto"


def test_compute_lagging_overlap_type_separate():
    """Test overlap classification for separate clusters."""
    lagging = Polygon([(-70.0, -33.0), (-70.1, -33.0), (-70.1, -33.1), (-70.0, -33.1)])
    official = Polygon(
        [(-70.5, -34.0), (-70.6, -34.0), (-70.6, -34.1), (-70.5, -34.1)]
    )

    result = gap_analysis.compute_lagging_overlap_type(lagging, official)
    assert result == "Separado"


def test_compute_cluster_overlap_analysis():
    """Test overlap analysis with actual polygon computation."""
    # Create attractions data with clusters
    df = pd.DataFrame({
        "NOMBRE": [f"A{i}" for i in range(6)],
        "CLUSTER": [0, 0, 0, 1, 1, 1],
        "REGION": ["R1"] * 6,
        "JERARQUIA": ["NACIONAL"] * 3 + ["LOCAL"] * 3,
        "nombre": [None] * 6,  # All "lagging" (no destination match)
    })

    # Cluster hulls — cluster 0 contained inside dest, cluster 1 separate
    cluster_hulls = {
        0: [(-70.0, -33.0), (-70.1, -33.0), (-70.1, -33.1), (-70.0, -33.1), (-70.0, -33.0)],
        1: [(-75.0, -50.0), (-75.1, -50.0), (-75.1, -50.1), (-75.0, -50.1), (-75.0, -50.0)],
    }

    # Destination polygons — large area around cluster 0
    dest_polygons = {
        "DestA": Polygon([(-71, -32), (-69, -32), (-69, -34), (-71, -34)]),
    }

    result = gap_analysis.compute_cluster_overlap_analysis(
        df, cluster_hulls, pd.DataFrame(), dest_polygons
    )

    assert len(result) == 2
    assert "overlap_type" in result.columns
    assert "nearest_destination" in result.columns

    # Cluster 0 should be "Contenido" (inside DestA)
    row0 = result[result["cluster_id"] == 0].iloc[0]
    assert row0["overlap_type"] == "Contenido"
    assert row0["nearest_destination"] == "DestA"

    # Cluster 1 should be "Separado" or "Genuinamente rezagado" (far away)
    row1 = result[result["cluster_id"] == 1].iloc[0]
    assert row1["overlap_type"] in ("Separado", "Genuinamente rezagado")


def test_generate_opportunity_report(cluster_summary):
    """Test opportunity report generation."""
    df_class = gap_analysis.classify_anchor_status(cluster_summary)
    report = gap_analysis.generate_opportunity_report(df_class)

    # Should have aggregations by region
    assert len(report) > 0

    # Should have expected columns
    assert "n_opportunity_clusters" in report.columns
    assert "total_attractions" in report.columns
    assert "n_sin_ancla" in report.columns
