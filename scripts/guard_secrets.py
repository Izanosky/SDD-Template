#!/usr/bin/env python3
"""PreToolUse (Bash|PowerShell): bloquea comandos que pueden sacar un secreto.

Los permisos `deny` de settings.json cubren Read/Grep/Edit, pero para la
shell solo comparan prefijos de texto: `type backend\\.env`, `Get-Content`
o `$env:MI_TOKEN` los esquivan. Este hook mira el comando entero.

Los nombres de los secretos salen de `harness.json` ("secretos"), para que
no haya una segunda lista que se desincronice.

Exit 2 = bloqueado; el motivo va por stderr y lo lee el agente.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _secretos() -> tuple[str, ...]:
    try:
        datos = json.loads((RAIZ / "harness.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ()
    return tuple(s for s in datos.get("secretos", []) if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", s))


def _reglas() -> list[tuple[re.Pattern[str], str]]:
    reglas = [
        # Cualquier fichero .env salvo la plantilla .env.example. `.venv` no
        # casa: el punto va delante de la v, no de la e.
        (re.compile(r"(?<![\w-])\.env(?!\.example\b)(?![\w-])"),
         "toca un fichero .env (solo .env.example es legible)"),
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


def motivo(comando: str) -> str | None:
    for patron, texto in _reglas():
        if patron.search(comando):
            return texto
    return None


def main() -> int:
    try:
        entrada = json.load(sys.stdin)
    except ValueError:
        return 0
    comando = (entrada.get("tool_input") or {}).get("command") or ""
    razon = motivo(comando)
    if razon is None:
        return 0
    print(f"Bloqueado por scripts/guard_secrets.py: el comando {razon}. "
          "Los secretos no pasan por el contexto de un agente (CLAUDE.md, "
          "Prohibiciones). Si hace falta, pideselo al humano.",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
