"""
Unit tests for the data loader / Tests unitarios para el cargador de datos.
"""

import pytest
from pathlib import Path


def test_wines_loaded():
    from app.data.loader import WINES
    assert len(WINES) > 0


def test_wines_have_required_fields():
    from app.data.loader import WINES
    required = {"id", "winery", "wine_name", "year", "rating", "region",
                "price_euros", "vine_type", "grape_variety", "wine_ageing",
                "quality_price_ratio", "luxury_category", "cluster_id"}
    for wine in WINES[:10]:
        assert required.issubset(wine.keys())


def test_wine_ageing_normalised():
    """wine_ageing must be 'Joven' or 'Crianza', not raw 0/1 integers."""
    from app.data.loader import WINES
    valid = {"Joven", "Crianza"}
    assert all(w["wine_ageing"] in valid for w in WINES)


def test_luxury_category_is_bool():
    from app.data.loader import WINES
    assert all(isinstance(w["luxury_category"], bool) for w in WINES)


def test_ids_are_unique_and_sequential():
    from app.data.loader import WINES
    ids = [w["id"] for w in WINES]
    assert ids == list(range(1, len(WINES) + 1))


def test_flavor_descriptor_always_present():
    """flavor_descriptor must exist on every wine (empty string if missing in CSV)."""
    from app.data.loader import WINES
    assert all("flavor_descriptor" in w for w in WINES)


def test_missing_csv_raises_clear_error(tmp_path, monkeypatch):
    """FileNotFoundError must include instructions to re-run the notebooks."""
    import app.data.loader as loader_mod
    monkeypatch.setattr(loader_mod, "_CSV_PATH", tmp_path / "missing.csv")
    with pytest.raises(FileNotFoundError, match="notebooks"):
        loader_mod._load_wines()


def test_missing_columns_raises_value_error(tmp_path, monkeypatch):
    """ValueError must fire when the CSV lacks required columns."""
    import pandas as pd
    import app.data.loader as loader_mod

    bad_csv = tmp_path / "bad.csv"
    pd.DataFrame({"winery": ["A"], "wine_name": ["B"]}).to_csv(bad_csv, index=False)
    monkeypatch.setattr(loader_mod, "_CSV_PATH", bad_csv)
    with pytest.raises(ValueError, match="missing required columns"):
        loader_mod._load_wines()
