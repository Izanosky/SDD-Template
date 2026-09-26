import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VALID_STATUS = {"pending", "spec_ready", "in_progress", "done"}


def _features():
    return json.loads((RAIZ / "feature_list.json").read_text(encoding="utf-8"))


def _scopes():
    return set(json.loads((RAIZ / "harness.json").read_text(encoding="utf-8"))["scopes"])


def test_es_json_valido_y_lista():
    assert isinstance(_features(), list)


def test_ids_unicos():
    ids = [f["id"] for f in _features()]
    assert len(ids) == len(set(ids))


def test_campos_obligatorios_y_valores_validos():
    scopes = _scopes()
    for f in _features():
        assert f["status"] in VALID_STATUS, f["id"]
        assert isinstance(f["sdd"], bool), f["id"]
        assert f["scope"], f["id"]
        assert set(f["scope"]) <= scopes, f"{f['id']}: scope fuera de harness.json"


def test_no_hay_contador_de_intentos():
    # El numero de carpetas IT<n> ya es esa senal; un contador aparte se
    # desincroniza.
    for f in _features():
        assert "review_attempts" not in f, f["id"]


def test_como_mucho_una_feature_en_curso():
    en_curso = [f["id"] for f in _features() if f["status"] in {"spec_ready", "in_progress"}]
    assert len(en_curso) <= 1, en_curso
