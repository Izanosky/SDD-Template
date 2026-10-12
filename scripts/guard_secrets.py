#!/usr/bin/env python3
"""PreToolUse (Bash|PowerShell): bloquea comandos que pueden sacar un secreto
o saltarse el pre-commit.

Los permisos `deny` de settings.json cubren Read/Grep/Edit, pero para la
shell solo comparan prefijos de texto: `type backend\\.env`, `Get-Content`
o `$env:MI_TOKEN` los esquivan. Este hook mira el comando entero.

Los nombres de los secretos salen de `harness.json` ("secretos"), para que
no haya una segunda lista que se desincronice.

El pre-commit es la ultima puerta antes de que un secreto exista en un
commit: `--no-verify`, `commit -n` o un `core.hooksPath` distinto de
`.githooks` lo apagan sin dejar rastro (idea del hook block-no-verify de ECC).

Y lo que no tiene vuelta atras (idea de safety-guard de ECC): reescribir la
historia (CLAUDE.md, Reglas duras) y matar procesos por nombre. Leccion del
piloto: un `taskkill /IM node.exe` mato todos los node de la maquina.

Exit 2 = bloqueado; el motivo va por stderr y lo lee el agente.
"""
import json
import re
import shlex
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_ENV = re.compile(r"(?<![\w-])\.env(?!\.example\b)(?!\w)")
_BUSCADORES = {"grep", "egrep", "fgrep", "rg"}


def _secretos() -> tuple[str, ...]:
    try:
        datos = json.loads((RAIZ / "harness.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ()
    return tuple(s for s in datos.get("secretos", []) if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", s))


# El cuerpo de un heredoc es texto (codigo que se escribe o se pasa a un
# interprete), no comandos. Leccion: `print(fn(env))` o `; env |` dentro de
# un `python - <<EOF` se leian como volcado del entorno.
_HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1([^\n]*)\n.*?^\s*\2\s*$", re.M | re.S)

_VOLCADOS = [
    # Una linea nueva tambien separa comandos: `cd x\nenv` vuelca.
    re.compile(r"(^|[;&|(\n]\s*)(printenv|env|set|export\s+-p)\s*($|[;&|)\n])"),
    re.compile(r"\b(Get-ChildItem|gci|dir|ls|Get-Item|gi)\s+env:", re.I),
    re.compile(r"\[Environment\]::GetEnvironmentVariables", re.I),
]


def _reglas() -> list[tuple[re.Pattern[str], str]]:
    reglas = []
    nombres = "|".join(_secretos())
    if nombres:
        reglas += [
            # Expandir el valor: $X, ${X}, $env:X, %X%.
            (re.compile(rf"(\$\{{?|\$env:|%)({nombres})\b", re.I),
             "expande el valor de un secreto"),
            (re.compile(rf"(environ|getenv|process\.env)\W+({nombres})\b", re.I),
             "lee el valor de un secreto desde codigo"),
        ]
    return reglas


def _sin_patron_de_busqueda(comando: str) -> str:
    """`grep -n "x.env" notas.txt` busca un texto, no lee un .env.

    Solo para un buscador suelto (sin tuberias ni encadenados): se quita su
    primer argumento posicional, que es el patron. Ante cualquier duda se
    devuelve el comando entero, y la regla de .env sigue mirandolo todo.
    """
    if re.search(r"[;&|`$<>]", comando):
        return comando
    try:
        partes = shlex.split(comando)
    except ValueError:
        return comando
    if not partes or Path(partes[0]).name not in _BUSCADORES:
        return comando
    # Con -e/-f/--regexp/--file el patron va en la opcion y el primer
    # posicional ya es un fichero. Leccion: `grep -e. .env` quitaba el .env.
    if any(re.match(r"-[^-]*[ef]|--(regexp|file)\b", p) for p in partes[1:]):
        return comando
    for i, p in enumerate(partes[1:], 1):
        if not p.startswith("-"):
            return " ".join(partes[:i] + partes[i + 1:])
    return comando


def motivo(comando: str) -> str | None:
    # Cualquier fichero .env (tambien .env-prod) salvo la plantilla
    # .env.example. `.venv` no casa: el punto va delante de la v, no de la e.
    if _ENV.search(_sin_patron_de_busqueda(comando)):
        return "toca un fichero .env (solo .env.example es legible)"
    # Con la marca sin comillas, bash expande $X dentro del heredoc: las
    # reglas de secretos siguen mirando el comando entero.
    sin_heredocs = _HEREDOC.sub(r"\3", comando)
    if any(p.search(sin_heredocs) for p in _VOLCADOS):
        return "vuelca todas las variables de entorno"
    for patron, texto in _reglas():
        if patron.search(comando):
            return texto
    return None


def _tramos(comando: str) -> list[list[str]] | None:
    """Por tokens, no por texto: un mensaje de commit que cite un comando pasa.

    None si hay comillas sin cerrar; quien llama mira el texto entero.
    """
    try:
        # La linea nueva separa comandos, salvo dentro de comillas.
        lexer = shlex.shlex(_HEREDOC.sub(r"\3", comando), posix=True,
                            punctuation_chars="();<>|&\n")
        lexer.whitespace = " \t\r"
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return None
    tramos, tramo = [], []
    for t in tokens + [";"]:
        if t and set(t) <= set(";&|()\n"):
            if tramo:
                tramos.append(tramo)
            tramo = []
        else:
            tramo.append(t)
    return tramos


def salta_el_pre_commit(comando: str) -> bool:
    tramos = _tramos(comando)
    if tramos is None:
        # Comillas sin cerrar: se mira el texto entero, aunque sobre-bloquee.
        return bool(re.search(r"--no-verify|core\.hookspath", comando, re.I))
    return any(_tramo_salta(t) for t in tramos)


def _es_git(tramo: list[str]) -> bool:
    return "git" in (Path(t).stem.lower() for t in tramo[:3])


def destructivo(comando: str) -> str | None:
    tramos = _tramos(comando)
    if tramos is None:
        tramos = [comando.split()]
    previo: list[str] = []
    for tramo in tramos:
        bajos = [t.lower() for t in tramo]
        orden = Path(bajos[0]).stem
        if (orden in ("pkill", "killall")
                or (orden == "taskkill" and "/im" in bajos)
                or (orden in ("stop-process", "spps") and "-name" in bajos)
                # `Get-Process node | Stop-Process`
                or (orden in ("stop-process", "spps", "kill") and previo
                    and Path(previo[0]).stem in ("get-process", "gps", "ps")
                    and "-id" not in previo)):
            return ("mata procesos por nombre (todos los de la maquina, no solo "
                    "los tuyos). Paralo por el PID que arrancaste")
        if _es_git(tramo) and (
                "--amend" in bajos
                or ("push" in bajos and any(t == "-f" or t.startswith("--force") for t in bajos))
                or any(t in ("rebase", "filter-branch", "filter-repo") for t in bajos)):
            return ("reescribe la historia de git (--amend, push --force, rebase, "
                    "filter-branch): el historial es la evidencia de cada iteracion")
        if _es_git(tramo) and _descarta_cambios(tramo):
            return ("descarta cambios sin commitear: el trabajo de todas las IT vive "
                    "sin commitear hasta que el humano commitea. Restaura desde tu copia")
        previo = bajos
    return None


def _descarta_cambios(tramo: list[str]) -> bool:
    """reset --hard, checkout/restore de ficheros, clean -f, stash drop/clear.

    Leccion del piloto: un agente comprobo un rojo "restaurando bridge.py de
    HEAD", que borra todo lo que las IT anteriores cambiaron en ese fichero.
    """
    t = tramo
    if "reset" in t and "--hard" in t:
        return True
    if "checkout" in t and ("--" in t or "." in t or "-f" in t or "--force" in t):
        return True
    if "restore" in t and ("--worktree" in t or "-W" in t
                           or not ("--staged" in t or "-S" in t)):
        return True
    if "clean" in t and any(re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*|--force", x) for x in t):
        return True
    return "stash" in t and ("drop" in t or "clear" in t)


def _tramo_salta(tramo: list[str]) -> bool:
    if not _es_git(tramo):
        return False
    bajos = [t.lower() for t in tramo]
    if "--no-verify" in bajos or ("commit" in bajos and "-n" in bajos):
        return True
    if "core.hookspath" in bajos and ("--unset" in bajos or "--unset-all" in bajos):
        return True
    for i, t in enumerate(bajos):
        valor = None
        if t.startswith("core.hookspath="):
            valor = t.split("=", 1)[1]
        elif t == "core.hookspath" and i + 1 < len(bajos):
            valor = bajos[i + 1]
        if valor is not None and valor.strip("/\\") != ".githooks":
            return True
    return False


def main() -> int:
    try:
        # lstrip: algunas shells de Windows anteponen un BOM al reenviar stdin.
        # Bytes en UTF-8: en Windows sys.stdin decodifica con la pagina ANSI.
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace").lstrip("﻿"))
        comando = (entrada.get("tool_input") or {}).get("command") or ""
    except (ValueError, AttributeError):
        # Falla cerrado: una entrada que no se entiende no se da por segura.
        print("Bloqueado por scripts/guard_secrets.py: entrada del hook ilegible.",
              file=sys.stderr)
        return 2
    if salta_el_pre_commit(comando):
        print("Bloqueado por scripts/guard_secrets.py: el comando se salta el "
              "pre-commit (--no-verify, commit -n o core.hooksPath distinto de "
              ".githooks). Si un hook falla, arregla la causa; si sobra, lo "
              "decide el humano.", file=sys.stderr)
        return 2
    peligro = destructivo(comando)
    if peligro:
        print(f"Bloqueado por scripts/guard_secrets.py: el comando {peligro}. "
              "Si de verdad hace falta, lo ejecuta el humano.", file=sys.stderr)
        return 2
    razon = motivo(comando)
    if razon is None:
        return 0
    print(f"Bloqueado por scripts/guard_secrets.py: el comando {razon}. "
          "Los secretos no pasan por el contexto de un agente (CLAUDE.md, "
          "Reglas duras). Si hace falta, pideselo al humano.",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
