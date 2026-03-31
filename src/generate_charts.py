import json
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    """Convertit les types numpy en types Python natifs pour json.dumps."""
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

CITY_COLORS = {
    "Lyon": "#00e5b0",
    "Paris": "#ff5f6d",
    "Bordeaux": "#ffc857",
    "Pays Basque": "#7b8cde",
}


def build_spider_chart_payload(spider_chart: dict) -> dict:
    """
    Transforme les métriques normalisées en datasets Chart.js pour radar chart.
    """
    datasets = []

    for city_obj in spider_chart["cities"]:
        city = city_obj["city"]
        color = CITY_COLORS.get(city, "#9aa4b2")

        datasets.append({
            "label": city,
            "data": [city_obj["normalized"][label] for label in spider_chart["labels"]],
            "rawValues": city_obj["raw"],
            "borderColor": color,
            "backgroundColor": color + "22",
            "pointBackgroundColor": color,
            "pointBorderColor": color,
            "pointRadius": 3,
            "borderWidth": 2,
            "fill": True,
            "tension": 0.25,
        })

    return {
        "labels": spider_chart["labels"],
        "datasets": datasets,
    }


def generate_chart_configs(stats: dict) -> str:
    payload = {
        "stats":              stats["stats"],
        "prix_par_ville":     stats["prix_par_ville"],
        "room_type":          stats["room_type"],
        "dispo_par_ville":    stats["dispo_par_ville"],
        "listings_par_ville": stats["listings_par_ville"],
        "top_hosts":          stats["top_hosts"],
        "min_nights":         stats["min_nights"],
        "reviews_par_ville":  stats["reviews_par_ville"],
        "spider_attractivite": build_spider_chart_payload(stats["spider_chart"]),
        "cities":             stats["cities"],
    }

    return json.dumps(payload, ensure_ascii=False, indent=2, cls=NumpyEncoder)