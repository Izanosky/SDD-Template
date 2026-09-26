#!/usr/bin/env python3
"""Estado de despacho del harness. Lo invoca el leader en cada arranque.

Devuelve en una linea de JSON que feature toca y que accion. Deriva todo del
disco (feature_list.json y las carpetas progress/<F>/IT<n>/): no hay ningun
estado aparte que mantener sincronizado.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _ultima_iteracion(feature_id: str) -> int:
    carpeta = ROOT / "progress" / feature_id
    if not carpeta.is_dir():
        return 0
    its = []
    for d in carpeta.iterdir():
        m = re.fullmatch(r"IT(\d+)", d.name)
        if m and d.is_dir():
            its.append(int(m.group(1)))
    return max(its, default=0)


def _veredicto(feature_id: str, it: int, fichero: str) -> str | None:
    """APPROVED, CHANGES_REQUESTED, o None si el fichero no existe."""
    ruta = ROOT / "progress" / feature_id / f"IT{it}" / fichero
    if not ruta.is_file():
        return None
    texto = ruta.read_text(encoding="utf-8")
    if "CHANGES_REQUESTED" in texto:
        return "CHANGES_REQUESTED"
    if "APPROVED" in texto:
        return "APPROVED"
    return None


def next_action() -> dict:
    features = json.loads((ROOT / "feature_list.json").read_text(encoding="utf-8"))
    activa = next((f for f in features if f["status"] != "done"), None)
    if activa is None:
        return {"action": "TODO_HECHO"}

    fid, estado = activa["id"], activa["status"]
    base = {"feature": fid, "status": estado, "scope": activa["scope"]}

    if estado == "pending":
        return {**base, "iteration": 0, "action": "LANZAR_SPEC_AUTHOR"}
    if estado == "spec_ready":
        return {**base, "iteration": 0, "action": "PEDIR_APROBACION_HUMANA"}

    it = _ultima_iteracion(fid)
    if it == 0:
        return {**base, "iteration": 1, "action": "CREAR_IT1_Y_LANZAR_IMPLEMENTER"}

    base = {**base, "iteration": it}

    # Leccion: una carpeta IT<n> recien creada (o de una sesion interrumpida)
    # sin impl.md no se revisa: no hay nada que revisar. Sin esta guarda el
    # despacho pedia LANZAR_REVIEWER sobre una carpeta vacia.
    if not (ROOT / "progress" / fid / f"IT{it}" / "impl.md").is_file():
        return {**base, "action": f"LANZAR_IMPLEMENTER_EN_IT{it}"}

    review = _veredicto(fid, it, "review.md")
    security = _veredicto(fid, it, "security.md")

    if review is None:
        return {**base, "action": "LANZAR_REVIEWER"}
    if review == "CHANGES_REQUESTED":
        return {**base, "action": f"CREAR_IT{it + 1}_LANZAR_IMPLEMENTER_LUEGO_REVIEWER"}
    if security is None:
        return {**base, "action": "LANZAR_SECURITY_REVIEWER"}
    if security == "CHANGES_REQUESTED":
        # Un fix de seguridad puede alterar comportamiento ya aprobado
        # funcionalmente, asi que se re-verifica el reviewer ANTES que seguridad.
        return {
            **base,
            "action": f"CREAR_IT{it + 1}_LANZAR_IMPLEMENTER_LUEGO_REVIEWER_Y_SECURITY",
        }
    return {**base, "action": "LANZAR_IMPLEMENTER_PASO_8_MARCAR_DONE"}


if __name__ == "__main__":
    print(json.dumps(next_action(), ensure_ascii=False))
