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

def load_paris(path="data/listings-paris.csv"):
    df = pd.read_csv(path, sep=",")
    df = clean_paris(df)
    df["city"] = "Paris"
    return df

def load_bordeaux(path="data/listings-bordeaux.csv"):
    df = pd.read_csv(path, sep=",")
    df = clean_bordeaux(df)
    df["city"] = "Bordeaux"
    return df

# nettoyage --------
def clean_lyon(df):
    # Suppression des colonnes inutiles
    df = df.drop(columns=["id", "license", "neighbourhood_group"])
    # Interpolation linéaire sur les prix manquants
    df["price"] = df["price"].interpolate(method="linear")
    return df

def clean_paysbasque(df):
    # Suppression des colonnes inutiles
    df = df.drop(columns=["id", "license", "neighbourhood"])
    # Renommage pour harmoniser avec les autres bases
    df = df.rename(columns = {"neighbourhood_group": "neighbourhood"})
    # Interpolation linéaire sur les prix manquants
    df["price"] = df["price"].interpolate(method="linear")
    return df

def clean_paris(df): # ATTENTION : Paris a 0 prix !!!!! A VOIR !!!!!!
    df = df.drop(columns = ["id", "license", "neighbourhood_group"])
    # df["price"] = df["price"].interpolate(method = "linear")
    return df

def clean_bordeaux(df):
    df = df.drop(columns = ["id", "license", "neighbourhood"])
    df = df.rename(columns = {"neighbourhood_group": "neighbourhood"})
    df["price"] = df["price"].interpolate(method = "linear")
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