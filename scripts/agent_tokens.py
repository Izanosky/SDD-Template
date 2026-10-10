#!/usr/bin/env python3
"""Consumo real de un subagente, por ejecucion, leido de su transcript.

El `subagent_tokens` que devuelve la herramienta Agent es el tamano del
contexto al terminar, no lo gastado: en una reanudacion arrastra todo lo
anterior y no cuenta las relecturas de cache. Leccion: sumarlo daba un total
que no cuadraba con nada (piloto, 2026-10-03).

    bash scripts/py.sh scripts/agent_tokens.py <agent_id>
    bash scripts/py.sh scripts/agent_tokens.py <agent_id> --run 3
    bash scripts/py.sh scripts/agent_tokens.py --file <transcript.jsonl>

Una ejecucion termina en su llamada a SubagentHandback o cuando llega otro
mensaje al agente (el SendMessage que la reanuda): las versiones recientes
de Claude Code no escriben SubagentHandback en el transcript. Por cada ejecucion imprime `run,inicio,minutos,tokens,cache_read,skills`:
- tokens = input + cache_creation + output (lo nuevo de esa ejecucion);
- cache_read = relecturas de cache (la mayor parte del gasto real);
- skills = las invocadas con la herramienta Skill, separadas por `|`. Las
  precargadas (`skills:` del agente) no aparecen: no se invocan. Leccion:
  la linea "Skills usadas" que escribia cada agente mezclaba lo invocado con
  "criterio aplicado a mano" y no servia para medir.
Cada mensaje de la API se cuenta una vez (el transcript lo repite por bloque).
"""
import json
import sys
from datetime import datetime
from pathlib import Path


def _hora(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _usos_de_herramienta(entrada: dict, nombre: str) -> list[dict]:
    contenido = (entrada.get("message") or {}).get("content") or []
    if not isinstance(contenido, list):
        return []
    return [b for b in contenido if b.get("type") == "tool_use" and b.get("name") == nombre]


def _es_mensaje(entrada: dict) -> bool:
    """Texto que llega al agente (encargo, reanudacion), no un resultado de herramienta."""
    if entrada.get("type") == "assistant":
        return True  # sin mensaje previo visible, la ejecucion empieza al primer paso
    contenido = (entrada.get("message") or {}).get("content")
    if entrada.get("type") != "user" or contenido is None:
        return False
    return isinstance(contenido, str) or any(b.get("type") != "tool_result" for b in contenido)


def ejecuciones(lineas) -> list[dict]:
    """Agrupa el transcript en ejecuciones y suma su uso."""
    runs, usos, skills, inicio, fin = [], {}, {}, None, None

    def cerrar():
        if usos:
            u = usos.values()
            runs.append({
                "inicio": inicio, "fin": fin,
                "tokens": sum(x.get("input_tokens", 0) + x.get("cache_creation_input_tokens", 0)
                              + x.get("output_tokens", 0) for x in u),
                "cache_read": sum(x.get("cache_read_input_tokens", 0) for x in u),
                "skills": list(skills.values()),
            })

    for linea in lineas:
        try:
            e = json.loads(linea)
        except ValueError:
            continue
        ts = e.get("timestamp")
        m = e.get("message") or {}
        if e.get("type") == "user" and _es_mensaje(e) and usos:
            cerrar()  # mensaje nuevo tras trabajo ya hecho: otra ejecucion
            usos, skills, inicio, fin = {}, {}, None, None
        # Empieza en el encargo o el SendMessage, no en el resultado del
        # handback anterior: si no, los minutos cuentan la espera entre medias.
        if ts and not inicio and _es_mensaje(e):
            inicio = ts
        if ts and inicio:
            fin = ts
        if m.get("usage"):
            usos[m.get("id") or len(usos)] = m["usage"]  # ultima entrada de cada mensaje
        for b in _usos_de_herramienta(e, "Skill"):
            skills[b.get("id") or len(skills)] = str((b.get("input") or {}).get("skill", "?"))
        if _usos_de_herramienta(e, "SubagentHandback"):
            cerrar()
            usos, skills, inicio, fin = {}, {}, None, None
    cerrar()  # ejecucion sin handback (cortada o en curso)
    return runs


def _transcript(agent_id: str) -> Path:
    raiz = Path.home() / ".claude" / "projects"
    hallados = sorted(raiz.glob(f"*/*/subagents/agent-{agent_id}*.jsonl"),
                      key=lambda p: p.stat().st_mtime)
    if not hallados:
        sys.exit(f"Sin transcript para agent-{agent_id} en {raiz}")
    return hallados[-1]


def main(argv: list[str]) -> int:
    run = int(argv[argv.index("--run") + 1]) if "--run" in argv else None
    ruta = Path(argv[argv.index("--file") + 1]) if "--file" in argv else _transcript(argv[0])
    print("run,inicio,minutos,tokens,cache_read,skills")
    for i, r in enumerate(ejecuciones(ruta.read_text(encoding="utf-8").splitlines()), 1):
        if run in (None, i):
            minutos = round((_hora(r["fin"]) - _hora(r["inicio"])).total_seconds() / 60)
            print(f"{i},{r['inicio'][:19]},{minutos},{r['tokens']},{r['cache_read']},"
                  f"{'|'.join(r['skills'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
