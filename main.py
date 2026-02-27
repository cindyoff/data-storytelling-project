from src.load_data import load_all
from src.compute_stats import compute_all_stats
from src.generate_charts import generate_chart_configs
from src.build_dashboard import build

if __name__ == "__main__":
    print("Chargement et nettoyage des données...")
    df = load_all()

    print("Calcul des statistiques...")
    stats = compute_all_stats(df)

    print("Génération des configs Chart.js...")
    charts = generate_chart_configs(stats)

    print("Construction du dashboard HTML...")
    build(charts, template="templates/dashboard.html", output="output/dashboard.html")

    print("Dashboard généré dans output/dashboard.html")