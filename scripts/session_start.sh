#!/usr/bin/env bash
# SessionStart (startup, resume, clear, compact): inyecta el estado que los
# agentes ya dejaron en disco. Solo concatena; no interpreta nada.
#
# Corto a proposito: Claude Code recorta la salida de un hook a 10.000
# caracteres (deja un preview de 2.000). Por eso no vuelca los veredictos:
# da sus rutas y el leader lee lo que necesite.
set -uo pipefail
# La raiz es la del propio script, no la del directorio actual.
cd "$(dirname "$0")/.." || exit 0
PY="bash scripts/py.sh"

echo "=== state.py ==="
ESTADO="$($PY scripts/state.py 2>/dev/null || echo '{"error": "scripts/state.py fallo"}')"
echo "$ESTADO"

echo
echo "=== progress/current.md (primeras 80 lineas) ==="
if [ -f progress/current.md ]; then head -n 80 progress/current.md; else echo "(no existe)"; fi

FEATURE="$(printf '%s' "$ESTADO" | $PY -c \
  'import json,sys; print(json.load(sys.stdin).get("feature",""))' 2>/dev/null || true)"
[ -z "$FEATURE" ] && exit 0
IT="$(ls -d "progress/$FEATURE"/IT* 2>/dev/null | sort -V | tail -1 || true)"
[ -z "$IT" ] && exit 0

echo
echo "=== Ultima iteracion: $IT ==="
# evidence.md no se lista: el leader no lo lee nunca.
for f in impl.md review.md security.md; do
  [ -f "$IT/$f" ] && echo "$IT/$f"
done
exit 0
