import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="sin bash")


def _git(cwd, *args):
    return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
                          cwd=cwd, check=True, capture_output=True, text=True).stdout


def _foto(cwd):
    return subprocess.run([BASH, str(RAIZ / "scripts/foto.sh")], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def test_la_foto_ve_lo_nuevo_sin_tocar_el_indice(tmp_path):
    # Leccion: sin commits por IT, el reviewer no tenia contra que comparar.
    _git(tmp_path, "init", "-q")
    (tmp_path / "a.txt").write_text("a\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("secreto\n", encoding="utf-8")
    base = _foto(tmp_path)  # funciona tambien sin ningun commit
    (tmp_path / "a.txt").write_text("a\nb\n", encoding="utf-8")
    (tmp_path / "nuevo.txt").write_text("n\n", encoding="utf-8")
    (tmp_path / "secreto").write_text("s\n", encoding="utf-8")
    cambios = _git(tmp_path, "diff", "--name-only", base, _foto(tmp_path)).split()
    assert cambios == ["a.txt", "nuevo.txt"]
    assert _git(tmp_path, "diff", "--cached", "--name-only") == ""
