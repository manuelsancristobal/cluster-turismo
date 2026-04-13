"""Tests for preprocessing module."""

import os

import pandas as pd
import pytest

from tourism_gaps import preprocessing


@pytest.fixture
def sample_data():
    """Load sample attractions CSV."""
    fixtures_dir = os.path.dirname(__file__)
    return pd.read_csv(os.path.join(fixtures_dir, "fixtures/sample_attractions.csv"))


def test_filter_permanent_attractions(sample_data):
    """Test that events are filtered out."""
    df = preprocessing.filter_permanent_attractions(sample_data)

    # Should remove the "ACONTECIMIENTOS PROGRAMADOS" row
    assert len(df) < len(sample_data)
    assert (df["CATEGORIA"] == "ACONTECIMIENTOS PROGRAMADOS").sum() == 0

    # Should keep all other attractions
    assert len(df) == len(sample_data) - 1


def test_validate_coordinates(sample_data):
    """Test coordinate validation for Chilean bounds."""
    df = preprocessing.validate_coordinates(sample_data)

    # All coordinates should be within Chilean bounds
    assert (df["POINT_Y"] >= -56).all()
    assert (df["POINT_Y"] <= -17).all()
    assert (df["POINT_X"] >= -75).all()
    assert (df["POINT_X"] <= -66).all()


def test_validate_coordinates_removes_outliers():
    """Test that invalid coordinates are removed."""
    data = {
        "NOMBRE": ["Valid1", "Invalid1", "Valid2", "Invalid2"],
        "POINT_Y": [-33.0, -60.0, -35.0, -10.0],  # -60 and -10 are out of bounds
        "POINT_X": [-70.0, -70.0, -71.0, -71.0],
    }
    df = pd.DataFrame(data)
    df_valid = preprocessing.validate_coordinates(df)

    assert len(df_valid) == 2
    assert "Valid1" in df_valid["NOMBRE"].values
    assert "Valid2" in df_valid["NOMBRE"].values


def test_normalize_commune_codes():
    """Test that commune codes are normalized."""
    data = {
        "COD_COM": ["  01001  ", "02001", " 03001"],
        "NOMBRE": ["A", "B", "C"],
    }
    df = pd.DataFrame(data)
    df_norm = preprocessing.normalize_commune_codes(df)

    expected = ["01001", "02001", "03001"]
    assert df_norm["COD_COM"].tolist() == expected


def test_get_hierarchy_color_map():
    """Test hierarchy color mapping."""
    colors = preprocessing.get_hierarchy_color_map()

    assert "INTERNACIONAL" in colors
    assert "NACIONAL" in colors
    assert "REGIONAL" in colors
    assert "LOCAL" in colors

    # Check format (RGB list)
    for color in colors.values():
        assert len(color) == 3
        assert all(isinstance(c, int) for c in color)


def test_get_hierarchy_radius_map():
    """Test hierarchy radius mapping."""
    radii = preprocessing.get_hierarchy_radius_map()

    assert radii["INTERNACIONAL"] > radii["LOCAL"]
    assert radii["NACIONAL"] > radii["REGIONAL"]


def test_assign_hierarchy_styling(sample_data):
    """Test that styling columns are added."""
    df = preprocessing.assign_hierarchy_styling(sample_data)

    assert "color" in df.columns
    assert "radius" in df.columns
    assert len(df) == len(sample_data)

    # Check that colors were mapped correctly
    assert df[df["JERARQUÍA"] == "INTERNACIONAL"]["color"].notna().all()


def test_get_cluster_color_palette():
    """Test cluster color generation."""
    colors = preprocessing.get_cluster_color_palette(30)

    assert len(colors) == 30
    # Check format
    for cluster_id, color in colors.items():
        assert len(color) == 3


def test_assign_cluster_colors(sample_data):
    """Test cluster color assignment."""
    # Add dummy cluster column
    sample_data["CLUSTER"] = [0, 0, 1, 1, 0, 1, 2, 2, 1, 2, 0, 0, -1, 1, 2, 0]

    df = preprocessing.assign_cluster_colors(sample_data, n_clusters=3)

    assert "cluster_color" in df.columns
    assert len(df) == len(sample_data)


def test_get_anchor_color_map():
    """Test anchor status color mapping."""
    colors = preprocessing.get_anchor_color_map()

    assert "Con ancla internacional" in colors
    assert "Solo ancla nacional" in colors
    assert "Sin ancla" in colors
    assert "Ruido" in colors

    # Check colors are distinct
    unique_colors = set(str(c) for c in colors.values())
    assert len(unique_colors) == 4
