"""
Tests unitaires pour src/generate_charts.py.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import pytest
import numpy as np
from src.generate_charts import NumpyEncoder, build_spider_chart_payload, generate_chart_configs
from src.compute_stats import compute_all_stats

# numpy encoder
class TestNumpyEncoder:
    def test_encodes_numpy_int(self):
        data = {"val": np.int64(42)}
        result = json.loads(json.dumps(data, cls=NumpyEncoder))
        assert result["val"] == 42
        assert isinstance(result["val"], int)

    def test_encodes_numpy_float(self):
        data = {"val": np.float32(3.14)}
        result = json.loads(json.dumps(data, cls=NumpyEncoder))
        assert abs(result["val"] - 3.14) < 0.01
        assert isinstance(result["val"], float)

    def test_encodes_numpy_array(self):
        data = {"arr": np.array([1, 2, 3])}
        result = json.loads(json.dumps(data, cls=NumpyEncoder))
        assert result["arr"] == [1, 2, 3]
        assert isinstance(result["arr"], list)

    def test_raises_for_unserializable_object(self):
        class Foo:
            pass
        with pytest.raises(TypeError):
            json.dumps({"x": Foo()}, cls=NumpyEncoder)

# build_spider_chart_payload
def _make_spider_chart():
    """Spider chart minimal avec deux villes."""
    return {
        "labels": ["Prix moyen", "Disponibilité", "Reviews 12m", "Min nights", "Nb annonces"],
        "cities": [
            {
                "city": "Lyon",
                "raw":  {"Prix moyen": 80, "Disponibilité": 100, "Reviews 12m": 3, "Min nights": 2, "Nb annonces": 2},
                "normalized": {"Prix moyen": 50.0, "Disponibilité": 33.3, "Reviews 12m": 37.5, "Min nights": 0.0, "Nb annonces": 100.0},
            },
            {
                "city": "Paris",
                "raw":  {"Prix moyen": 120, "Disponibilité": 50, "Reviews 12m": 8, "Min nights": 7, "Nb annonces": 1},
                "normalized": {"Prix moyen": 100.0, "Disponibilité": 0.0, "Reviews 12m": 100.0, "Min nights": 100.0, "Nb annonces": 0.0},
            },
        ],
    }


class TestBuildSpiderChartPayload:
    def test_returns_labels_and_datasets(self):
        result = build_spider_chart_payload(_make_spider_chart())
        assert "labels" in result
        assert "datasets" in result

    def test_one_dataset_per_city(self):
        spider = _make_spider_chart()
        result = build_spider_chart_payload(spider)
        assert len(result["datasets"]) == len(spider["cities"])

    def test_dataset_label_matches_city(self):
        result = build_spider_chart_payload(_make_spider_chart())
        labels = [ds["label"] for ds in result["datasets"]]
        assert "Lyon" in labels
        assert "Paris" in labels

    def test_data_length_matches_labels(self):
        spider = _make_spider_chart()
        result = build_spider_chart_payload(spider)
        for ds in result["datasets"]:
            assert len(ds["data"]) == len(spider["labels"])

    def test_known_city_gets_correct_color(self):
        result = build_spider_chart_payload(_make_spider_chart())
        lyon_ds = next(ds for ds in result["datasets"] if ds["label"] == "Lyon")
        assert lyon_ds["borderColor"] == "#00e5b0"

    def test_unknown_city_gets_fallback_color(self):
        spider = {
            "labels": ["Prix moyen"],
            "cities": [{
                "city": "Atlantis",
                "raw": {"Prix moyen": 50},
                "normalized": {"Prix moyen": 50.0},
            }],
        }
        result = build_spider_chart_payload(spider)
        assert result["datasets"][0]["borderColor"] == "#9aa4b2"

    def test_background_color_is_transparent_variant(self):
        result = build_spider_chart_payload(_make_spider_chart())
        for ds in result["datasets"]:
            # backgroundColor = borderColor + "22"
            assert ds["backgroundColor"] == ds["borderColor"] + "22"

# generate chart configs
class TestGenerateChartConfigs:
    @pytest.fixture
    def stats(self, minimal_df):
        return compute_all_stats(minimal_df)

    def test_returns_valid_json(self, stats):
        result = generate_chart_configs(stats)
        parsed = json.loads(result)  # ne doit pas lever d'exception
        assert isinstance(parsed, dict)

    def test_top_level_keys_present(self, stats):
        parsed = json.loads(generate_chart_configs(stats))
        for key in ["stats", "prix_par_ville", "room_type", "dispo_par_ville",
                    "listings_par_ville", "top_hosts", "min_nights",
                    "reviews_par_ville", "spider_attractivite", "cities"]:
            assert key in parsed, f"Clé manquante dans le JSON : {key}"

    def test_spider_attractivite_structure(self, stats):
        parsed = json.loads(generate_chart_configs(stats))
        spider = parsed["spider_attractivite"]
        assert "labels" in spider
        assert "datasets" in spider
        assert isinstance(spider["datasets"], list)

    def test_numpy_types_not_present(self, stats):
        """Le JSON doit être désérialisable sans erreur (NumpyEncoder appliqué)."""
        raw = generate_chart_configs(stats)
        # json.loads lèverait une exception si des types numpy subsistaient
        json.loads(raw)
