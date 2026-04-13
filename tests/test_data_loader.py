"""Tests for data_loader module."""

import os
import tempfile
import zipfile

import pandas as pd
import pytest

from tourism_gaps import data_loader


def test_load_attractions_excel(tmp_path):
    """Test loading attractions from Excel."""
    df = pd.DataFrame({
        "NOMBRE": ["A", "B"],
        "POINT_Y": [-33.0, -34.0],
        "POINT_X": [-70.0, -71.0],
    })
    path = tmp_path / "test.xlsx"
    df.to_excel(path, index=False)

    result = data_loader.load_attractions_excel(str(path))
    assert len(result) == 2
    assert "NOMBRE" in result.columns
    assert result["NOMBRE"].tolist() == ["A", "B"]


def test_extract_kml_from_kmz(tmp_path):
    """Test KML extraction from KMZ archive."""
    kml_content = '<?xml version="1.0"?><kml><Document></Document></kml>'
    kmz_path = tmp_path / "test.kmz"
    with zipfile.ZipFile(kmz_path, "w") as zf:
        zf.writestr("doc.kml", kml_content)

    result = data_loader.extract_kml_from_kmz(str(kmz_path))
    assert "<kml>" in result
    assert "<Document>" in result


def test_parse_kml_placemarks():
    """Test KML placemark parsing."""
    kml = """
    <Placemark>
        <name>Dest1</name>
        <ExtendedData><SchemaData>
            <SimpleData name="codigo">C01</SimpleData>
            <SimpleData name="region">RegionA</SimpleData>
            <SimpleData name="tipo">TipoA</SimpleData>
        </SchemaData></ExtendedData>
        <Polygon><outerBoundaryIs><LinearRing>
            <coordinates>-70.0,-33.0,0 -71.0,-33.0,0 -71.0,-34.0,0 -70.0,-34.0,0 -70.0,-33.0,0</coordinates>
        </LinearRing></outerBoundaryIs></Polygon>
    </Placemark>
    """
    placemarks = data_loader.parse_kml_placemarks(kml)
    assert len(placemarks) == 1
    assert placemarks[0]["nombre"] == "Dest1"
    assert placemarks[0]["codigo"] == "C01"
    assert placemarks[0]["region"] == "RegionA"
    assert len(placemarks[0]["coordinates"]) == 5


def test_parse_kml_placemarks_skips_unnamed():
    """Test that placemarks without names are skipped."""
    kml = """
    <Placemark>
        <Polygon><outerBoundaryIs><LinearRing>
            <coordinates>-70.0,-33.0,0 -71.0,-33.0,0 -71.0,-34.0,0</coordinates>
        </LinearRing></outerBoundaryIs></Polygon>
    </Placemark>
    """
    placemarks = data_loader.parse_kml_placemarks(kml)
    assert len(placemarks) == 0


def test_extract_kml_field():
    """Test SimpleData field extraction."""
    content = '<SimpleData name="region">Atacama</SimpleData>'
    assert data_loader.extract_kml_field(content, "region") == "Atacama"
    assert data_loader.extract_kml_field(content, "nonexistent") is None


def test_extract_coordinates_from_linearring():
    """Test coordinate extraction from LinearRing."""
    content = """
    <LinearRing>
        <coordinates>-70.0,-33.0,0 -71.0,-34.0,0 -72.0,-35.0,0</coordinates>
    </LinearRing>
    """
    coords = data_loader.extract_coordinates_from_linearring(content)
    assert len(coords) == 3
    assert coords[0] == (-70.0, -33.0)
    assert coords[1] == (-71.0, -34.0)


def test_extract_coordinates_from_linearring_empty():
    """Test coordinate extraction with no LinearRing."""
    coords = data_loader.extract_coordinates_from_linearring("<Point></Point>")
    assert coords == []


def test_simplify_polygon_coordinates_noop():
    """Test that short coordinate lists are returned unchanged."""
    coords = [(0, 0), (1, 1), (2, 2)]
    result = data_loader.simplify_polygon_coordinates(coords, max_points=10)
    assert result == coords


def test_simplify_polygon_coordinates_reduces():
    """Test that long coordinate lists are simplified."""
    coords = [(i, i) for i in range(200)]
    result = data_loader.simplify_polygon_coordinates(coords, max_points=50)
    assert len(result) <= 55  # some tolerance for rounding
    assert result[0] == coords[0]
    assert result[-1] == coords[-1]
