import os

PLACEHOLDER = "{{ CHART_DATA_JSON }}"

def build(chart_json: str,
          template: str = "templates/dashboard.html",
          output:   str = "output/dashboard.html") -> None:
    """
    Lit le template HTML, remplace le placeholder par le JSON des données,
    et écrit le fichier final dans output/.

    Args:
        chart_json : chaîne JSON retournée par generate_chart_configs()
        template   : chemin vers le fichier template
        output     : chemin du fichier HTML généré
    """
    # ── Lecture du template ────────────────────────────────────────
    with open(template, "r", encoding="utf-8") as f:
        html = f.read()

    # ── Vérification du placeholder ───────────────────────────────
    if PLACEHOLDER not in html:
        raise ValueError(
            f"Placeholder '{PLACEHOLDER}' introuvable dans {template}. "
            "Vérifiez que le template contient bien `const DATA = {{ CHART_DATA_JSON }};`"
        )

    # ── Injection des données ──────────────────────────────────────
    html = html.replace(PLACEHOLDER, chart_json)

    # ── Création du dossier output si nécessaire ───────────────────
    os.makedirs(os.path.dirname(output), exist_ok=True)

    # ── Écriture du fichier final ──────────────────────────────────
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  → Fichier généré : {os.path.abspath(output)}")
    print(f"  → Taille         : {os.path.getsize(output) / 1024:.1f} Ko")