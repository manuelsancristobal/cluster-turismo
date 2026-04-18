# Metodología: Clustering Espacial y Análisis de Brechas

## 1. Resumen Ejecutivo

Este documento describe la metodología analítica utilizada para identificar brechas de inversión turística en Chile. El proyecto combina **clustering espacial** (HDBSCAN) con **análisis cualitativo de brechas** para priorizar regiones para inversión en desarrollo turístico.

**Innovación clave**: Uso de "atractivos ancla" (atractivos de nivel internacional) como proxy de madurez de mercado para identificar regiones desatendidas.

---

## 2. Marco Conceptual

### 2.1 El Concepto de "Atractivo Ancla"

En geografía comercial, un **tenant ancla** es un negocio principal y reconocido que atrae clientes a un centro comercial, haciendo viables a los tenants secundarios. Aplicamos este concepto al turismo:

Un **atractivo ancla** es un activo turístico de clase mundial, reconocido internacionalmente, que:
- Atrae visitantes desde fuera de la región
- Crea demanda económica para atractivos secundarios
- Valida la región como destino turístico

**Clasificación:**
- **Ancla Internacional**: Atractivos reconocidos globalmente (ej., géiseres de Atacama, trekking en Patagonia)
- **Ancla Nacional**: Conocidos en todo Chile (ej., rutas del vino regionales, monumentos específicos)
- **Sin Ancla**: Solo atractivos regionales/locales con limitada atracción externa

**Insight estratégico**: Un clúster con solo anclas "nacionales" puede tener infraestructura turística desarrollada pero carece del atractivo internacional necesario para competir globalmente—una oportunidad de brecha.

### 2.2 Modelo de Desarrollo Turístico

Postulamos un modelo de desarrollo en tres etapas:

| Etapa | Tipo de Ancla | Infraestructura | Madurez de Mercado | Estrategia de Desarrollo |
|-------|--------------|-----------------|---------------------|--------------------------|
| **Maduro** | Internacional | Alta | Comprobada | Consolidación, expansión de calidad |
| **Crecimiento** | Solo nacional | Media | Emergente | Posicionamiento internacional |
| **Naciente** | Ninguna | Baja | Temprana | Desarrollo de ancla |

Este proyecto se enfoca en identificar clústeres en las etapas de "Crecimiento" y "Naciente" para intervención de política pública.

---

## 3. Datos y Fuentes

### 3.1 Dataset Primario: SERNATUR 2020

**Fuente**: Servicio Nacional de Turismo (SERNATUR), autoridad oficial de turismo de Chile

**Cobertura**:
- 4.048 atractivos permanentes (excluye eventos temporales)
- 16 atributos por atractivo (nombre, categoría, región, coordenadas, jerarquía, etc.)
- Actualizado 2020

**Clasificación de Jerarquía** (usada para determinación de ancla):
```
JERARQUÍA (Nivel de Jerarquía)
├── LOCAL         (atrae dentro de la comuna)
├── REGIONAL      (atrae dentro de la región)
├── NACIONAL      (atrae desde otras regiones)
└── INTERNACIONAL (atrae visitantes internacionales)
```

**Cobertura Geográfica**:
- Chile continental: latitud -17° a -56°, longitud -66° a -75°
- Excluye Isla de Pascua, Juan Fernández (no continentales)

### 3.2 Dataset Secundario: Destinos SERNATUR 2025

**Fuente**: Destinos turísticos oficiales SERNATUR (actualización 2025)

**Cobertura**:
- 78 zonas turísticas oficiales
- L��mites de polígonos (formato KMZ - Google Earth)
- Clasificación regional

**Uso**: Dataset de validación para verificar cómo los atractivos se alinean con las zonas oficiales de desarrollo turístico

### 3.3 Calidad de Datos

- **Completitud**: >99% de registros tienen coordenadas válidas
- **Precisión Geográfica**: ±100m para atractivos urbanos, ±1km para remotos
- **Temporal**: Rango de datos 2020-2025 (mínima estacionalidad en atractivos permanentes)
- **Validación**: Coordenadas validadas contra límites geográficos chilenos

---

## 4. Metodología: Procesamiento de Datos

### 4.1 Pipeline de Limpieza de Datos

```
Excel bruto → Filtrar Permanentes → Validar Coordenadas → Normalizar Códigos → Datos Clusterizados
```

**Paso 1: Filtrar Atractivos Permanentes**
```python
df = df[df['CATEGORIA'] != "ACONTECIMIENTOS PROGRAMADOS"]
```
Elimina ~150 eventos temporales (festivales, conferencias), reteniendo solo atractivos permanentes

**Paso 2: Validar Coordenadas Geográficas**
- Latitud: -56° ≤ lat ≤ -17°
- Longitud: -75° ≤ lon ≤ -66°
- Elimina: 0.2% registros inválidos (outliers no continentales)

**Paso 3: Normalizar Códigos de Comuna**
- Elimina espacios en blanco de COD_COM (identificador de comuna)
- Asegura merge consistente con polígonos de destino

**Resultado**: 4.048 atractivos limpios y geo-validados listos para clustering

### 4.2 Ingeniería de Variables

**Codificación de Jerarquía** (para visualización y clasificación de ancla):
```
LOCAL: RGB [180, 180, 180], Radio 1.0
REGIONAL: RGB [130, 170, 210], Radio 1.5
NACIONAL: RGB [70, 130, 180], Radio 2.0
INTERNACIONAL: RGB [220, 30, 120], Radio 3.0
```

**Extracción Regional**:
- Cada atractivo pertenece a una de 16 regiones administrativas
- Agrupados regionalmente para coincidir con jurisdicciones de política pública

---

## 5. Metodología: Clustering Espacial

### 5.1 Selección de Algoritmo: HDBSCAN

Elegimos **HDBSCAN** sobre alternativas (k-means, DBSCAN) porque:

| Algoritmo | Pros | Contras | ¿Adecuado? |
|-----------|------|---------|-------------|
| **K-means** | Rápido, simple | Requiere k pre-especificado; clústeres esféricos | ❌ |
| **DBSCAN** | Encuentra clústeres arbitrarios | Parámetro eps difícil de ajustar; escala única | ⚠️ |
| **HDBSCAN** | Multi-escala, no requiere k, robusto | Ligeramente más lento | ✅ |

**Ventajas de HDBSCAN para Turismo**:
1. **Sin conteo de clústeres pre-especificado**: No sabemos cuántos clústeres turísticos existen
2. **Basado en densidad**: Encuentra áreas de alta concentración (hotspots turísticos)
3. **Manejo de ruido**: Identifica atractivos aislados (sitios potenciales de desarrollo)
4. **Jerárquico**: Puede visualizar estructuras multi-escala

### 5.2 Métrica de Distancia: Haversine

**¿Por qué Haversine sobre Euclidiana?**

La distancia euclidiana en lat/lon es incorrecta para datos geográficos porque:
- Asume superficie plana (la Tierra es esférica)
- Distorsiona distancias en latitudes altas

Distancia haversine:
$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\phi_2 - \phi_1}{2}\right) + \cos(\phi_1) \cos(\phi_2) \sin^2\left(\frac{\lambda_2 - \lambda_1}{2}\right)}\right)$$

Donde:
- R = Radio de la Tierra (6.371 km)
- φ = latitud (radianes)
- λ = longitud (radianes)

**Implementación**:
```python
# Convertir a radianes
coords_rad = np.radians(df[['POINT_Y', 'POINT_X']].values)

# HDBSCAN con haversine
clusterer = hdbscan.HDBSCAN(metric='haversine', min_cluster_size=10)
clusters = clusterer.fit_predict(coords_rad)
```

### 5.3 Ajuste de Parámetros

**min_cluster_size = 10**:
- Muy pequeño (<5): Crea micro-clústeres espurios
- Óptimo (10): ~80 clústeres (coincide con regiones de política pública)
- Muy grande (>20): Sobre-agrega zonas turísticas distintas

**Fundamento**: 10 atractivos representan una economía local viable (asumiendo 1 principal + 9 atractivos secundarios)

### 5.4 Resultado del Clustering

**Resultados**:
- **79 clústeres** identificados
- ~33% de atractivos clasificados como ruido (etiqueta -1) - atractivos aislados/dispersos
- ~67% de atractivos asignados a clústeres

**Interpretación**:
- Los clústeres representan zonas turísticas orgánicas (emergentes de la distribución de atractivos)
- Los puntos de ruido representan joyas aisladas o áreas desatendidas

---

## 6. Metodología: Análisis de Brechas

### 6.1 Clasificación de Estado de Ancla

Para cada clúster, contar atractivos por nivel de jerarquía:

```python
n_internacional = (df[df['CLUSTER']==i]['JERARQUÍA'] == 'INTERNACIONAL').sum()
n_nacional = (df[df['CLUSTER']==i]['JERARQUÍA'] == 'NACIONAL').sum()
```

Luego clasificar:

```python
if n_internacional > 0:
    status = "Con ancla internacional"     # Mercado maduro
elif n_nacional > 0:
    status = "Solo ancla nacional"         # Mercado en crecimiento ← PRIORIDAD
else:
    status = "Sin ancla"                   # Mercado naciente ← PRIORIDAD
```

**Distribución** (79 clústeres):
- 52 clústeres: "Con ancla internacional" (maduros)
- 26 clústeres: "Solo ancla nacional" (crecimiento - oportunidad de desarrollo)
- ~1-2 clústeres: "Sin ancla" (nacientes - mayor prioridad)

### 6.2 Ranking de Oportunidades de Inversión

Dentro de los clústeres de "crecimiento" y "nacientes", rankear por:

1. **Prioridad 1 (Máxima)**: Sin atractivos ancla
   - Potencial de desarrollo greenfield
   - Requiere inversión en ancla

2. **Prioridad 2 (Media)**: Solo ancla nacional
   - Mercado regional emergente
   - Necesita posicionamiento internacional

3. **Prioridad 3 (Menor)**: Clústeres con madurez de infraestructura
   - Menos urgente, zonas de inversión existentes

### 6.3 Análisis de Superposición Geográfica

Comparar clústeres HDBSCAN con **destinos oficiales SERNATUR** (78 zonas):

**Categorías**:
- **Contenido**: Clúster 90%+ dentro de destino oficial (alineado)
- **Parcialmente superpuesto**: 10-90% superposición (alineación parcial)
- **Genuinamente rezagado**: <10% superposición (fuera de zonas oficiales - oportunidad de desarrollo)

**Hallazgo**: ~35% de los atractivos rezagados caen fuera de destinos oficiales, sugiriendo oportunidades perdidas en el proceso de designación oficial.

---

## 7. Validación y Sensibilidad

### 7.1 Verificaciones de Robustez

**Sensibilidad de tamaño mínimo de clúster**:
| Tamaño Mín | Núm Clústeres | Clúster Mayor | Tamaño Promedio |
|------------|---------------|---------------|-----------------|
| 5 | 125 | 203 | 32 |
| 10 | 79 | 245 | 51 | ← **Seleccionado**
| 15 | 58 | 267 | 70 |
| 20 | 45 | 298 | 90 |

**Conclusión**: min_cluster_size=10 provee un balance razonable entre granularidad y estabilidad

### 7.2 Validación Geográfica

- Los clústeres se alinean con regiones turísticas conocidas (Atacama, Patagonia, Central)
- No hay clústeres espurios en regiones deshabitadas
- El clustering costero vs. interior tiene sentido geográfico

### 7.3 Alineación con Política Pública

80 clústeres HDBSCAN vs. 16 regiones administrativas:
- Promedio 5 clústeres por región
- Sugiere heterogeneidad turística sub-regional que vale la pena abordar

---

## 8. Limitaciones y Trabajo Futuro

### 8.1 Limitaciones Conocidas

1. **Foto estática**: Datos 2020; no captura la recuperación post-COVID-19
2. **Clasificación de jerarquía**: Basada en categorización SERNATUR (subjetiva)
3. **Impacto económico**: Sin ponderación por número de visitantes o ingresos
4. **Accesibilidad**: No considera distancia a centros poblados
5. **Estacionalidad**: Asume atracción uniforme todo el año

### 8.2 Mejoras Futuras

- **Clustering dinámico**: Datos en tiempo real con actualizaciones trimestrales
- **Análisis de flujo de visitantes**: Integrar estadísticas de visitantes SERNATUR
- **Análisis de redes**: Modelar combinaciones de atractivos (potencial de bundling)
- **Impacto económico**: Estimar empleo e ingresos por clúster
- **Mapeo de accesibilidad**: Incluir infraestructura (distancia a carreteras, aeropuertos)

---

## 9. Reproducibilidad

### 9.1 Implementación en Python

Todo el análisis implementado en Python modular (ver `/src/cluster_turismo/`):

- `data_loader.py`: Carga de archivos Excel y KMZ
- `preprocessing.py`: Limpieza y validación de datos
- `clustering.py`: HDBSCAN + cascos convexos
- `gap_analysis.py`: Clasificación de ancla y ranking de oportunidades
- `visualization.py`: Salidas PyDeck, Folium, Matplotlib

### 9.2 Información de Versiones

- Python 3.10+
- hdbscan 0.8.33+
- pandas 2.0+
- shapely 2.0+

### 9.3 Ejecutar el Análisis

```bash
# Instalar
pip install -e .

# Ejecutar clustering
python -c "
  from cluster_turismo import clustering, preprocessing, data_loader
  df = data_loader.load_attractions_excel('data/ATRACTIVOS_TURÍSTICOS_NACIONAL_2020.xlsx')
  df = preprocessing.filter_permanent_attractions(df)
  df = clustering.run_hdbscan_spatial(df)
  print(f'Clústeres encontrados: {len(set(df[\"CLUSTER\"]))}')
"

# Generar reporte
jupyter nbconvert --execute "notebooks/Publico_Visualización_de_Atractivos.ipynb"
```

---

## 10. Referencias

### Artículos Clave
- Campello, R. J., Moulavi, D., & Sander, J. (2013). "Density-Based Clustering Based on Hierarchical Density Estimates." ICDM.
- Fórmula Haversine: Haversine - Wikipedia

### Contexto de Política Pública
- SERNATUR (2024): "Estrategia Nacional de Turismo 2024-2028"
- Planes Regionales de Desarrollo Turístico (varias regiones)

### Fuentes de Datos
- SERNATUR Oficial: https://www.sernatur.cl
- Formato KMZ Google Earth: https://support.google.com/earth/answer/7365595

---

## Apéndice: Detalles Matemáticos

### A.1 Fórmula de Distancia Haversine

Para dos puntos (φ₁, λ₁) y (φ₂, λ₂):

$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\phi_2 - \phi_1}{2}\right) + \cos(\phi_1) \cos(\phi_2) \sin^2\left(\frac{\lambda_2 - \lambda_1}{2}\right)}\right)$$

### A.2 Pasos del Algoritmo HDBSCAN

1. Calcular grafo de k-distancias (k=5 vecinos)
2. Calcular distancia de alcanzabilidad mutua
3. Construir árbol de expansión mínima
4. Calcular puntajes de estabilidad de clústeres
5. Extraer clústeres podando dendrograma

---

**Versión del Documento**: 1.0
**Última Actualización**: 2024
**Autor**: Manuel San Cristóbal
**Licencia**: MIT
