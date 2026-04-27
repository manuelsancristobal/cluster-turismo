"""Generar assets del portafolio: mapas interactivos y gráficos estáticos."""

from __future__ import annotations

import folium
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from folium.plugins import GroupedLayerControl
from matplotlib.patches import Patch
from shapely.geometry import Polygon

from cluster_turismo import clustering, data_loader, gap_analysis, preprocessing
from cluster_turismo.config import (
    ASSETS_DIR,
    ASSETS_IMG_DIR,
    BAR_COLOR_CON_ANCLA,
    BAR_COLOR_SIN_ANCLA,
    BAR_COLOR_SOLO_NACION,
    CHILE_LAT,
    CHILE_LON,
    EXCEL_PATH,
    HDBSCAN_MIN_CLUSTER_SIZE,
    HIER_COLORS_HEX,
    HULL_COLORS_HEX,
    KMZ_PATH,
    OVERLAP_COLORS_HEX,
    PLOT_DPI,
    PLOT_STYLE,
)

matplotlib.use("Agg")  # Backend no interactivo


def _build_label(comunas_series: pd.Series) -> str:
    """Construye etiqueta descriptiva para el clúster."""
    ranked = comunas_series.value_counts().index.tolist()
    ranked = [str(c).title() for c in ranked]
    if len(ranked) >= 4:
        return f"{ranked[0]} y alrededores"
    return " - ".join(ranked)


def generate() -> None:
    """Ejecuta el pipeline completo de generación de assets."""
    ASSETS_IMG_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Carga y preprocesamiento
    print("Cargando datos...")
    df_raw = pd.read_excel(EXCEL_PATH)
    df = preprocessing.filter_permanent_attractions(df_raw)
    df = preprocessing.validate_coordinates(df)
    print(f"  {len(df)} atractivos permanentes cargados")

    # 2. Clustering
    print("Ejecutando clustering HDBSCAN...")
    df_clustered = clustering.run_hdbscan_spatial(df, min_cluster_size=HDBSCAN_MIN_CLUSTER_SIZE)
    n_clusters = len(set(df_clustered["CLUSTER"])) - (1 if -1 in df_clustered["CLUSTER"].values else 0)

    # 3. Resumen de clústeres
    print("Resumiendo clústeres...")
    summary = clustering.summarize_clusters(df_clustered, hierarchy_col="JERARQUIA")
    summary_classified = gap_analysis.classify_anchor_status(summary)

    cluster_labels = {}
    for cluster_id in summary_classified.index:
        comunas = df_clustered[df_clustered["CLUSTER"] == cluster_id]["COMUNA"]
        cluster_labels[cluster_id] = _build_label(comunas)

    # 3b. Identificar puntos de ruido como atractivos "rezagados"
    df_lagging = df_clustered[df_clustered["CLUSTER"] == -1].copy()
    n_lagging = len(df_lagging)
    pct_lagging = (n_lagging / len(df_clustered)) * 100
    print(f"Atractivos ruido/no asignados: {n_lagging} ({pct_lagging:.1f}%)")

    if n_lagging > 10:
        print("Clusterizando atractivos de ruido...")
        df_lagging_clustered = clustering.run_hdbscan_spatial(df_lagging, min_cluster_size=HDBSCAN_MIN_CLUSTER_SIZE)
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

    # 3c. Cargar destinos oficiales desde KMZ
    print("Cargando destinos oficiales desde KMZ...")
    if KMZ_PATH.exists():
        df_destinations = data_loader.load_kmz_destinations(str(KMZ_PATH))
        print(f"  {len(df_destinations)} destinos oficiales cargados")
    else:
        print(f"  ADVERTENCIA: Archivo KMZ no encontrado en {KMZ_PATH}, omitiendo comparación de destinos")
        df_destinations = pd.DataFrame()

    hulls = clustering.compute_cluster_convex_hulls(df_clustered)

    # 4. Generar gráficos
    plt.style.use(PLOT_STYLE)
    plt.rcParams.update(
        {
            "figure.dpi": PLOT_DPI,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "font.size": 10,
            "savefig.dpi": PLOT_DPI,
            "savefig.bbox": "tight",
        }
    )

    # Gráfico 1: Histogramas
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
    fig.savefig(ASSETS_IMG_DIR / "histogramas_coordenadas.png")
    plt.close(fig)

    # Gráfico 2: Barras
    print("Generando gráfico de barras de clústeres...")
    top_clusters = summary.head(15).sort_values("n_attractions")
    fig, ax = plt.subplots(figsize=(14, 8))
    colors = [
        BAR_COLOR_SIN_ANCLA
        if summary_classified.loc[i, "anchor_status"] == "Sin ancla"
        else BAR_COLOR_SOLO_NACION
        if summary_classified.loc[i, "anchor_status"] == "Solo ancla nacional"
        else BAR_COLOR_CON_ANCLA
        for i in top_clusters.index
    ]
    ax.barh(range(len(top_clusters)), top_clusters["n_attractions"], color=colors, edgecolor="white")
    ax.set_yticks(range(len(top_clusters)))
    ax.set_yticklabels([cluster_labels.get(i, f"Clúster {i}") for i in top_clusters.index])
    ax.set_xlabel("Cantidad de Atractivos")
    ax.set_title("Top 15 Clústeres por Cantidad de Atractivos")
    legend_elements = [
        Patch(facecolor=BAR_COLOR_CON_ANCLA, label="Con ancla internacional"),
        Patch(facecolor=BAR_COLOR_SOLO_NACION, label="Solo ancla nacional"),
        Patch(facecolor=BAR_COLOR_SIN_ANCLA, label="Sin ancla"),
    ]
    ax.legend(handles=legend_elements, loc="lower right").get_frame().set_alpha(0.9)
    plt.tight_layout()
    fig.savefig(ASSETS_IMG_DIR / "top_clusters.png")
    plt.close(fig)

    # Gráfico 3: Donut anclas
    print("Generando gráfico donut de anclas...")
    anchor_counts = summary_classified["anchor_status"].value_counts()
    color_map = {
        "Con ancla internacional": BAR_COLOR_CON_ANCLA,
        "Solo ancla nacional": BAR_COLOR_SOLO_NACION,
        "Sin ancla": BAR_COLOR_SIN_ANCLA,
    }
    donut_colors = [color_map.get(s, "#999") for s in anchor_counts.index]
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.pie(
        anchor_counts.values,
        labels=anchor_counts.index,
        autopct="%1.1f%%",
        colors=donut_colors,
        startangle=90,
        textprops={"fontsize": 11},
    )
    ax.add_artist(plt.Circle((0, 0), 0.70, fc="white"))
    ax.set_title(f"Distribución de {n_clusters} Clústeres por Categoría de Ancla")
    plt.tight_layout()
    fig.savefig(ASSETS_IMG_DIR / "donut_anclas.png")
    plt.close(fig)

    # Gráfico 4: Jerarquías
    print("Generando gráfico de jerarquías...")
    hierarchy_counts = df["JERARQUIA"].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        hierarchy_counts.index,
        hierarchy_counts.values,
        color=[HIER_COLORS_HEX.get(h, "#999") for h in hierarchy_counts.index],
        edgecolor="white",
    )
    ax.set_ylabel("Cantidad de Atractivos")
    ax.set_title("Atractivos por Nivel de Jerarquía")
    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 20,
            str(int(bar.get_height())),
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    plt.tight_layout()
    fig.savefig(ASSETS_IMG_DIR / "jerarquias.png")
    plt.close(fig)

    # Gráfico 5: Superposición clústeres rezagados
    if df_lagging_clustered is not None:
        print("Generando gráfico donut de superposición...")
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

        for cluster_id in lagging_hulls:
            try:
                lagging_poly = Polygon(lagging_hulls[cluster_id])
                if not lagging_poly.is_valid:
                    continue
                best_type = "Genuinamente rezagado"
                best_score = 0
                for main_poly in main_hulls_polys.values():
                    otype = gap_analysis.compute_lagging_overlap_type(lagging_poly, main_poly)
                    score = overlap_rank.get(otype, 0)
                    if score > best_score:
                        best_score = score
                        best_type = otype
                if best_type == "Separado":
                    best_type = "Genuinamente rezagado"
                if best_type in overlap_counts:
                    overlap_counts[best_type] += 1
            except Exception:
                continue

        if sum(overlap_counts.values()) > 0:
            overlap_counts = {k: v for k, v in overlap_counts.items() if v > 0}
            fig, ax = plt.subplots(figsize=(9, 7))
            ax.pie(
                overlap_counts.values(),
                labels=overlap_counts.keys(),
                autopct="%1.1f%%",
                colors=[OVERLAP_COLORS_HEX.get(k, "#999") for k in overlap_counts.keys()],
                startangle=90,
            )
            ax.add_artist(plt.Circle((0, 0), 0.70, fc="white"))
            ax.set_title("Clasificación de Clústeres Rezagados por Tipo de Superposición")
            plt.tight_layout()
            fig.savefig(ASSETS_IMG_DIR / "donut_superposicion.png")
            plt.close(fig)

    # 5. Mapa Folium
    print("Generando mapa interactivo Folium...")
    m = folium.Map(location=[CHILE_LAT, CHILE_LON], zoom_start=5, tiles="CartoDB positron")

    hierarchy_groups = []
    for hier in ["INTERNACIONAL", "NACIONAL", "REGIONAL", "LOCAL"]:
        fg = folium.FeatureGroup(name=hier.capitalize(), show=(hier in ["INTERNACIONAL", "NACIONAL"]))
        subset = df_clustered[df_clustered["JERARQUIA"] == hier]
        for _, row in subset.iterrows():
            folium.CircleMarker(
                location=[row["POINT_Y"], row["POINT_X"]],
                radius={"INTERNACIONAL": 7, "NACIONAL": 5, "REGIONAL": 3, "LOCAL": 2}.get(hier, 2),
                popup=folium.Popup(
                    f"<b>{row['NOMBRE']}</b><br><span style='color: {HIER_COLORS_HEX[hier]}'>● {hier}</span>",
                    max_width=300,
                ),
                color=HIER_COLORS_HEX[hier],
                fill=True,
                fillColor=HIER_COLORS_HEX[hier],
                fillOpacity=0.7,
            ).add_to(fg)
        fg.add_to(m)
        hierarchy_groups.append(fg)

    fg_hulls = folium.FeatureGroup(name="Límites de Clústeres", show=False)
    for cluster_id, hull_coords in hulls.items():
        anchor = summary_classified.loc[cluster_id, "anchor_status"]
        folium.Polygon(
            locations=[[lat, lon] for lat, lon in hull_coords],
            color=HULL_COLORS_HEX.get(anchor, "#999"),
            fill=True,
            fillOpacity=0.15,
            weight=2,
            popup=f"{cluster_labels.get(cluster_id)} — {anchor}",
        ).add_to(fg_hulls)
    fg_hulls.add_to(m)

    GroupedLayerControl(
        groups={"Destinos & Clústeres": [fg_hulls], "Atractivos por Jerarquía": hierarchy_groups},
        collapsed=False,
    ).add_to(m)

    m.save(ASSETS_DIR / "mapa_interactivo.html")
    print(f"  Mapa guardado: {ASSETS_DIR / 'mapa_interactivo.html'}")


if __name__ == "__main__":
    generate()
