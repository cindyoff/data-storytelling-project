"""
Tests unitaires pour src/build_dashboard.py.

On utilise des fichiers temporaires (tmp_path) pour éviter toute
dépendance aux fichiers réels du projet.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.build_dashboard import build, PLACEHOLDER


SAMPLE_JSON = '{"avg_price": 85.5}'


def _make_template(directory, content=None):
    """Crée le dossier si nécessaire, écrit un template HTML et retourne son chemin."""
    if content is None:
        content = f"<html><body><script>const DATA = {PLACEHOLDER};</script></body></html>"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "dashboard.html"
    path.write_text(content, encoding="utf-8")
    return str(path)

# cas nominal 
class TestBuildNominal:
    def test_output_file_created(self, tmp_path):
        template = _make_template(tmp_path / "templates")
        output = str(tmp_path / "output" / "dashboard.html")

        build(SAMPLE_JSON, template=template, output=output)

        assert os.path.exists(output)

    def test_output_contains_injected_json(self, tmp_path):
        template = _make_template(tmp_path / "templates")
        output = str(tmp_path / "output" / "dashboard.html")

        build(SAMPLE_JSON, template=template, output=output)

        content = open(output, encoding="utf-8").read()
        assert SAMPLE_JSON in content

    def test_placeholder_no_longer_present_in_output(self, tmp_path):
        template = _make_template(tmp_path / "templates")
        output = str(tmp_path / "output" / "dashboard.html")

        build(SAMPLE_JSON, template=template, output=output)

        content = open(output, encoding="utf-8").read()
        assert PLACEHOLDER not in content

    def test_output_dir_created_automatically(self, tmp_path):
        template = _make_template(tmp_path / "templates")
        # Dossier output n'existe pas encore
        output = str(tmp_path / "new_subdir" / "deep" / "dashboard.html")

        build(SAMPLE_JSON, template=template, output=output)

        assert os.path.exists(output)

# placeholder manquant
class TestBuildMissingPlaceholder:
    def test_raises_value_error(self, tmp_path):
        template = _make_template(
            tmp_path / "templates",
            content="<html><body>Pas de placeholder ici.</body></html>"
        )
        output = str(tmp_path / "output" / "dashboard.html")

        with pytest.raises(ValueError, match=PLACEHOLDER.replace("{", r"\{").replace("}", r"\}")):
            build(SAMPLE_JSON, template=template, output=output)

    def test_output_not_created_on_error(self, tmp_path):
        template = _make_template(
            tmp_path / "templates",
            content="<html>no placeholder</html>"
        )
        output = str(tmp_path / "output" / "dashboard.html")

        with pytest.raises(ValueError):
            build(SAMPLE_JSON, template=template, output=output)

        assert not os.path.exists(output)

# template introuvable
class TestBuildMissingTemplate:
    def test_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            build(SAMPLE_JSON,
                  template=str(tmp_path / "nonexistent.html"),
                  output=str(tmp_path / "out.html"))

# contenu fichier de sortie 
class TestBuildOutputContent:
    def test_rest_of_html_preserved(self, tmp_path):
        html_body = f"<h1>Mon titre</h1>{PLACEHOLDER}<footer>pied</footer>"
        template = _make_template(tmp_path / "templates", content=html_body)
        output = str(tmp_path / "out.html")

        build(SAMPLE_JSON, template=template, output=output)

        content = open(output, encoding="utf-8").read()
        assert "<h1>Mon titre</h1>" in content
        assert "<footer>pied</footer>" in content

    def test_multiple_runs_overwrite(self, tmp_path):
        (tmp_path / "templates").mkdir(parents=True, exist_ok=True)
        template = _make_template(tmp_path / "templates")
        output = str(tmp_path / "out.html")

        build('{"first": 1}', template=template, output=output)
        build('{"second": 2}', template=template, output=output)

        content = open(output, encoding="utf-8").read()
        assert '"second": 2' in content
        assert '"first": 1' not in content
