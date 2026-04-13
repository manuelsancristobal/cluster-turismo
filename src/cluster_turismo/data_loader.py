"""Data loading and parsing functions for tourism attractions and destinations."""

import re
import zipfile
from typing import Dict, List

import pandas as pd


def load_attractions_excel(filepath: str) -> pd.DataFrame:
    """
    Load Chilean tourism attractions from SERNATUR Excel file.

    Parameters
    ----------
    filepath : str
        Path to ATRACTIVOS_TURÍSTICOS_NACIONAL_2020.xlsx

    Returns
    -------
    pd.DataFrame
        DataFrame with all attractions data including hierarchy, category, coordinates
    """
    df = pd.read_excel(filepath)
    return df


def load_kmz_destinations(filepath: str) -> pd.DataFrame:
    """
    Load tourist destinations from KMZ (compressed KML) file.

    Extracts KML from the KMZ archive, parses Placemark elements,
    and returns a DataFrame with destination boundaries and metadata.

    Parameters
    ----------
    filepath : str
        Path to Destinos_Nacional-Publico.kmz

    Returns
    -------
    pd.DataFrame
        DataFrame with destination names, codes, regions, and polygon coordinates
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
    Extract KML content from KMZ (ZIP) archive.

    Parameters
    ----------
    kmz_path : str
        Path to .kmz file

    Returns
    -------
    str
        Raw KML XML content

    Raises
    ------
    FileNotFoundError
        If doc.kml not found in archive
    """
    with zipfile.ZipFile(kmz_path, "r") as zip_ref:
        kml_bytes = zip_ref.read("doc.kml")
    return kml_bytes.decode("utf-8")


def parse_kml_placemarks(kml_string: str) -> List[Dict]:
    """
    Parse KML Placemark elements to extract destination metadata and boundaries.

    Parameters
    ----------
    kml_string : str
        Raw KML XML content

    Returns
    -------
    List[Dict]
        List of dictionaries with placemark data (nombre, codigo, region, coordinates)
    """
    placemarks = []

    # Find all Placemark blocks
    placemark_pattern = r"<Placemark>(.*?)</Placemark>"
    placemark_matches = re.finditer(placemark_pattern, kml_string, re.DOTALL)

    for match in placemark_matches:
        pm_content = match.group(1)

        # Extract name
        name_match = re.search(r"<name>(.*?)</name>", pm_content)
        nombre = name_match.group(1) if name_match else None

        # Extract extended data fields (codes, regions from SimpleData elements)
        codigo = extract_kml_field(pm_content, "codigo")
        region = extract_kml_field(pm_content, "region")
        tipo = extract_kml_field(pm_content, "tipo")

        # Extract coordinates from LinearRing
        coords = extract_coordinates_from_linearring(pm_content)

        if nombre and coords:  # Only include if has name and geometry
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
    Extract SimpleData field value from KML Placemark extended data.

    Parameters
    ----------
    pm_content : str
        Placemark XML content
    field_name : str
        Name of the field to extract

    Returns
    -------
    str or None
        Field value if found, else None
    """
    pattern = rf'<SimpleData name="{field_name}">(.*?)</SimpleData>'
    match = re.search(pattern, pm_content)
    return match.group(1) if match else None


def extract_coordinates_from_linearring(pm_content: str) -> List[tuple]:
    """
    Extract coordinate pairs from KML LinearRing element.

    Parameters
    ----------
    pm_content : str
        Placemark XML content with Polygon/LinearRing

    Returns
    -------
    List[tuple]
        List of (lon, lat) tuples, or empty list if not found
    """
    # Find coordinates text in LinearRing
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
    Simplify polygon by reducing number of coordinate points.

    Uses a basic thinning algorithm to reduce complexity while preserving shape.

    Parameters
    ----------
    coordinates : List[tuple]
        List of (lon, lat) coordinate tuples
    max_points : int
        Maximum number of points to keep (default 80)

    Returns
    -------
    List[tuple]
        Simplified coordinate list
    """
    if len(coordinates) <= max_points:
        return coordinates

    # Simple thinning: keep first, last, and evenly spaced points
    step = len(coordinates) // max_points
    simplified = coordinates[::step]

    # Ensure last point is included
    if simplified[-1] != coordinates[-1]:
        simplified.append(coordinates[-1])

    return simplified
