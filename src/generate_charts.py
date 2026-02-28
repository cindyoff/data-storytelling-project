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
        "cities":             stats["cities"],
    }

    return json.dumps(payload, ensure_ascii=False, indent=2, cls=NumpyEncoder)