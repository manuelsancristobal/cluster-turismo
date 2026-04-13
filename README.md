# Chile Tourism Gaps: Identifying Investment Opportunities Through Spatial Clustering

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/manuelsancristobal/chile-tourism-gaps/workflows/CI/badge.svg)](https://github.com/manuelsancristobal/chile-tourism-gaps/actions)

A data science project analyzing Chilean tourism attractions to identify geographic clusters and investment gaps using HDBSCAN spatial clustering.

## Overview

This project analyzes 4,048 permanent Chilean tourism attractions from the 2020 SERNATUR (Servicio Nacional de Turismo) registry to:

- **Identify 79 spatial clusters** of tourism attractions using HDBSCAN with haversine metric
- **Classify investment gaps**: ~33% of tourism clusters lack international-level anchor attractions
- **Pinpoint development opportunities**: Regions with national infrastructure but missing world-class attractions
- **Support policy decisions**: Data-driven analysis for regional tourism development strategy

## Key Findings

- **79 territorial clusters** identified from ~3,996 permanent attractions across Chile
- **52 clusters with international anchors** - mature tourism markets
- **26 clusters with only national-level anchors** - moderate development potential
- **~33% of clusters operate without international anchor attractions** - strategic gap for investment

## Tech Stack

| Category | Technologies |
|----------|---------------|
| **Data Processing** | Pandas, NumPy |
| **Spatial Clustering** | HDBSCAN (haversine metric) |
| **Geospatial** | Shapely, GeoPandas |
| **Interactive Maps** | PyDeck, Folium |
| **Visualization** | Matplotlib, Seaborn |
| **Testing** | pytest, pytest-cov |
| **Code Quality** | ruff, black |

## Project Structure

```
chile-tourism-gaps/
├── README.md                           # This file
├── index.html                          # Portfolio page (GitHub Pages)
├── pyproject.toml                      # Project configuration
│
├── src/tourism_gaps/                   # Main Python package
│   ├── data_loader.py                  # Load Excel & KMZ files
│   ├── preprocessing.py                # Data cleaning & validation
│   ├── clustering.py                   # HDBSCAN spatial clustering
│   ├── gap_analysis.py                 # Opportunity identification
│   ├── visualization.py                # PyDeck, Folium, Matplotlib
│   └── geo_utils.py                    # Geospatial utilities
│
├── scripts/
│   └── generate_assets.py             # Generate all charts & maps
│
├── notebooks/                          # Jupyter analysis notebooks
│   ├── Publico_Visualización_de_Atractivos.ipynb
│   └── Comparacion_Atractivos_Destinos.ipynb
│
├── tests/                              # Unit tests
│   ├── test_preprocessing.py
│   ├── test_clustering.py
│   ├── test_gap_analysis.py
│   └── fixtures/                       # Test data
│
├── data/                               # (not committed) Original XLSX & KMZ files
│
├── assets/                             # Generated visual assets
│   ├── mapa_interactivo.html           # Interactive Folium map
│   └── img/                            # Static chart images
│
└── docs/                               # Documentation
    └── methodology.md                  # Detailed methodology
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip or conda

### Quick Start

```bash
# Clone repository
git clone https://github.com/manuelsancristobal/chile-tourism-gaps.git
cd chile-tourism-gaps

# Install package in development mode
make install-dev

# Run tests
make test

# Run linting
make lint
```

### Data Setup

Download source data from SERNATUR:
1. `ATRACTIVOS_TURÍSTICOS_NACIONAL_2020.xlsx` → `data/`
2. `Destinos_Nacional-Publico.kmz` → `data/`

Then run notebooks:
```bash
jupyter lab notebooks/
```

## Usage

### Python API

```python
from tourism_gaps import clustering, preprocessing, gap_analysis, data_loader

# Load and preprocess attractions
df = data_loader.load_attractions_excel("data/ATRACTIVOS_TURÍSTICOS_NACIONAL_2020.xlsx")
df = preprocessing.filter_permanent_attractions(df)
df = preprocessing.validate_coordinates(df)

# Run HDBSCAN spatial clustering
df_clustered = clustering.run_hdbscan_spatial(df, min_cluster_size=10)

# Summarize clusters
summary = clustering.summarize_clusters(df_clustered)

# Identify investment gaps
summary = gap_analysis.classify_anchor_status(summary)
opportunities = gap_analysis.identify_investment_opportunities(df_clustered, summary)
```

### Command Line

```bash
# Run all tests
make test

# Generate coverage report
make coverage

# Export interactive maps
make maps

# Execute notebooks
make run-notebooks
```

## Methodology

### Spatial Clustering Approach

The project uses **HDBSCAN** (Hierarchical Density-Based Spatial Clustering of Applications with Noise) with the **haversine distance metric**, appropriate for geographic coordinates on a sphere.

**Algorithm parameters:**
- Metric: Haversine (accounts for Earth's curvature)
- Min cluster size: 10 attractions
- Distance threshold: Estimated from data density

**Process:**
1. Convert latitude/longitude to radians
2. Compute pairwise haversine distances
3. Identify density-connected components
4. Calculate convex hull for each cluster
5. Classify clusters by highest-level anchor attractions

### Gap Analysis Logic

**Anchor Classification:**
- **International Anchor**: Cluster has 1+ INTERNACIONAL-level attractions → developed market
- **National Anchor**: Only NACIONAL-level, no international → development potential
- **No Anchor**: No attractions above REGIONAL → highest investment priority

**Investment Opportunity Priority:**
1. **High**: Clusters without any anchor attractions (greenfield opportunities)
2. **Medium**: Clusters with only national anchors (capacity expansion)
3. **Low**: Clusters with international anchors (mature markets)

## Visualizations

### Interactive Maps (PyDeck)
- **Hierarchy Map**: Color-coded by attraction level (local → international)
- **Cluster Map**: Geographic clusters with convex hull boundaries
- **Gap Map**: Investment opportunities by priority level

### Comparative Analysis (Folium)
- **Destination Map**: Official tourism destinations with attractions overlay
- **Lagging Attractions Map**: Unassigned attractions outside official boundaries

### Statistics (Matplotlib)
- Cluster size distribution
- Anchor status breakdown (donut chart)
- Regional opportunity summary

## Testing

Project includes unit tests for core modules:

```bash
# Run tests with coverage
make coverage

# Run specific test file
pytest tests/test_clustering.py -v

# Run tests matching pattern
pytest -k "anchor" -v
```

**Test coverage includes:**
- Data preprocessing & validation
- HDBSCAN clustering & hull computation
- Gap analysis & opportunity classification
- Visualization output generation

## Documentation

- **[README_es.md](README_es.md)** - Spanish documentation with bilingual narrative
- **[docs/methodology.md](docs/methodology.md)** - Detailed methodology & algorithm explanations
- **[Inline docstrings](src/tourism_gaps/)** - Google-style docstrings for all functions

## Citation

If you use this analysis in research or policy contexts, please cite:

```
@misc{chile-tourism-gaps,
  title={Identifying Tourism Investment Gaps in Chile Through Spatial Clustering},
  author={Tourism Data Analysis},
  year={2024},
  url={https://github.com/manuelsancristobal/chile-tourism-gaps}
}
```

## Data Sources

- **SERNATUR**: [Atractivos Turísticos Nacional 2020](https://www.sernatur.cl)
  - 4,048 permanent tourism attractions
  - Hierarchy levels: Local, Regional, Nacional, Internacional
  - 12+ attraction categories

- **SERNATUR**: Official Tourism Destinations (2025)
  - 78 official tourism zones
  - Polygon boundaries in KMZ (Google Earth) format
  - Regional classification

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make changes with tests
4. Submit pull request

All contributions should maintain:
- >80% test coverage
- Clean git history (descriptive commit messages)
- Code style compliance (ruff format)

## License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

Free for academic, government, and commercial use.

## Contact & Support

- **Issue Tracker**: [GitHub Issues](https://github.com/manuelsancristobal/chile-tourism-gaps/issues)
- **Email**: msancristo@fen.uchile.cl
- **Web**: https://github.com/manuelsancristobal/chile-tourism-gaps

---

**Status**: Active Development | **Last Updated**: 2024 | **Stable**: v0.1.0
