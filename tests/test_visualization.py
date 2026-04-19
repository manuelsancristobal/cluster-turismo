"""Tests for visualization module."""

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for tests

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from cluster_turismo import visualization


@pytest.fixture
def sample_styled_data():
    """Create sample dataframe with styling columns."""
    df = pd.DataFrame(
        {
            "NOMBRE": ["A", "B", "C"],
            "POINT_Y": [-33.0, -34.0, -35.0],
            "POINT_X": [-70.0, -71.0, -72.0],
            "JERARQUIA": ["INTERNACIONAL", "NACIONAL", "LOCAL"],
            "CATEGORIA": ["Cultura", "Naturaleza", "Deporte"],
            "CLUSTER": [0, 0, 1],
            "color": [[220, 30, 120], [70, 130, 180], [180, 180, 180]],
            "radius": [3, 2, 1],
        }
    )
    return df


@pytest.fixture
def sample_summary():
    """Create sample cluster summary with anchor status."""
    df = pd.DataFrame(
        {
            "n_attractions": [10, 5, 3],
            "anchor_status": ["Con ancla internacional", "Solo ancla nacional", "Sin ancla"],
            "n_internacional": [3, 0, 0],
            "n_nacional": [5, 3, 0],
        },
        index=[0, 1, 2],
    )
    return df


def test_create_folium_map():
    """Test base Folium map creation."""
    m = visualization.create_folium_map()
    assert m is not None
    html = m._repr_html_()
    assert "leaflet" in html.lower() or "folium" in html.lower() or len(html) > 100


def test_create_folium_map_custom_center():
    """Test Folium map with custom center."""
    m = visualization.create_folium_map(center_lat=-27.0, center_lon=-70.0)
    assert m is not None


def test_plot_distribution_histograms():
    """Test histogram generation returns valid figure."""
    df = pd.DataFrame(
        {
            "POINT_Y": [-33.0, -34.0, -35.0, -36.0],
            "POINT_X": [-70.0, -71.0, -72.0, -73.0],
        }
    )
    fig = visualization.plot_distribution_histograms(df)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_plot_cluster_bar_chart():
    """Test cluster bar chart generation."""
    df = pd.DataFrame(
        {
            "n_attractions": [50, 30, 20, 10],
        },
        index=[0, 1, 2, 3],
    )
    fig = visualization.plot_cluster_bar_chart(df, n_top=3)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    # Check that bars are drawn
    ax = fig.axes[0]
    assert len(ax.patches) == 3
    plt.close(fig)


def test_plot_anchor_distribution(sample_summary):
    """Test anchor donut chart generation."""
    fig = visualization.plot_anchor_distribution(sample_summary)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_add_attractions_to_folium():
    """Test adding attraction markers to Folium map."""
    m = visualization.create_folium_map()
    df = pd.DataFrame(
        {
            "NOMBRE": ["A", "B"],
            "POINT_Y": [-33.0, -34.0],
            "POINT_X": [-70.0, -71.0],
            "JERARQUIA": ["INTERNACIONAL", "NACIONAL"],
            "color": ["red", "blue"],
        }
    )
    result = visualization.add_attractions_to_folium(m, df)
    assert result is not None


def test_add_polygons_to_folium():
    """Test adding polygon boundaries to Folium map."""
    m = visualization.create_folium_map()
    df = pd.DataFrame(
        {
            "nombre": ["Region1"],
            "coordinates": [[(-70, -33), (-71, -33), (-71, -34), (-70, -34), (-70, -33)]],
        }
    )
    result = visualization.add_polygons_to_folium(m, df)
    assert result is not None


def test_save_folium_html(tmp_path):
    """Test saving Folium map to HTML."""
    m = visualization.create_folium_map()
    path = str(tmp_path / "test_map.html")
    visualization.save_folium_html(m, path)
    with open(path) as f:
        content = f.read()
    assert len(content) > 100
    assert "leaflet" in content.lower() or "map" in content.lower()
