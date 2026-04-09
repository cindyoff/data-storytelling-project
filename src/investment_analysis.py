import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.load_data import load_all


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
STATIC_DIR = BASE_DIR / "static"


def charger_donnees(data_path=DATA_DIR):
    df = load_all(str(data_path))
    return df


def preparer_dates(df):
    if "last_review" in df.columns:
        df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
        df["year"] = df["last_review"].dt.year
    else:
        print("Pas de colonne last_review")

    if "host_since" in df.columns:
        df["host_since"] = pd.to_datetime(df["host_since"], errors="coerce")
        df["host_year"] = df["host_since"].dt.year
    else:
        print("Pas de colonne host_since")

    return df


def nettoyer_donnees(df):
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df[df["price"].notna()]
        df = df[df["price"] > 0]

    if "availability_365" in df.columns:
        df["availability_365"] = pd.to_numeric(df["availability_365"], errors="coerce").fillna(0)

    if "number_of_reviews" in df.columns:
        df["number_of_reviews"] = pd.to_numeric(df["number_of_reviews"], errors="coerce").fillna(0)

    if "city" in df.columns:
        df["city"] = df["city"].fillna("Inconnue")

    return df


def afficher_infos_colonnes(df):
    print("Colonnes du dataset :")
    print(df.columns.tolist())

    if "year" in df.columns:
        print("\nAnnées trouvées dans last_review :")
        print(df["year"].value_counts().sort_index())

    if "host_year" in df.columns:
        print("\nAnnées trouvées dans host_since :")
        print(df["host_year"].value_counts().sort_index())


def verifier_prix(df):
    if "price" not in df.columns:
        print("Pas de colonne price")
        return

    print("=== VERIFICATION DES PRIX ===")
    print("Nombre total de lignes :", len(df))
    print("Prix manquants :", df["price"].isna().sum())
    print("Prix non manquants :", df["price"].notna().sum())
    print("Prix = 0 :", (df["price"] == 0).sum())
    print("Prix < 0 :", (df["price"] < 0).sum())

    if "city" in df.columns:
        print("\nPrix manquants par ville :")
        print(df.groupby("city")["price"].apply(lambda x: x.isna().sum()))

        print("\nRésumé des prix par ville :")
        print(df.groupby("city")["price"].describe())


def calculer_indicateurs(df):
    df["estimated_booked_days"] = 365 - df["availability_365"]
    df["estimated_revenue"] = df["price"] * df["estimated_booked_days"]

    df["investment_score"] = (
        df["price"] * df["availability_365"]
    ) / (df["number_of_reviews"] + 1)

    return df


def analyser_revenu_demande(df):
    analysis = df.groupby("city")[["estimated_revenue", "number_of_reviews"]].mean()

    print("\n=== REVENU VS DEMANDE ===")
    print(analysis)

    return analysis


def analyser_evolution_prix(df):
    if "year" not in df.columns:
        return pd.Series(dtype=float)

    trend = df.dropna(subset=["year"]).groupby("year")["price"].mean()

    print("\n=== EVOLUTION PRIX ===")
    print(trend)

    return trend


def analyser_evolution_prix_par_ville(df):
    if "year" not in df.columns:
        return pd.DataFrame()

    trend_by_city = (
        df.dropna(subset=["year"])
          .groupby(["city", "year"])["price"]
          .mean()
          .reset_index()
    )

    print("\n=== EVOLUTION PRIX PAR VILLE ===")
    print(trend_by_city)

    return trend_by_city


def creer_dossier_sortie():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generer_graphique_revenu(df):
    revenue_by_city = df.groupby("city")["estimated_revenue"].mean().sort_values(ascending=False)

    plt.figure(figsize=(8, 5))
    revenue_by_city.plot(kind="bar")
    plt.title("Revenu estimé moyen par ville")
    plt.xlabel("Ville")
    plt.ylabel("Revenu estimé")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(STATIC_DIR / "revenue_by_city.png")
    plt.close()

    return revenue_by_city


def generer_graphique_demande(df):
    demand_by_city = df.groupby("city")["number_of_reviews"].mean().sort_values(ascending=False)

    plt.figure(figsize=(8, 5))
    demand_by_city.plot(kind="bar")
    plt.title("Demande moyenne par ville")
    plt.xlabel("Ville")
    plt.ylabel("Nombre moyen de reviews")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(STATIC_DIR / "demand_by_city.png")
    plt.close()

    return demand_by_city


def generer_graphique_prix_par_annee(df):
    if "year" not in df.columns:
        return pd.Series(dtype=float)

    price_by_year = df.dropna(subset=["year"]).groupby("year")["price"].mean()

    plt.figure(figsize=(8, 5))
    price_by_year.plot(kind="line", marker="o")
    plt.title("Evolution moyenne des prix par année")
    plt.xlabel("Année")
    plt.ylabel("Prix moyen")
    plt.tight_layout()
    plt.savefig(STATIC_DIR / "price_by_year.png")
    plt.close()

    return price_by_year


def generer_graphique_score_investissement(df):
    score_by_city = df.groupby("city")["investment_score"].mean().sort_values(ascending=False)

    plt.figure(figsize=(8, 5))
    score_by_city.plot(kind="bar")
    plt.title("Score d'investissement moyen par ville")
    plt.xlabel("Ville")
    plt.ylabel("Score d'investissement")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(STATIC_DIR / "investment_score_by_city.png")
    plt.close()

    return score_by_city


def sauvegarder_json_investissement(df):
    revenue_by_city = df.groupby("city")["estimated_revenue"].mean().round(2)
    demand_by_city = df.groupby("city")["number_of_reviews"].mean().round(2)
    score_by_city = df.groupby("city")["investment_score"].mean().round(2)

    if "year" in df.columns:
        trend_global = (
            df.dropna(subset=["year"])
              .groupby("year")["price"]
              .mean()
              .round(2)
        )
    else:
        trend_global = pd.Series(dtype=float)

    investment_data = {
        "investment_revenue": {
            "labels": revenue_by_city.index.tolist(),
            "values": revenue_by_city.tolist()
        },
        "investment_demand": {
            "labels": demand_by_city.index.tolist(),
            "values": demand_by_city.tolist()
        },
        "investment_score_by_city": {
            "labels": score_by_city.index.tolist(),
            "values": score_by_city.tolist()
        },
        "investment_trend": {
            "labels": trend_global.index.astype(int).astype(str).tolist() if len(trend_global) > 0 else [],
            "values": trend_global.tolist() if len(trend_global) > 0 else []
        },
        "cities": {}
    }

    for city in df["city"].dropna().unique():
        city_df = df[df["city"] == city]

        if "year" in city_df.columns:
            city_trend = (
                city_df.dropna(subset=["year"])
                       .groupby("year")["price"]
                       .mean()
                       .round(2)
            )
        else:
            city_trend = pd.Series(dtype=float)

        investment_data["cities"][city] = {
            "investment": {
                "revenue": round(city_df["estimated_revenue"].mean(), 2),
                "demand": round(city_df["number_of_reviews"].mean(), 2),
                "score": round(city_df["investment_score"].mean(), 2)
            },
            "investment_trend": {
                "labels": city_trend.index.astype(int).astype(str).tolist() if len(city_trend) > 0 else [],
                "values": city_trend.tolist() if len(city_trend) > 0 else []
            }
        }

    output_file = OUTPUT_DIR / "investment_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(investment_data, f, ensure_ascii=False, indent=2)

    print(f"\nJSON généré dans {output_file}")


def main():
    creer_dossier_sortie()

    df = charger_donnees(DATA_DIR)
    df = preparer_dates(df)
    df = nettoyer_donnees(df)

    afficher_infos_colonnes(df)
    verifier_prix(df)

    df = calculer_indicateurs(df)

    analyser_revenu_demande(df)
    analyser_evolution_prix(df)
    analyser_evolution_prix_par_ville(df)

    generer_graphique_revenu(df)
    generer_graphique_demande(df)
    generer_graphique_prix_par_annee(df)
    generer_graphique_score_investissement(df)

    sauvegarder_json_investissement(df)

    print(f"\nGraphiques générés dans {STATIC_DIR}")
    print(f"JSON généré dans {OUTPUT_DIR / 'investment_data.json'}")

def compute_investment_dashboard_data(df):
    df = preparer_dates(df.copy())
    df = nettoyer_donnees(df)
    df = calculer_indicateurs(df)

    revenue_by_city = df.groupby("city")["estimated_revenue"].mean().round(2)
    demand_by_city = df.groupby("city")["number_of_reviews"].mean().round(2)
    score_by_city = df.groupby("city")["investment_score"].mean().round(2)

    if "year" in df.columns:
        trend_global = (
            df.dropna(subset=["year"])
              .groupby("year")["price"]
              .mean()
              .round(2)
        )
    else:
        trend_global = pd.Series(dtype=float)

    investment_data = {
        "investment_revenue": {
            "labels": revenue_by_city.index.tolist(),
            "values": revenue_by_city.tolist()
        },
        "investment_demand": {
            "labels": demand_by_city.index.tolist(),
            "values": demand_by_city.tolist()
        },
        "investment_score_by_city": {
            "labels": score_by_city.index.tolist(),
            "values": score_by_city.tolist()
        },
        "investment_trend": {
            "labels": trend_global.index.astype(int).astype(str).tolist() if len(trend_global) > 0 else [],
            "values": trend_global.tolist() if len(trend_global) > 0 else []
        },
        "cities": {}
    }

    for city in df["city"].dropna().unique():
        city_df = df[df["city"] == city]

        if "year" in city_df.columns:
            city_trend = (
                city_df.dropna(subset=["year"])
                       .groupby("year")["price"]
                       .mean()
                       .round(2)
            )
        else:
            city_trend = pd.Series(dtype=float)

        investment_data["cities"][city] = {
            "investment": {
                "revenue": round(city_df["estimated_revenue"].mean(), 2),
                "demand": round(city_df["number_of_reviews"].mean(), 2),
                "score": round(city_df["investment_score"].mean(), 2)
            },
            "investment_trend": {
                "labels": city_trend.index.astype(int).astype(str).tolist() if len(city_trend) > 0 else [],
                "values": city_trend.tolist() if len(city_trend) > 0 else []
            }
        }

    return investment_data

if __name__ == "__main__":
    main()