import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts import state  # noqa: E402

F = {"id": "F01", "title": "t", "status": "in_progress", "sdd": True, "scope": ["a"]}
IMPL = ("progress/F01/IT1/impl.md", "informe\n## Sabotajes\nN/A: solo texto")


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


def test_carpeta_it_sin_impl_reanuda_implementer_no_reviewer(tmp_path, monkeypatch):
    # Leccion: una IT vacia se despachaba como LANZAR_REVIEWER.
    _preparar(tmp_path, monkeypatch, [F])
    (tmp_path / "progress/F01/IT1").mkdir(parents=True)
    assert state.next_action()["action"] == "REANUDAR_IMPLEMENTER"


def test_impl_sin_sabotajes_vuelve_al_implementer(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [("progress/F01/IT1/impl.md", "informe")])
    assert state.next_action()["action"] == "DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES"


def test_sabotajes_en_evidence_cuentan(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        ("progress/F01/IT1/impl.md", "informe"),
        ("progress/F01/IT1/evidence.md", "## Sabotajes\n| linea | test |"),
    ])
    assert state.next_action()["action"] == "LANZAR_REVIEWER"


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
    assert state.next_action()["action"] == "LANZAR_IMPLEMENTER_CIERRE_MARCAR_DONE"


def test_ambos_approved_con_tramo_pendiente_abre_siguiente_it(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
        ("progress/F01/IT1/security.md", "Veredicto: APPROVED"),
        ("specs/F01/tasks.md", "- [x] **T1 — a**\n- [ ] **T2 — b**\n"
                               "- [ ] **T3 — UNICA TASK CON SERVICIOS REALES**\n"),
    ])
    assert state.next_action()["action"] == "CREAR_IT2_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO"


# "PRUEBA REAL": specs escritas con la plantilla anterior.
@pytest.mark.parametrize("cabecera", ["UNICA TASK CON SERVICIOS REALES",
                                      "PRUEBA REAL · la ejecuta el humano"])
def test_solo_falta_la_task_humana_cierra(tmp_path, monkeypatch, cabecera):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
        ("progress/F01/IT1/security.md", "Veredicto: APPROVED"),
        ("specs/F01/tasks.md", f"- [x] **T1 — a**\n- [ ] **T2 — {cabecera}**\n"),
    ])
    assert state.next_action()["action"] == "LANZAR_IMPLEMENTER_CIERRE_MARCAR_DONE"


def test_auditoria_sin_cambios_se_avisa(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "done"}], [
        ("progress/audits/2026-01-01/informe.md", "x"),
        ("progress/audits/2026-02-01/informe.md", "x"),
        ("progress/audits/2026-02-01/cambios.md", "x"),
    ])
    assert state.next_action() == {"action": "TODO_HECHO", "audits_pending": ["2026-01-01"]}


def test_coge_la_iteracion_mas_alta(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: CHANGES_REQUESTED"),
        ("progress/F01/IT2/impl.md", IMPL[1]),
        ("progress/F01/IT2/review.md", "Veredicto: APPROVED"),
    ])
    r = state.next_action()
    assert r["iteration"] == 2
    assert r["action"] == "LANZAR_SECURITY_REVIEWER"


def test_todo_done(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "done"}])
    assert state.next_action()["action"] == "TODO_HECHO"


def test_approved_que_cita_un_rechazo_anterior_sigue_aprobado(tmp_path, monkeypatch):
    # Leccion: buscar la palabra en todo el fichero abria una IT de mas.
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md",
         "**Veredicto:** APPROVED\n\nLa IT anterior fue CHANGES_REQUESTED por tests."),
    ])
    assert state.next_action()["action"] == "LANZAR_SECURITY_REVIEWER"


def test_sin_linea_de_veredicto_no_hay_veredicto(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL, ("progress/F01/IT1/review.md", "Borrador: todo parece APPROVED"),
    ])
    assert state.next_action()["action"] == "LANZAR_REVIEWER"


def test_task_de_tramo_sin_negrita_cuenta_como_pendiente(tmp_path, monkeypatch):
    # Leccion: sin negrita la regex no la veia y la feature se cerraba sin el tramo.
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
        ("progress/F01/IT1/security.md", "Veredicto: APPROVED"),
        ("specs/F01/tasks.md", "- [x] T1 — a\n- [ ] T2 — tramo siguiente\n"),
    ])
    assert state.next_action()["action"] == "CREAR_IT2_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO"


def test_mencionar_sabotajes_no_es_tener_la_seccion(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        ("progress/F01/IT1/impl.md", "Falta la seccion ## Sabotajes, la hare luego"),
    ])
    assert state.next_action()["action"] == "DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES"


def test_fichero_no_utf8_no_tumba_el_despacho(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [IMPL])
    (tmp_path / "progress/F01/IT1/review.md").write_bytes(b"Veredicto: APPROVED\n\x97 cp1252")
    assert state.next_action()["action"] == "LANZAR_SECURITY_REVIEWER"


def test_modo_ligero_salta_spec_y_aprobacion(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "pending", "sdd": False}])
    r = state.next_action()
    assert r["action"] == "CREAR_IT1_Y_LANZAR_IMPLEMENTER"
    assert r["modo"] == "ligero"


def test_modo_ligero_mantiene_los_dos_vetos(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "pending", "sdd": False}], [
        IMPL, ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
    ])
    assert state.next_action()["action"] == "LANZAR_SECURITY_REVIEWER"
