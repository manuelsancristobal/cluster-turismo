"""Fixtures compartidas de pytest."""

from __future__ import annotations

import os

import pandas as pd
import pytest


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Carga el CSV de atractivos de ejemplo desde tests/fixtures/."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    return pd.read_csv(os.path.join(fixtures_dir, "sample_attractions.csv"))
