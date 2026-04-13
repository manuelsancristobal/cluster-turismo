"""
Chile Tourism Gaps Analysis.

A comprehensive spatial clustering and gap analysis of Chilean tourism attractions
using HDBSCAN to identify investment opportunities in underserved regions.
"""

__version__ = "0.1.0"
__author__ = "Tourism Data Analysis"

from . import clustering
from . import data_loader
from . import gap_analysis
from . import geo_utils
from . import preprocessing
from . import visualization

__all__ = [
    "clustering",
    "data_loader",
    "gap_analysis",
    "geo_utils",
    "preprocessing",
    "visualization",
]
