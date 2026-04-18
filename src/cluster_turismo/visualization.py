"""Funciones de visualización para mapas y gráficos."""

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
    Crea un mapa de dispersión PyDeck coloreado por jerarquía de atractivos.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataframe de atractivos con columnas de color y radio
    lat_col : str
        Columna de latitud (por defecto: 'POINT_Y')
    lon_col : str
        Columna de longitud (por defecto: 'POINT_X')
    color_col : str
        Columna de asignación de color (por defecto: 'color')
    radius_col : str
        Columna de asignación de radio (por defecto: 'radius')

    Retorna
    -------
    pdk.Deck
        Objeto de mapa PyDeck interactivo
    """
    # Calcular vista centrada en Chile
    viewport = pdk.ViewState(
        latitude=-35.6751, longitude=-71.5430, zoom=4, pitch=0, bearing=0
    )

    # Crear capa de dispersión
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

    # Crear tooltip
    tooltip = {
        "html": "<b>{NOMBRE}</b><br/>Jerarquía: {JERARQUIA}<br/>Categoría: {CATEGORIA}",
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
    Crea un mapa PyDeck mostrando clústeres con límites de envolvente convexa.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataframe de atractivos agrupados en clústeres
    cluster_hulls : Dict[int, List]
        Diccionario que mapea ID de clúster a listas de coordenadas de envolvente
    lat_col : str
        Columna de latitud (por defecto: 'POINT_Y')
    lon_col : str
        Columna de longitud (por defecto: 'POINT_X')
    cluster_col : str
        Nombre de columna de clúster (por defecto: 'CLUSTER')

    Retorna
    -------
    pdk.Deck
        Mapa interactivo con puntos y límites poligonales
    """
    # Calcular vista
    viewport = pdk.ViewState(
        latitude=-35.6751, longitude=-71.5430, zoom=4, pitch=0, bearing=0
    )

    # Capa de dispersión para puntos
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

    # Capa de polígonos para envolventes de clústeres
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
    Crea un mapa PyDeck mostrando brechas de inversión por estado de ancla.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataframe agrupado con columna anchor_color
    cluster_hulls : Dict[int, List]
        Polígonos de límites de clústeres
    lat_col : str
        Columna de latitud (por defecto: 'POINT_Y')
    lon_col : str
        Columna de longitud (por defecto: 'POINT_X')
    color_col : str
        Columna de color para estado de ancla (por defecto: 'anchor_color')

    Retorna
    -------
    pdk.Deck
        Mapa interactivo de oportunidades de brecha
    """
    # Vista
    viewport = pdk.ViewState(
        latitude=-35.6751, longitude=-71.5430, zoom=4, pitch=0, bearing=0
    )

    # Puntos coloreados por estado de ancla
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

    # Polígonos de envolventes
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
    Crea un mapa base Folium de Chile.

    Parámetros
    ----------
    center_lat : float
        Latitud central (por defecto: centro de Chile)
    center_lon : float
        Longitud central (por defecto: centro de Chile)

    Retorna
    -------
    folium.Map
        Objeto de mapa base Folium
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
    Agrega puntos de atractivos al mapa Folium.

    Parámetros
    ----------
    map_obj : folium.Map
        Mapa Folium al que agregar
    df : pd.DataFrame
        Dataframe de atractivos
    lat_col : str
        Columna de latitud (por defecto: 'POINT_Y')
    lon_col : str
        Columna de longitud (por defecto: 'POINT_X')
    color_col : str
        Columna de color (por defecto: 'color')
    name : str
        Nombre del grupo de características (por defecto: 'Attractions')

    Retorna
    -------
    folium.Map
        Objeto de mapa actualizado
    """
    fg = folium.FeatureGroup(name=name)

    for idx, row in df.iterrows():
        popup = f"{row.get('NOMBRE')}<br/>Jerarquía: {row.get('JERARQUIA', row.get('JERARQUÍA'))}"
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
    Agrega límites poligonales al mapa Folium.

    Parámetros
    ----------
    map_obj : folium.Map
        Mapa Folium al que agregar
    df : pd.DataFrame
        Dataframe con coordenadas de polígonos
    coords_col : str
        Columna de coordenadas (por defecto: 'coordinates')
    name_col : str
        Columna de nombre/etiqueta (por defecto: 'nombre')
    color : str
        Color del polígono (por defecto: 'blue')
    name : str
        Nombre del grupo de características (por defecto: 'Regions')

    Retorna
    -------
    folium.Map
        Objeto de mapa actualizado
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
    Crea histogramas de distribución de coordenadas.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataframe de atractivos
    lat_col : str
        Columna de latitud (por defecto: 'POINT_Y')
    lon_col : str
        Columna de longitud (por defecto: 'POINT_X')

    Retorna
    -------
    plt.Figure
        Figura de matplotlib con histogramas
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].hist(df[lon_col], bins=50, color="steelblue", edgecolor="black")
    axes[0].set_xlabel("Longitud")
    axes[0].set_ylabel("Cantidad")
    axes[0].set_title("Distribución de Atractivos por Longitud")

    axes[1].hist(df[lat_col], bins=50, color="steelblue", edgecolor="black")
    axes[1].set_xlabel("Latitud")
    axes[1].set_ylabel("Cantidad")
    axes[1].set_title("Distribución de Atractivos por Latitud")

    plt.tight_layout()
    return fig


def plot_cluster_bar_chart(summary_df: pd.DataFrame, n_top: int = 15) -> plt.Figure:
    """
    Crea gráfico de barras horizontal de atractivos por clúster.

    Parámetros
    ----------
    summary_df : pd.DataFrame
        Dataframe resumen de clústeres
    n_top : int
        Número de clústeres principales a mostrar (por defecto: 15)

    Retorna
    -------
    plt.Figure
        Figura de matplotlib con gráfico de barras
    """
    top = summary_df.head(n_top).sort_values("n_attractions")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(len(top)), top["n_attractions"], color="steelblue", edgecolor="black")
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels([f"Cluster {i}" for i in top.index])
    ax.set_xlabel("Número de Atractivos")
    ax.set_title(f"Top {n_top} Clústeres por Cantidad de Atractivos")
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    return fig


def plot_anchor_distribution(
    summary_df: pd.DataFrame, color_map: Optional[Dict] = None
) -> plt.Figure:
    """
    Crea gráfico de dona de distribución de estado de ancla de clústeres.

    Parámetros
    ----------
    summary_df : pd.DataFrame
        Resumen de clústeres con columna anchor_status
    color_map : Dict, optional
        Mapeo de colores para estado de ancla (usa valores por defecto si no se proporciona)

    Retorna
    -------
    plt.Figure
        Figura de matplotlib con gráfico de dona
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

    # Crear agujero de dona
    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    ax.add_artist(centre_circle)

    ax.set_title("Distribución de Clústeres por Estado de Ancla")
    plt.tight_layout()
    return fig


def save_pydeck_html(deck: pdk.Deck, filepath: str) -> None:
    """
    Guarda un mapa PyDeck en archivo HTML.

    Parámetros
    ----------
    deck : pdk.Deck
        Objeto deck de PyDeck
    filepath : str
        Ruta del archivo de salida
    """
    html = deck.to_html()
    with open(filepath, "w") as f:
        f.write(html)
    print(f"Mapa guardado en {filepath}")


def save_folium_html(map_obj: folium.Map, filepath: str) -> None:
    """
    Guarda un mapa Folium en archivo HTML.

    Parámetros
    ----------
    map_obj : folium.Map
        Objeto de mapa Folium
    filepath : str
        Ruta del archivo de salida
    """
    map_obj.save(filepath)
    print(f"Mapa guardado en {filepath}")
