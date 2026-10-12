import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import guard_secrets  # noqa: E402


@pytest.fixture(autouse=True)
def _secretos_de_prueba(tmp_path, monkeypatch):
    (tmp_path / "harness.json").write_text(
        json.dumps({"secretos": ["MI_TOKEN", "DB_PASSWORD"]}), encoding="utf-8")
    monkeypatch.setattr(guard_secrets, "RAIZ", tmp_path)


BLOQUEADOS = [
    "cat backend/.env",
    "type backend\\.env",
    "Get-Content backend/.env",
    "grep KEY .env",
    "cp backend/.env /tmp/x",
    "cat .env.local",
    "echo $MI_TOKEN",
    "echo ${DB_PASSWORD}",
    "Write-Output $env:MI_TOKEN",
    "echo %DB_PASSWORD%",
    "python -c \"import os; print(os.environ['MI_TOKEN'])\"",
    "node -e \"console.log(process.env.MI_TOKEN)\"",
    "printenv",
    "env | grep TOKEN",
    "set",
    "Get-ChildItem env:",
    "gci Env:",
    # El patron de busqueda se ignora, pero el fichero buscado no.
    "grep -e KEY .env",
    "grep -n TOKEN .env | head",
    "rg KEY backend/.env",
    # Leccion: con el patron dentro de la opcion se quitaba el .env.
    "grep -e. .env",
    "grep -ne. .env",
    "rg --regexp=. .env",
    "grep -f .env x",
    "cat .env-prod",
    "cd app\nenv",
    "cat <<EOF; env\nx\nEOF",
    # Sin comillas en la marca, bash expande el secreto dentro del heredoc.
    "cat <<EOF\n$MI_TOKEN\nEOF",
]

PERMITIDOS = [
    "cat backend/.env.example",
    "source backend/.venv/bin/activate",
    "grep -rn MI_TOKEN src",
    "python scripts/state.py",
    "git status",
    "./init.sh --all",
    "env FOO=1 pytest",
    # Leccion: buscar el TEXTO ".env" en la documentacion no lee ningun .env.
    'grep -n "./.env" notas.txt',
    "rg '\\.env' docs",
    # Leccion del piloto: codigo dentro de un heredoc se leia como volcado.
    "python - <<'EOF'\nprint(fn(env))\nEOF",
    "cat >> t.py <<EOF\n    x = 1; env | 2\nset\nEOF",
]


@pytest.mark.parametrize("comando", BLOQUEADOS)
def test_bloquea(comando):
    assert guard_secrets.motivo(comando) is not None


@pytest.mark.parametrize("comando", PERMITIDOS)
def test_permite(comando):
    assert guard_secrets.motivo(comando) is None


def _hook(entrada: str):
    return subprocess.run([sys.executable, str(RAIZ / "scripts/guard_secrets.py")],
                          input=entrada.encode("utf-8"), capture_output=True)


def test_hook_bloquea_con_codigo_2():
    assert _hook(json.dumps({"tool_input": {"command": "printenv"}})).returncode == 2


def test_hook_deja_pasar_lo_seguro_aunque_venga_con_bom():
    assert _hook("﻿" + json.dumps({"tool_input": {"command": "git status"}})).returncode == 0


def test_hook_falla_cerrado_si_la_entrada_es_ilegible():
    assert _hook("esto no es json").returncode == 2


BASH = shutil.which("bash")


@pytest.mark.skipif(BASH is None, reason="sin bash")
def test_lanzador_sin_python_bloquea():
    # Leccion: un hook cuyo interprete no existe es un error NO bloqueante en
    # Claude Code; el lanzador convierte ese caso en un bloqueo (codigo 2).
    r = subprocess.run([BASH, str(RAIZ / "scripts/py.sh"), "-c", "pass"],
                       env={"PATH": "/nonexistent"}, capture_output=True, text=True)
    assert r.returncode == 2


@pytest.mark.skipif(BASH is None, reason="sin bash")
def test_lanzador_con_python_ejecuta():
    # Sin comillas en el argumento: la bash de Git en Windows las quita.
    r = subprocess.run([BASH, str(RAIZ / "scripts/py.sh"), "-c", "print(6*7)"],
                       env={**os.environ, "PYTHON": sys.executable}, capture_output=True, text=True)
    assert r.returncode == 0 and "42" in r.stdout


SALTAN_EL_PRE_COMMIT = [
    "git commit --no-verify -m x",
    "git commit -n -m x",
    "git push --no-verify",
    "git -c core.hooksPath=/dev/null commit -m x",
    "git config core.hooksPath .git/hooks",
    "git config --unset core.hooksPath",
    "cd app && git commit --no-verify -m x",
    "git.exe commit --no-verify -m x",
]

RESPETAN_EL_PRE_COMMIT = [
    "git commit -m x",
    # Leccion: mirar el texto entero bloqueaba un mensaje que lo mencionaba.
    'git commit -m "docs: bloquear --no-verify"',
    "git config core.hooksPath .githooks",
    "git push -n",
    "git log -n 5",
    "echo --no-verify",
]


@pytest.mark.parametrize("comando", SALTAN_EL_PRE_COMMIT)
def test_bloquea_saltarse_el_pre_commit(comando):
    assert guard_secrets.salta_el_pre_commit(comando)


@pytest.mark.parametrize("comando", RESPETAN_EL_PRE_COMMIT)
def test_permite_git_normal(comando):
    assert not guard_secrets.salta_el_pre_commit(comando)


DESTRUCTIVOS = [
    # Leccion del piloto: mato todos los node de la maquina.
    "taskkill /F /IM node.exe",
    "cd app\ntaskkill /IM python.exe /F",
    "pkill node",
    "killall python3",
    "Stop-Process -Name node -Force",
    "Get-Process node | Stop-Process",
    "git commit --amend --no-edit",
    "git push --force origin main",
    "git push -f",
    "git push --force-with-lease",
    "git rebase main",
    "git filter-branch --tree-filter x",
    # Leccion del piloto: "restaurar de HEAD" borra el trabajo sin commitear.
    "git checkout HEAD -- app/bridge.py",
    "git checkout -- .",
    "git checkout .",
    "git restore app/bridge.py",
    "git restore --staged --worktree x",
    "git reset --hard",
    "git clean -fd",
    "git stash drop",
]

NO_DESTRUCTIVOS = [
    "taskkill /PID 4242 /F",
    "Stop-Process -Id 4242",
    "Get-Process -Id 4242 | Stop-Process",
    "kill 4242",
    "git push origin main",
    'git commit -m "docs: no usar taskkill /IM ni --amend"',
    "cat > notas.sh <<'EOF'\ngit rebase main\nEOF",
    "git checkout -b prueba",
    "git restore --staged x",
    "git reset HEAD x",
    "git clean -n",
    "git stash",
    "git diff HEAD -- app/bridge.py",
]


@pytest.mark.parametrize("comando", DESTRUCTIVOS)
def test_bloquea_lo_destructivo(comando):
    assert guard_secrets.destructivo(comando)


@pytest.mark.parametrize("comando", NO_DESTRUCTIVOS)
def test_permite_lo_acotado(comando):
    assert guard_secrets.destructivo(comando) is None


def test_hook_bloquea_no_verify_con_codigo_2():
    r = _hook(json.dumps({"tool_input": {"command": "git commit --no-verify -m x"}}))
    assert r.returncode == 2 and b"pre-commit" in r.stderr
