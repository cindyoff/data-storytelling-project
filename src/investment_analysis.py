import pandas as pd


def preparer_donnees_investissement(df):
    df = df.copy()

    # utiliser directement le prix normalisé si disponible
    if "price_norm" in df.columns:
        df["price_metric"] = pd.to_numeric(df["price_norm"], errors="coerce")
    elif "price" in df.columns:
        df["price_metric"] = pd.to_numeric(df["price"], errors="coerce")
    else:
        df["price_metric"] = pd.NA

    if "availability_365" in df.columns:
        df["availability_365"] = pd.to_numeric(df["availability_365"], errors="coerce")
    else:
        df["availability_365"] = 0

    if "number_of_reviews" in df.columns:
        df["number_of_reviews"] = pd.to_numeric(
            df["number_of_reviews"], errors="coerce"
        ).fillna(0)
    else:
        df["number_of_reviews"] = 0

    if "calculated_host_listings_count" in df.columns:
        df["calculated_host_listings_count"] = pd.to_numeric(
            df["calculated_host_listings_count"], errors="coerce"
        ).fillna(1)
    else:
        df["calculated_host_listings_count"] = 1

    if "city" in df.columns:
        df["city"] = df["city"].fillna("Inconnue")
    else:
        df["city"] = "Inconnue"

    if "neighbourhood" in df.columns:
        df["neighbourhood"] = df["neighbourhood"].fillna("Inconnu")
    else:
        df["neighbourhood"] = "Inconnu"

    if "room_type" in df.columns:
        df["room_type"] = df["room_type"].fillna("Inconnu")
    else:
        df["room_type"] = "Inconnu"

    df = df[df["price_metric"].notna()]
    df = df[df["price_metric"] >= 0]

    df = df[df["availability_365"].notna()]
    df = df[(df["availability_365"] >= 0) & (df["availability_365"] <= 365)]

    return df


def analyser_prix_median_par_quartier(df):
    quartier_stats = (
        df.groupby(["city", "neighbourhood"])["price_metric"]
        .median()
        .reset_index(name="median_price")
        .sort_values(["city", "median_price"], ascending=[True, False])
    )
    return quartier_stats


def analyser_room_type_investissement(df):
    room_stats = (
        df.groupby(["city", "room_type"])
        .agg(
            median_price=("price_metric", "median"),
            avg_reviews=("number_of_reviews", "mean"),
            avg_availability=("availability_365", "mean"),
            listings_count=("price_metric", "count"),
        )
        .reset_index()
    )

    room_stats["estimated_booked_days"] = 365 - room_stats["avg_availability"]
    room_stats["investment_score"] = (
        room_stats["median_price"] * room_stats["estimated_booked_days"]
    ).round(4)

    return room_stats.sort_values(
        ["city", "investment_score"], ascending=[True, False]
    )


def analyser_prix_normalise_par_ville(df):
    city_price_stats = (
        df.groupby("city")
        .agg(
            median_price=("price_metric", "median"),
            avg_price=("price_metric", "mean"),
            listings_count=("price_metric", "count"),
        )
        .sort_values("median_price", ascending=False)
    )

    # price_metric est déjà normalisé via load_all()
    city_price_stats["price_normalized"] = city_price_stats["median_price"].round(4)

    return city_price_stats


def analyser_score_investissement_par_ville(df):
    city_stats = (
        df.groupby("city")
        .agg(
            median_price=("price_metric", "median"),
            avg_availability=("availability_365", "mean"),
            avg_reviews=("number_of_reviews", "mean"),
            listings_count=("price_metric", "count"),
        )
        .copy()
    )

    city_stats["estimated_booked_days"] = 365 - city_stats["avg_availability"]
    city_stats["investment_score"] = (
        city_stats["median_price"] * city_stats["estimated_booked_days"]
    ).round(4)

    city_stats = city_stats.sort_values("investment_score", ascending=False)
    return city_stats


def top_quartiers_par_ville(quartier_stats, top_n=5):
    result = {}

    for city in quartier_stats["city"].dropna().unique():
        city_df = quartier_stats[quartier_stats["city"] == city].head(top_n)
        result[city] = {
            "labels": city_df["neighbourhood"].tolist(),
            "values": city_df["median_price"].round(4).tolist(),
        }

    return result


def room_type_payload_par_ville(room_stats):
    result = {}

    for city in room_stats["city"].dropna().unique():
        city_df = room_stats[room_stats["city"] == city]
        result[city] = {
            "labels": city_df["room_type"].tolist(),
            "median_price": city_df["median_price"].round(4).tolist(),
            "investment_score": city_df["investment_score"].round(4).tolist(),
            "avg_reviews": city_df["avg_reviews"].round(2).tolist(),
        }

    return result


def compute_investment_dashboard_data(df):
    df = preparer_donnees_investissement(df)

    quartier_stats = analyser_prix_median_par_quartier(df)
    room_stats = analyser_room_type_investissement(df)
    city_price_stats = analyser_prix_normalise_par_ville(df)
    city_investment_stats = analyser_score_investissement_par_ville(df)

    ranking_labels = city_investment_stats.index.tolist()
    ranking_values = city_investment_stats["investment_score"].round(4).tolist()

    global_quartiers = (
        quartier_stats.groupby("neighbourhood")["median_price"]
        .median()
        .sort_values(ascending=False)
        .head(10)
    )

    room_type_global = (
        room_stats.groupby("room_type")
        .agg(
            median_price=("median_price", "mean"),
            investment_score=("investment_score", "mean"),
            avg_reviews=("avg_reviews", "mean"),
        )
        .reset_index()
    )

    investment_data = {
        "median_price_by_neighbourhood": {
            "labels": global_quartiers.index.tolist(),
            "values": global_quartiers.round(4).tolist(),
        },
        "price_normalized_by_city": {
            "labels": city_price_stats.index.tolist(),
            "values": city_price_stats["price_normalized"].round(4).tolist(),
        },
        "investment_score_by_city": {
            "labels": city_investment_stats.index.tolist(),
            "values": city_investment_stats["investment_score"].round(4).tolist(),
        },
        "investment_ranking": {
            "labels": ranking_labels,
            "values": ranking_values,
        },
        "room_type_investment": {
            "labels": room_type_global["room_type"].tolist(),
            "median_price": room_type_global["median_price"].round(4).tolist(),
            "investment_score": room_type_global["investment_score"].round(4).tolist(),
            "avg_reviews": room_type_global["avg_reviews"].round(2).tolist(),
        },
        "cities": {},
    }

    quartiers_top = top_quartiers_par_ville(quartier_stats, top_n=5)
    room_types_city = room_type_payload_par_ville(room_stats)

    for city in df["city"].dropna().unique():
        city_df = df[df["city"] == city]

        city_price_row = (
            city_price_stats.loc[city] if city in city_price_stats.index else None
        )
        city_investment_row = (
            city_investment_stats.loc[city]
            if city in city_investment_stats.index
            else None
        )

        investment_data["cities"][city] = {
            "investment": {
                "median_price": round(city_df["price_metric"].median(), 4),
                "avg_reviews": round(city_df["number_of_reviews"].mean(), 2),
                "avg_availability": round(city_df["availability_365"].mean(), 2),
                "price_normalized": round(float(city_price_row["price_normalized"]), 4)
                if city_price_row is not None
                else 0,
                "investment_score": round(
                    float(city_investment_row["investment_score"]), 4
                )
                if city_investment_row is not None
                else 0,
                "rank": ranking_labels.index(city) + 1
                if city in ranking_labels
                else None,
            },
            "median_price_by_neighbourhood": quartiers_top.get(
                city, {"labels": [], "values": []}
            ),
            "room_type_investment": room_types_city.get(
                city,
                {
                    "labels": [],
                    "median_price": [],
                    "investment_score": [],
                    "avg_reviews": [],
                },
            ),
        }

    return investment_data