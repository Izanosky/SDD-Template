import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import guard_config  # noqa: E402


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(guard_config, "RAIZ", tmp_path)
    for f in ("eslint.config.js", "web/tsconfig.app.json", "ruff.toml", "pyproject.toml",
              ".claude/settings.json", ".githooks/pre-commit", "src/app.py", "web/vite.config.ts"):
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f).write_text("x", encoding="utf-8")
    return tmp_path


def _entrada(ruta, **datos):
    return {"tool_name": "Edit", "tool_input": {"file_path": str(ruta), **datos}}


@pytest.mark.parametrize("fichero", ["eslint.config.js", "web/tsconfig.app.json", "ruff.toml",
                                     ".claude/settings.json", ".githooks/pre-commit"])
def test_pregunta_antes_de_tocar_configuracion(repo, fichero):
    assert guard_config.motivo(_entrada(repo / fichero)) is not None


@pytest.mark.parametrize("fichero", ["src/app.py", "web/vite.config.ts"])
def test_el_codigo_no_pregunta(repo, fichero):
    assert guard_config.motivo(_entrada(repo / fichero)) is None


def test_crear_un_fichero_nuevo_no_pregunta(repo):
    assert guard_config.motivo(_entrada(repo / "web" / "eslint.config.mjs")) is None


def test_pyproject_solo_pregunta_si_toca_herramientas(repo):
    py = repo / "pyproject.toml"
    assert guard_config.motivo(_entrada(py, old_string="version = \"1\"", new_string="version = \"2\"")) is None
    assert guard_config.motivo(_entrada(py, old_string="strict = true", new_string="strict = false"))
    assert guard_config.motivo(_entrada(py, edits=[{"old_string": "x", "new_string": "[tool.ruff]"}]))


def _hook(entrada: str):
    return subprocess.run([sys.executable, str(RAIZ / "scripts/guard_config.py")],
                          input=entrada.encode("utf-8"), capture_output=True, text=False)


def test_el_hook_devuelve_ask():
    r = _hook(json.dumps(_entrada(RAIZ / ".claude/settings.json")))
    salida = json.loads(r.stdout.decode("utf-8"))
    assert r.returncode == 0
    assert salida["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_el_hook_deja_pasar_si_la_entrada_es_ilegible():
    r = _hook("no es json")
    assert r.returncode == 0 and r.stdout == b""
