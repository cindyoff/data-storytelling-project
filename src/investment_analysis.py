import pandas as pd


def preparer_donnees_investissement(df):
    df = df.copy()

    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")

    if "availability_365" in df.columns:
        df["availability_365"] = pd.to_numeric(df["availability_365"], errors="coerce")

    if "number_of_reviews" in df.columns:
        df["number_of_reviews"] = pd.to_numeric(
            df["number_of_reviews"], errors="coerce"
        ).fillna(0)

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

    df = df[df["price"].notna()]
    df = df[df["price"] > 0]

    if "availability_365" in df.columns:
        df = df[df["availability_365"].notna()]
        df = df[(df["availability_365"] >= 0) & (df["availability_365"] <= 365)]
    else:
        df["availability_365"] = 0

    return df


def normaliser_serie(s):
    s = s.astype(float)

    if len(s) == 0:
        return s

    min_val = s.min()
    max_val = s.max()

    if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
        return pd.Series([50.0] * len(s), index=s.index)

    return ((s - min_val) / (max_val - min_val)) * 100


def analyser_prix_median_par_quartier(df):
    quartier_stats = (
        df.groupby(["city", "neighbourhood"])["price"]
        .median()
        .reset_index(name="median_price")
        .sort_values(["city", "median_price"], ascending=[True, False])
    )
    return quartier_stats


def analyser_room_type_investissement(df):
    room_stats = (
        df.groupby(["city", "room_type"])
        .agg(
            median_price=("price", "median"),
            avg_reviews=("number_of_reviews", "mean"),
            avg_availability=("availability_365", "mean"),
            listings_count=("price", "count"),
        )
        .reset_index()
    )

    room_stats["estimated_booked_days"] = 365 - room_stats["avg_availability"]
    room_stats["estimated_revenue"] = (
        room_stats["median_price"] * room_stats["estimated_booked_days"]
    ).round(2)

    return room_stats.sort_values(["city", "estimated_revenue"], ascending=[True, False])


def analyser_prix_normalise_par_ville(df):
    city_price_stats = (
        df.groupby("city")
        .agg(
            median_price=("price", "median"),
            avg_price=("price", "mean"),
            listings_count=("price", "count"),
        )
        .sort_values("median_price", ascending=False)
    )

    city_price_stats["price_normalized"] = (
        normaliser_serie(city_price_stats["median_price"]).round(2)
    )

    return city_price_stats


def analyser_revenu_estime_par_ville(df):
    city_revenue_stats = (
        df.groupby("city")
        .agg(
            median_price=("price", "median"),
            avg_availability=("availability_365", "mean"),
            avg_reviews=("number_of_reviews", "mean"),
            listings_count=("price", "count"),
        )
        .copy()
    )

    city_revenue_stats["estimated_booked_days"] = 365 - city_revenue_stats["avg_availability"]
    city_revenue_stats["estimated_revenue"] = (
        city_revenue_stats["median_price"] * city_revenue_stats["estimated_booked_days"]
    ).round(2)

    city_revenue_stats = city_revenue_stats.sort_values("estimated_revenue", ascending=False)
    return city_revenue_stats


def top_quartiers_par_ville(quartier_stats, top_n=5):
    result = {}

    for city in quartier_stats["city"].dropna().unique():
        city_df = quartier_stats[quartier_stats["city"] == city].head(top_n)
        result[city] = {
            "labels": city_df["neighbourhood"].tolist(),
            "values": city_df["median_price"].round(2).tolist(),
        }

    return result


def room_type_payload_par_ville(room_stats):
    result = {}

    for city in room_stats["city"].dropna().unique():
        city_df = room_stats[room_stats["city"] == city]
        result[city] = {
            "labels": city_df["room_type"].tolist(),
            "median_price": city_df["median_price"].round(2).tolist(),
            "estimated_revenue": city_df["estimated_revenue"].round(2).tolist(),
            "avg_reviews": city_df["avg_reviews"].round(2).tolist(),
        }

    return result


def compute_investment_dashboard_data(df):
    df = preparer_donnees_investissement(df)

    quartier_stats = analyser_prix_median_par_quartier(df)
    room_stats = analyser_room_type_investissement(df)
    city_price_stats = analyser_prix_normalise_par_ville(df)
    city_revenue_stats = analyser_revenu_estime_par_ville(df)

    revenue_ranking_labels = city_revenue_stats.index.tolist()
    revenue_ranking_values = city_revenue_stats["estimated_revenue"].round(2).tolist()

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
            estimated_revenue=("estimated_revenue", "mean"),
            avg_reviews=("avg_reviews", "mean"),
        )
        .reset_index()
    )

    investment_data = {
        "median_price_by_neighbourhood": {
            "labels": global_quartiers.index.tolist(),
            "values": global_quartiers.round(2).tolist(),
        },
        "price_normalized_by_city": {
            "labels": city_price_stats.index.tolist(),
            "values": city_price_stats["price_normalized"].round(2).tolist(),
        },
        "estimated_revenue_by_city": {
            "labels": city_revenue_stats.index.tolist(),
            "values": city_revenue_stats["estimated_revenue"].round(2).tolist(),
        },
        "investment_ranking": {
            "labels": revenue_ranking_labels,
            "values": revenue_ranking_values,
        },
        "room_type_investment": {
            "labels": room_type_global["room_type"].tolist(),
            "median_price": room_type_global["median_price"].round(2).tolist(),
            "estimated_revenue": room_type_global["estimated_revenue"].round(2).tolist(),
            "avg_reviews": room_type_global["avg_reviews"].round(2).tolist(),
        },
        "cities": {},
    }

    quartiers_top = top_quartiers_par_ville(quartier_stats, top_n=5)
    room_types_city = room_type_payload_par_ville(room_stats)

    for city in df["city"].dropna().unique():
        city_df = df[df["city"] == city]

        city_price_row = city_price_stats.loc[city] if city in city_price_stats.index else None
        city_revenue_row = city_revenue_stats.loc[city] if city in city_revenue_stats.index else None

        investment_data["cities"][city] = {
            "investment": {
                "median_price": round(city_df["price"].median(), 2),
                "avg_reviews": round(city_df["number_of_reviews"].mean(), 2),
                "avg_availability": round(city_df["availability_365"].mean(), 2),
                "price_normalized": round(float(city_price_row["price_normalized"]), 2) if city_price_row is not None else 0,
                "estimated_revenue": round(float(city_revenue_row["estimated_revenue"]), 2) if city_revenue_row is not None else 0,
                "rank": revenue_ranking_labels.index(city) + 1 if city in revenue_ranking_labels else None,
            },
            "median_price_by_neighbourhood": quartiers_top.get(
                city, {"labels": [], "values": []}
            ),
            "room_type_investment": room_types_city.get(
                city,
                {"labels": [], "median_price": [], "estimated_revenue": [], "avg_reviews": []},
            ),
        }

    return investment_data