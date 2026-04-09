from src.load_data import load_all
from src.compute_stats import compute_all_stats
from src.generate_charts import generate_chart_configs
from src.build_dashboard import build
from src.investment_analysis import compute_investment_dashboard_data


if __name__ == "__main__":
    print("Chargement et nettoyage des données...")
    df = load_all()

    print("Calcul des statistiques principales...")
    stats = compute_all_stats(df)

    print("Calcul des statistiques d'investissement...")
    investment_stats = compute_investment_dashboard_data(df)

    print("Fusion des statistiques...")
    stats["investment_revenue"] = investment_stats["investment_revenue"]
    stats["investment_demand"] = investment_stats["investment_demand"]
    stats["investment_score_by_city"] = investment_stats["investment_score_by_city"]
    stats["investment_trend"] = investment_stats["investment_trend"]

    for city, city_payload in investment_stats["cities"].items():
        if city in stats["cities"]:
            stats["cities"][city].update(city_payload)

    print("Génération des configs Chart.js...")
    charts = generate_chart_configs(stats)

    print("Construction du dashboard HTML...")
    build(charts, template="templates/dashboard.html", output="output/dashboard.html")

    print("Dashboard généré dans output/dashboard.html")