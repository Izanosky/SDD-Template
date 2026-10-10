import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import metricas  # noqa: E402
import state  # noqa: E402


def _transcript(ruta: Path) -> Path:
    lineas = [
        {"type": "user", "timestamp": "2026-10-10T10:00:00Z", "message": {"content": "encargo"}},
        {"type": "assistant", "timestamp": "2026-10-10T10:04:00Z", "message": {
            "id": "a", "content": [], "usage": {"input_tokens": 10, "output_tokens": 2,
                                                "cache_read_input_tokens": 300}}},
    ]
    ruta.write_text("\n".join(json.dumps(x) for x in lineas), encoding="utf-8")
    return ruta


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for rol in ("leader", "implementer", "reviewer", "spec_author"):
        (tmp_path / ".claude" / "agents").mkdir(parents=True, exist_ok=True)
        (tmp_path / ".claude" / "agents" / f"{rol}.md").write_text("---\n---\n", encoding="utf-8")
    (tmp_path / "progress" / "F01" / "IT2").mkdir(parents=True)
    (tmp_path / "progress" / "arranque.md").write_text("Estado: APROBADO\n", encoding="utf-8")
    (tmp_path / "feature_list.json").write_text(json.dumps([{
        "id": "F01", "status": "in_progress", "sdd": True, "scope": ["a"]}]), encoding="utf-8")
    monkeypatch.setattr(metricas, "RAIZ", tmp_path)
    monkeypatch.setattr(state, "ROOT", tmp_path)
    return tmp_path


def test_fila_del_reviewer_con_veredicto_y_causa(repo):
    (repo / "progress/F01/IT2/review.md").write_text(
        "Veredicto: CHANGES_REQUESTED\nCausa: tests\n", encoding="utf-8")
    fila = metricas.fila({"agent_type": "reviewer",
                          "agent_transcript_path": str(_transcript(repo / "t.jsonl"))})
    assert fila == ["2026-10-10", "F01", "2", "reviewer", "12", "300", "4",
                    "CHANGES_REQUESTED", "tests", ""]


def test_spec_author_va_en_la_it_0(repo):
    fila = metricas.fila({"agent_type": "spec_author",
                          "agent_transcript_path": str(_transcript(repo / "t.jsonl"))})
    assert fila[1:4] == ["F01", "0", "spec_author"]


def test_agentes_ajenos_al_harness_no_se_apuntan(repo):
    assert metricas.fila({"agent_type": "Explore",
                          "agent_transcript_path": str(_transcript(repo / "t.jsonl"))}) is None


def test_el_hook_nunca_bloquea_al_subagente():
    # Un SubagentStop con codigo 2 impediria que el subagente terminara.
    r = subprocess.run([sys.executable, str(RAIZ / "scripts/metricas.py")],
                       input=b"no es json", capture_output=True)
    assert r.returncode == 0
