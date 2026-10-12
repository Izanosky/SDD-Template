import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import comparar  # noqa: E402

# F01: IT1 rechazada por tests, IT2 (correccion) aprobada, IT3 tramo nuevo
# aprobado a la primera. Formato antiguo (9 columnas) mezclado con el nuevo.
CSV = """fecha,feature,it,rol,tokens,cache_read,minutos,veredicto,causa
d,F01,1,implementer,100,0,10,,,,claude-sonnet
d,F01,1,reviewer,50,0,5,CHANGES_REQUESTED,tests
d,F01,2,implementer,30,0,3,,,,claude-opus
d,F01,2,reviewer,10,0,1,APPROVED,
d,F01,3,implementer,60,0,6,,,,claude-opus
d,F01,3,reviewer,20,0,2,APPROVED,
d,F01,3,security_reviewer,30,0,3,APPROVED,
d,-,0,explorer,999,0,9,,
"""


def _resumen(tmp_path):
    ruta = tmp_path / "m.csv"
    ruta.write_text(CSV, encoding="utf-8")
    return comparar.resumen(comparar.leer(ruta))


def test_primeras_entregas_y_peso_de_la_correccion(tmp_path):
    r = _resumen(tmp_path)
    # Primeras entregas: IT1 (rechazada) e IT3 (aprobada); IT2 es correccion.
    assert r["Primeras entregas aprobadas por el reviewer"] == "1/2 (50 %)"
    assert r["Rechazos del reviewer por causa"] == "tests 1"
    assert r["Tokens en IT de corrección"] == "13 %"  # 40 de 300
    assert r["IT por feature (media)"] == "3.0"
    assert r["Ejecuciones de agentes"] == "7"  # el explorer sin feature no cuenta


def test_implementer_por_modelo(tmp_path):
    r = _resumen(tmp_path)
    assert r["Implementer claude-sonnet: primeras aprobadas"] == "0/1 (0 %)"
    assert r["Implementer claude-opus: primeras aprobadas"] == "1/1 (100 %)"
