#!/usr/bin/env python3
"""Compara dos progress/metrics.csv: ¿surtio efecto un cambio del harness?

    bash scripts/py.sh scripts/comparar.py BASE.csv [ACTUAL.csv]

ACTUAL es progress/metrics.csv si no se da. BASE suele ser la linea base de
otro proyecto o de antes del cambio (p. ej. la del piloto). Saca las cifras
que motivaron los cambios: primeras entregas aprobadas, rechazos por causa,
peso de las IT de correccion, pasadas del security_reviewer, coste por
feature y, con la columna `modelo`, el implementer por modelo.

Las columnas se leen por posicion: los ficheros antiguos (sin `skills` ni
`modelo`) valen igual. Con pocas features es un indicio, no una prueba.
"""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COLUMNAS = ("fecha", "feature", "it", "rol", "tokens", "cache_read", "minutos",
            "veredicto", "causa", "skills", "modelo")
IMPLEMENTERS = {"implementer", "implementer_ui"}


def leer(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8", newline="") as f:
        filas = list(csv.reader(f))
    datos = []
    for fila in filas[1:]:
        d = dict(zip(COLUMNAS, fila + [""] * (len(COLUMNAS) - len(fila))))
        if d["feature"] in {"-", "audit", ""} or not d["it"].isdigit():
            continue
        d["it"] = int(d["it"])
        for k in ("tokens", "cache_read", "minutos"):
            d[k] = int(d[k] or 0)
        datos.append(d)
    return datos


def _pct(a: float, b: float) -> str:
    return f"{100 * a / b:.0f} %" if b else "—"


def resumen(filas: list[dict]) -> dict[str, str]:
    # Ultimo veredicto de cada rol en cada IT (una reanudacion lo repite).
    veredictos = {(f["feature"], f["it"], f["rol"]): (f["veredicto"], f["causa"])
                  for f in filas if f["veredicto"]}
    rechazadas = {(fe, it) for (fe, it, _), (v, _) in veredictos.items()
                  if v == "CHANGES_REQUESTED"}
    revisadas = {(fe, it) for (fe, it, rol) in veredictos if rol == "reviewer"}
    # Primera entrega: IT revisada cuya anterior no fue rechazada (IT1 o un tramo nuevo).
    primeras = {k for k in revisadas if (k[0], k[1] - 1) not in rechazadas}
    correccion = {(f["feature"], f["it"]) for f in filas
                  if f["it"] >= 1 and (f["feature"], f["it"] - 1) in rechazadas}
    its = defaultdict(int)
    for f in filas:
        if f["rol"] in IMPLEMENTERS:
            its[f["feature"]] = max(its[f["feature"]], f["it"])
    n = len(its)
    causas = Counter(c or "sin causa" for (_, _, rol), (v, c) in veredictos.items()
                     if rol == "reviewer" and v == "CHANGES_REQUESTED")
    seguridad = [v for (_, _, rol), (v, _) in veredictos.items() if rol == "security_reviewer"]
    tokens = sum(f["tokens"] for f in filas)
    minutos = sum(f["minutos"] for f in filas)
    en_corr = [f for f in filas if (f["feature"], f["it"]) in correccion]
    r = {
        "Ejecuciones de agentes": str(len(filas)),
        "Features con implementación": str(n),
        "IT por feature (media)": f"{sum(its.values()) / n:.1f}" if n else "—",
        "Primeras entregas aprobadas por el reviewer":
            f"{len(primeras - rechazadas)}/{len(primeras)} ({_pct(len(primeras - rechazadas), len(primeras))})",
        "Rechazos del reviewer por causa":
            ", ".join(f"{c} {k}" for c, k in sorted(causas.items())) or "ninguno",
        "Pasadas del security_reviewer (rechazos)":
            f"{len(seguridad)} ({seguridad.count('CHANGES_REQUESTED')})",
        "Tokens nuevos por feature (media)": f"{tokens // n:,}".replace(",", ".") if n else "—",
        "Relecturas de caché por feature (media)":
            f"{sum(f['cache_read'] for f in filas) // n:,}".replace(",", ".") if n else "—",
        "Minutos por feature (media)": f"{minutos / n:.0f}" if n else "—",
        "Tokens en IT de corrección": _pct(sum(f["tokens"] for f in en_corr), tokens),
        "Minutos en IT de corrección": _pct(sum(f["minutos"] for f in en_corr), minutos),
    }
    # El implementer por modelo: primeras entregas que aprueba el reviewer.
    modelo_de = {(f["feature"], f["it"]): f["modelo"] or "sin dato"
                 for f in filas if f["rol"] in IMPLEMENTERS}
    for modelo in sorted(set(modelo_de.values())):
        suyas = {k for k in primeras if modelo_de.get(k) == modelo}
        ok = len(suyas - rechazadas)
        r[f"Implementer {modelo}: primeras aprobadas"] = f"{ok}/{len(suyas)} ({_pct(ok, len(suyas))})"
    return r


def tabla(base: dict[str, str], actual: dict[str, str]) -> str:
    lineas = ["| Métrica | Base | Actual |", "|---|---|---|"]
    for k in list(base) + [k for k in actual if k not in base]:
        lineas.append(f"| {k} | {base.get(k, '—')} | {actual.get(k, '—')} |")
    return "\n".join(lineas)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows no es UTF-8
    base = Path(argv[0])
    actual = Path(argv[1]) if len(argv) > 1 else RAIZ / "progress" / "metrics.csv"
    print(tabla(resumen(leer(base)), resumen(leer(actual))))
    print("\nCon pocas features, un indicio y no una prueba; mira también "
          "`Features con implementación`.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
