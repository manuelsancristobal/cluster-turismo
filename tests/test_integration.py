"""Tests de integración con datos reales."""

from __future__ import annotations

import pytest

from cluster_turismo import clustering, data_loader, gap_analysis, preprocessing
from cluster_turismo.config import EXCEL_PATH, HDBSCAN_MIN_CLUSTER_SIZE

pytestmark = pytest.mark.skipif(
    not EXCEL_PATH.exists(),
    reason=f"Requiere {EXCEL_PATH}",
)


@pytest.fixture(scope="module")
def df_processed():
    """Carga y procesa los datos reales para los tests."""
    df_raw = data_loader.load_attractions_excel(str(EXCEL_PATH))
    df = preprocessing.filter_permanent_attractions(df_raw)
    df = preprocessing.validate_coordinates(df)
    return df


class TestDataIntegrity:
    def test_has_expected_columns(self, df_processed):
        """Verificar presencia de columnas críticas."""
        expected = {"NOMBRE", "JERARQUIA", "CATEGORIA", "REGION", "POINT_Y", "POINT_X"}
        assert expected.issubset(set(df_processed.columns))

    def test_no_programmed_events(self, df_processed):
        """Verificar que el filtro de permanencia funcionó."""
        assert (df_processed["CATEGORIA"] == "ACONTECIMIENTOS PROGRAMADOS").sum() == 0


class TestClusteringIntegrity:
    def test_hdbscan_produces_clusters(self, df_processed):
        """Verificar que el clustering genere grupos razonables."""
        df_clustered = clustering.run_hdbscan_spatial(df_processed, min_cluster_size=HDBSCAN_MIN_CLUSTER_SIZE)
        n_clusters = len(set(df_clustered["CLUSTER"])) - (1 if -1 in df_clustered["CLUSTER"].values else 0)
        assert n_clusters >= 5

    def test_anchor_classification_covers_all(self, df_processed):
        """Verificar clasificación de anclas."""
        df_clustered = clustering.run_hdbscan_spatial(df_processed, min_cluster_size=HDBSCAN_MIN_CLUSTER_SIZE)
        summary = clustering.summarize_clusters(df_clustered, hierarchy_col="JERARQUIA")
        df_classified = gap_analysis.classify_anchor_status(summary)
        valid = {"Con ancla internacional", "Solo ancla nacional", "Sin ancla"}
        assert set(df_classified["anchor_status"].unique()).issubset(valid)
