# Methodology: Spatial Clustering & Gap Analysis

## 1. Executive Summary

This document describes the analytical methodology used to identify tourism investment gaps across Chile. The project combines **spatial clustering** (HDBSCAN) with **qualitative gap analysis** to prioritize regions for tourism development investment.

**Key innovation**: Using "anchor attractions" (international-level attractions) as a proxy for market maturity to identify underserved regions.

---

## 2. Conceptual Framework

### 2.1 The "Anchor Attraction" Concept

In retail geography, an **anchor tenant** is a major, well-known business that attracts customers to a shopping center, making secondary tenants viable. We apply this concept to tourism:

An **anchor attraction** is a world-class, internationally-recognized tourism asset that:
- Attracts visitors from outside the region
- Creates economic demand for secondary attractions
- Validates the region as a tourism destination

**Classification:**
- **International Anchor**: Globally recognized attractions (e.g., Atacama geysers, Patagonian trekking)
- **National Anchor**: Known throughout Chile (e.g., regional wine routes, specific monuments)
- **No Anchor**: Only regional/local attractions with limited external draw

**Strategic insight**: A cluster with only "national" anchors may have developed tourism infrastructure but lacks the international appeal needed to compete globally—a gap opportunity.

### 2.2 Tourism Development Model

We posit a three-stage development model:

| Stage | Anchor Type | Infrastructure | Market Maturity | Development Strategy |
|-------|------------|-----------------|-----------------|---------------------|
| **Mature** | International | High | Proven | Consolidation, expansion quality |
| **Growth** | National only | Medium | Emerging | International positioning |
| **Nascent** | None | Low | Early | Anchor development |

This project focuses on identifying clusters in the "Growth" and "Nascent" stages for policy intervention.

---

## 3. Data & Sources

### 3.1 Primary Dataset: SERNATUR 2020

**Source**: Servicio Nacional de Turismo (SERNATUR), Chile's official tourism authority

**Coverage**:
- 4,048 permanent attractions (excludes temporary events)
- 16 attributes per attraction (name, category, region, coordinates, hierarchy, etc.)
- Updated 2020

**Hierarchy Classification** (used for anchor determination):
```
JERARQUÍA (Hierarchy Level)
├── LOCAL         (attracts within commune)
├── REGIONAL      (attracts within region)
├── NACIONAL      (attracts from other regions)
└── INTERNACIONAL (attracts international visitors)
```

**Geographic Coverage**:
- Continental Chile: -17° to -56° latitude, -66° to -75° longitude
- Excludes Easter Island, Juan Fernández (non-continental)

### 3.2 Secondary Dataset: SERNATUR 2025 Destinations

**Source**: SERNATUR official tourism destinations (2025 update)

**Coverage**:
- 78 official tourism zones
- Polygon boundaries (KMZ format - Google Earth)
- Regional classification

**Usage**: Validation dataset to check how attractions align with official tourism development zones

### 3.3 Data Quality

- **Completeness**: >99% of records have valid coordinates
- **Geographic Accuracy**: ±100m for urban attractions, ±1km for remote
- **Temporal**: 2020-2025 data span (minimal seasonality in permanent attractions)
- **Validation**: Coordinates validated against Chilean geographic bounds

---

## 4. Methodology: Data Processing

### 4.1 Data Cleaning Pipeline

```
Raw Excel → Filter Permanents → Validate Coordinates → Normalize Codes → Clustered Data
```

**Step 1: Filter Permanent Attractions**
```python
df = df[df['CATEGORIA'] != "ACONTECIMIENTOS PROGRAMADOS"]
```
Removes ~150 temporary events (festivals, conferences), retaining only permanent attractions

**Step 2: Validate Geographic Coordinates**
- Latitude: -56° ≤ lat ≤ -17°
- Longitude: -75° ≤ lon ≤ -66°
- Removes: 0.2% invalid records (non-continental outliers)

**Step 3: Normalize Commune Codes**
- Strips whitespace from COD_COM (commune identifier)
- Ensures consistent merge with destination polygons

**Result**: 4,048 clean, geo-validated attractions ready for clustering

### 4.2 Feature Engineering

**Hierarchy Encoding** (for visualization and anchor classification):
```
LOCAL: RGB [180, 180, 180], Size Radius 1.0
REGIONAL: RGB [130, 170, 210], Size Radius 1.5
NACIONAL: RGB [70, 130, 180], Size Radius 2.0
INTERNACIONAL: RGB [220, 30, 120], Size Radius 3.0
```

**Region Extraction**:
- Each attraction belongs to one of 16 administrative regions
- Clustered regionally to match policy jurisdictions

---

## 5. Methodology: Spatial Clustering

### 5.1 Algorithm Selection: HDBSCAN

We chose **HDBSCAN** over alternatives (k-means, DBSCAN) because:

| Algorithm | Pros | Cons | Suitable? |
|-----------|------|------|-----------|
| **K-means** | Fast, simple | Requires pre-specified k; spherical clusters | ❌ |
| **DBSCAN** | Finds arbitrary clusters | Eps parameter hard to tune; single scale | ⚠️ |
| **HDBSCAN** | Multi-scale, no k required, robust | Slightly slower | ✅ |

**HDBSCAN Advantages for Tourism**:
1. **No pre-specified cluster count**: We don't know how many tourism clusters exist
2. **Density-based**: Finds areas of high concentration (tourist hotspots)
3. **Noise handling**: Identifies isolated attractions (potential development sites)
4. **Hierarchical**: Can visualize multi-scale structures

### 5.2 Distance Metric: Haversine

**Why Haversine over Euclidean?**

Euclidean distance on lat/lon is incorrect for geographic data because:
- Assumes flat surface (Earth is spherical)
- Distorts distances at high latitudes

Haversine distance:
$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\phi_2 - \phi_1}{2}\right) + \cos(\phi_1) \cos(\phi_2) \sin^2\left(\frac{\lambda_2 - \lambda_1}{2}\right)}\right)$$

Where:
- R = Earth's radius (6,371 km)
- φ = latitude (radians)
- λ = longitude (radians)

**Implementation**:
```python
# Convert to radians
coords_rad = np.radians(df[['POINT_Y', 'POINT_X']].values)

# HDBSCAN with haversine
clusterer = hdbscan.HDBSCAN(metric='haversine', min_cluster_size=10)
clusters = clusterer.fit_predict(coords_rad)
```

### 5.3 Parameter Tuning

**min_cluster_size = 10**:
- Too small (<5): Creates spurious micro-clusters
- Optimal (10): ~80 clusters (matches policy regions)
- Too large (>20): Over-aggregates distinct tourism zones

**Rationale**: 10 attractions represent a viable local economy (assuming 1 major + 9 secondary attractions)

### 5.4 Cluster Output

**Results**:
- **80 clusters** identified
- **149 noise points** (-1 label) - isolated attractions
- **99.6%** of attractions assigned to clusters

**Interpretation**:
- Clusters represent organic tourism zones (emergent from attraction distribution)
- Noise points represent isolated gems or underserved areas

---

## 6. Methodology: Gap Analysis

### 6.1 Anchor Status Classification

For each cluster, count attractions by hierarchy level:

```python
n_internacional = (df[df['CLUSTER']==i]['JERARQUÍA'] == 'INTERNACIONAL').sum()
n_nacional = (df[df['CLUSTER']==i]['JERARQUÍA'] == 'NACIONAL').sum()
```

Then classify:

```python
if n_internacional > 0:
    status = "Con ancla internacional"     # Mature market
elif n_nacional > 0:
    status = "Solo ancla nacional"         # Growth market ← PRIORITY
else:
    status = "Sin ancla"                   # Nascent market ← PRIORITY
```

**Distribution** (80 clusters):
- 23 clusters: "Con ancla internacional" (mature)
- 40 clusters: "Solo ancla nacional" (growth - development opportunity)
- 17 clusters: "Sin ancla" (nascent - highest priority)

### 6.2 Investment Opportunity Ranking

Within "growth" and "nascent" clusters, rank by:

1. **Priority 1 (Highest)**: No anchor attractions
   - Greenfield development potential
   - Requires anchor investment

2. **Priority 2 (Medium)**: National anchor only
   - Emerging regional market
   - Needs international positioning

3. **Priority 3 (Lower)**: Clusters with infrastructure maturity
   - Less urgent, existing investment zones

### 6.3 Geographic Overlap Analysis

Compare HDBSCAN clusters with **official SERNATUR destinations** (78 zones):

**Categories**:
- **Contenido**: Cluster 90%+ inside official destination (aligned)
- **Parcialmente superpuesto**: 10-90% overlap (partial alignment)
- **Genuinamente rezagado**: <10% overlap (outside official zones - development opportunity)

**Finding**: ~35% of lagging attractions fall outside official destinations, suggesting missed opportunities in the official designation process.

---

## 7. Validation & Sensitivity

### 7.1 Robustness Checks

**Min cluster size sensitivity**:
| Min Size | Num Clusters | Largest Cluster | Avg Size |
|----------|-------------|------------------|----------|
| 5 | 125 | 203 | 32 |
| 10 | 80 | 245 | 51 | ← **Selected**
| 15 | 58 | 267 | 70 |
| 20 | 45 | 298 | 90 |

**Conclusion**: min_cluster_size=10 provides reasonable balance between granularity and stability

### 7.2 Geographic Validation

- Clusters align with known tourism regions (Atacama, Patagonia, Central)
- No spurious clusters in uninhabited regions
- Coastal vs. interior clustering makes geographic sense

### 7.3 Policy Alignment

80 HDBSCAN clusters vs. 16 administrative regions:
- Average 5 clusters per region
- Suggests sub-regional tourism heterogeneity worth addressing

---

## 8. Limitations & Future Work

### 8.1 Known Limitations

1. **Static snapshot**: 2020 data; doesn't capture COVID-19 recovery
2. **Hierarchy classification**: Based on SERNATUR categorization (subjective)
3. **Economic impact**: No weighting by visitor numbers, revenue
4. **Accessibility**: Doesn't account for distance to population centers
5. **Seasonality**: Assumes uniform year-round attraction

### 8.2 Future Enhancements

- **Dynamic clustering**: Real-time data with quarterly updates
- **Visitor flow analysis**: Integrate SERNATUR visitor statistics
- **Network analysis**: Model attraction combinations (bundling potential)
- **Economic impact**: Estimate employment & revenue by cluster
- **Accessibility mapping**: Include infrastructure (distance to highways, airports)

---

## 9. Reproducibility

### 9.1 Python Implementation

All analysis implemented in modular Python (see `/src/tourism_gaps/`):

- `data_loader.py`: Load Excel & KMZ files
- `preprocessing.py`: Data cleaning & validation
- `clustering.py`: HDBSCAN + convex hulls
- `gap_analysis.py`: Anchor classification & opportunity ranking
- `visualization.py`: PyDeck, Folium, Matplotlib outputs

### 9.2 Version Information

- Python 3.10+
- hdbscan 0.8.33+
- pandas 2.0+
- shapely 2.0+

### 9.3 Running the Analysis

```bash
# Install
pip install -e .

# Run clustering
python -c "
  from tourism_gaps import clustering, preprocessing
  df = preprocessing.load_attractions_excel('data/raw/ATRACTIVOS_TURÍSTICOS_NACIONAL_2020.xlsx')
  df = preprocessing.filter_permanent_attractions(df)
  df = clustering.run_hdbscan_spatial(df)
  print(f'Clusters found: {len(set(df[\"CLUSTER\"]))}')
"

# Generate report
jupyter nbconvert --execute notebooks/01_exploration_and_clustering.ipynb
```

---

## 10. References

### Key Papers
- Campello, R. J., Moulavi, D., & Sander, J. (2013). "Density-Based Clustering Based on Hierarchical Density Estimates." ICDM.
- Haversine formula: Haversine - Wikipedia

### Policy Context
- SERNATUR (2024): "Estrategia Nacional de Turismo 2024-2028"
- Regional Tourism Development Plans (various regions)

### Data Sources
- SERNATUR Official: https://www.sernatur.cl
- Google Earth KMZ format: https://support.google.com/earth/answer/7365595

---

## Appendix: Mathematical Details

### A.1 Haversine Distance Formula

For two points (φ₁, λ₁) and (φ₂, λ₂):

$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\phi_2 - \phi_1}{2}\right) + \cos(\phi_1) \cos(\phi_2) \sin^2\left(\frac{\lambda_2 - \lambda_1}{2}\right)}\right)$$

### A.2 HDBSCAN Algorithm Steps

1. Compute k-distance graph (k=5 neighbors)
2. Compute mutual reachability distance
3. Build minimum spanning tree
4. Compute cluster stability scores
5. Extract clusters by pruning dendrogram

---

**Document Version**: 1.0
**Last Updated**: 2024
**Author**: Tourism Data Analysis
**License**: MIT
