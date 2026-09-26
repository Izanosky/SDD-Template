import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts import state  # noqa: E402

F = {"id": "F01", "title": "t", "status": "in_progress", "sdd": True, "scope": ["a"]}
IMPL = ("progress/F01/IT1/impl.md", "informe")


def _preparar(tmp_path, monkeypatch, features, ficheros=()):
    (tmp_path / "feature_list.json").write_text(json.dumps(features), encoding="utf-8")
    for ruta, contenido in ficheros:
        f = tmp_path / ruta
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(contenido, encoding="utf-8")
    monkeypatch.setattr(state, "ROOT", tmp_path)


def test_pending_lanza_spec_author(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "pending"}])
    assert state.next_action()["action"] == "LANZAR_SPEC_AUTHOR"


def test_spec_ready_pide_aprobacion_humana(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "spec_ready"}])
    assert state.next_action()["action"] == "PEDIR_APROBACION_HUMANA"


def test_in_progress_sin_iteraciones_crea_it1(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F])
    r = state.next_action()
    assert r["action"] == "CREAR_IT1_Y_LANZAR_IMPLEMENTER"
    assert r["iteration"] == 1


def test_carpeta_it_sin_impl_lanza_implementer_no_reviewer(tmp_path, monkeypatch):
    # Leccion: una IT vacia se despachaba como LANZAR_REVIEWER.
    _preparar(tmp_path, monkeypatch, [F])
    (tmp_path / "progress/F01/IT1").mkdir(parents=True)
    assert state.next_action()["action"] == "LANZAR_IMPLEMENTER_EN_IT1"


def test_impl_sin_review_lanza_reviewer(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [IMPL])
    assert state.next_action()["action"] == "LANZAR_REVIEWER"


def test_review_approved_sin_security_lanza_security(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F],
              [IMPL, ("progress/F01/IT1/review.md", "Veredicto: APPROVED")])
    assert state.next_action()["action"] == "LANZAR_SECURITY_REVIEWER"


def test_review_rechazado_crea_siguiente_it(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F],
              [IMPL, ("progress/F01/IT1/review.md", "Veredicto: CHANGES_REQUESTED")])
    assert state.next_action()["action"] == "CREAR_IT2_LANZAR_IMPLEMENTER_LUEGO_REVIEWER"


def test_security_rechazado_reverifica_ambos(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
        ("progress/F01/IT1/security.md", "Veredicto: CHANGES_REQUESTED"),
    ])
    assert state.next_action()["action"] == \
        "CREAR_IT2_LANZAR_IMPLEMENTER_LUEGO_REVIEWER_Y_SECURITY"


def test_ambos_approved_cierra(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
        ("progress/F01/IT1/security.md", "Veredicto: APPROVED"),
    ])
    assert state.next_action()["action"] == "LANZAR_IMPLEMENTER_PASO_8_MARCAR_DONE"


def test_coge_la_iteracion_mas_alta(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: CHANGES_REQUESTED"),
        ("progress/F01/IT2/impl.md", "informe"),
        ("progress/F01/IT2/review.md", "Veredicto: APPROVED"),
    ])
    r = state.next_action()
    assert r["iteration"] == 2
    assert r["action"] == "LANZAR_SECURITY_REVIEWER"


def test_todo_done(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "done"}])
    assert state.next_action()["action"] == "TODO_HECHO"
