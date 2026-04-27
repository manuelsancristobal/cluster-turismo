"""Constantes, rutas y configuración del proyecto cluster-turismo."""

from __future__ import annotations

import os
from pathlib import Path

# Rutas
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"
ASSETS_IMG_DIR = ASSETS_DIR / "img"

EXCEL_FILENAME = "ATRACTIVOS_TURÍSTICOS_NACIONAL_2020.xlsx"
KMZ_FILENAME = "Destinos_Nacional-Publico.kmz"
EXCEL_PATH = DATA_DIR / "raw" / EXCEL_FILENAME
KMZ_PATH = DATA_DIR / "raw" / KMZ_FILENAME

_jekyll_env = os.getenv("JEKYLL_REPO")
JEKYLL_REPO: Path | None = Path(_jekyll_env) if _jekyll_env else None
JEKYLL_BASE = (JEKYLL_REPO / "proyectos" / "cluster-turismo") if JEKYLL_REPO else None
JEKYLL_ASSETS_DIR = (JEKYLL_BASE / "assets") if JEKYLL_BASE else None
JEKYLL_IMG_DIR = (JEKYLL_BASE / "assets" / "img") if JEKYLL_BASE else None
JEKYLL_PROJECTS_DIR = (JEKYLL_REPO / "_projects") if JEKYLL_REPO else None
JEKYLL_PROJECT_MD = PROJECT_ROOT / "jekyll" / "cluster-turismo.md"

# Viewport de Chile
CHILE_LAT = -35.6751
CHILE_LON = -71.5430
CHILE_ZOOM = 4

# Límites continentales de Chile
CHILE_LAT_MIN = -56
CHILE_LAT_MAX = -17
CHILE_LON_MIN = -75
CHILE_LON_MAX = -66

# Parámetros HDBSCAN
HDBSCAN_MIN_CLUSTER_SIZE = 10
HDBSCAN_METRIC = "haversine"

# Colores jerarquía (hex canónico)
HIER_COLORS_HEX: dict[str, str] = {
    "INTERNACIONAL": "#dc1e78",  # [220, 30, 120]
    "NACIONAL":      "#4682b4",  # [70, 130, 180]
    "REGIONAL":      "#82aad2",  # [130, 170, 210]
    "LOCAL":         "#b4b4b4",  # [180, 180, 180]
}

# Colores estado de ancla (hex canónico)
ANCHOR_COLORS_HEX: dict[str, str] = {
    "Con ancla internacional": "#2ecc71",  # [46, 204, 113]
    "Solo ancla nacional":     "#f39c12",  # [243, 156, 18]
    "Sin ancla":               "#e74c3c",  # [231, 76, 60]
    "Ruido":                   "#969696",  # [150, 150, 150]
}

# Colores barras matplotlib
BAR_COLOR_PRIMARY     = "#2171b5"
BAR_COLOR_SIN_ANCLA   = "#cb181d"
BAR_COLOR_SOLO_NACION = "#f59322"
BAR_COLOR_CON_ANCLA   = "#2ca02c"

# Colores cascos Folium
HULL_COLORS_HEX: dict[str, str] = {
    "Con ancla internacional": "#2ecc71",
    "Solo ancla nacional":     "#f39c12",
    "Sin ancla":               "#e74c3c",
}

# Colores clusters rezagados
LAGGING_HULL_COLOR  = "#9b59b6"
LAGGING_POINT_COLOR = "#2c3e50"

# Colores superposición
OVERLAP_COLORS_HEX: dict[str, str] = {
    "Contenido":                 "#a8e6cf",
    "Parcialmente superpuesto":  "#ffd3b6",
    "Genuinamente rezagado":     "#ffaaa5",
}

# Umbrales de análisis de brechas
OVERLAP_THRESHOLD_CONTAINED = 0.9
OVERLAP_THRESHOLD_PARTIAL   = 0.1

# Estilo gráficos
PLOT_STYLE = "seaborn-v0_8-whitegrid"
PLOT_DPI   = 150
