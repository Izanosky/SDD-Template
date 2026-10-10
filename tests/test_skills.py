import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import skills  # noqa: E402


def _skill(carpeta: Path, nombre: str) -> None:
    carpeta.mkdir(parents=True)
    (carpeta / "SKILL.md").write_text(f"---\nname: {nombre}\ndescription: x\n---\n", encoding="utf-8")


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    config, proyecto = tmp_path / "config", tmp_path / "proyecto"
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(config))
    monkeypatch.setattr(skills, "RAIZ", proyecto)
    (proyecto / ".claude" / "agents").mkdir(parents=True)
    (proyecto / ".claude" / "agents" / "implementer.md").write_text(
        "---\nname: implementer\nmodel: sonnet\nskills:\n  - precargada\n  - falta\n---\n"
        "# implementer\n---\nskills:\n  - no-es-frontmatter\n", encoding="utf-8")
    (proyecto / ".claude" / "settings.json").write_text(
        json.dumps({"skillOverrides": {"oculta": "user-invocable-only"}}), encoding="utf-8")
    (proyecto / "harness.json").write_text(
        json.dumps({"skills_revisadas": ["plug:revisada"]}), encoding="utf-8")
    _skill(proyecto / ".claude" / "skills" / "arranque", "arranque")
    for nombre in ("precargada", "oculta", "nueva"):
        _skill(config / "skills" / nombre, nombre)
    # Carpeta con nombre distinto del de su SKILL.md: manda el `name:`.
    _skill(config / "skills" / "carpeta-rara", "con-nombre")
    # Plugin del directorio de skills.
    plugin_dir = config / "skills" / "mi-plugin"
    (plugin_dir / ".claude-plugin").mkdir(parents=True)
    (plugin_dir / ".claude-plugin" / "plugin.json").write_text('{"name": "mi-plugin"}', encoding="utf-8")
    _skill(plugin_dir / "skills" / "audita", "audita")
    # Plugins instalados: uno activo y otro no.
    for clave, nombre in (("plug@m", "revisada"), ("plug@m", "otra"), ("apagado@m", "x")):
        _skill(tmp_path / "cache" / clave.split("@")[0] / "skills" / nombre, nombre)
    (config / "plugins").mkdir(parents=True)
    (config / "plugins" / "installed_plugins.json").write_text(json.dumps({"plugins": {
        "plug@m": [{"installPath": str(tmp_path / "cache" / "plug")}],
        "apagado@m": [{"installPath": str(tmp_path / "cache" / "apagado")}],
    }}), encoding="utf-8")
    (config / "settings.json").write_text(
        json.dumps({"enabledPlugins": {"plug@m": True, "apagado@m": False}}), encoding="utf-8")
    return proyecto


def test_informa_de_las_nuevas_y_de_las_ausentes(entorno):
    datos = skills.informe()
    assert datos["nuevas"] == ["con-nombre", "mi-plugin:audita", "nueva", "plug:otra"]
    assert datos["ausentes"] == ["falta (implementer)"]


def test_solo_lee_las_skills_del_frontmatter(entorno):
    assert "no-es-frontmatter" not in skills.precargadas()


def test_un_plugin_desactivado_en_el_proyecto_no_cuenta(entorno):
    (entorno / ".claude" / "settings.json").write_text(
        json.dumps({"enabledPlugins": {"plug@m": False}}), encoding="utf-8")
    assert "plug:otra" not in skills.informe()["nuevas"]


def test_sin_nada_que_decir_no_imprime_nada(entorno, capsys):
    (entorno / "harness.json").write_text(json.dumps({"skills_revisadas": [
        "plug:revisada", "plug:otra", "mi-plugin:audita", "nueva", "con-nombre"]}), encoding="utf-8")
    (entorno / ".claude" / "agents" / "implementer.md").write_text(
        "---\nname: implementer\nskills:\n  - precargada\n---\n", encoding="utf-8")
    skills.main([])
    assert capsys.readouterr().out == ""


def test_la_plantilla_no_precarga_nada_raro():
    # Cada skill precargada en la plantilla figura en el README, que es donde
    # el usuario mira que instalar.
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    for skill in skills.precargadas():
        assert f"`{skill}`" in readme, skill
