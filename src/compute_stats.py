import pandas as pd
import numpy as np

CITIES = ["Lyon", "Paris", "Bordeaux", "Pays Basque"]


def compute_global_stats(df):
    """KPIs globaux toutes villes confondues."""
    return {
        "avg_price":         round(float(df["price"].mean()), 2),
        "med_price":         round(float(df["price"].median()), 2),
        "avg_avail":         round(float(df["availability_365"].mean()), 2),
        "total_listings":    int(len(df)),
        "nb_hosts":          int(df["host_id"].nunique()),
        "ratio":             round(len(df) / df["host_id"].nunique(), 2),
        "med_minnights":     int(df["minimum_nights"].median()),
        "avg_reviews_month": round(float(df["reviews_per_month"].dropna().mean()), 2),
    }


def compute_prix_par_ville(df):
    """Prix moyen par ville."""
    grp = df.groupby("city")["price"].mean().round(2)
    return {
        "labels": list(grp.index),
        "values": list(grp.values.astype(float)),
    }


def compute_dispo_par_ville(df):
    """Disponibilité moyenne par ville."""
    grp = df.groupby("city")["availability_365"].mean().round(1)
    return {
        "labels": list(grp.index),
        "values": list(grp.values.astype(float)),
    }


def compute_room_type(df):
    """Répartition des types de logements."""
    grp = df["room_type"].value_counts()
    return {
        "labels": list(grp.index),
        "values": list(grp.values.astype(int)),
    }


def compute_listings_par_ville(df):
    """Nombre de listings par ville."""
    grp = df["city"].value_counts()
    return {
        "labels": list(grp.index),
        "values": list(grp.values.astype(int)),
    }


def compute_top_hosts(df, n=10):
    """Top N hôtes par nombre de listings."""
    grp = (
        df.groupby(["host_id", "host_name"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(n)
    )
    labels = [f"{row['host_name']} (#{row['host_id']})" for _, row in grp.iterrows()]
    return {
        "labels": labels,
        "values": list(grp["count"].astype(int)),
    }


def compute_min_nights(df):
    """Distribution des minimum_nights (regroupé par catégories)."""
    bins   = [0, 1, 2, 3, 7, 14, 30, 90, 365, np.inf]
    labels = ["1 n", "2 n", "3 n", "4-7 n", "8-14 n", "15-30 n", "31-90 n", "91-365 n", "365+ n"]
    grp = pd.cut(df["minimum_nights"], bins=bins, labels=labels).value_counts().sort_index()
    return {
        "labels": list(grp.index.astype(str)),
        "values": list(grp.values.astype(int)),
    }


def compute_reviews_par_ville(df):
    """Reviews par mois moyennes par ville."""
    grp = df.groupby("city")["reviews_per_month"].mean().round(2)
    return {
        "labels": list(grp.index),
        "values": list(grp.values.astype(float)),
    }


def compute_spider_raw_metrics(df):
    """
    Métriques brutes du spider chart par ville.
    On utilise :
    - prix moyen
    - disponibilité moyenne
    - nb de reviews sur les 12 derniers mois
    - minimum nights médian
    - nb total d'annonces
    """
    rows = []

    for city in CITIES:
        sub = df[df["city"] == city]
        if sub.empty:
            continue

        rows.append({
            "city": city,
            "Prix moyen": round(float(sub["price"].mean()), 2),
            "Disponibilité": round(float(sub["availability_365"].mean()), 2),
            "Reviews 12m": round(float(sub["number_of_reviews_ltm"].fillna(0).mean()), 2),
            "Nb nuits min": int(sub["minimum_nights"].median()),
            "Nb annonces": int(len(sub)),
        })

    return rows


def normalize_spider_metrics(spider_rows):
    """
    Normalise chaque métrique sur une échelle 0-100 pour affichage radar.
    Conserve aussi les valeurs brutes pour les tooltips.
    """
    metric_labels = ["Prix moyen", "Disponibilité", "Reviews 12m", "Nb nuits min", "Nb annonces"]

    normalized_rows = []
    for row in spider_rows:
        normalized_rows.append({
            "city": row["city"],
            "raw": {k: row[k] for k in metric_labels},
            "normalized": {}
        })

    for metric in metric_labels:
        values = [row[metric] for row in spider_rows]
        vmin = min(values)
        vmax = max(values)

        if vmax == vmin:
            norm_values = [100.0] * len(values)
        else:
            norm_values = [round((v - vmin) / (vmax - vmin) * 100, 1) for v in values]

        for i, norm_v in enumerate(norm_values):
            normalized_rows[i]["normalized"][metric] = norm_v

    return {
        "labels": metric_labels,
        "cities": normalized_rows
    }

def compute_city_detail(df, city):
    """Stats détaillées pour une seule ville (utilisé par le filtre JS)."""
    sub = df[df["city"] == city]
    if sub.empty:
        return {}
    spider_raw = {
        "Prix moyen": round(float(sub["price"].mean()), 2),
        "Disponibilité": round(float(sub["availability_365"].mean()), 2),
        "Reviews 12m": round(float(sub["number_of_reviews_ltm"].fillna(0).mean()), 2),
        "Nb nuits min": int(sub["minimum_nights"].median()),
        "Nb annonces": int(len(sub)),
    }
    return {
        "avg_price":         round(float(sub["price"].mean()), 2),
        "med_price":         round(float(sub["price"].median()), 2),
        "avg_avail":         round(float(sub["availability_365"].mean()), 2),
        "count":             int(len(sub)),
        "nb_hosts":          int(sub["host_id"].nunique()),
        "ratio":             round(len(sub) / sub["host_id"].nunique(), 2),
        "med_minnights":     int(sub["minimum_nights"].median()),
        "avg_reviews_month": round(float(sub["reviews_per_month"].dropna().mean()), 2),
        "room_type":         compute_room_type(sub),
        "top_hosts":         compute_top_hosts(sub),
        "min_nights":        compute_min_nights(sub),
        "spider_raw":        spider_raw,
    }


def compute_top_hosts_reviews_timeline(df):
    """
    Top 3 des hôtes toutes villes confondues par période (année/mois),
    selon le nombre de reviews.
    
    Hypothèse: on utilise number_of_reviews_ltm comme proxy d'activité
    sur la période associée à last_review.
    """
    required_cols = ["host_id", "host_name", "city", "number_of_reviews_ltm", "review_year", "review_month", "review_period"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        return {"periods": [], "items": []}

    sub = df.dropna(subset=["review_year", "review_month", "review_period"]).copy()

    if sub.empty:
        return {"periods": [], "items": []}

    grouped = (
        sub.groupby(
            ["review_period", "review_year", "review_month", "host_id", "host_name"],
            as_index=False
        )
        .agg(
            reviews=("number_of_reviews_ltm", "sum"),
            city=("city", lambda s: s.mode().iat[0] if not s.mode().empty else s.iloc[0])
        )
    )
    items = []
    periods = []

    for (period, year, month), g in grouped.groupby(["review_period", "review_year", "review_month"]):
        top3 = (
            g.sort_values(["reviews", "host_name"], ascending=[False, True])
             .head(3)
        )

        top3_records = []
        for _, row in top3.iterrows():
            top3_records.append({
                "host_id": int(row["host_id"]),
                "host_name": row["host_name"],
                "reviews": float(row["reviews"]),
                "city": row["city"],
                "avatar": None
            })

        periods.append({
            "period": period,
            "year": int(year),
            "month": int(month)
        })

        items.append({
            "period": period,
            "year": int(year),
            "month": int(month),
            "top3": top3_records
        })

    periods = sorted(periods, key=lambda x: (x["year"], x["month"]))
    items = sorted(items, key=lambda x: (x["year"], x["month"]))
    return {
        "periods": periods,
        "items": items
    }

def compute_all_stats(df):
    """Point d'entrée : renvoie un dict complet prêt pour generate_charts.py."""
    spider_rows = compute_spider_raw_metrics(df)
    spider_chart = normalize_spider_metrics(spider_rows)
    return {
        "stats":              compute_global_stats(df),
        "prix_par_ville":     compute_prix_par_ville(df),
        "dispo_par_ville":    compute_dispo_par_ville(df),
        "room_type":          compute_room_type(df),
        "listings_par_ville": compute_listings_par_ville(df),
        "top_hosts":          compute_top_hosts(df),
        "min_nights":         compute_min_nights(df),
        "reviews_par_ville":  compute_reviews_par_ville(df),
        "spider_chart":       spider_chart,
        "top_hosts_reviews_timeline": compute_top_hosts_reviews_timeline(df),
        "cities": {
            city: compute_city_detail(df, city)
            for city in CITIES
            if city in df["city"].unique()
        },
    }