#!/usr/bin/env python3
"""SubagentStop: anade a progress/metrics.csv la linea de la ejecucion que
acaba de terminar.

Antes la escribia el leader a mano tras cada agente: una llamada a
agent_tokens.py y una edicion por ejecucion, en el contexto mas caro de
todos (la sesion principal releia cada paso). Claude Code lanza este hook en
cada ejecucion de un subagente, tambien al reanudarlo con SendMessage, con
`agent_type` y `agent_transcript_path` (comprobado el 2026-10-10).

- feature e IT: las que despacha state.py (IT 0 para spec_author y
  explorer); con una auditoria pendiente, feature `audit`.
- veredicto y causa: las lineas `Veredicto:` y `Causa:` de review.md o
  security.md de esa IT.

Nunca falla hacia fuera: un SubagentStop con codigo 2 impediria que el
subagente terminara. Los errores van a stderr y el hook sale con 0.
"""
import csv
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import agent_tokens  # noqa: E402
import state  # noqa: E402

_CAUSA = re.compile(r"^\W*Causa\W*(codigo|tests|spec|otro)\b", re.M | re.I)
_REVISORES = {"reviewer": "review.md", "security_reviewer": "security.md"}


def _roles() -> set[str]:
    return {p.stem for p in (RAIZ / ".claude" / "agents").glob("*.md")} - {"leader"}


def _ultima_it_escrita() -> tuple[str, int] | None:
    its = [d for d in (RAIZ / "progress").glob("*/IT*")
           if d.is_dir() and re.fullmatch(r"IT\d+", d.name)]
    if not its:
        return None
    reciente = max(its, key=lambda d: max([f.stat().st_mtime for f in d.iterdir()]
                                          + [d.stat().st_mtime]))
    return reciente.parent.name, int(reciente.name[2:])


def fila(entrada: dict) -> list[str] | None:
    rol = entrada.get("agent_type") or ""
    transcript = Path(entrada.get("agent_transcript_path") or "")
    if rol not in _roles() or not transcript.is_file():
        return None
    runs = agent_tokens.ejecuciones(transcript.read_text(encoding="utf-8").splitlines())
    if not runs:
        return None
    r = runs[-1]
    estado = state.next_action()
    feature = estado.get("feature", "-")
    if estado.get("audits_pending") and rol == "security_reviewer":
        feature, it = "audit", estado["audits_pending"][-1]
    elif rol in {"spec_author", "explorer"}:
        it = 0
    else:
        # La IT que el agente acaba de escribir, no la que despacha state.py:
        # el cierre marca `done` y state.py ya apunta a la feature siguiente.
        feature, it = _ultima_it_escrita() or (feature, 0)
    veredicto = causa = ""
    if rol in _REVISORES and feature not in {"-", "audit"}:
        ruta = RAIZ / "progress" / feature / f"IT{it}" / _REVISORES[rol]
        texto = ruta.read_text(encoding="utf-8", errors="replace") if ruta.is_file() else ""
        m = state._VEREDICTO.search(texto)
        veredicto = m.group(1).upper() if m else ""
        c = _CAUSA.search(texto) if veredicto == "CHANGES_REQUESTED" else None
        causa = c.group(1).lower() if c else ""
    minutos = round((agent_tokens._hora(r["fin"]) - agent_tokens._hora(r["inicio"])).total_seconds() / 60)
    return [r["inicio"][:10], feature, str(it), rol, str(r["tokens"]), str(r["cache_read"]),
            str(minutos), veredicto, causa, "|".join(r["skills"]), r["modelo"]]


def main() -> int:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace").lstrip("﻿"))
        linea = fila(entrada)
        if linea:
            with (RAIZ / "progress" / "metrics.csv").open("a", encoding="utf-8", newline="") as f:
                csv.writer(f, lineterminator="\n").writerow(linea)
    except Exception as e:  # noqa: BLE001 - un fallo aqui no debe bloquear al subagente
        print(f"metricas.py: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
