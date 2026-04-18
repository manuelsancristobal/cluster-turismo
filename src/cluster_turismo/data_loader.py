"""Funciones de carga y análisis de datos para atractivos turísticos y destinos."""

import re
import zipfile
from typing import Dict, List

import pandas as pd


def load_attractions_excel(filepath: str) -> pd.DataFrame:
    """
    Cargar atractivos turísticos chilenos desde archivo Excel de SERNATUR.

    Parámetros
    ----------
    filepath : str
        Ruta a ATRACTIVOS_TURÍSTICOS_NACIONAL_2020.xlsx

    Retorna
    -------
    pd.DataFrame
        DataFrame con todos los datos de atractivos incluyendo jerarquía, categoría, coordenadas
    """
    df = pd.read_excel(filepath)
    return df


def load_kmz_destinations(filepath: str) -> pd.DataFrame:
    """
    Cargar destinos turísticos desde archivo KMZ (KML comprimido).

    Extrae el KML del archivo KMZ, analiza los elementos Placemark
    y retorna un DataFrame con los límites y metadatos de los destinos.

    Parámetros
    ----------
    filepath : str
        Ruta a Destinos_Nacional-Publico.kmz

    Retorna
    -------
    pd.DataFrame
        DataFrame con nombres de destinos, códigos, regiones y coordenadas de polígonos
    """
    kml_string = extract_kml_from_kmz(filepath)
    placemarks = parse_kml_placemarks(kml_string)

    records = []
    for pm in placemarks:
        records.append(
            {
                "nombre": pm.get("nombre"),
                "codigo": pm.get("codigo"),
                "region": pm.get("region"),
                "tipo": pm.get("tipo"),
                "coordinates": pm.get("coordinates"),
            }
        )

    df = pd.DataFrame(records)
    return df


def extract_kml_from_kmz(kmz_path: str) -> str:
    """
    Extraer contenido KML de archivo KMZ (ZIP).

    Parámetros
    ----------
    kmz_path : str
        Ruta al archivo .kmz

    Retorna
    -------
    str
        Contenido XML KML sin procesar

    Lanza
    -----
    FileNotFoundError
        Si doc.kml no se encuentra en el archivo comprimido
    """
    with zipfile.ZipFile(kmz_path, "r") as zip_ref:
        kml_bytes = zip_ref.read("doc.kml")
    return kml_bytes.decode("utf-8")


def parse_kml_placemarks(kml_string: str) -> List[Dict]:
    """
    Analizar elementos Placemark del KML para extraer metadatos y límites de destinos.

    Parámetros
    ----------
    kml_string : str
        Contenido XML KML sin procesar

    Retorna
    -------
    List[Dict]
        Lista de diccionarios con datos de placemark (nombre, codigo, region, coordinates)
    """
    placemarks = []

    # Buscar todos los bloques Placemark
    placemark_pattern = r"<Placemark>(.*?)</Placemark>"
    placemark_matches = re.finditer(placemark_pattern, kml_string, re.DOTALL)

    for match in placemark_matches:
        pm_content = match.group(1)

        # Extraer nombre
        name_match = re.search(r"<name>(.*?)</name>", pm_content)
        nombre = name_match.group(1) if name_match else None

        # Extraer campos de datos extendidos (códigos, regiones de elementos SimpleData)
        codigo = extract_kml_field(pm_content, "codigo")
        region = extract_kml_field(pm_content, "region")
        tipo = extract_kml_field(pm_content, "tipo")

        # Extraer coordenadas de LinearRing
        coords = extract_coordinates_from_linearring(pm_content)

        if nombre and coords:  # Solo incluir si tiene nombre y geometría
            placemarks.append(
                {
                    "nombre": nombre,
                    "codigo": codigo,
                    "region": region,
                    "tipo": tipo,
                    "coordinates": coords,
                }
            )

    return placemarks


def extract_kml_field(pm_content: str, field_name: str) -> str:
    """
    Extraer valor de campo SimpleData de los datos extendidos del Placemark KML.

    Parámetros
    ----------
    pm_content : str
        Contenido XML del Placemark
    field_name : str
        Nombre del campo a extraer

    Retorna
    -------
    str o None
        Valor del campo si se encuentra, sino None
    """
    pattern = rf'<SimpleData name="{field_name}">(.*?)</SimpleData>'
    match = re.search(pattern, pm_content)
    return match.group(1) if match else None


def extract_coordinates_from_linearring(pm_content: str) -> List[tuple]:
    """
    Extraer pares de coordenadas del elemento KML LinearRing.

    Parámetros
    ----------
    pm_content : str
        Contenido XML del Placemark con Polygon/LinearRing

    Retorna
    -------
    List[tuple]
        Lista de tuplas (lon, lat), o lista vacía si no se encuentra
    """
    # Buscar texto de coordenadas en LinearRing
    coords_match = re.search(
        r"<LinearRing>.*?<coordinates>(.*?)</coordinates>", pm_content, re.DOTALL
    )
    if not coords_match:
        return []

    coords_text = coords_match.group(1).strip()
    coords_list = []

    for coord_str in coords_text.split():
        parts = coord_str.split(",")
        if len(parts) >= 2:
            try:
                lon = float(parts[0])
                lat = float(parts[1])
                coords_list.append((lon, lat))
            except ValueError:
                continue

    return coords_list


def simplify_polygon_coordinates(
    coordinates: List[tuple], max_points: int = 80
) -> List[tuple]:
    """
    Simplificar polígono reduciendo el número de puntos de coordenadas.

    Usa un algoritmo básico de raleo para reducir la complejidad preservando la forma.

    Parámetros
    ----------
    coordinates : List[tuple]
        Lista de tuplas de coordenadas (lon, lat)
    max_points : int
        Número máximo de puntos a conservar (por defecto 80)

    Retorna
    -------
    List[tuple]
        Lista de coordenadas simplificada
    """
    if len(coordinates) <= max_points:
        return coordinates

    # Raleo simple: conservar primer punto, último y puntos equidistantes
    step = len(coordinates) // max_points
    simplified = coordinates[::step]

    # Asegurar que el último punto esté incluido
    if simplified[-1] != coordinates[-1]:
        simplified.append(coordinates[-1])

    return simplified
