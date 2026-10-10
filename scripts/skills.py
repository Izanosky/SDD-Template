#!/usr/bin/env python3
"""Skills instaladas que el harness aun no ha clasificado, y las que le faltan.

Una skill nueva no se usa sola: nadie la precarga y ningun agente sabe que
existe. Una precargada que falta tampoco avisa: Claude Code se la salta sin
error. Leccion: en el piloto ningun subagente invoco una skill bajo demanda
en 110 ejecuciones; solo la precarga (`skills:` del agente) es fiable.

    bash scripts/py.sh scripts/skills.py          # texto, vacio si no hay nada
    bash scripts/py.sh scripts/skills.py --json

Clasificada = la precarga algun agente, tiene estado en `skillOverrides` de
`.claude/settings.json` (o `settings.local.json`), o esta en
`skills_revisadas` de `harness.json`: las de plugin, a las que
`skillOverrides` no llega, tanto si las usa una skill del harness como si
se descartaron. Las de `.claude/skills/` del proyecto son del harness y no
cuentan.
"""
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _config() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def _json(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _nombre(skill_md: Path) -> str:
    try:
        cabecera = skill_md.read_text(encoding="utf-8").split("---")[1]
    except (OSError, IndexError, UnicodeDecodeError):
        return skill_md.parent.name
    m = re.search(r"^name:\s*(\S+)", cabecera, re.M)
    return m.group(1).strip("'\"") if m else skill_md.parent.name


def _de_plugin(raiz: Path, plugin: str) -> set[str]:
    return {f"{plugin}:{_nombre(p)}" for p in raiz.glob("skills/*/SKILL.md")}


def instaladas() -> set[str]:
    """Skills de usuario, plugins del directorio de skills y plugins activos."""
    config, nombres = _config(), set()
    for d in sorted((config / "skills").glob("*")):
        manifiesto = d / ".claude-plugin" / "plugin.json"
        if manifiesto.is_file():
            nombres |= _de_plugin(d, _json(manifiesto).get("name") or d.name)
        elif (d / "SKILL.md").is_file():
            nombres.add(_nombre(d / "SKILL.md"))
    activos = dict(_json(config / "settings.json").get("enabledPlugins") or {})
    for f in ("settings.json", "settings.local.json"):
        activos.update(_json(RAIZ / ".claude" / f).get("enabledPlugins") or {})
    instalados = _json(config / "plugins" / "installed_plugins.json").get("plugins") or {}
    for clave, entradas in instalados.items():
        if activos.get(clave) and entradas:
            ruta = Path(entradas[0].get("installPath", ""))
            nombres |= _de_plugin(ruta, clave.split("@")[0])
    return nombres


def precargadas() -> dict[str, set[str]]:
    """skill -> agentes que la precargan (lista `skills:` del frontmatter)."""
    usos: dict[str, set[str]] = {}
    for agente in (RAIZ / ".claude" / "agents").glob("*.md"):
        partes = agente.read_text(encoding="utf-8").split("---")
        bloque = re.search(r"^skills:\s*\n((?:[ \t]+-.*\n?)+)", partes[1] if len(partes) > 2 else "", re.M)
        for linea in (bloque.group(1).splitlines() if bloque else []):
            usos.setdefault(linea.strip().lstrip("-").strip().strip("'\""), set()).add(agente.stem)
    return usos


def clasificadas() -> set[str]:
    nombres = set(precargadas())
    for f in ("settings.json", "settings.local.json"):
        nombres |= set(_json(RAIZ / ".claude" / f).get("skillOverrides") or {})
    nombres |= set(_json(RAIZ / "harness.json").get("skills_revisadas") or [])
    nombres |= {_nombre(p) for p in (RAIZ / ".claude" / "skills").glob("*/SKILL.md")}
    return nombres


def informe() -> dict[str, list[str]]:
    hay = instaladas()
    return {
        "nuevas": sorted(hay - clasificadas()),
        "ausentes": sorted(f"{s} ({', '.join(sorted(a))})"
                           for s, a in precargadas().items() if s not in hay),
    }


def main(argv: list[str]) -> int:
    datos = informe()
    if "--json" in argv:
        print(json.dumps(datos, ensure_ascii=False))
        return 0
    if datos["nuevas"]:
        print("Skills nuevas sin clasificar (propon al humano un rol o descartarlas): "
              + ", ".join(datos["nuevas"]))
    if datos["ausentes"]:
        print("Skills precargadas que no estan instaladas (Claude Code las ignora): "
              + ", ".join(datos["ausentes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
