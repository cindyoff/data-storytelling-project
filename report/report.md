# Data storytelling - Final project

# Introduction
Ce projet s'inscrit dans la finalité du cours "Data Storytelling", donné par Pr. Pietriga et Pr. Prouzeau. Le but du projet est de créer un support, en l'occurrence un dashboard, pour exposer les différentes visualisations permettant de mieux comprendre les données à disposition. 

# Structure du projet
```
data-storytelling-project/
├── main.py
│
├── report/
│   ├── report.md
│   ├── habib.jpg
│   └── cindy.jpeg
│
├── data/
│   ├── listings-bordeaux.csv
│   ├── listings-lyon.csv
│   ├── listings-paris.csv
│   ├── listings-paysbasque.csv
│   └── prix-paris.csv
│
├── output/
│   └── dashboard.html
│
├── templates/
│   └── dashboard.html
│
├── src/
│   ├── build_dashboard.py
│   ├── compute_stats.py
│   ├── generate_charts.py
│   └── load_data.py
│
└── tests/
    ├── index.html
    ├── script.js
    └── styles.css
```

# Données
Ce projet mobilise des données provenant de deux sources différentes. Tout d'abord, les bases de données sous format CSV (comma-separated values) commençant par "listings-" proviennent du site web [Inside Airbnb](https://insideairbnb.com/fr/get-the-data/), qui répertorie l'ensemble des données par ville de chaque pays disponible. Nous avons décidé de choisir la France comme pays d'étude pour ce projet. Par conséquent, nous obtenons les villes suivantes : 
- Bordeaux (`listings-bordeaux.csv`)
- Lyon (`listings-lyon.csv`)
- Paris (`listings-paris.csv`)
- Villes de la région Pays Basque (`listings-paysbasque.csv`)

En plus de cela, une dernière base de données est ajoutée pour remédier à un problème critique de valeurs manquantes au niveau des prix pour la ville de Paris. En effet, tous les prix de Paris étant manquant, une jointure est effectuée entre `listings-paris.csv` et `prix-paris.csv`, sur la clé primaire `id` du logement, correspondant à un identifiant unique pour chaque logement listé. Cela permettra donc d'apporter une solution au problème de valeurs manquantes. À présent, `listings-paris.csv` ne présente aucune valeur manquante. 

# Processus de réflexion
+++ mentionner les graphiques

Authors : 
- Habib Karamoko (hdkaramoko)
- Oumalheir Souley Na Lado (Ouma-Souley)
- Cindy Tran (cindyoff)

ENSAE - MS Data Science - 2026