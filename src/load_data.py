import pandas as pd
import numpy as np

# fonctions de load (chargement) -----------
def load_lyon(path="data/listings-lyon.csv"):
    df = pd.read_csv(path, sep=",")
    df = clean_lyon(df)
    df["city"] = "Lyon"
    return df

def load_paysbasque(path="data/listings-paysbasque.csv"):
    df = pd.read_csv(path, sep=",")
    df = clean_paysbasque(df)
    df["city"] = "Pays Basque"
    return df

def load_bordeaux(path="data/listings-bordeaux.csv"):
    df = pd.read_csv(path, sep=",")
    df = clean_bordeaux(df)
    df["city"] = "Bordeaux"
    return df

def load_prix_paris(path="data/prix-paris.csv"):
    df = pd.read_csv(path, sep=",", encoding="latin-1")
    df = clean_prix_paris(df)
    return df

def load_paris(path="data/listings-paris.csv", prix_path="data/prix-paris.csv"):
    # import des deux bases de données
    df = pd.read_csv(path, sep=",")
    df_prix = load_prix_paris(prix_path)

    # supprimer la colonne vide "price" dans listings-paris.csv
    del df["price"]

    # inner join sur id
    df = df.merge(df_prix, on="id", how="inner")

    # nettoyage de la base Paris après merge
    df = clean_paris(df)

    # attribut de la ville
    df["city"] = "Paris"
    return df


# nettoyage --------

def clean_price_column(df, col="price"):
    df[col] = (
        df[col]
        .astype(str)
        .str.replace("€", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace(r"[^\d.]", "", regex=True)
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# Rajout de l'attribut "ville principale" devant chaque neighbour
def centre_peripherie(dataframe: pd.DataFrame, ville: str, variable_voisinage: str):
    dict_map = {}
    unique_voisinage = dataframe[variable_voisinage].unique()
    check = False
    for elem in unique_voisinage:
        if elem == ville:
            check = True
    if check:
        for elem in unique_voisinage:
            if elem == ville:
                dict_map[elem] = f"{ville}-Centre"
            else:
                dict_map[elem] = f"{ville}-{elem}"
    return dict_map


def clean_lyon(df):
    # suppression variables
    df = df.drop(columns=["id", "license", "neighbourhood_group"])

    # nettoyage du prix
    df = clean_price_column(df, "price")

    # interpolation linéaire des prix
    df["price"] = df["price"].interpolate(method="linear")

    # suppression guillemets dans noms
    df["name"] = df["name"].str.replace('""', '', regex=False)
    return df


def clean_paysbasque(df):
    # suppression variables
    df = df.drop(columns=["id", "license", "neighbourhood"])

    # renommer variables
    df = df.rename(columns={"neighbourhood_group": "neighbourhood"})

    # nettoyage du prix
    df = clean_price_column(df, "price")

    # interpolation linéaire des prix
    df["price"] = df["price"].interpolate(method="linear")

    # suppression guillemets
    df["name"] = df["name"].str.replace('""', '', regex=False)
    return df


def clean_paris(df):
    # suppression variables
    df = df.drop(columns=["id", "license", "neighbourhood_group"])

    # nettoyage du prix
    df = clean_price_column(df, "price")

    # suppression guillemets
    df["name"] = df["name"].str.replace('""', '', regex=False)

    return df


def clean_prix_paris(df):
    # garder seulement la clé de jointure et les prix
    df = df[["listing_id", "price"]]

    # renommer "listing_id" en "id"
    df = df.rename(columns={"listing_id": "id"})

    # nettoyage du prix
    df = clean_price_column(df, "price")

    return df


def clean_bordeaux(df):
    # suppression variables
    df = df.drop(columns=["id", "license", "neighbourhood"])

    # renommer variables
    df = df.rename(columns={"neighbourhood_group": "neighbourhood"})

    # nettoyage du prix
    df = clean_price_column(df, "price")

    # interpolation linéaire
    df["price"] = df["price"].interpolate(method="linear")

    # suppression guillemets
    df["name"] = df["name"].str.replace('""', '', regex=False)

    # formater noms de région
    df["neighbourhood"] = df["neighbourhood"].replace("Bgles", "Begles")
    df["neighbourhood"] = df["neighbourhood"].replace("Saint-Mdard-en-Jalles", "Saint-Medard-en-Jalles")
    df["neighbourhood"] = df["neighbourhood"].replace("Le Taillan-Mdoc", "Le Taillan-Medoc")
    df["neighbourhood"] = df["neighbourhood"].replace("Saint-Aubin-de-Mdoc", "Saint-Aubin-de-Medoc")
    df["neighbourhood"] = df["neighbourhood"].replace("Artigues-Prs-Bordeaux", "Artigues-Pres-Bordeaux")
    df["neighbourhood"] = df["neighbourhood"].replace("Ambs", "Ambes")

    # ajout attribut "Bordeaux" devant chaque région
    df["neighbourhood"] = df["neighbourhood"].map(
        centre_peripherie(df, "Bordeaux", "neighbourhood")
    )

    return df


# normalisation globale --------
def normalize_prices_global(df):
    df = df.copy()

    # log pour réduire l'effet des valeurs extrêmes
    df["log_price"] = np.log1p(df["price"])

    # min-max global
    df["price_norm"] = (
        (df["log_price"] - df["log_price"].min()) /
        (df["log_price"].max() - df["log_price"].min())
    )

    return df


# concat all datasets ---------
def load_all(data_dir="data/"):
    dfs = [
        load_lyon(f"{data_dir}listings-lyon.csv"),
        load_paysbasque(f"{data_dir}listings-paysbasque.csv"),
        load_paris(
            f"{data_dir}listings-paris.csv",
            prix_path=f"{data_dir}prix-paris.csv"
        ),
        load_bordeaux(f"{data_dir}listings-bordeaux.csv"),
    ]
    df = pd.concat(dfs, ignore_index=True)

    # normalisation globale des prix
    df = normalize_prices_global(df)

    return df