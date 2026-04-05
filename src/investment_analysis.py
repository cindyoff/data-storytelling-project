import pandas as pd
from load_data import load_all

df = load_all("../data/")

print("Colonnes du dataset :")
print(df.columns.tolist())

if "last_review" in df.columns:
    df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
    df["year"] = df["last_review"].dt.year
    print("\nAnnées trouvées dans last_review :")
    print(df["year"].value_counts().sort_index())
else:
    print("\nPas de colonne last_review")

if "host_since" in df.columns:
    df["host_since"] = pd.to_datetime(df["host_since"], errors="coerce")
    df["host_year"] = df["host_since"].dt.year
    print("\nAnnées trouvées dans host_since :")
    print(df["host_year"].value_counts().sort_index())
else:
    print("\nPas de colonne host_since")
    

print("=== VERIFICATION DES PRIX ===")
print("Nombre total de lignes :", len(df))
print("Prix manquants :", df["price"].isna().sum())
print("Prix non manquants :", df["price"].notna().sum())
print("Prix = 0 :", (df["price"] == 0).sum())
print("Prix < 0 :", (df["price"] < 0).sum())

print("\nPrix manquants par ville :")
print(df.groupby("city")["price"].apply(lambda x: x.isna().sum()))

print("\nRésumé des prix par ville :")
print(df.groupby("city")["price"].describe())


#Calcul du score 
df["estimated_booked_days"] = 365 - df["availability_365"]
df["estimated_revenue"] = df["price"] * df["estimated_booked_days"]

df["investment_score"] = (
    df["price"] * df["availability_365"]
) / (df["number_of_reviews"] + 1)

#Comparaison entre le reenue et la demande
analysis = df.groupby("city")[["estimated_revenue", "number_of_reviews"]].mean()
print("\n=== REVENU VS DEMANDE ===")
print(analysis)

# Analyse temporelle
trend = df.groupby("year")["price"].mean()

print("\n=== EVOLUTION PRIX ===")
print(trend)

df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
df["year"] = df["last_review"].dt.year

trend_by_city = (
    df.dropna(subset=["year"])
      .groupby(["city", "year"])["price"]
      .mean()
      .reset_index()
)

print(trend_by_city)


import os
import matplotlib.pyplot as plt

# dossier de sortie
os.makedirs("../static", exist_ok=True)

# -----------------------------
# 1) Revenu estimé par ville
# -----------------------------
revenue_by_city = df.groupby("city")["estimated_revenue"].mean().sort_values(ascending=False)

plt.figure(figsize=(8,5))
revenue_by_city.plot(kind="bar")
plt.title("Revenu estimé moyen par ville")
plt.xlabel("Ville")
plt.ylabel("Revenu estimé")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("../static/revenue_by_city.png")
plt.close()

# -----------------------------
# 2) Demande moyenne par ville
# -----------------------------
demand_by_city = df.groupby("city")["number_of_reviews"].mean().sort_values(ascending=False)

plt.figure(figsize=(8,5))
demand_by_city.plot(kind="bar")
plt.title("Demande moyenne par ville")
plt.xlabel("Ville")
plt.ylabel("Nombre moyen de reviews")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("../static/demand_by_city.png")
plt.close()

# -----------------------------
# 3) Evolution du prix par année
# -----------------------------
price_by_year = df.groupby("year")["price"].mean()

plt.figure(figsize=(8,5))
price_by_year.plot(kind="line", marker="o")
plt.title("Evolution moyenne des prix par année")
plt.xlabel("Année")
plt.ylabel("Prix moyen")
plt.tight_layout()
plt.savefig("../static/price_by_year.png")
plt.close()

print("Graphiques générés dans ../static/")

import json

investment_data = df.groupby("city")["estimated_revenue"].mean().to_dict()

with open("../output/investment_data.json", "w") as f:
    json.dump(investment_data, f)