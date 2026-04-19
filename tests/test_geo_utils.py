"""Tests for geo_utils module."""

import pandas as pd
import pytest
from shapely.geometry import Polygon

from cluster_turismo import geo_utils


def test_build_shapely_polygons():
    """Test building Shapely polygons from dataframe."""
    df = pd.DataFrame(
        {
            "nombre": ["Dest1", "Dest2"],
            "coordinates": [
                [(-70, -33), (-71, -33), (-71, -34), (-70, -34), (-70, -33)],
                [(-72, -35), (-73, -35), (-73, -36), (-72, -36), (-72, -35)],
            ],
        }
    )
    polygons = geo_utils.build_shapely_polygons(df)
    assert len(polygons) == 2
    assert "Dest1" in polygons
    assert isinstance(polygons["Dest1"], Polygon)


def test_build_shapely_polygons_skips_invalid():
    """Test that entries with too few coords are skipped."""
    df = pd.DataFrame(
        {
            "nombre": ["Good", "Bad"],
            "coordinates": [
                [(-70, -33), (-71, -33), (-71, -34), (-70, -34)],
                [(-70, -33)],  # Only 1 point — not enough
            ],
        }
    )
    polygons = geo_utils.build_shapely_polygons(df)
    assert "Good" in polygons
    assert "Bad" not in polygons


def test_build_shapely_polygons_skips_unnamed():
    """Test that entries without names are skipped."""
    df = pd.DataFrame(
        {
            "nombre": [None],
            "coordinates": [[(-70, -33), (-71, -33), (-71, -34), (-70, -34)]],
        }
    )
    polygons = geo_utils.build_shapely_polygons(df)
    assert len(polygons) == 0


def test_point_in_polygon_check():
    """Test point-in-polygon containment check."""
    points = pd.DataFrame(
        {
            "NOMBRE": ["Inside", "Outside"],
            "POINT_Y": [-33.5, -40.0],
            "POINT_X": [-70.5, -75.0],
        }
    )
    polygons = pd.DataFrame(
        {
            "nombre": ["Dest1"],
            "coordinates": [[(-71, -33), (-70, -33), (-70, -34), (-71, -34), (-71, -33)]],
        }
    )
    result = geo_utils.point_in_polygon_check(points, polygons)
    assert "in_destination" in result.columns
    assert "destination_name" in result.columns
    assert result.iloc[0]["in_destination"]
    assert result.iloc[0]["destination_name"] == "Dest1"
    assert not result.iloc[1]["in_destination"]
    assert pd.isna(result.iloc[1]["destination_name"])


def test_compute_cluster_centroid():
    """Test centroid computation."""
    df = pd.DataFrame(
        {
            "POINT_Y": [-33.0, -35.0],
            "POINT_X": [-70.0, -72.0],
        }
    )
    lat, lon = geo_utils.compute_cluster_centroid(df)
    assert lat == pytest.approx(-34.0)
    assert lon == pytest.approx(-71.0)


def test_compute_geographic_bounds():
    """Test bounding box computation."""
    df = pd.DataFrame(
        {
            "POINT_Y": [-33.0, -35.0, -34.0],
            "POINT_X": [-70.0, -72.0, -71.0],
        }
    )
    bounds = geo_utils.compute_geographic_bounds(df)
    assert bounds["north"] == -33.0
    assert bounds["south"] == -35.0
    assert bounds["east"] == -70.0
    assert bounds["west"] == -72.0


def test_haversine_distance_same_point():
    """Test that distance between same point is zero."""
    d = geo_utils.haversine_distance(-33.0, -70.0, -33.0, -70.0)
    assert d == pytest.approx(0.0)


def test_haversine_distance_known():
    """Test haversine with a known approximate distance."""
    # Santiago (-33.45, -70.65) to Valparaiso (-33.05, -71.62) ~100km
    d = geo_utils.haversine_distance(-33.45, -70.65, -33.05, -71.62)
    assert 80 < d < 120
