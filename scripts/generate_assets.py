"""Generar assets del portafolio: mapas interactivos y gráficos estáticos.

Ejecutar este script para crear todos los assets visuales.
Salida: assets/
"""

import os
import sys

# Agregar proyecto al path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

import matplotlib
import pandas as pd

matplotlib.use("Agg")  # Backend no interactivo
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

from cluster_turismo import clustering, data_loader, gap_analysis, preprocessing

# ── Rutas ──────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
IMG_DIR = os.path.join(ASSETS_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)

EXCEL_PATH = os.path.join(DATA_DIR, "ATRACTIVOS_TURÍSTICOS_NACIONAL_2020.xlsx")
KMZ_PATH = os.path.join(DATA_DIR, "Destinos_Nacional-Publico.kmz")

# ── 1. Carga y preprocesamiento ──────────────────────────────────────────
print("Cargando datos...")
df_raw = pd.read_excel(EXCEL_PATH)
df = preprocessing.filter_permanent_attractions(df_raw)
df = preprocessing.validate_coordinates(df)
print(f"  {len(df)} atractivos permanentes cargados")

# ── 2. Clustering ──────────────────────────────────────────────────────────
print("Ejecutando clustering HDBSCAN...")
df_clustered = clustering.run_hdbscan_spatial(df, min_cluster_size=10)

n_clusters = len(set(df_clustered["CLUSTER"])) - (1 if -1 in df_clustered["CLUSTER"].values else 0)

# ── 3. Resumen de clústeres ────────────────────────────────────────────────
print("Resumiendo clústeres...")
summary = clustering.summarize_clusters(df_clustered, hierarchy_col="JERARQUIA")
summary_classified = gap_analysis.classify_anchor_status(summary)


# Construir etiquetas de clúster desde comunas
def _build_label(comunas_series):
    ranked = comunas_series.value_counts().index.tolist()
    ranked = [c.title() for c in ranked]
    if len(ranked) >= 4:
        return f"{ranked[0]} y alrededores"
    return " - ".join(ranked)


cluster_labels = {}
for cluster_id in summary_classified.index:
    comunas = df_clustered[df_clustered["CLUSTER"] == cluster_id]["COMUNA"]
    cluster_labels[cluster_id] = _build_label(comunas)

# ── 3b. Identificar puntos de ruido como atractivos "rezagados" ──────────
df_lagging = df_clustered[df_clustered["CLUSTER"] == -1].copy()
n_lagging = len(df_lagging)
pct_lagging = (n_lagging / len(df_clustered)) * 100
print(f"Atractivos ruido/no asignados: {n_lagging} ({pct_lagging:.1f}%)")

# Clusterizar atractivos rezagados
if n_lagging > 10:
    print("Clusterizando atractivos de ruido...")
    df_lagging_clustered = clustering.run_hdbscan_spatial(df_lagging, min_cluster_size=10)
    lagging_hulls = clustering.compute_cluster_convex_hulls(df_lagging_clustered)
    lagging_labels = {}
    for cid in df_lagging_clustered[df_lagging_clustered["CLUSTER"] != -1]["CLUSTER"].unique():
        comunas = df_lagging_clustered[df_lagging_clustered["CLUSTER"] == cid]["COMUNA"]
        lagging_labels[cid] = _build_label(comunas)
    print(f"  {len(lagging_hulls)} clústeres de ruido identificados")
else:
    df_lagging_clustered = None
    lagging_hulls = {}
    lagging_labels = {}

# ── 3c. Cargar destinos oficiales desde KMZ ──────────────────────────────
print("Cargando destinos oficiales desde KMZ...")
if os.path.exists(KMZ_PATH):
    df_destinations = data_loader.load_kmz_destinations(KMZ_PATH)
    print(f"  {len(df_destinations)} destinos oficiales cargados")
else:
    print(f"  ADVERTENCIA: Archivo KMZ no encontrado en {KMZ_PATH}, omitiendo comparación de destinos")
    df_destinations = pd.DataFrame()

# Calcular cascos convexos de clústeres (usado por gráficos y mapa)
hulls = clustering.compute_cluster_convex_hulls(df_clustered)

# ── 4. Generar gráficos ────────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update(
    {
        "figure.dpi": 150,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "font.size": 10,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    }
)

# ── Gráfico 1: Histogramas de distribución de coordenadas ──
print("Generando histogramas...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].hist(df["POINT_X"], bins=50, color="#2171b5", edgecolor="white", alpha=0.9)
axes[0].set_xlabel("Longitud (°O)")
axes[0].set_ylabel("Cantidad")
axes[0].set_title("Distribución por Longitud")

axes[1].hist(df["POINT_Y"], bins=50, color="#2171b5", edgecolor="white", alpha=0.9)
axes[1].set_xlabel("Latitud (°S)")
axes[1].set_ylabel("Cantidad")
axes[1].set_title("Distribución por Latitud")

plt.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "histogramas_coordenadas.png"))
plt.close(fig)

# ── Gráfico 2: Barras de tamaño de clústeres ──
print("Generando gráfico de barras de clústeres...")
top_clusters = summary.head(15).sort_values("n_attractions")

fig, ax = plt.subplots(figsize=(14, 8))
colors = [
    "#cb181d"
    if summary_classified.loc[i, "anchor_status"] == "Sin ancla"
    else "#f59322"
    if summary_classified.loc[i, "anchor_status"] == "Solo ancla nacional"
    else "#2ca02c"
    for i in top_clusters.index
]

ax.barh(range(len(top_clusters)), top_clusters["n_attractions"], color=colors, edgecolor="white")
ax.set_yticks(range(len(top_clusters)))
ax.set_yticklabels([cluster_labels.get(i, f"Clúster {i}") for i in top_clusters.index])
ax.set_xlabel("Cantidad de Atractivos")
ax.set_title("Top 15 Clústeres por Cantidad de Atractivos")

# Leyenda
from matplotlib.patches import Patch

legend_elements = [
    Patch(facecolor="#2ca02c", label="Con ancla internacional"),
    Patch(facecolor="#f59322", label="Solo ancla nacional"),
    Patch(facecolor="#cb181d", label="Sin ancla"),
]
legend = ax.legend(handles=legend_elements, loc="lower right")
legend.get_frame().set_alpha(0.9)

plt.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "top_clusters.png"))
plt.close(fig)

# ── Gráfico 3: Donut de anclas ──
print("Generando gráfico donut de anclas...")
anchor_counts = summary_classified["anchor_status"].value_counts()

color_map = {
    "Con ancla internacional": "#2ca02c",
    "Solo ancla nacional": "#f59322",
    "Sin ancla": "#cb181d",
}
donut_colors = [color_map.get(s, "#999") for s in anchor_counts.index]

fig, ax = plt.subplots(figsize=(9, 7))
wedges, texts, autotexts = ax.pie(
    anchor_counts.values,
    labels=anchor_counts.index,
    autopct="%1.1f%%",
    colors=donut_colors,
    startangle=90,
    textprops={"fontsize": 11},
)
for autotext in autotexts:
    autotext.set_fontsize(13)
    autotext.set_fontweight("bold")

centre_circle = plt.Circle((0, 0), 0.70, fc="white")
ax.add_artist(centre_circle)
ax.set_title(f"Distribución de {n_clusters} Clústeres por Categoría de Ancla")

plt.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "donut_anclas.png"))
plt.close(fig)

# ── Gráfico 4: Distribución de jerarquía ──
print("Generando gráfico de jerarquías...")
hierarchy_counts = df["JERARQUIA"].value_counts()
hier_colors = {
    "LOCAL": "#c9c9c9",
    "REGIONAL": "#6baed6",
    "NACIONAL": "#2171b5",
    "INTERNACIONAL": "#dc1e78",
}

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(
    hierarchy_counts.index,
    hierarchy_counts.values,
    color=[hier_colors.get(h, "#999") for h in hierarchy_counts.index],
    edgecolor="white",
)
ax.set_ylabel("Cantidad de Atractivos")
ax.set_title("Atractivos por Nivel de Jerarquía")

for bar, count in zip(bars, hierarchy_counts.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 20,
        str(count),
        ha="center",
        va="bottom",
        fontweight="bold",
    )

plt.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "jerarquias.png"))
plt.close(fig)

# ── Gráfico 5: Donut de tipo de superposición de clústeres rezagados ──
if df_lagging_clustered is not None:
    print("Generando gráfico donut de superposición...")
    # Calcular superposición real entre cascos de clústeres rezagados y principales
    from cluster_turismo.gap_analysis import compute_lagging_overlap_type

    # Construir polígonos Shapely desde cascos de clústeres principales
    main_hulls_polys = {}
    for cid, coords in hulls.items():
        try:
            poly = Polygon(coords)
            if poly.is_valid:
                main_hulls_polys[cid] = poly
        except Exception:
            pass

    overlap_counts = {"Contenido": 0, "Parcialmente superpuesto": 0, "Genuinamente rezagado": 0}
    overlap_rank = {"Contenido": 3, "Parcialmente superpuesto": 2, "Genuinamente rezagado": 1, "Separado": 0}

    for cluster_id in lagging_hulls.keys():
        try:
            lagging_poly = Polygon(lagging_hulls[cluster_id])
            if not lagging_poly.is_valid:
                continue
        except Exception:
            continue

        # Buscar mejor superposición con cualquier casco de clúster principal
        best_type = "Genuinamente rezagado"
        best_score = 0
        for main_cid, main_poly in main_hulls_polys.items():
            otype = compute_lagging_overlap_type(lagging_poly, main_poly)
            score = overlap_rank.get(otype, 0)
            if score > best_score:
                best_score = score
                best_type = otype

        # Mapear "Separado" a "Genuinamente rezagado" para el gráfico
        if best_type == "Separado":
            best_type = "Genuinamente rezagado"
        if best_type in overlap_counts:
            overlap_counts[best_type] += 1

    # Solo generar gráfico si hay resultados
    if sum(overlap_counts.values()) > 0:
        color_map_overlap = {
            "Contenido": "#a8e6cf",
            "Parcialmente superpuesto": "#ffd3b6",
            "Genuinamente rezagado": "#ffaaa5",
        }
        # Filtrar categorías con conteo cero para gráfico más limpio
        overlap_counts = {k: v for k, v in overlap_counts.items() if v > 0}
        donut_colors_overlap = [color_map_overlap.get(k, "#999") for k in overlap_counts.keys()]

        fig, ax = plt.subplots(figsize=(9, 7))
        wedges, texts, autotexts = ax.pie(
            overlap_counts.values(),
            labels=overlap_counts.keys(),
            autopct="%1.1f%%",
            colors=donut_colors_overlap,
            startangle=90,
            textprops={"fontsize": 11},
        )
        for autotext in autotexts:
            autotext.set_fontsize(13)
            autotext.set_fontweight("bold")

        centre_circle = plt.Circle((0, 0), 0.70, fc="white")
        ax.add_artist(centre_circle)
        ax.set_title("Clasificación de Clústeres Rezagados por Tipo de Superposición")

        plt.tight_layout()
        fig.savefig(os.path.join(IMG_DIR, "donut_superposicion.png"))
        plt.close(fig)
    else:
        print("  ADVERTENCIA: Sin resultados de superposición, omitiendo gráfico donut_superposicion")

# ── Gráfico 6: Atractivos rezagados por región ��─
if df_lagging_clustered is not None:
    print("Generando gráfico de atractivos rezagados por región...")
    region_counts = df_lagging["REGION"].value_counts().head(12)

    fig, ax = plt.subplots(figsize=(14, 8))
    bars = ax.barh(range(len(region_counts)), region_counts.values, color="#cb181d", edgecolor="white")
    ax.set_yticks(range(len(region_counts)))
    ax.set_yticklabels(region_counts.index)
    ax.set_xlabel("Cantidad de Atractivos Rezagados")
    ax.set_title("Top 12 Regiones con Atractivos sin Destino Oficial")

    # Agregar etiquetas de valor
    for i, (bar, count) in enumerate(zip(bars, region_counts.values)):
        ax.text(count + 2, i, str(count), va="center", fontweight="bold")

    plt.tight_layout()
    fig.savefig(os.path.join(IMG_DIR, "rezagados_por_region.png"))
    plt.close(fig)

# ── Gráfico 7: Boxplot comparativo de tamaños oficiales vs rezagados ──
if df_lagging_clustered is not None and len(summary) > 0:
    print("Generando boxplot comparativo...")

    # Obtener tamaños de clústeres oficiales
    official_sizes = summary["n_attractions"].values

    # Obtener tamaños de clústeres rezagados
    lagging_cluster_summary = clustering.summarize_clusters(df_lagging_clustered, hierarchy_col="JERARQUIA")
    lagging_sizes = lagging_cluster_summary["n_attractions"].values

    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(
        [official_sizes, lagging_sizes],
        labels=["Destinos Oficiales", "Clústeres Rezagados"],
        patch_artist=True,
        widths=0.6,
    )

    # Colorear las cajas
    colors = ["#2ca02c", "#cb181d"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel("Cantidad de Atractivos por Clúster")
    ax.set_title("Comparación: Tamaño de Destinos Oficiales vs Clústeres Rezagados")

    plt.tight_layout()
    fig.savefig(os.path.join(IMG_DIR, "comparativa_boxplot.png"))
    plt.close(fig)

# ── 5. Generar mapa interactivo Folium ─────────────────────────────────────
print("Generando mapa interactivo Folium...")
import folium
from folium.plugins import GroupedLayerControl

# Crear mapa base
m = folium.Map(location=[-35.6751, -71.5430], zoom_start=5, tiles="CartoDB positron")

# Color por jerarquía
HIER_COLORS = {
    "INTERNACIONAL": "#dc1e78",
    "NACIONAL": "#4682b4",
    "REGIONAL": "#82b1d4",
    "LOCAL": "#bdc3c7",
}

# Agregar capas de jerarquía
hierarchy_groups = []
for hier in ["INTERNACIONAL", "NACIONAL", "REGIONAL", "LOCAL"]:
    fg = folium.FeatureGroup(name=hier.capitalize(), show=(hier in ["INTERNACIONAL", "NACIONAL"]))
    subset = df_clustered[df_clustered["JERARQUIA"] == hier]

    for _, row in subset.iterrows():
        cluster_name = cluster_labels.get(row.get("CLUSTER"), f"Clúster {row.get('CLUSTER', '?')}")
        popup_html = f"""
        <div style="font-family: 'Inter', sans-serif; min-width: 200px;">
            <b style="font-size: 13px;">{row.get("NOMBRE", "N/A")}</b><br>
            <span style="color: {HIER_COLORS[hier]}; font-weight: bold;">● {hier}</span><br>
            <small>Categoría: {row.get("CATEGORIA", "N/A")}</small><br>
            <small>Región: {row.get("REGION", "N/A")}</small><br>
            <small>Clúster: {cluster_name}</small>
        </div>
        """
        radius = {"INTERNACIONAL": 7, "NACIONAL": 5, "REGIONAL": 3, "LOCAL": 2}.get(hier, 2)
        folium.CircleMarker(
            location=[row["POINT_Y"], row["POINT_X"]],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row.get('NOMBRE', 'N/A')} — {cluster_name}",
            color=HIER_COLORS[hier],
            fill=True,
            fillColor=HIER_COLORS[hier],
            fillOpacity=0.7,
            weight=1,
        ).add_to(fg)

    fg.add_to(m)
    hierarchy_groups.append(fg)

# Agregar cascos de clústeres
fg_hulls = folium.FeatureGroup(name="Límites de Clústeres", show=False)

for cluster_id, hull_coords in hulls.items():
    anchor = (
        summary_classified.loc[cluster_id, "anchor_status"] if cluster_id in summary_classified.index else "Sin ancla"
    )
    hull_color = {"Con ancla internacional": "#2ecc71", "Solo ancla nacional": "#f39c12", "Sin ancla": "#e74c3c"}.get(
        anchor, "#999"
    )

    folium.Polygon(
        locations=[[lat, lon] for lat, lon in hull_coords],
        color=hull_color,
        fill=True,
        fillOpacity=0.15,
        weight=2,
        popup=f"{cluster_labels.get(cluster_id, f'Clúster {cluster_id}')} — {anchor}",
        tooltip=cluster_labels.get(cluster_id, f"Clúster {cluster_id}"),
    ).add_to(fg_hulls)

fg_hulls.add_to(m)

# Agregar capa de clústeres rezagados
if df_lagging_clustered is not None and len(lagging_hulls) > 0:
    fg_lagging = folium.FeatureGroup(name="Clústeres Rezagados", show=False)

    for cluster_id, hull_coords in lagging_hulls.items():
        folium.Polygon(
            locations=[[lat, lon] for lat, lon in hull_coords],
            color="#9b59b6",
            fill=True,
            fillOpacity=0.2,
            weight=2,
            popup=f"Rezagado: {lagging_labels.get(cluster_id, f'Clúster {cluster_id}')}",
            tooltip=lagging_labels.get(cluster_id, f"Clúster rezagado {cluster_id}"),
        ).add_to(fg_lagging)

    fg_lagging.add_to(m)

    # Agregar puntos de atractivos rezagados como capa separada
    fg_lagging_points = folium.FeatureGroup(name="Atractivos sin Destino", show=False)
    for _, row in df_lagging_clustered.iterrows():
        lagging_name = lagging_labels.get(row.get("CLUSTER"), f"Clúster {row.get('CLUSTER', '?')}")
        popup_html = f"""
        <div style="font-family: 'Inter', sans-serif; min-width: 200px;">
            <b style="font-size: 13px;">{row.get("NOMBRE", "N/A")}</b><br>
            <span style="color: #555; font-weight: bold;">● Sin destino oficial</span><br>
            <small>Región: {row.get("REGION", "N/A")}</small><br>
            <small>Clúster: {lagging_name}</small>
        </div>
        """
        folium.CircleMarker(
            location=[row["POINT_Y"], row["POINT_X"]],
            radius=3,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row.get("NOMBRE", "N/A"),
            color="#2c3e50",
            fill=True,
            fillColor="#2c3e50",
            fillOpacity=0.6,
            weight=1,
        ).add_to(fg_lagging_points)

    fg_lagging_points.add_to(m)

# Control de capas — checkboxes agrupados
cluster_layers = [fg_hulls]
if df_lagging_clustered is not None and len(lagging_hulls) > 0:
    cluster_layers.extend([fg_lagging, fg_lagging_points])

GroupedLayerControl(
    groups={
        "Destinos & Clústeres": cluster_layers,
        "Atractivos por Jerarquía": hierarchy_groups,
    },
    exclusive_groups=False,
    collapsed=False,
).add_to(m)

# Leyenda
legend_html = """
<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
     background-color: white; padding: 15px; border-radius: 8px;
     box-shadow: 0 2px 6px rgba(0,0,0,0.3); font-family: 'Inter', sans-serif; font-size: 12px;">
    <b style="font-size: 13px;">Leyenda</b><br>
    <b>Jerarquía:</b><br>
    <span style="color: #dc1e78;">●</span> Internacional<br>
    <span style="color: #4682b4;">●</span> Nacional<br>
    <span style="color: #82b1d4;">●</span> Regional<br>
    <span style="color: #bdc3c7;">●</span> Local<br>
    <hr style="margin: 5px 0;">
    <b>Clústeres:</b><br>
    <span style="color: #2ecc71;">■</span> Con ancla internacional<br>
    <span style="color: #f39c12;">■</span> Solo ancla nacional<br>
    <span style="color: #e74c3c;">■</span> Sin ancla<br>
    <hr style="margin: 5px 0;">
    <b>Rezagados:</b><br>
    <span style="color: #9b59b6;">■</span> Clústeres Rezagados
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Guardar
map_path = os.path.join(ASSETS_DIR, "mapa_interactivo.html")
m.save(map_path)
print(f"  Mapa guardado: {map_path}")

# ── 6. Estadísticas resumen para la página ─────────────────────────────────
print("\n" + "=" * 50)
print("ESTAD��STICAS PARA PÁGINA DE PORTAFOLIO:")
print(f"  Total de atractivos: {len(df)}")
print(f"  Clústeres encontrados: {n_clusters}")
print(f"  Atractivos ruido/no asignados: {n_lagging} ({pct_lagging:.1f}%)")
if df_lagging_clustered is not None:
    print(f"  Clústeres de ruido identificados: {len(lagging_hulls)}")
print("  Distribución de anclas:")
for status, count in anchor_counts.items():
    print(f"    {status}: {count}")
print("=" * 50)

print(f"\nTodos los assets guardados en: {ASSETS_DIR}")
print("Archivos generados:")
for root, dirs, files in os.walk(ASSETS_DIR):
    for f in files:
        full = os.path.join(root, f)
        size_mb = os.path.getsize(full) / 1024 / 1024
        print(f"  {os.path.relpath(full, ASSETS_DIR)} ({size_mb:.1f} MB)")
