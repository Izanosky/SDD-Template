#!/usr/bin/env python3
"""Estado de despacho del harness. Lo invoca el leader en cada arranque.

Devuelve en una linea de JSON que feature toca y que accion. Deriva todo del
disco (feature_list.json, specs/<F>/tasks.md y progress/<F>/IT<n>/): no hay
ningun estado aparte que mantener sincronizado.

Los marcadores que lee son fijos (HARNESS.md, "Marcadores"): la linea
`Veredicto: APPROVED|CHANGES_REQUESTED`, el encabezado `## Sabotajes`,
`SERVICIOS REALES` en la cabecera de la task humana, `Estado: APROBADO` en
`progress/arranque.md` y `Aprobada por el humano: AAAA-MM-DD` en el
`design.md` de una spec.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Solo cuenta una linea propia de veredicto. Leccion: buscar la palabra en
# todo el fichero leia como rechazo un APPROVED que citaba la IT anterior.
_VEREDICTO = re.compile(r"^\W*Veredicto\W*(APPROVED|CHANGES_REQUESTED)\b", re.M | re.I)
_SABOTAJES = re.compile(r"^#{2,3}\s*Sabotajes\b", re.M)
# Con o sin negrita: una task sin `**` no puede quedar fuera del recuento.
_TASK_ABIERTA = re.compile(r"^\s*[-*]\s+\[ \]\s*\**\s*T\d+.*$", re.M)
_TASK_HUMANA = ("SERVICIOS REALES", "PRUEBA REAL")
_ARRANQUE_APROBADO = re.compile(r"^\W*Estado\W*APROBADO\b", re.M | re.I)
_SPEC_APROBADA = re.compile(r"^\W*Aprobada por el humano\W*\d{4}-\d{2}-\d{2}", re.M | re.I)


def _leer(ruta: Path) -> str:
    # errors="replace": un fichero guardado en ANSI no debe tumbar el despacho.
    return ruta.read_text(encoding="utf-8", errors="replace")


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
    """APPROVED, CHANGES_REQUESTED, o None si no hay linea de veredicto."""
    ruta = ROOT / "progress" / feature_id / f"IT{it}" / fichero
    if not ruta.is_file():
        return None
    m = _VEREDICTO.search(_leer(ruta))
    return m.group(1).upper() if m else None


# Paso 6 del implementer: sin la tabla de sabotajes no se gasta una revision.
def _tiene_sabotajes(feature_id: str, it: int) -> bool:
    carpeta = ROOT / "progress" / feature_id / f"IT{it}"
    return any(_SABOTAJES.search(_leer(carpeta / f))
               for f in ("impl.md", "evidence.md") if (carpeta / f).is_file())


# Iteraciones por tramos: tasks sin marcar que no son la humana.
def _tasks_pendientes(feature_id: str) -> int:
    ruta = ROOT / "specs" / feature_id / "tasks.md"
    if not ruta.is_file():
        return 0
    # "PRUEBA REAL" es el marcador de la plantilla anterior: sin el, una spec
    # vieja abria tramos para siempre con una task que nadie puede ejecutar.
    return sum(not any(m in t for m in _TASK_HUMANA) for t in _TASK_ABIERTA.findall(_leer(ruta)))


# La aprobacion es la marca del humano en design.md, no el campo status.
# Leccion: nadie tenia la orden de pasar la feature a in_progress y el
# despacho se quedaba pidiendo aprobacion para siempre.
def _spec_aprobada(feature_id: str) -> bool:
    ruta = ROOT / "specs" / feature_id / "design.md"
    return ruta.is_file() and bool(_SPEC_APROBADA.search(_leer(ruta)))


# Una auditoria sin cambios.md tiene hallazgos sin destino.
def _auditorias_pendientes() -> list[str]:
    carpeta = ROOT / "progress" / "audits"
    if not carpeta.is_dir():
        return []
    return sorted(d.name for d in carpeta.iterdir() if d.is_dir() and not (d / "cambios.md").is_file())


def next_action() -> dict:
    r = _despacho()
    pendientes = _auditorias_pendientes()
    return {**r, "audits_pending": pendientes} if pendientes else r


def _despacho() -> dict:
    # Del arranque salen los documentos que guian todo lo demas: sin el
    # aprobado no se escribe ninguna spec. Leccion: el stack decidido a
    # medias obligo a cambiar de framework a mitad de la primera feature.
    arranque = ROOT / "progress" / "arranque.md"
    if not (arranque.is_file() and _ARRANQUE_APROBADO.search(_leer(arranque))):
        return {"action": "ARRANQUE"}

    features = json.loads(_leer(ROOT / "feature_list.json"))
    activa = next((f for f in features if f["status"] != "done"), None)
    if activa is None:
        return {"action": "TODO_HECHO"}

    fid, estado = activa["id"], activa["status"]
    base = {"feature": fid, "status": estado, "scope": activa["scope"]}

    # Modo ligero: "sdd": false lo decide el humano al escribir la feature, y
    # sustituye a la spec y a su aprobacion. Los dos vetos se mantienen.
    if activa.get("sdd", True) is False:
        base["modo"] = "ligero"
    elif estado == "pending":
        return {**base, "iteration": 0, "action": "LANZAR_SPEC_AUTHOR"}
    elif estado == "spec_ready" and not _spec_aprobada(fid):
        return {**base, "iteration": 0, "action": "PEDIR_APROBACION_HUMANA"}

    it = _ultima_iteracion(fid)
    if it == 0:
        return {**base, "iteration": 1, "action": "CREAR_IT1_Y_LANZAR_IMPLEMENTER"}

    base = {**base, "iteration": it}
    carpeta = ROOT / "progress" / fid / f"IT{it}"

    # Una IT descartada (el humano cambia de stack o de rumbo con ella sin
    # revisar) cuenta como rechazada: la siguiente parte de ahi. Leccion: el
    # despacho pedia revisar una IT de un framework ya abandonado.
    if (carpeta / "descartada.md").is_file():
        review = security = "CHANGES_REQUESTED"
    else:
        # Leccion: una IT sin impl.md se despachaba como "revisar". Sin
        # impl.md el implementer se paro a medias: se reanuda el mismo agente.
        if not (carpeta / "impl.md").is_file():
            return {**base, "action": "REANUDAR_IMPLEMENTER"}
        if not _tiene_sabotajes(fid, it):
            return {**base, "action": "DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES"}
        review = _veredicto(fid, it, "review.md")
        security = _veredicto(fid, it, "security.md")

    # Primero el veto funcional, siempre. Cualquier rechazo (tambien de
    # seguridad) abre otra IT que vuelve a pasar por el reviewer: un arreglo
    # puede romper lo que estaba aprobado.
    if review is None:
        return {**base, "action": "LANZAR_REVIEWER"}
    if "CHANGES_REQUESTED" in (review, security):
        return {**base, "action": f"CREAR_IT{it + 1}_LANZAR_IMPLEMENTER_LUEGO_REVIEWER"}
    if _tasks_pendientes(fid):
        return {**base, "action": f"CREAR_IT{it + 1}_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO"}

    # Ultimo tramo (o modo ligero): el security_reviewer, solo sobre una IT que
    # el reviewer ya aprobo, y una vez por feature salvo que rechace.
    # Lecciones del piloto: en cada tramo paso 47 veces y rechazo 2; y en
    # paralelo con el reviewer revisaba IT que este iba a rechazar (el 51 %,
    # ~61 k tokens por pasada) para ahorrar unos 3 minutos.
    if security is None:
        return {**base, "action": "LANZAR_SECURITY_REVIEWER"}
    return {**base, "action": "LANZAR_IMPLEMENTER_CIERRE_MARCAR_DONE"}


if __name__ == "__main__":
    print(json.dumps(next_action(), ensure_ascii=False))
