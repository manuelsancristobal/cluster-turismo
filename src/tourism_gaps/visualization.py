"""Visualization functions for maps and charts."""

from typing import Dict, List, Optional

import folium
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pydeck as pdk
from matplotlib import cm

from . import preprocessing


def create_pydeck_hierarchy_map(
    df: pd.DataFrame,
    lat_col: str = "POINT_Y",
    lon_col: str = "POINT_X",
    color_col: str = "color",
    radius_col: str = "radius",
) -> pdk.Deck:
    """
    Create PyDeck scatter map colored by attraction hierarchy.

    Parameters
    ----------
    df : pd.DataFrame
        Attractions dataframe with color and radius columns
    lat_col : str
        Latitude column (default: 'POINT_Y')
    lon_col : str
        Longitude column (default: 'POINT_X')
    color_col : str
        Color assignment column (default: 'color')
    radius_col : str
        Radius assignment column (default: 'radius')

    Returns
    -------
    pdk.Deck
        Interactive PyDeck map object
    """
    # Compute viewport centered on Chile
    viewport = pdk.ViewState(
        latitude=-35.6751, longitude=-71.5430, zoom=4, pitch=0, bearing=0
    )

    # Create scatterplot layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        pickable=True,
        stroked=False,
        filled=True,
        radiusScale=6,
        radiusMinPixels=2,
        radiusMaxPixels=60,
        lineWidthMinPixels=0,
        get_position=[lon_col, lat_col],
        get_fill_color=color_col,
        get_radius=radius_col,
        get_line_color=[0, 0, 0],
    )

    # Create tooltip
    tooltip = {
        "html": "<b>{NOMBRE}</b><br/>Jerarquía: {JERARQUÍA}<br/>Categoría: {CATEGORIA}",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    }

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=viewport,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/light-v11",
    )

    return deck


def create_pydeck_cluster_map(
    df: pd.DataFrame,
    cluster_hulls: Dict[int, List],
    lat_col: str = "POINT_Y",
    lon_col: str = "POINT_X",
    cluster_col: str = "CLUSTER",
) -> pdk.Deck:
    """
    Create PyDeck map showing clusters with convex hull boundaries.

    Parameters
    ----------
    df : pd.DataFrame
        Clustered attractions dataframe
    cluster_hulls : Dict[int, List]
        Dictionary mapping cluster ID to hull coordinate lists
    lat_col : str
        Latitude column (default: 'POINT_Y')
    lon_col : str
        Longitude column (default: 'POINT_X')
    cluster_col : str
        Cluster column name (default: 'CLUSTER')

    Returns
    -------
    pdk.Deck
        Interactive map with points and polygon boundaries
    """
    # Compute viewport
    viewport = pdk.ViewState(
        latitude=-35.6751, longitude=-71.5430, zoom=4, pitch=0, bearing=0
    )

    # Scatterplot layer for points
    points_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        pickable=True,
        stroked=False,
        filled=True,
        radiusScale=4,
        get_position=[lon_col, lat_col],
        get_fill_color="cluster_color",
        get_radius=150,
    )

    # Polygon layer for cluster hulls
    hull_features = []
    for cluster_id, hull_coords in cluster_hulls.items():
        hull_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [hull_coords]},
                "properties": {"cluster_id": cluster_id},
            }
        )

    hull_geojson = {"type": "FeatureCollection", "features": hull_features}

    polygon_layer = pdk.Layer(
        "GeoJsonLayer",
        data=hull_geojson,
        stroked=True,
        filled=False,
        pickable=False,
        line_width_min_pixels=1,
        get_line_color=[0, 0, 0],
    )

    tooltip = {
        "html": "<b>Cluster {CLUSTER}</b><br/>Atractivos: {n_attractions}",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    }

    deck = pdk.Deck(
        layers=[points_layer, polygon_layer],
        initial_view_state=viewport,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/light-v11",
    )

    return deck


def create_pydeck_gap_map(
    df: pd.DataFrame,
    cluster_hulls: Dict[int, List],
    lat_col: str = "POINT_Y",
    lon_col: str = "POINT_X",
    color_col: str = "anchor_color",
) -> pdk.Deck:
    """
    Create PyDeck map showing investment gaps by anchor status.

    Parameters
    ----------
    df : pd.DataFrame
        Clustered dataframe with anchor_color column
    cluster_hulls : Dict[int, List]
        Cluster boundary polygons
    lat_col : str
        Latitude column (default: 'POINT_Y')
    lon_col : str
        Longitude column (default: 'POINT_X')
    color_col : str
        Color column for anchor status (default: 'anchor_color')

    Returns
    -------
    pdk.Deck
        Interactive gap opportunity map
    """
    # Viewport
    viewport = pdk.ViewState(
        latitude=-35.6751, longitude=-71.5430, zoom=4, pitch=0, bearing=0
    )

    # Points colored by anchor status
    points_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        pickable=True,
        stroked=False,
        filled=True,
        radiusScale=4,
        get_position=[lon_col, lat_col],
        get_fill_color=color_col,
        get_radius=150,
    )

    # Hull polygons
    hull_features = []
    for cluster_id, hull_coords in cluster_hulls.items():
        hull_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [hull_coords]},
                "properties": {"cluster_id": cluster_id},
            }
        )

    hull_geojson = {"type": "FeatureCollection", "features": hull_features}

    polygon_layer = pdk.Layer(
        "GeoJsonLayer",
        data=hull_geojson,
        stroked=True,
        filled=False,
        pickable=False,
        line_width_min_pixels=1,
        get_line_color=[100, 100, 100],
    )

    deck = pdk.Deck(
        layers=[points_layer, polygon_layer],
        initial_view_state=viewport,
        map_style="mapbox://styles/mapbox/light-v11",
    )

    return deck


def create_folium_map(
    center_lat: float = -35.6751, center_lon: float = -71.5430
) -> folium.Map:
    """
    Create base Folium map of Chile.

    Parameters
    ----------
    center_lat : float
        Center latitude (default: Chile center)
    center_lon : float
        Center longitude (default: Chile center)

    Returns
    -------
    folium.Map
        Base Folium map object
    """
    map_obj = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=4,
        tiles="OpenStreetMap",
    )
    return map_obj


def add_attractions_to_folium(
    map_obj: folium.Map,
    df: pd.DataFrame,
    lat_col: str = "POINT_Y",
    lon_col: str = "POINT_X",
    color_col: str = "color",
    name: str = "Attractions",
) -> folium.Map:
    """
    Add attraction points to Folium map.

    Parameters
    ----------
    map_obj : folium.Map
        Folium map to add to
    df : pd.DataFrame
        Attractions dataframe
    lat_col : str
        Latitude column (default: 'POINT_Y')
    lon_col : str
        Longitude column (default: 'POINT_X')
    color_col : str
        Color column (default: 'color')
    name : str
        Feature group name (default: 'Attractions')

    Returns
    -------
    folium.Map
        Updated map object
    """
    fg = folium.FeatureGroup(name=name)

    for idx, row in df.iterrows():
        popup = f"{row.get('NOMBRE')}<br/>Jerarquía: {row.get('JERARQUÍA')}"
        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=3,
            popup=popup,
            color="black",
            fill=True,
            fillColor=f"#{row.get(color_col, 'black')}",
            fillOpacity=0.7,
        ).add_to(fg)

    fg.add_to(map_obj)
    return map_obj


def add_polygons_to_folium(
    map_obj: folium.Map,
    df: pd.DataFrame,
    coords_col: str = "coordinates",
    name_col: str = "nombre",
    color: str = "blue",
    name: str = "Regions",
) -> folium.Map:
    """
    Add polygon boundaries to Folium map.

    Parameters
    ----------
    map_obj : folium.Map
        Folium map to add to
    df : pd.DataFrame
        Dataframe with polygon coordinates
    coords_col : str
        Coordinates column (default: 'coordinates')
    name_col : str
        Name/label column (default: 'nombre')
    color : str
        Polygon color (default: 'blue')
    name : str
        Feature group name (default: 'Regions')

    Returns
    -------
    folium.Map
        Updated map object
    """
    fg = folium.FeatureGroup(name=name)

    for idx, row in df.iterrows():
        coords = row.get(coords_col)
        polygon_name = row.get(name_col)

        if coords and len(coords) >= 3:
            folium.Polygon(
                locations=[[lat, lon] for lon, lat in coords],
                popup=polygon_name,
                color=color,
                fill=True,
                fillOpacity=0.2,
            ).add_to(fg)

    fg.add_to(map_obj)
    return map_obj


def plot_distribution_histograms(
    df: pd.DataFrame, lat_col: str = "POINT_Y", lon_col: str = "POINT_X"
) -> plt.Figure:
    """
    Create histograms of coordinate distributions.

    Parameters
    ----------
    df : pd.DataFrame
        Attractions dataframe
    lat_col : str
        Latitude column (default: 'POINT_Y')
    lon_col : str
        Longitude column (default: 'POINT_X')

    Returns
    -------
    plt.Figure
        Matplotlib figure with histograms
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].hist(df[lon_col], bins=50, color="steelblue", edgecolor="black")
    axes[0].set_xlabel("Longitude")
    axes[0].set_ylabel("Count")
    axes[0].set_title("Distribution of Attractions by Longitude")

    axes[1].hist(df[lat_col], bins=50, color="steelblue", edgecolor="black")
    axes[1].set_xlabel("Latitude")
    axes[1].set_ylabel("Count")
    axes[1].set_title("Distribution of Attractions by Latitude")

    plt.tight_layout()
    return fig


def plot_cluster_bar_chart(summary_df: pd.DataFrame, n_top: int = 15) -> plt.Figure:
    """
    Create horizontal bar chart of attractions per cluster.

    Parameters
    ----------
    summary_df : pd.DataFrame
        Cluster summary dataframe
    n_top : int
        Number of top clusters to show (default: 15)

    Returns
    -------
    plt.Figure
        Matplotlib figure with bar chart
    """
    top = summary_df.head(n_top).sort_values("n_attractions")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(len(top)), top["n_attractions"], color="steelblue", edgecolor="black")
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels([f"Cluster {i}" for i in top.index])
    ax.set_xlabel("Number of Attractions")
    ax.set_title(f"Top {n_top} Clusters by Attraction Count")
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    return fig


def plot_anchor_distribution(
    summary_df: pd.DataFrame, color_map: Optional[Dict] = None
) -> plt.Figure:
    """
    Create donut chart of cluster anchor status distribution.

    Parameters
    ----------
    summary_df : pd.DataFrame
        Cluster summary with anchor_status column
    color_map : Dict, optional
        Color mapping for anchor status (uses default if not provided)

    Returns
    -------
    plt.Figure
        Matplotlib figure with donut chart
    """
    if color_map is None:
        color_map = preprocessing.get_anchor_color_map()

    status_counts = summary_df["anchor_status"].value_counts()
    colors = [color_map.get(status, [100, 100, 100]) for status in status_counts.index]
    colors_normalized = [[c / 255 for c in color] for color in colors]

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        status_counts.values,
        labels=status_counts.index,
        autopct="%1.1f%%",
        colors=colors_normalized,
        startangle=90,
    )

    # Create donut hole
    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    ax.add_artist(centre_circle)

    ax.set_title("Cluster Distribution by Anchor Status")
    plt.tight_layout()
    return fig


def save_pydeck_html(deck: pdk.Deck, filepath: str) -> None:
    """
    Save PyDeck map to HTML file.

    Parameters
    ----------
    deck : pdk.Deck
        PyDeck deck object
    filepath : str
        Output file path
    """
    html = deck.to_html()
    with open(filepath, "w") as f:
        f.write(html)
    print(f"Map saved to {filepath}")


def save_folium_html(map_obj: folium.Map, filepath: str) -> None:
    """
    Save Folium map to HTML file.

    Parameters
    ----------
    map_obj : folium.Map
        Folium map object
    filepath : str
        Output file path
    """
    map_obj.save(filepath)
    print(f"Map saved to {filepath}")
