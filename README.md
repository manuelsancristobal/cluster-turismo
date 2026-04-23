# Brechas Turísticas de Chile: Identificación de Oportunidades de Inversión

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-green.svg)](LICENSE)

Proyecto de análisis de datos que identifica brechas geográficas en la distribución de atractivos turísticos chilenos mediante clustering espacial HDBSCAN.

## Descripción General

Este proyecto analiza **~3,996 atractivos turísticos permanentes** del registro nacional de SERNATUR 2020 para:

- **Identificar 79 clústeres espaciales** de atractivos turísticos usando HDBSCAN con métrica haversine
- **Clasificar brechas de inversión**: ~33% de los clústeres turísticos carecen de atractivos ancla de nivel internacional
- **Detectar oportunidades de desarrollo**: Regiones con infraestructura turística nacional pero sin atractivos de clase mundial
- **Fundamentar decisiones de política pública**: Análisis basado en datos para estrategia de desarrollo turístico regional

## Hallazgos Clave

- **79 clústeres territoriales** identificados a partir de ~3,996 atractivos permanentes
- **52 clústeres con ancla internacional** - mercados turísticos maduros
- **26 clústeres con solo ancla nacional** - potencial de desarrollo moderado
- **1 clúster sin atractivos ancla** - prioridad máxima para inversión
- **~33% de los atractivos no asignados a ningún clúster** - brecha estratégica

## Stack Tecnológico

| Categoría | Tecnologías |
|-----------|-------------|
| **Procesamiento** | Pandas, NumPy |
| **Clustering Espacial** | HDBSCAN (métrica haversine) |
| **Geoespacial** | Shapely |
| **Mapas Interactivos** | PyDeck, Folium |
| **Visualización** | Matplotlib, Seaborn |
| **Testing** | pytest, pytest-cov |
| **Calidad de Código** | ruff |

## Estructura del Proyecto

```
cluster-turismo/
├── README.md                           # Este archivo
├── LICENSE                             # Licencia MIT
├── pyproject.toml                      # Configuración del proyecto
├── Makefile                            # Automatización
│
├── src/cluster_turismo/                   # Paquete Python principal
│   ├── data_loader.py                  # Carga de archivos Excel & KMZ
│   ├── preprocessing.py                # Limpieza y validación
│   ├── clustering.py                   # Clustering HDBSCAN
│   ├── gap_analysis.py                 # Identificación de oportunidades
│   ├── visualization.py                # Mapas y gráficos
│   └── geo_utils.py                    # Utilidades geoespaciales
│
├── notebooks/                          # Notebooks Jupyter
│   ├── Publico_Visualización_de_Atractivos.ipynb
│   └── Comparacion_Atractivos_Destinos.ipynb
│
├── tests/                              # Tests unitarios
│   ├── test_preprocessing.py
│   ├── test_clustering.py
│   ├── test_gap_analysis.py
│   └── fixtures/                       # Datos de prueba
│
├── data/                               # (no committeado) Archivos originales
│
├── assets/                             # Resultados generados (en .gitignore)
│   ├── mapa_interactivo.html           # Mapa interactivo Folium
│   └── img/                            # Visualizaciones estáticas
│
└── docs/                               # Documentación
    ├── methodology.md                  # Metodología detallada
    └── images/                         # Capturas de pantalla
```

## Guía para Principiantes

### ¿Qué es `make`?

`make` es una herramienta que ejecuta comandos predefinidos. En vez de recordar comandos largos, solo escribes `make` seguido de una palabra clave. Para ver todos los comandos disponibles:

```bash
make help
```

### Requisitos Previos

1. **Python 3.10 o superior** — [Descargar aquí](https://www.python.org/downloads/)
2. **Git** — [Descargar aquí](https://git-scm.com/downloads)
3. **Make** — En Windows viene incluido con Git Bash. En macOS/Linux ya está instalado.

### Instalación paso a paso

```bash
# 1. Clonar el repositorio
git clone https://github.com/manuelsancristobal/cluster-turismo.git
cd cluster-turismo

# 2. Crear un entorno virtual (aísla las dependencias de este proyecto)
python -m venv .venv

# 3. Activar el entorno virtual
source .venv/Scripts/activate   # Windows (Git Bash)
# source .venv/bin/activate     # Linux / macOS

# 4. Instalar el proyecto y sus dependencias (incluye herramientas de desarrollo)
make install-dev
```

### Comandos principales

Todos los comandos se ejecutan desde la carpeta raíz del proyecto, con el entorno virtual activado.

```bash
make help             # Muestra todos los comandos disponibles
make test             # Ejecuta los tests para verificar que todo funciona
make lint             # Verifica la calidad del código
make coverage         # Tests + reporte de cobertura (abre htmlcov/index.html)
make generate-assets  # Genera gráficos y mapa interactivo
make deploy           # Genera assets + copia al repo Jekyll (portafolio web)
make clean            # Elimina archivos temporales
```

### Flujo de trabajo típico

```bash
# 1. Verificar que todo funciona
make test

# 2. Generar los gráficos y el mapa interactivo
make generate-assets

# 3. Si modificaste el análisis en jekyll/cluster-turismo.md:
make deploy     # Genera assets y los copia al repo Jekyll
```

### ¿Cómo actualizo el análisis en el portafolio web?

```
Tu proyecto                    Repo Jekyll                   Sitio web
─────────────                  ──────────                    ─────────

jekyll/cluster-turismo.md ──┐
                            ├─ make deploy ──→  _projects/cluster-turismo.md
assets/img/*.png          ──┘                  proyectos/cluster-turismo/assets/
                                                      │
                                                git push ──→  manuelsancristobal.github.io
```

**Para modificar texto de análisis:**

1. Edita `jekyll/cluster-turismo.md` con los cambios que quieras
2. Ejecuta `make deploy` (genera assets + copia todo al repo Jekyll local)
3. Ve a la carpeta del repo Jekyll (`~/manuelsancristobal.github.io`)
4. Ejecuta `git add . && git commit -m "actualizar análisis" && git push`
5. Espera ~1 minuto y el cambio aparece en tu sitio web

**Para agregar un gráfico nuevo:**

1. Genera el gráfico con `make generate-assets` (los PNGs quedan en `assets/img/`)
2. Edita `jekyll/cluster-turismo.md` y agrega la referencia al gráfico:
   ```markdown
   ![Descripción del gráfico](./assets/img/mi_grafico.png)
   ```
3. Ejecuta `make deploy` (copia el `.md`, los PNGs y el mapa al repo Jekyll)
4. Ve al repo Jekyll, haz commit y push

> **Importante:** `make deploy` solo copia archivos a tu computador. El sitio web no se actualiza hasta que haces `git push` en el repo Jekyll.

---

### Configuración de Datos

Descargar datos de SERNATUR y colocarlos en la carpeta `data/`:
1. `ATRACTIVOS_TURÍSTICOS_NACIONAL_2020.xlsx`
2. `Destinos_Nacional-Publico.kmz`

Luego ejecutar notebooks:
```bash
jupyter lab notebooks/
```

## Uso Avanzado

### API Python

```python
from cluster_turismo import clustering, preprocessing, gap_analysis, data_loader

# Cargar y preprocesar atractivos
df = data_loader.load_attractions_excel("data/ATRACTIVOS_TURÍSTICOS_NACIONAL_2020.xlsx")
df = preprocessing.filter_permanent_attractions(df)
df = preprocessing.validate_coordinates(df)

# Ejecutar clustering HDBSCAN
df_clustered = clustering.run_hdbscan_spatial(df, min_cluster_size=10)

# Resumir clústeres
summary = clustering.summarize_clusters(df_clustered)

# Identificar brechas
summary = gap_analysis.classify_anchor_status(summary)
opportunities = gap_analysis.identify_investment_opportunities(df_clustered, summary)
```

### Comandos adicionales

```bash
make coverage         # Tests con reporte de cobertura
make maps             # Exportar notebooks como mapas HTML
make run-notebooks    # Ejecutar todos los notebooks
```

## Metodología

### Enfoque de Clustering Espacial

El proyecto utiliza **HDBSCAN** (Hierarchical Density-Based Spatial Clustering of Applications with Noise) con **métrica haversine**, adecuada para coordenadas geográficas en una esfera.

**Parámetros del algoritmo:**
- Métrica: Haversine (considera curvatura terrestre)
- Tamaño mínimo de clúster: 10 atractivos
- Umbral de distancia: Estimado desde densidad de datos

**Proceso:**
1. Convertir latitud/longitud a radianes
2. Calcular distancias haversine pares
3. Identificar componentes conectados por densidad
4. Calcular casco convexo para cada clúster
5. Clasificar clústeres por atractivo ancla de nivel más alto

### Lógica del Análisis de Brechas

**Clasificación de Atractivos Ancla:**
- **Ancla Internacional**: Clúster tiene 1+ atractivos INTERNACIONAL → mercado desarrollado
- **Ancla Nacional**: Solo atractivos NACIONAL, sin internacional → potencial de desarrollo
- **Sin Ancla**: Sin atractivos superiores a REGIONAL → mayor prioridad de inversión

**Prioridad de Oportunidades de Inversión:**
1. **Alta**: Clústeres sin atractivos ancla (oportunidades greenfield)
2. **Media**: Clústeres con solo anchores nacionales (expansión)
3. **Baja**: Clústeres con anchores internacionales (mercados maduros)

## Visualizaciones

### Mapas Interactivos (PyDeck)
- **Mapa de Jerarquía**: Codificado por nivel de atractivo (local → internacional)
- **Mapa de Clústeres**: Clústeres geográficos con límites de casco convexo
- **Mapa de Brechas**: Oportunidades de inversión por nivel de prioridad

### Análisis Comparativo (Folium)
- **Mapa de Destinos**: Destinos turísticos oficiales con overlay de atractivos
- **Mapa de Atractivos Rezagados**: Atractivos no asignados fuera de límites oficiales

### Estadísticas (Matplotlib)
- Distribución de tamaños de clúster
- Desglose de estado de ancla (gráfico de dona)
- Resumen de oportunidades regionales

## Testing

Proyecto incluye tests unitarios comprehensivos con 80%+ cobertura:

```bash
# Ejecutar tests con cobertura
make coverage

# Ejecutar archivo específico
pytest tests/test_clustering.py -v

# Ejecutar tests que coincidan con patrón
pytest -k "anchor" -v
```

**Cobertura de tests:**
- Preprocesamiento y validación de datos
- Clustering HDBSCAN y cálculo de cascos
- Análisis de brechas y clasificación de oportunidades
- Generación de visualizaciones

## Documentación

- **[docs/methodology.md](docs/methodology.md)** - Metodología detallada y explicaciones de algoritmos
- **[Docstrings inline](src/cluster_turismo/)** - Docstrings Google-style para todas las funciones

## Citación

Si usa este análisis en investigación o contextos de política pública, cite como:

```
@misc{cluster-turismo,
  title={Identificación de Brechas Turísticas de Chile Mediante Clustering Espacial},
  author={Manuel San Cristóbal},
  year={2024},
  url={https://github.com/manuelsancristobal/cluster-turismo}
}
```

## Fuentes de Datos

- **SERNATUR**: [Atractivos Turísticos Nacional 2020](https://www.sernatur.cl)
  - 4,048 atractivos turísticos permanentes
  - Niveles de jerarquía: Local, Regional, Nacional, Internacional
  - 12+ categorías de atractivos

- **SERNATUR**: Destinos Turísticos Oficiales (2025)
  - 78 zonas turísticas oficiales
  - Límites de polígonos en formato KMZ (Google Earth)
  - Clasificación regional

## Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Hacer fork del repositorio
2. Crear rama de feature (`git checkout -b feature/mejora`)
3. Hacer cambios con tests
4. Enviar pull request

Todas las contribuciones deben mantener:
- >80% cobertura de tests
- Historial git limpio (mensajes descriptivos)
- Cumplimiento de estilo (ruff format)

## Licencia

Este proyecto está bajo la **Licencia MIT** - ver archivo [LICENSE](LICENSE) para detalles.

Libre para uso académico, gubernamental y comercial.

## Contacto

- **Issue Tracker**: [GitHub Issues](https://github.com/manuelsancristobal/cluster-turismo/issues)
- **Email**: msancristo@fen.uchile.cl
- **Web**: https://github.com/manuelsancristobal/cluster-turismo

---

**Estado**: Desarrollo Activo | **Última Actualización**: 2024 | **Versión Estable**: v0.1.0
