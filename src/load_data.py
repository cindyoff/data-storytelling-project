import pandas as pd

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

def load_prix_paris(path = "data/prix-paris.csv"):
    df = pd.read_csv(path, sep = ",", encoding = "latin-1")
    df = clean_prix_paris(df)
    return df 

def load_paris(path="data/listings-paris.csv", prix_path = "data/prix-paris.csv"):
    # import des deux bases de données
    df = pd.read_csv(path, sep = ",")
    df_prix = load_prix_paris(prix_path)

    # supprimer la colonne vide "price" dans listings-paris.csv
    del df["price"]

    # inner join sur id
    df = df.merge(df_prix, on = "id", how = "inner")
    
    # attribut de la ville
    df["city"] = "Paris"
    return df

# nettoyage --------
def clean_lyon(df):
    # suppression variables
    df = df.drop(columns=["id", "license", "neighbourhood_group"])

    # interpolation linéaire des prix
    df["price"] = df["price"].interpolate(method="linear")

    # suppression guillemets dans noms
    df["name"] = df["name"].str.replace('""', '', regex = False)
    return df

def clean_paysbasque(df):
    # suppression variables
    df = df.drop(columns=["id", "license", "neighbourhood"])
    
    # renommer variables
    df = df.rename(columns = {"neighbourhood_group": "neighbourhood"})
    
    # interpolation linéaire des prix
    df["price"] = df["price"].interpolate(method="linear")

    # suppression guillemets
    df["name"] = df["name"].str.replace('""', '', regex = False)
    return df

def clean_paris(df):
    # suppression variables
    df = df.drop(columns = ["id", "license", "neighbourhood_group"])

    # suppression guillemets
    df["name"] = df["name"].str.replace('""', '', regex = False)

    return df

def clean_prix_paris(df):
    # garder seulement la clé de jointure et les prix
    df = df[["listing_id", "price"]]

    # renommer "listing_id" en "id"
    df = df.rename(columns = {
        "listing_id": "id"
    })

    return df

def clean_bordeaux(df):
    # suppression variables
    df = df.drop(columns = ["id", "license", "neighbourhood"])

    # renommer variables
    df = df.rename(columns = {"neighbourhood_group": "neighbourhood"})

    # interpolation linéaire
    df["price"] = df["price"].interpolate(method = "linear")

    # suppression guillemets
    df["name"] = df["name"].str.replace('""', '', regex = False)

    # formater noms de région
    df["neighbourhood"] = df["neighbourhood"].replace("Bgles", "Begles")
    df["neighbourhood"] = df["neighbourhood"].replace("Saint-Mdard-en-Jalles", "Saint-Medard-en-Jalles")
    df["neighbourhood"] = df["neighbourhood"].replace("Le Taillan-Mdoc", "Le Taillan-Medoc")
    df["neighbourhood"] = df["neighbourhood"].replace("Saint-Aubin-de-Mdoc", "Saint-Aubin-de-Medoc")
    df["neighbourhood"] = df["neighbourhood"].replace("Artigues-Prs-Bordeaux", "Artigues-Pres-Bordeaux")
    df["neighbourhood"] = df["neighbourhood"].replace("Ambs", "Ambes")
    df["neighbourhood"] = df["neighbourhood"].replace("Bordeaux", "Centre")

    # ajout attribut "Bordeaux" devant chaque région
    # df["neighbourhood"] = "Bordeaux - " + df["neighborhood"]
    return df 

# concat all datasets ---------
def load_all(data_dir="data/"):
    dfs = [
        load_lyon(f"{data_dir}listings-lyon.csv"),
        load_paysbasque(f"{data_dir}listings-paysbasque.csv"),
        load_paris(f"{data_dir}listings-paris.csv"),
        load_bordeaux(f"{data_dir}listings-bordeaux.csv"),
    ]
    df = pd.concat(dfs, ignore_index=True)
    return df