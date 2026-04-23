"""Paquete para clustering espacial y análisis de brechas de atractivos turísticos."""

__version__ = "1.0.0"

from . import (
    clustering,
    config,
    data_loader,
    gap_analysis,
    geo_utils,
    preprocessing,
    visualization,
)

__all__ = [
    "clustering",
    "config",
    "data_loader",
    "gap_analysis",
    "geo_utils",
    "preprocessing",
    "visualization",
]
