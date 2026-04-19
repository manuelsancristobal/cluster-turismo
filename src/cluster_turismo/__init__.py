"""Análisis de Brechas en Turismo de Chile.

Análisis integral de agrupamiento espacial y brechas de atractivos turísticos
chilenos usando HDBSCAN para identificar oportunidades de inversión en regiones
desatendidas.
"""

__version__ = "0.1.0"
__author__ = "Manuel San Cristóbal"

from . import clustering, data_loader, gap_analysis, geo_utils, preprocessing, visualization

__all__ = [
    "clustering",
    "data_loader",
    "gap_analysis",
    "geo_utils",
    "preprocessing",
    "visualization",
]
