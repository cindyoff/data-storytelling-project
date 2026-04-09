"""
Tests unitaires pour src/compute_stats.py.

Chaque fonction est testée isolément à partir du DataFrame minimal
fourni par la fixture `minimal_df` (conftest.py).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
import numpy as np
from src.compute_stats import (
    compute_global_stats,
    compute_prix_par_ville,
    compute_dispo_par_ville,
    compute_room_type,
    compute_listings_par_ville,
    compute_top_hosts,
    compute_min_nights,
    compute_reviews_par_ville,
    compute_spider_raw_metrics,
    normalize_spider_metrics,
    compute_city_detail,
    compute_all_stats,
)


# ---------------------------------------------------------------------------
# compute_global_stats
# ---------------------------------------------------------------------------

class TestComputeGlobalStats:
    def test_returns_required_keys(self, minimal_df):
        result = compute_global_stats(minimal_df)
        for key in ["avg_price", "med_price", "avg_avail", "total_listings",
                    "nb_hosts", "ratio", "med_minnights", "avg_reviews_month"]:
            assert key in result, f"Clé manquante : {key}"

    def test_total_listings(self, minimal_df):
        assert compute_global_stats(minimal_df)["total_listings"] == len(minimal_df)

    def test_nb_hosts(self, minimal_df):
        result = compute_global_stats(minimal_df)
        assert result["nb_hosts"] == minimal_df["host_id"].nunique()

    def test_avg_price_type(self, minimal_df):
        result = compute_global_stats(minimal_df)
        assert isinstance(result["avg_price"], float)

    def test_ratio_positive(self, minimal_df):
        result = compute_global_stats(minimal_df)
        assert result["ratio"] > 0


# ---------------------------------------------------------------------------
# compute_prix_par_ville
# ---------------------------------------------------------------------------

class TestComputePrixParVille:
    def test_labels_and_values_same_length(self, minimal_df):
        result = compute_prix_par_ville(minimal_df)
        assert len(result["labels"]) == len(result["values"])

    def test_all_cities_present(self, minimal_df):
        result = compute_prix_par_ville(minimal_df)
        for city in minimal_df["city"].unique():
            assert city in result["labels"]

    def test_values_are_floats(self, minimal_df):
        result = compute_prix_par_ville(minimal_df)
        assert all(isinstance(v, float) for v in result["values"])


# ---------------------------------------------------------------------------
# compute_dispo_par_ville
# ---------------------------------------------------------------------------

class TestComputeDispoParVille:
    def test_structure(self, minimal_df):
        result = compute_dispo_par_ville(minimal_df)
        assert "labels" in result and "values" in result

    def test_values_between_0_and_365(self, minimal_df):
        result = compute_dispo_par_ville(minimal_df)
        assert all(0 <= v <= 365 for v in result["values"])


# ---------------------------------------------------------------------------
# compute_room_type
# ---------------------------------------------------------------------------

class TestComputeRoomType:
    def test_structure(self, minimal_df):
        result = compute_room_type(minimal_df)
        assert "labels" in result and "values" in result

    def test_counts_sum_to_total(self, minimal_df):
        result = compute_room_type(minimal_df)
        assert sum(result["values"]) == len(minimal_df)

    def test_values_are_ints(self, minimal_df):
        result = compute_room_type(minimal_df)
        assert all(isinstance(v, (int, np.integer)) for v in result["values"])


# ---------------------------------------------------------------------------
# compute_listings_par_ville
# ---------------------------------------------------------------------------

class TestComputeListingsParVille:
    def test_sum_equals_total(self, minimal_df):
        result = compute_listings_par_ville(minimal_df)
        assert sum(result["values"]) == len(minimal_df)

    def test_all_cities_present(self, minimal_df):
        result = compute_listings_par_ville(minimal_df)
        for city in minimal_df["city"].unique():
            assert city in result["labels"]


# ---------------------------------------------------------------------------
# compute_top_hosts
# ---------------------------------------------------------------------------

class TestComputeTopHosts:
    def test_returns_at_most_n(self, minimal_df):
        result = compute_top_hosts(minimal_df, n=2)
        assert len(result["labels"]) <= 2

    def test_sorted_descending(self, minimal_df):
        result = compute_top_hosts(minimal_df, n=10)
        values = result["values"]
        assert values == sorted(values, reverse=True)

    def test_label_contains_host_name(self, minimal_df):
        result = compute_top_hosts(minimal_df, n=10)
        for label in result["labels"]:
            # format : "Name (#id)"
            assert "#" in label


# ---------------------------------------------------------------------------
# compute_min_nights
# ---------------------------------------------------------------------------

class TestComputeMinNights:
    def test_labels_count(self, minimal_df):
        result = compute_min_nights(minimal_df)
        # 9 catégories définies dans la fonction
        assert len(result["labels"]) == 9

    def test_values_sum_to_total(self, minimal_df):
        result = compute_min_nights(minimal_df)
        assert sum(result["values"]) == len(minimal_df)


# ---------------------------------------------------------------------------
# compute_reviews_par_ville
# ---------------------------------------------------------------------------

class TestComputeReviewsParVille:
    def test_structure(self, minimal_df):
        result = compute_reviews_par_ville(minimal_df)
        assert "labels" in result and "values" in result

    def test_non_negative_values(self, minimal_df):
        result = compute_reviews_par_ville(minimal_df)
        assert all(v >= 0 for v in result["values"])


# ---------------------------------------------------------------------------
# compute_spider_raw_metrics
# ---------------------------------------------------------------------------

class TestComputeSpiderRawMetrics:
    def test_returns_list_of_dicts(self, minimal_df):
        result = compute_spider_raw_metrics(minimal_df)
        assert isinstance(result, list)
        for row in result:
            assert "city" in row

    def test_expected_keys_per_city(self, minimal_df):
        result = compute_spider_raw_metrics(minimal_df)
        expected = {"city", "Prix moyen", "Disponibilité", "Reviews 12m", "Min nights", "Nb annonces"}
        for row in result:
            assert set(row.keys()) == expected

    def test_only_known_cities(self, minimal_df):
        result = compute_spider_raw_metrics(minimal_df)
        cities_in_df = minimal_df["city"].unique()
        for row in result:
            assert row["city"] in cities_in_df


# ---------------------------------------------------------------------------
# normalize_spider_metrics
# ---------------------------------------------------------------------------

class TestNormalizeSpiderMetrics:
    def _make_spider_rows(self):
        return [
            {"city": "Lyon",     "Prix moyen": 80,  "Disponibilité": 100, "Reviews 12m": 3,  "Min nights": 2,  "Nb annonces": 2},
            {"city": "Paris",    "Prix moyen": 120, "Disponibilité": 50,  "Reviews 12m": 8,  "Min nights": 7,  "Nb annonces": 1},
            {"city": "Bordeaux", "Prix moyen": 30,  "Disponibilité": 300, "Reviews 12m": 0,  "Min nights": 30, "Nb annonces": 1},
        ]

    def test_structure(self):
        rows = self._make_spider_rows()
        result = normalize_spider_metrics(rows)
        assert "labels" in result and "cities" in result

    def test_normalized_values_between_0_and_100(self):
        rows = self._make_spider_rows()
        result = normalize_spider_metrics(rows)
        for city_obj in result["cities"]:
            for v in city_obj["normalized"].values():
                assert 0.0 <= v <= 100.0, f"Valeur hors [0,100] : {v}"

    def test_all_cities_present(self):
        rows = self._make_spider_rows()
        result = normalize_spider_metrics(rows)
        cities = [obj["city"] for obj in result["cities"]]
        assert "Lyon" in cities and "Paris" in cities

    def test_equal_values_normalized_to_100(self):
        """Si toutes les villes ont la même valeur, la normalisation doit renvoyer 100."""
        rows = [
            {"city": "A", "Prix moyen": 50, "Disponibilité": 50, "Reviews 12m": 50, "Min nights": 50, "Nb annonces": 50},
            {"city": "B", "Prix moyen": 50, "Disponibilité": 50, "Reviews 12m": 50, "Min nights": 50, "Nb annonces": 50},
        ]
        result = normalize_spider_metrics(rows)
        for city_obj in result["cities"]:
            for v in city_obj["normalized"].values():
                assert v == 100.0

    def test_raw_values_preserved(self):
        rows = self._make_spider_rows()
        result = normalize_spider_metrics(rows)
        for city_obj in result["cities"]:
            assert "raw" in city_obj


# ---------------------------------------------------------------------------
# compute_city_detail
# ---------------------------------------------------------------------------

class TestComputeCityDetail:
    def test_returns_empty_for_unknown_city(self, minimal_df):
        result = compute_city_detail(minimal_df, "Tokyo")
        assert result == {}

    def test_returns_expected_keys(self, minimal_df):
        result = compute_city_detail(minimal_df, "Lyon")
        for key in ["avg_price", "med_price", "avg_avail", "count",
                    "nb_hosts", "ratio", "med_minnights", "avg_reviews_month",
                    "room_type", "top_hosts", "min_nights", "spider_raw"]:
            assert key in result, f"Clé manquante : {key}"

    def test_count_matches_city_rows(self, minimal_df):
        result = compute_city_detail(minimal_df, "Lyon")
        expected = int((minimal_df["city"] == "Lyon").sum())
        assert result["count"] == expected


# ---------------------------------------------------------------------------
# compute_all_stats (test d'intégration léger)
# ---------------------------------------------------------------------------

class TestComputeAllStats:
    def test_top_level_keys(self, minimal_df):
        result = compute_all_stats(minimal_df)
        for key in ["stats", "prix_par_ville", "dispo_par_ville", "room_type",
                    "listings_par_ville", "top_hosts", "min_nights",
                    "reviews_par_ville", "spider_chart", "cities"]:
            assert key in result, f"Clé manquante : {key}"

    def test_cities_dict_contains_known_cities(self, minimal_df):
        result = compute_all_stats(minimal_df)
        for city in minimal_df["city"].unique():
            assert city in result["cities"]


