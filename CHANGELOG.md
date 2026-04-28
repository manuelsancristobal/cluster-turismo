# Changelog

En este archivo puedes encontrar todos los cambios notables de este proyecto.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

## [0.1.0] - 2025

### Added
- Pipeline ETL completo: carga de Excel SERNATUR 2020 + KMZ destinos oficiales
- Clustering espacial con HDBSCAN y métrica Haversine sobre 3.996 atractivos permanentes
- Análisis de brechas: clasificación de clústeres por tipo de ancla (internacional, nacional, sin ancla)
- Generación de assets: 7 gráficos matplotlib + mapa interactivo Folium
- Deploy automatizado a portafolio Jekyll (`scripts/deploy.py`)
- Suite de tests con pytest (80%+ cobertura)
- CI con GitHub Actions (Python 3.10, 3.11, 3.12)
- Pre-commit hooks (ruff, nbstripout, hooks estándar)
- Documentación técnica de metodología (`docs/methodology.md`)

### Changed
- Proyecto renombrado de `chile-tourism-gaps` a `cluster-turismo`
- Documentación y código españolizado
