import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import agent_tokens  # noqa: E402


def _l(**e):
    return json.dumps(e)


def _uso(msg_id, ts, entrada, cache, bloques=()):
    return _l(type="assistant", timestamp=ts, message={
        "id": msg_id, "content": list(bloques),
        "usage": {"input_tokens": entrada, "output_tokens": 1, "cache_read_input_tokens": cache}})


def test_separa_ejecuciones_y_cuenta_cada_mensaje_una_vez():
    lineas = [
        _l(type="user", timestamp="2026-10-10T10:00:00Z", message={"content": "encargo"}),
        _uso("a", "2026-10-10T10:01:00Z", 10, 100),
        # El transcript repite el mensaje por bloque: se cuenta una vez.
        _uso("a", "2026-10-10T10:01:00Z", 10, 100,
             [{"type": "tool_use", "id": "t1", "name": "Skill", "input": {"skill": "migration"}}]),
        _uso("b", "2026-10-10T10:05:00Z", 5, 50,
             [{"type": "tool_use", "id": "t2", "name": "SubagentHandback", "input": {}}]),
        _l(type="user", timestamp="2026-10-10T11:00:00Z", message={"content": "reanuda"}),
        _uso("c", "2026-10-10T11:02:00Z", 7, 70),
    ]
    r1, r2 = agent_tokens.ejecuciones(lineas)
    assert (r1["tokens"], r1["cache_read"], r1["skills"]) == (17, 150, ["migration"])
    assert (r2["tokens"], r2["cache_read"], r2["skills"]) == (8, 70, [])
    assert r2["inicio"] == "2026-10-10T11:00:00Z"
