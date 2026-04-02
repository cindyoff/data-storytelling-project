# Data storytelling - Final project

# Auteurs
- Habib Karamoko - @hdkaramoko
- Oumalheir Souley Na Lado - @Ouma-Souley
- Cindy Tran - @cindyoff

ENSAE - MS Data Science - 2026

---

# Sommaire
1. [Introduction](#introduction)
2. [Structure du projet](#structure-du-projet)
3. [Données](#données)
4. [Lancement du projet](#lancement-du-projet)
5. [Langages et packages](#langages-et-packages)
6. [Architecture et fonctionnement](#architecture-et-fonctionnement)
7. [Processus de création](#processus-de-création)
8. [Visualisations](#visualisations)
9. [Limites du projet](#limites-du-projet)
10. [Conclusion](#conclusion)
11. [Références](#références)
12. [Auteurs](#auteurs)

# Introduction
Ce projet s'inscrit dans le cadre du cours "Data Storytelling", donné par Pr. Pietriga et Pr. Prouzeau à l'ENSAE Paris. Il porte sur l'analyse des données de la plateforme Airbnb en France, un marché particulièrement dynamique : la France figure en effet parmi les destinations les plus prisées au monde, et Airbnb y joue un rôle croissant dans l'offre d'hébergement touristique et de courte durée.

L'objectif du projet ici est de concevoir un dashboard interactif permettant de mettre en valeur, de manière claire et accessible, les informations contenues dans les données à disposition. Il s'agit alors de proposer un ensemble de visualisations pertinentes qui donnent à voir les caractéristiques de l'offre Airbnb sous différents angles : répartition géographique des logements, niveaux de prix, types d'hébergements, disponibilité, profils des hôtes ou encore attractivité relative des villes. Le dashboard couvre quatre territoires français : Paris, Lyon, Bordeaux et le Pays Basque.

Ce rapport accompagne le projet en décrivant les données mobilisées, l'architecture technique retenue, le processus de création des visualisations, ainsi que les limites identifiées.

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

En plus de cela, une dernière base de données est ajoutée pour remédier à un problème critique de valeurs manquantes au niveau des prix pour la ville de Paris. En effet, tous les prix de Paris étant manquant, une jointure est effectuée entre `listings-paris.csv` et `prix-paris.csv`, sur la clé primaire `id` du logement, correspondant à un identifiant unique pour chaque logement listé. Cela permettra donc d'apporter une solution au problème de valeurs manquantes. Le jeu de données `prix-paris.csv`, quant à lui, provient de l'assemblement de données sous [Kaggle](https://www.kaggle.com/datasets/abaghyangor/airbnb-paris?resource=download&select=Listings.csv). À présent, `listings-paris.csv` ne présente aucune valeur manquante. 

# Lancement du projet
Afin de mettre le dashboard en relief, la commande suivante suffit pour lancer le tout : 
```bash
python main.py
```
En conséquence, le dashboard final, sous format HTML, est retrouvé et stocké dans le dossier `output/`. 

# Langages et packages
**Backend — Python**
- `pandas` : chargement des fichiers CSV, nettoyage des données (suppression de colonnes, appellation des variables, formatage des chaînes), jointure entre `listings-paris.csv` et `prix-paris.csv` sur la clé `id`, concaténation des quatre villes en un seul DataFrame pandas
- `numpy` : calculs statistiques (moyennes, médianes, normalisations) et transformation en séries des types numpy en JSON via l'encoder `NumpyEncoder`
- `json` : chaîne JSON des statistiques injectée dans le template HTML

**Frontend — HTML/CSS/JavaScript**
- `Chart.js 4.4.1` : génération des graphiques interactifs (barres, camembert, spider chart...)
- `Leaflet.js 1.9.4` : carte interactive géolocalisant les logements par ville avec bulles d'informations
- `D3.js` : visualisations avancées réalisées directement en JavaScript, notamment le spider chart et le classement dynamique des hôtes avec filtres temporels
- Google Fonts (`Syne`, `Outfit`, `JetBrains Mono`) : typographie du dashboard
- CSS custom properties (variables) : système de thème sombre cohérent sur l'ensemble des composants

# Architecture et fonctionnement
Le projet repose sur une architecture de **génération de site statique** : Python produit un fichier HTML autonome qui embarque toutes les données ; aucun serveur n'est nécessaire à l'exécution.

**Pipeline backend (`main.py`)**
1. **Chargement & nettoyage** (`load_data.py`) : lecture des fichiers CSV, interpolation linéaire des valeurs manquantes sur les prix, jointure des prix de Paris, ajout d'une colonne `city` pour indiquer la ville correspondante et concaténation en un unique DataFrame
2. **Calcul des statistiques** (`compute_stats.py`) : agrégations par ville (prix moyen, disponibilité, type de logement, top hôtes, nuits minimum, avis, métriques normalisées pour le spider chart)
3. **Génération des configurations** (`generate_charts.py`) : transformation des statistiques en un dictionnaire conforme au format attendu par Chart.js et D3, puis transformation en chaîne JSON
4. **Construction du dashboard** (`build_dashboard.py`) : lecture du template `templates/dashboard.html`, remplacement du placeholder `{{ CHART_DATA_JSON }}` par le JSON généré, écriture du fichier final dans `output/dashboard.html`

**Frontend (`templates/dashboard.html`)**
- Le fichier template contient l'ensemble du HTML, CSS et JavaScript et la variable `const DATA` est initialisée au chargement avec le JSON injecté par Python
- La sidebar permet la navigation entre les pages du dashboard : le JavaScript lit `DATA` pour instancier les graphiques Chart.js, la carte Leaflet et les visualisations D3
- Le résultat est un fichier HTML standalone, statique : il peut être ouvert directement dans un navigateur sans serveur ni dépendance externe

# Processus de création
Les croquis dans le dossier ```report/``` du projet montrent le processus de création d'une poignée de graphiques présents dans le dashboard final. En plus de cela, le dahsboard présente une combinaison de graphiques crées sous Python et JavaScript avec le package D3. Cela inclut le spider chart, présent en page 4 du dashboard, ainsi que le classement des hôtes en fonction des filtres temporels. Ces croquis ont été réalisés dans le cadre du quatrième cours "data storytelling" dispensé par Pr. Prouzeau. 

# Visualisations
+++ expliquer chaque visualisation et leur but

# Limites du projet
## Limites liées aux données
- **Couverture géographique restreinte** : seules quatre villes/régions françaises sont couvertes (Paris, Lyon, Bordeaux, Pays Basque), ce qui ne permet pas de généraliser les conclusions à l'ensemble du territoire national
- **Données statiques** : les fichiers CSV constituent des instantanés à une date précise, donc le dashboard ne reflète pas l'évolution en temps réel du marché Airbnb

## Limites techniques
- **Dashboard statique sans backend** : l'architecture de génération de site statique implique que toute mise à jour des données nécessite de relancer le pipeline Python et de régénérer le fichier HTML manuellement
- **Dépendances internet** : le dashboard requiert une connexion internet pour charger Chart.js, Leaflet.js et les polices Google Fonts ; il ne fonctionne pas hors ligne
- **Toutes les données contenues dans un seul fichier HTML** : le JSON injecté dans `output/dashboard.html` grossit proportionnellement au volume de données, ce qui peut dégrader les performances à plus grande échelle

# Conclusion
Ce projet a permis de concevoir et de déployer un dashboard interactif dédié à l'analyse du marché Airbnb dans quatre villes et régions françaises : Paris, Lyon, Bordeaux et le Pays Basque. En combinant un pipeline de traitement de données en Python et un frontend entièrement rendu en HTML/CSS/JavaScript, nous avons pu proposer un outil de visualisation autonome, sans serveur, accessible directement depuis un navigateur.

Sur le plan analytique, le dashboard met en lumière des disparités marquées entre les villes, tant en termes de prix que de types de logements proposés ou de disponibilité. Ces résultats illustrent la richesse du storytelling par la donnée : là où un tableau de chiffres bruts resterait opaque, les visualisations rendent immédiatement lisibles des tendances qui nécessiteraient autrement une analyse approfondie.

D'un point de vue technique, ce projet a été l'occasion de mettre en pratique une architecture de génération de site statique, en articulant un backend Python structuré en modules indépendants et un frontend s'appuyant sur des bibliothèques de visualisation reconnues. Le choix d'un fichier HTML standalone facilite le partage et la reproductibilité du dashboard sans infrastructure supplémentaire.

Enfin, les limites identifiées ouvrent des perspectives d'amélioration, notamment vers un dashboard dynamique connecté à une API ou mis à jour de façon périodique. Ce travail constitue néanmoins une base pour explorer plus avant les données du marché locatif de courte durée en France.

# Références
- Bases de données source [Airbnb](https://insideairbnb.com/fr/get-the-data/)
- Base de données des [prix de Paris](https://www.kaggle.com/datasets/abaghyangor/airbnb-paris?resource=download&select=Listings.csv)
- Polices utilisés provenant de [Google Fonts](https://fonts.google.com/share?selection.family=Syne:wght@400;600;700;800|Outfit:wght@300;400;500;600|JetBrains+Mono:wght@400;500)
- Graphiques sous JavaScript [D3](https://observablehq.com/@d3/gallery?utm_source=d3js-org&utm_medium=hero&utm_campaign=try-observable)