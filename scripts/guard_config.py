#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit): pide confirmacion al humano antes de
cambiar la configuracion de lint, formato, tipos o del propio harness.

Un agente atascado en un check tiende a relajar la regla (un `ignore`, un
`strict: false`) en vez de arreglar el codigo, y el diff lo esconde entre
muchos cambios. Idea del hook config-protection de ECC; aqui no bloquea:
devuelve "ask", porque a veces el cambio es legitimo y lo aprueba el humano.

Crear un fichero nuevo no pregunta (el montaje los crea). Cambiar el texto
por la shell (sed, cat >) no pasa por aqui.
ATAJO: solo Edit/Write · si un agente lo esquiva por la shell, anadir esos
patrones a guard_secrets.py.

Si la entrada no se entiende, deja pasar: un fallo de este hook no debe
impedir editar codigo (el de secretos, en cambio, falla cerrado).
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_NOMBRES = re.compile(
    r"(\.?eslintrc(\.\w+)?|eslint\.config\.\w+|\.?prettierrc(\.\w+)?|prettier\.config\.\w+"
    r"|tsconfig(\.[\w-]+)?\.json|biome\.jsonc?|\.?ruff\.toml|\.?mypy\.ini|\.flake8|\.pylintrc"
    r"|pytest\.ini|setup\.cfg|\.golangci\.\w+|\.stylelintrc(\.\w+)?|\.gitleaks\.toml"
    r"|vitest\.config\.\w+|jest\.config\.\w+)", re.I)
# En pyproject.toml solo preocupa la configuracion de herramientas, no las
# dependencias ni la version.
_PYPROJECT = re.compile(r"\[tool\.|^\s*(ignore|extend-ignore|select|per-file-ignores|strict"
                        r"|disable_error_code|ignore_missing_imports|addopts|filterwarnings)\s*=",
                        re.M)


def _del_harness(ruta: Path) -> bool:
    try:
        rel = ruta.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return False
    return (rel.startswith((".githooks/", ".github/workflows/"))
            or rel in {".claude/settings.json", "init.sh"})


def motivo(entrada: dict) -> str | None:
    datos = entrada.get("tool_input") or {}
    ruta = Path(datos.get("file_path") or "")
    if not ruta.name or not ruta.is_file():
        return None
    if _del_harness(ruta):
        return "es configuracion del harness (la decide el humano)"
    if _NOMBRES.fullmatch(ruta.name):
        return "es configuracion de lint, formato, tipos o tests"
    if ruta.name == "pyproject.toml":
        texto = " ".join(str(datos.get(k, "")) for k in ("old_string", "new_string", "content"))
        texto += " ".join(str(e.get(k, "")) for e in datos.get("edits") or []
                          for k in ("old_string", "new_string"))
        if _PYPROJECT.search(texto):
            return "toca la configuracion de herramientas de pyproject.toml"
    return None


def main() -> int:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace").lstrip("﻿"))
    except ValueError:
        return 0
    razon = motivo(entrada) if isinstance(entrada, dict) else None
    if razon:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"scripts/guard_config.py: el fichero {razon}. Si un check falla, "
                "arregla el codigo; relajar la regla lo aprueba el humano."),
        }}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
