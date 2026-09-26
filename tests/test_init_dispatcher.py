import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _init(*args):
    # Ruta relativa a proposito: Git Bash en Windows se come las barras
    # invertidas de una ruta absoluta.
    return subprocess.run(["bash", "init.sh", *args],
                          capture_output=True, text=True, cwd=RAIZ)


def test_el_dispatcher_existe():
    assert (RAIZ / "init.sh").is_file()


def test_dry_run_anuncia_el_scope_de_la_feature_activa():
    # Leccion: el scope esperado sale de state.py, no de un literal: cambia
    # cada vez que se cierra la ultima feature de una fase. Y con
    # sys.executable: en el Linux del CI puede no existir `python`.
    estado = subprocess.run([sys.executable, "scripts/state.py"],
                            capture_output=True, text=True, cwd=RAIZ, check=True)
    scope = json.loads(estado.stdout).get("scope", [])
    r = _init("--dry-run")
    assert r.returncode == 0, r.stderr
    for stack in scope:
        assert stack in r.stdout


def test_un_scope_sin_init_sh_falla_en_vez_de_saltarselo():
    """Un stack sin init.sh no puede dar verde: seria un falso OK."""
    scopes = json.loads((RAIZ / "harness.json").read_text(encoding="utf-8"))["scopes"]
    if all((RAIZ / s / "init.sh").is_file() for s in scopes):
        return  # todos los stacks ya tienen init.sh: no hay caso que probar
    r = _init("--all")
    assert r.returncode != 0
    assert "FALTA" in r.stderr
