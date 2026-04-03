"""
Fixtures partagées entre tous les fichiers de tests.
"""
import pandas as pd
import pytest


@pytest.fixture
def minimal_df():
    """DataFrame minimal reproduisant la structure post-load_all()."""
    return pd.DataFrame({
        "name":                   ["Apt A", "Apt B", "Studio C", "Loft D", "Maison E"],
        "host_id":                [1, 1, 2, 3, 3],
        "host_name":              ["Alice", "Alice", "Bob", "Carol", "Carol"],
        "neighbourhood":          ["n1", "n2", "n1", "n3", "n3"],
        "room_type":              ["Entire home/apt", "Private room",
                                   "Entire home/apt", "Shared room", "Private room"],
        "price":                  [80.0,    50.0,    120.0,   30.0,    95.0],
        "minimum_nights":         [2, 1, 7, 30, 3],
        "number_of_reviews":      [10, 5, 20, 1, 8],
        "reviews_per_month":      [1.0, 0.5, 2.0, 0.1, 0.8],
        "number_of_reviews_ltm":  [3, 1, 8, 0, 2],
        "availability_365":       [100, 200, 50, 300, 150],
        "city":                   ["Lyon", "Lyon", "Paris", "Bordeaux", "Pays Basque"],
    })
