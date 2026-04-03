"""
Tests unitaires pour src/load_data.py.

On teste chaque fonction de nettoyage sur des DataFrames construits
manuellement, sans accès aux fichiers CSV réels.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import pytest
from src.load_data import (
    centre_peripherie,
    clean_lyon,
    clean_paysbasque,
    clean_bordeaux,
    clean_paris,
    clean_prix_paris,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_lyon_raw():
    """DataFrame brut au format listings-lyon.csv."""
    return pd.DataFrame({
        "id":                  [1, 2, 3],
        "name":                ['""Bel appart""', "Studio normal", "Chambre"],
        "host_id":             [10, 20, 30],
        "neighbourhood_group": ["Centre", "Sud", "Nord"],
        "neighbourhood":       ["n1", "n2", "n3"],
        "room_type":           ["Entire home/apt", "Private room", "Shared room"],
        "price":               [60.0, None, 80.0],  # NaN au milieu → interpolable
        "minimum_nights":      [2, 3, 1],
        "number_of_reviews":   [5, 10, 3],
        "reviews_per_month":   [0.5, 1.0, 0.3],
        "availability_365":    [100, 200, 150],
        "license":             [None, None, None],
    })


def _make_paysbasque_raw():
    return pd.DataFrame({
        "id":                  [1, 2],
        "name":                ['""Maison""', "Appart"],
        "host_id":             [10, 20],
        "neighbourhood":       ["Biarritz", "Bayonne"],
        "neighbourhood_group": ["Côte Basque", "Intérieur"],
        "room_type":           ["Entire home/apt", "Private room"],
        "price":               [100.0, None],
        "minimum_nights":      [1, 5],
        "number_of_reviews":   [2, 4],
        "reviews_per_month":   [0.3, 0.7],
        "availability_365":    [50, 150],
        "license":             [None, None],
    })


def _make_bordeaux_raw():
    # clean_bordeaux supprime "neighbourhood" et renomme "neighbourhood_group" en "neighbourhood".
    # Les valeurs significatives (ville, typos) doivent donc être dans neighbourhood_group.
    return pd.DataFrame({
        "id":                  [1, 2, 3],
        "name":                ["Loft", '""Studio""', "Chambre"],
        "host_id":             [10, 20, 30],
        "neighbourhood":       ["X", "Y", "Z"],           # sera supprimé
        "neighbourhood_group": ["Bordeaux", "Bgles", "Saint-Mdard-en-Jalles"],  # sera renommé
        "room_type":           ["Entire home/apt", "Private room", "Shared room"],
        "price":               [120.0, None, 60.0],
        "minimum_nights":      [2, 7, 1],
        "number_of_reviews":   [10, 3, 7],
        "reviews_per_month":   [1.0, 0.4, 0.9],
        "availability_365":    [200, 100, 300],
        "license":             [None, None, None],
    })


def _make_paris_raw():
    return pd.DataFrame({
        "id":                  [1, 2],
        "name":                ['""Cosy flat""', "Big apt"],
        "host_id":             [10, 20],
        "neighbourhood_group": ["Ile-de-France", "Ile-de-France"],
        "neighbourhood":       ["Marais", "Montmartre"],
        "room_type":           ["Entire home/apt", "Private room"],
        "price":               [150.0, 90.0],   # colonne qui sera supprimée
        "minimum_nights":      [3, 1],
        "number_of_reviews":   [20, 8],
        "reviews_per_month":   [2.0, 0.8],
        "availability_365":    [60, 180],
        "license":             [None, None],
    })


def _make_prix_paris_raw():
    return pd.DataFrame({
        "listing_id": [1, 2, 99],
        "price":      [155.0, 92.0, 200.0],
        "extra_col":  ["x", "y", "z"],
    })


# ---------------------------------------------------------------------------
# centre_peripherie
# ---------------------------------------------------------------------------

class TestCentrePeripherie:
    def test_centre_detected(self):
        df = pd.DataFrame({"neighbourhood": ["Lyon", "Vaise", "Croix-Rousse"]})
        mapping = centre_peripherie(df, "Lyon", "neighbourhood")
        assert mapping["Lyon"] == "Lyon-Centre"
        assert mapping["Vaise"] == "Lyon-Vaise"
        assert mapping["Croix-Rousse"] == "Lyon-Croix-Rousse"

    def test_no_centre(self):
        """Si la ville n'est pas dans les valeurs, retourne un dict vide."""
        df = pd.DataFrame({"neighbourhood": ["Vaise", "Croix-Rousse"]})
        mapping = centre_peripherie(df, "Lyon", "neighbourhood")
        assert mapping == {}

    def test_single_value_equal_to_city(self):
        df = pd.DataFrame({"neighbourhood": ["Bordeaux"]})
        mapping = centre_peripherie(df, "Bordeaux", "neighbourhood")
        assert mapping == {"Bordeaux": "Bordeaux-Centre"}


# ---------------------------------------------------------------------------
# clean_lyon
# ---------------------------------------------------------------------------

class TestCleanLyon:
    def test_drops_id_license_neighbourhood_group(self):
        df = clean_lyon(_make_lyon_raw())
        assert "id" not in df.columns
        assert "license" not in df.columns
        assert "neighbourhood_group" not in df.columns

    def test_price_interpolation(self):
        """La valeur None doit être interpolée (ici en première position → forward-fill)."""
        df = clean_lyon(_make_lyon_raw())
        assert df["price"].isna().sum() == 0

    def test_name_quotes_removed(self):
        df = clean_lyon(_make_lyon_raw())
        assert '""' not in df["name"].iloc[0]

    def test_existing_columns_preserved(self):
        df = clean_lyon(_make_lyon_raw())
        for col in ["name", "host_id", "neighbourhood", "room_type", "price"]:
            assert col in df.columns


# ---------------------------------------------------------------------------
# clean_paysbasque
# ---------------------------------------------------------------------------

class TestCleanPaysBasque:
    def test_drops_id_license_neighbourhood_group(self):
        """id, license et neighbourhood (original) sont supprimés ;
        neighbourhood_group est renommé en neighbourhood."""
        df = clean_paysbasque(_make_paysbasque_raw())
        assert "id" not in df.columns
        assert "license" not in df.columns
        assert "neighbourhood_group" not in df.columns

    def test_neighbourhood_group_renamed(self):
        df = clean_paysbasque(_make_paysbasque_raw())
        assert "neighbourhood" in df.columns       # renommée depuis neighbourhood_group

    def test_price_interpolation(self):
        df = clean_paysbasque(_make_paysbasque_raw())
        assert df["price"].isna().sum() == 0

    def test_name_quotes_removed(self):
        df = clean_paysbasque(_make_paysbasque_raw())
        assert '""' not in df["name"].iloc[0]


# ---------------------------------------------------------------------------
# clean_bordeaux
# ---------------------------------------------------------------------------

class TestCleanBordeaux:
    def test_drops_id_license_neighbourhood(self):
        df = clean_bordeaux(_make_bordeaux_raw())
        assert "id" not in df.columns
        assert "license" not in df.columns

    def test_neighbourhood_group_renamed(self):
        df = clean_bordeaux(_make_bordeaux_raw())
        assert "neighbourhood" in df.columns

    def test_price_interpolation(self):
        df = clean_bordeaux(_make_bordeaux_raw())
        assert df["price"].isna().sum() == 0

    def test_name_quotes_removed(self):
        df = clean_bordeaux(_make_bordeaux_raw())
        assert '""' not in df["name"].iloc[1]

    def test_neighbourhood_typos_corrected(self):
        df = clean_bordeaux(_make_bordeaux_raw())
        # "Bgles" → "Bordeaux-Begles", "Saint-Mdard-en-Jalles" → "Bordeaux-Saint-Medard-en-Jalles"
        values = df["neighbourhood"].tolist()
        assert any("Begles" in v for v in values), f"Begles attendu dans {values}"
        assert any("Saint-Medard" in v for v in values), f"Saint-Medard attendu dans {values}"

    def test_bordeaux_centre_prefix(self):
        df = clean_bordeaux(_make_bordeaux_raw())
        values = df["neighbourhood"].tolist()
        assert any("Bordeaux-Centre" in str(v) for v in values)


# ---------------------------------------------------------------------------
# clean_paris
# ---------------------------------------------------------------------------

class TestCleanParis:
    def test_drops_id_license_neighbourhood_group(self):
        df = clean_paris(_make_paris_raw())
        assert "id" not in df.columns
        assert "license" not in df.columns
        assert "neighbourhood_group" not in df.columns

    def test_name_quotes_removed(self):
        df = clean_paris(_make_paris_raw())
        assert '""' not in df["name"].iloc[0]

    def test_neighbourhood_preserved(self):
        df = clean_paris(_make_paris_raw())
        assert "neighbourhood" in df.columns


# ---------------------------------------------------------------------------
# clean_prix_paris
# ---------------------------------------------------------------------------

class TestCleanPrixParis:
    def test_keeps_only_id_and_price(self):
        df = clean_prix_paris(_make_prix_paris_raw())
        assert set(df.columns) == {"id", "price"}

    def test_listing_id_renamed_to_id(self):
        df = clean_prix_paris(_make_prix_paris_raw())
        assert "listing_id" not in df.columns
        assert "id" in df.columns

    def test_row_count_unchanged(self):
        raw = _make_prix_paris_raw()
        df = clean_prix_paris(raw)
        assert len(df) == len(raw)
