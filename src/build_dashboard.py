import os

PLACEHOLDER = "{{ CHART_DATA_JSON }}"

def build(chart_json: str,
          template: str = "templates/dashboard.html",
          output:   str = "output/dashboard.html") -> None:
    """
    Lecture fichier dans template/.html, remplacement du placeholder par le JSON des données et écriture du fichier final dans output/.html

    chart_json : chaîne JSON
    template : chemin vers fichier template/
    output : chemin du fichier final output/
    """
    # lecture template
    with open(template, "r", encoding="utf-8") as f:
        html = f.read()

    # vérification placeholder
    if PLACEHOLDER not in html:
        raise ValueError(
            f"Placeholder '{PLACEHOLDER}' introuvable dans {template}. "
            "Vérifiez que le template contient bien `const DATA = {{ CHART_DATA_JSON }}`"
        )

    # injection données
    html = html.replace(PLACEHOLDER, chart_json)

    # création dossier output/
    os.makedirs(os.path.dirname(output), exist_ok=True)

    # fichier final
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Fichier généré : {os.path.abspath(output)}")
    print(f"Taille : {os.path.getsize(output) / 1024:.1f} Ko")