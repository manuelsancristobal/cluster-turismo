"""Funciones utilitarias geoespaciales usando Shapely."""


import pandas as pd
from shapely.geometry import Point, Polygon


def build_shapely_polygons(df: pd.DataFrame, coords_col: str = "coordinates") -> dict[str, Polygon]:
    """Construir objetos Polygon de Shapely a partir de datos de coordenadas.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame con información de coordenadas (típicamente de data_loader.load_kmz_destinations)
    coords_col : str
        Nombre de la columna que contiene la lista de coordenadas (por defecto: 'coordinates')

    Retorna
    -------
    Dict[str, Polygon]
        Diccionario que mapea nombres de destinos a objetos Polygon de Shapely
    """
    polygons = {}

    for _idx, row in df.iterrows():
        name = row.get("nombre")
        coords = row.get(coords_col)

        if name and coords and len(coords) >= 3:
            try:
                polygon = Polygon(coords)
                if polygon.is_valid:
                    polygons[name] = polygon
            except Exception as e:
                print(f"No se pudo crear polígono para {name}: {e}")

    return polygons


def point_in_polygon_check(
    df_points: pd.DataFrame,
    df_polygons: pd.DataFrame,
    lat_col: str = "POINT_Y",
    lon_col: str = "POINT_X",
) -> pd.DataFrame:
    """Determinar si cada punto de atractivo cae dentro de algún polígono de destino.

    Parámetros
    ----------
    df_points : pd.DataFrame
        DataFrame de atractivos con coordenadas
    df_polygons : pd.DataFrame
        DataFrame de destinos con coordenadas de polígonos
    lat_col : str
        Columna de latitud en puntos (por defecto: 'POINT_Y')
    lon_col : str
        Columna de longitud en puntos (por defecto: 'POINT_X')

    Retorna
    -------
    pd.DataFrame
        DataFrame de puntos de entrada con columnas añadidas 'in_destination' y 'destination_name'
    """
    # Construir polígonos desde destinos
    polygons = build_shapely_polygons(df_polygons)

    # Verificar cada atractivo
    in_destination_list = []
    destination_names = []

    for _idx, row in df_points.iterrows():
        point = Point(row[lon_col], row[lat_col])

        found_dest = None
        for dest_name, polygon in polygons.items():
            if polygon.contains(point):
                found_dest = dest_name
                break

        in_destination_list.append(found_dest is not None)
        destination_names.append(found_dest)

    df_result = df_points.copy()
    df_result["in_destination"] = in_destination_list
    df_result["destination_name"] = destination_names

    return df_result


def compute_cluster_centroid(
    df: pd.DataFrame, lat_col: str = "POINT_Y", lon_col: str = "POINT_X"
) -> tuple[float, float]:
    """Calcular centroide (centro) de los puntos del clúster.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame con columnas de coordenadas
    lat_col : str
        Columna de latitud (por defecto: 'POINT_Y')
    lon_col : str
        Columna de longitud (por defecto: 'POINT_X')

    Retorna
    -------
    Tuple[float, float]
        (latitud, longitud) del centroide del clúster
    """
    lat = df[lat_col].mean()
    lon = df[lon_col].mean()
    return lat, lon


def compute_geographic_bounds(df: pd.DataFrame, lat_col: str = "POINT_Y", lon_col: str = "POINT_X") -> dict:
    """Calcular el cuadro delimitador geográfico de los puntos.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame con coordenadas
    lat_col : str
        Columna de latitud (por defecto: 'POINT_Y')
    lon_col : str
        Columna de longitud (por defecto: 'POINT_X')

    Retorna
    -------
    dict
        Diccionario con límites 'north', 'south', 'east', 'west'
    """
    return {
        "north": df[lat_col].max(),
        "south": df[lat_col].min(),
        "east": df[lon_col].max(),
        "west": df[lon_col].min(),
    }


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcular distancia haversine entre dos pares de coordenadas.

    Parámetros
    ----------
    lat1, lon1 : float
        Primer par de coordenadas en grados
    lat2, lon2 : float
        Segundo par de coordenadas en grados

    Retorna
    -------
    float
        Distancia en kilómetros
    """
    from math import asin, cos, radians, sin, sqrt

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radio de la Tierra en kilómetros
    return c * r
