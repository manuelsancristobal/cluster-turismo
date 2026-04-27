# Datos: Cluster Turismo

## Origen
- **Atractivos Turísticos**: SERNATUR (Servicio Nacional de Turismo, Chile). Dataset 2020.
- **Destinos Oficiales**: Subsecretaría de Turismo. Archivo KMZ de destinos nacionales.

## Estructura
- `raw/`: 
  - `ATRACTIVOS_TURÍSTICOS_NACIONAL_2020.xlsx`: Dataset original con ~4,000 atractivos.
  - `Destinos_Nacional-Publico.kmz`: Polígonos de los destinos turísticos oficiales.
- `processed/`: Resultados del clustering HDBSCAN y análisis de brechas (generados en tiempo de ejecución).
- `external/`: Datos complementarios (si aplica).

## Diccionario de Datos Clave (Atractivos)
- `JERARQUIA`: Nivel de importancia (Internacional, Nacional, Regional, Local).
- `CATEGORIA`: Tipo de atractivo (Natural, Manifestación Cultural, etc.).
- `X`, `Y`: Coordenadas geográficas (Longitud, Latitud).
