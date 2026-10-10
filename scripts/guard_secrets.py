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


def _reglas() -> list[tuple[re.Pattern[str], str]]:
    reglas = [
        # Volcar el entorno entero.
        (re.compile(r"(^|[;&|(]\s*)(printenv|env|set|export\s+-p)\s*($|[;&|)])"),
         "vuelca todas las variables de entorno"),
        (re.compile(r"\b(Get-ChildItem|gci|dir|ls|Get-Item|gi)\s+env:", re.I),
         "vuelca todas las variables de entorno"),
        (re.compile(r"\[Environment\]::GetEnvironmentVariables", re.I),
         "vuelca todas las variables de entorno"),
    ]
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
    for patron, texto in _reglas():
        if patron.search(comando):
            return texto
    return None


def salta_el_pre_commit(comando: str) -> bool:
    """Por tokens, no por texto: un mensaje de commit que mencione --no-verify pasa."""
    try:
        lexer = shlex.shlex(comando, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        # Comillas sin cerrar: se mira el texto entero, aunque sobre-bloquee.
        return bool(re.search(r"--no-verify|core\.hookspath", comando, re.I))
    tramo: list[str] = []
    for t in tokens + [";"]:
        if t and set(t) <= set(";&|()"):
            if _tramo_salta(tramo):
                return True
            tramo = []
        else:
            tramo.append(t)
    return False


def _tramo_salta(tramo: list[str]) -> bool:
    if "git" not in (Path(t).stem.lower() for t in tramo[:3]):
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
