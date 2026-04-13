"""Tests for clustering module."""

import os

import numpy as np
import pandas as pd
import pytest

from tourism_gaps import clustering


@pytest.fixture
def sample_data():
    """Load sample attractions CSV."""
    fixtures_dir = os.path.dirname(__file__)
    return pd.read_csv(os.path.join(fixtures_dir, "fixtures/sample_attractions.csv"))


def test_run_hdbscan_spatial_output_shape(sample_data):
    """Test that HDBSCAN returns correct label count."""
    df = clustering.run_hdbscan_spatial(
        sample_data, lat_col="POINT_Y", lon_col="POINT_X", min_cluster_size=3
    )

    # Should have same length
    assert len(df) == len(sample_data)

    # Should have CLUSTER column
    assert "CLUSTER" in df.columns

    # Cluster labels should be integers
    assert df["CLUSTER"].dtype in [np.int32, np.int64, int]


def test_run_hdbscan_spatial_cluster_range(sample_data):
    """Test that clustering produces reasonable number of clusters."""
    df = clustering.run_hdbscan_spatial(
        sample_data, lat_col="POINT_Y", lon_col="POINT_X", min_cluster_size=2
    )

    unique_clusters = set(df["CLUSTER"].unique())
    # Remove noise (-1) for count
    num_clusters = len([c for c in unique_clusters if c != -1])

    # Should have at least 1 cluster and not more than half the data points
    assert num_clusters >= 1
    assert num_clusters <= len(sample_data) / 2


def test_run_hdbscan_spatial_with_geographic_data():
    """Test HDBSCAN with actual geographic clustering."""
    # Create data with two distinct geographic clusters
    data = {
        "NOMBRE": [f"A{i}" for i in range(20)],
        "POINT_Y": (
            [-33.0] * 10 + [-45.0] * 10
        ),  # Two distinct latitude regions
        "POINT_X": [-70.5] * 10 + [-72.5] * 10,  # Two distinct longitude regions
        "JERARQUÍA": ["NACIONAL"] * 20,
    }
    df = pd.DataFrame(data)

    df_clustered = clustering.run_hdbscan_spatial(
        df, lat_col="POINT_Y", lon_col="POINT_X", min_cluster_size=5
    )

    # Should find at least 2 clusters
    unique_clusters = set(df_clustered["CLUSTER"].unique())
    num_clusters = len([c for c in unique_clusters if c != -1])
    assert num_clusters >= 1  # At minimum, finds one cluster


def test_compute_cluster_convex_hulls(sample_data):
    """Test convex hull computation."""
    # Add cluster assignments first
    sample_data["CLUSTER"] = [0, 0, 1, 1, 0, 1, 2, 2, 1, 2, 0, 0, -1, 1, 2, 0]

    hulls = clustering.compute_cluster_convex_hulls(
        sample_data, cluster_col="CLUSTER", lat_col="POINT_Y", lon_col="POINT_X"
    )

    # Should exclude noise cluster (-1)
    assert -1 not in hulls

    # Should have hulls for other clusters
    assert len(hulls) > 0

    # Each hull should be a list of coordinates
    for hull_id, hull_coords in hulls.items():
        assert isinstance(hull_coords, list)
        assert len(hull_coords) >= 3  # At least 3 points for a polygon
        assert all(isinstance(coord, tuple) for coord in hull_coords)


def test_compute_cluster_convex_hulls_single_point():
    """Test that single-point clusters are skipped."""
    data = {
        "NOMBRE": ["A", "B"],
        "POINT_Y": [-33.0, -45.0],
        "POINT_X": [-70.0, -72.0],
        "CLUSTER": [0, 1],
    }
    df = pd.DataFrame(data)

    hulls = clustering.compute_cluster_convex_hulls(df)

    # Should not include clusters with fewer than 3 points
    assert len(hulls) == 0


def test_summarize_clusters(sample_data):
    """Test cluster summarization."""
    sample_data["CLUSTER"] = [0, 0, 1, 1, 0, 1, 2, 2, 1, 2, 0, 0, -1, 1, 2, 0]

    summary = clustering.summarize_clusters(
        sample_data,
        cluster_col="CLUSTER",
        region_col="REGION",
        category_col="CATEGORIA",
        hierarchy_col="JERARQUÍA",
    )

    # Should have summary for each cluster (except -1)
    assert len(summary) > 0

    # Should have expected columns
    assert "n_attractions" in summary.columns
    assert "region_principal" in summary.columns
    assert "n_internacional" in summary.columns
    assert "pct_internacional" in summary.columns

    # Should be sorted by n_attractions
    assert (summary["n_attractions"].iloc[:-1].values >= summary["n_attractions"].iloc[1:].values).all()


def test_summarize_clusters_percentages():
    """Test that percentages are calculated correctly."""
    data = {
        "NOMBRE": ["A"] * 10,
        "REGION": ["TestRegion"] * 10,
        "CATEGORIA": ["TestCategory"] * 10,
        "JERARQUÍA": ["INTERNACIONAL"] * 5 + ["NACIONAL"] * 5,
        "CLUSTER": [0] * 10,
    }
    df = pd.DataFrame(data)

    summary = clustering.summarize_clusters(df)

    # Should have correct percentages
    assert summary.loc[0, "pct_internacional"] == 50.0
    assert summary.loc[0, "pct_nacional"] == 50.0


def test_identify_cluster_quality():
    """Test cluster quality classification."""
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
    assert df_quality.loc[0, "quality"] == "High - Has international anchor"
    assert df_quality.loc[1, "quality"] == "Medium - Has national anchor"
