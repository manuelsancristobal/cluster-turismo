# Cluster Turismo - Análisis Espacial de Atractivos

## Contexto
Este proyecto nació el año 2026, con la intención de identificar dónde había más atractivos turísticos, pero luego de un momento de revisión se transformó en una interesante forma de ver qué destinos tenían atractivos con potencial.

## Impacto y Valor del Proyecto
Este proyecto aplica técnicas de clustering espacial (HDBSCAN) para identificar concentraciones naturales de atractivos turísticos y contrastarlas con los destinos oficiales definidos por el Estado de Chile. La herramienta te permite detectar brechas de gobernanza, identificando "clústeres de mercado" que carecen de reconocimiento formal y destinos oficiales con baja densidad de atractivos ancla.

El espíritu de este trabajo es que puedas priorizar inversiones en infraestructura y planificar estratégicamente el territorio.

## Stack Tecnológico
- **Lenguaje**: Python 3.10+
- **Librerías Clave**: `Pandas`, `HDBSCAN` (Clustering), `Shapely` (Geometría), `Folium`/`Pydeck` (Mapas).
- **Calidad de Código**: `Ruff` (Linting con reglas D e I), `Pytest` (Tests de integración).
- **Infraestructura**: GitHub Actions (CI/CD).

## Arquitectura de Datos y Metodología
1. **Preprocesamiento**: Filtrado de atractivos permanentes y validación de coordenadas.
2. **Clustering Espacial**: Ejecución de HDBSCAN sobre coordenadas (Haversine) para identificar densidades.
3. **Análisis de Brechas**: Cálculo de intersección (Convex Hulls) entre clústeres identificados y destinos oficiales.
4. **Visualización**: Generación de mapas de calor, polígonos de clústeres y dashboards estáticos de brechas regionales.

## Quick Start (Reproducibilidad)
1. `git clone https://github.com/manuelsancristobal/cluster-turismo`
2. `make install-dev` (Instala dependencias)
3. `make test` (Ejecuta validaciones y cobertura)
4. `make run` (Genera assets y mapas en `assets/`)
5. `make deploy` (Sincroniza con el portafolio Jekyll)

## Estructura del Proyecto
- `src/`: Lógica de clustering, carga de datos geográficos y CLI.
- `data/`: Datos originales de SERNATUR y polígonos KMZ (`raw/`).
- `assets/`: Mapas interactivos y reportes visuales generados.
- `tests/`: Pruebas de integración y validación geométrica.

---
**Autor**: Manuel San Cristóbal Opazo 
**Licencia**: MIT
