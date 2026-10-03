import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts/check_docs_changelog.sh"
# Ruta completa: en Windows, "bash" a secas resuelve antes a System32 (WSL)
# que al PATH, y esa bash vuelve a expandir los argumentos.
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="sin bash")


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _repo(tmp_path, ficheros):
    _git(tmp_path, "init", "-q")
    for ruta in ficheros:
        f = tmp_path / ruta
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    _git(tmp_path, "add", *ficheros)


def _check(tmp_path, *args):
    return subprocess.run([BASH, str(SCRIPT), *args], cwd=tmp_path,
                          capture_output=True, text=True)


def test_cambio_en_docs_sin_changelog_bloquea(tmp_path):
    _repo(tmp_path, ["docs/security.md"])
    r = _check(tmp_path)
    assert r.returncode == 1
    assert "docs/security.md" in r.stderr


def test_cambio_en_docs_con_changelog_pasa(tmp_path):
    _repo(tmp_path, ["docs/security.md", "docs/CHANGELOG.md"])
    assert _check(tmp_path).returncode == 0


def test_cambio_fuera_de_docs_no_exige_changelog(tmp_path):
    _repo(tmp_path, ["src/main.py"])
    assert _check(tmp_path).returncode == 0


def test_rango_de_commits_para_el_ci(tmp_path):
    _repo(tmp_path, ["src/main.py"])
    _git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "a")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/specs.md").write_text("x", encoding="utf-8")
    _git(tmp_path, "add", "docs/specs.md")
    _git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "b")
    assert _check(tmp_path, "HEAD~1..HEAD").returncode == 1


def test_el_pre_commit_y_el_ci_usan_el_script():
    assert "scripts/check_docs_changelog.sh" in (RAIZ / ".githooks/pre-commit").read_text(encoding="utf-8")
    assert "scripts/check_docs_changelog.sh" in (RAIZ / ".github/workflows/ci.yml").read_text(encoding="utf-8")
