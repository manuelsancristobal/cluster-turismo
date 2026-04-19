"""Funciones de análisis de brechas e identificación de oportunidades."""


import pandas as pd
from shapely.geometry import Polygon


def _hier_col(df: pd.DataFrame) -> str:
    """Retorna el nombre de la columna de jerarquía presente en el dataframe."""
    if "JERARQUIA" in df.columns:
        return "JERARQUIA"
    return "JERARQUÍA"


def classify_anchor_status(
    df: pd.DataFrame, n_int_col: str = "n_internacional", n_nat_col: str = "n_nacional"
) -> pd.DataFrame:
    """Clasifica clústeres según el estado de atractivo ancla.

    Lógica de clasificación:
    - 'Con ancla internacional': Tiene 1+ atractivos de nivel internacional
    - 'Solo ancla nacional': Tiene atractivos nacionales pero no internacionales
    - 'Sin ancla': No tiene atractivos ancla (oportunidad de inversión)

    Parámetros
    ----------
    df : pd.DataFrame
        Dataframe resumen de clústeres con conteos por jerarquía
    n_int_col : str
        Nombre de columna para conteo de atractivos internacionales
    n_nat_col : str
        Nombre de columna para conteo de atractivos nacionales

    Retorna
    -------
    pd.DataFrame
        Dataframe de entrada con columna 'anchor_status' agregada
    """
    for col in [n_int_col, n_nat_col]:
        if col not in df.columns:
            raise KeyError(f"Columna '{col}' no encontrada en el dataframe. Columnas disponibles: {list(df.columns)}")

    def classify(row):
        if row[n_int_col] > 0:
            return "Con ancla internacional"
        elif row[n_nat_col] > 0:
            return "Solo ancla nacional"
        else:
            return "Sin ancla"

    df_classified = df.copy()
    df_classified["anchor_status"] = df_classified.apply(classify, axis=1)

    # Imprimir distribución
    print("\nDistribución de Estado de Ancla:")
    print(df_classified["anchor_status"].value_counts())

    return df_classified


def identify_investment_opportunities(df: pd.DataFrame, cluster_summary: pd.DataFrame) -> pd.DataFrame:
    """Identifica clústeres con oportunidades de inversión/desarrollo.

    Prioridad 1 (Máxima): Sin ancla - Sin atractivos ancla
    Prioridad 2 (Alta): Solo ancla nacional - Solo anclas de nivel nacional
    Prioridad 3 (Media): Con ancla internacional - Potencial de desarrollo completo

    Parámetros
    ----------
    df : pd.DataFrame
        Dataframe completo de atractivos con asignaciones de clúster
    cluster_summary : pd.DataFrame
        Resumen de clústeres con clasificaciones de ancla

    Retorna
    -------
    pd.DataFrame
        Dataframe de oportunidades ordenado por prioridad
    """
    opportunities = cluster_summary[cluster_summary["anchor_status"] != "Con ancla internacional"].copy()

    # Agregar contexto adicional desde el dataframe completo
    opportunities["communes"] = opportunities.index.map(
        lambda cluster_id: df[df["CLUSTER"] == cluster_id]["COMUNA"].unique()
    )

    opportunities["commune_names"] = opportunities["communes"].apply(
        lambda x: " - ".join(sorted(set(str(c) for c in x))) if len(x) > 0 else ""
    )

    # Calcular diversidad de categorías
    opportunities["category_diversity"] = opportunities.index.map(
        lambda cluster_id: df[df["CLUSTER"] == cluster_id]["CATEGORIA"].nunique()
    )

    # Asignar prioridad
    def get_priority(row):
        if row["anchor_status"] == "Sin ancla":
            return 1
        elif row["anchor_status"] == "Solo ancla nacional":
            return 2
        else:
            return 3

    opportunities["priority"] = opportunities.apply(get_priority, axis=1)

    return opportunities.sort_values("priority")


def compute_lagging_overlap_type(lagging_poly: Polygon, official_poly: Polygon) -> str:
    """Clasifica cómo un clúster de atractivos rezagados se superpone con destinos oficiales.

    Clasificación:
    - 'Contenido': >90% dentro del destino oficial
    - 'Parcialmente superpuesto': 10-90% de superposición
    - 'Genuinamente rezagado': <10% de superposición (clúster independiente)

    Parámetros
    ----------
    lagging_poly : Polygon
        Polígono del clúster de atractivos rezagados
    official_poly : Polygon
        Polígono del destino oficial

    Retorna
    -------
    str
        Clasificación del tipo de superposición
    """
    if not lagging_poly.intersects(official_poly):
        return "Separado"

    intersection = lagging_poly.intersection(official_poly)
    overlap_pct = intersection.area / lagging_poly.area if lagging_poly.area > 0 else 0

    if overlap_pct > 0.9:
        return "Contenido"
    elif overlap_pct > 0.1:
        return "Parcialmente superpuesto"
    else:
        return "Genuinamente rezagado"


def compute_cluster_overlap_analysis(
    df_attractions: pd.DataFrame,
    df_cluster_hulls: dict,
    df_destinations: pd.DataFrame,
    dest_polygons: dict,
) -> pd.DataFrame:
    """Analiza cómo los clústeres rezagados se superponen con destinos oficiales.

    Parámetros
    ----------
    df_attractions : pd.DataFrame
        Dataframe completo de atractivos con asignaciones de clúster
    df_cluster_hulls : dict
        Mapeo de ID de clúster a polígonos envolventes
    df_destinations : pd.DataFrame
        Dataframe de destinos
    dest_polygons : dict
        Mapeo de ID de destino a polígono Shapely

    Retorna
    -------
    pd.DataFrame
        Resultados del análisis con clasificaciones de superposición y recomendaciones
    """
    results = []

    # Identificar clústeres rezagados (aquellos con atractivos fuera de destinos oficiales)
    lagging_clusters = df_attractions[df_attractions["nombre"].isna()]["CLUSTER"].unique()

    for cluster_id in lagging_clusters:
        if cluster_id == -1:  # Omitir ruido
            continue

        cluster_data = df_attractions[df_attractions["CLUSTER"] == cluster_id]

        if cluster_id not in df_cluster_hulls:
            continue

        lagging_poly = Polygon(df_cluster_hulls[cluster_id])

        # Verificar superposición con cada destino oficial, conservando la mejor coincidencia
        best_overlap = None
        best_overlap_type = None
        best_overlap_area = -1.0

        overlap_rank = {"Contenido": 3, "Parcialmente superpuesto": 2, "Genuinamente rezagado": 1, "Separado": 0}

        for dest_name, dest_poly in dest_polygons.items():
            overlap_type = compute_lagging_overlap_type(lagging_poly, dest_poly)
            overlap_score = overlap_rank.get(overlap_type, 0)
            if overlap_score > best_overlap_area:
                best_overlap_area = overlap_score
                best_overlap = dest_name
                best_overlap_type = overlap_type

        results.append(
            {
                "cluster_id": cluster_id,
                "n_attractions": len(cluster_data),
                "main_region": cluster_data["REGION"].value_counts().index[0]
                if len(cluster_data) > 0 and len(cluster_data["REGION"].value_counts()) > 0
                else None,
                "overlap_type": best_overlap_type,
                "nearest_destination": best_overlap,
                "n_internacional": (cluster_data[_hier_col(cluster_data)] == "INTERNACIONAL").sum(),
                "n_nacional": (cluster_data[_hier_col(cluster_data)] == "NACIONAL").sum(),
            }
        )

    return pd.DataFrame(results)


def generate_opportunity_report(opportunities: pd.DataFrame, region_col: str = "region_principal") -> pd.DataFrame:
    """Genera resumen ejecutivo de oportunidades por región.

    Parámetros
    ----------
    opportunities : pd.DataFrame
        Dataframe de oportunidades desde identify_investment_opportunities()
    region_col : str
        Nombre de columna para región (por defecto: 'region_principal')

    Retorna
    -------
    pd.DataFrame
        Estadísticas resumen por región
    """
    report = opportunities.groupby(region_col).agg(
        n_opportunity_clusters=("anchor_status", "count"),
        total_attractions=("n_attractions", "sum"),
        avg_attractions_per_cluster=("n_attractions", "mean"),
        n_sin_ancla=("anchor_status", lambda x: (x == "Sin ancla").sum()),
        n_solo_nacional=("anchor_status", lambda x: (x == "Solo ancla nacional").sum()),
    )

    report = report.round(1).sort_values("n_opportunity_clusters", ascending=False)

    return report
