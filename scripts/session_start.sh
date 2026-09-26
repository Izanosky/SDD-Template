#!/usr/bin/env bash
# SessionStart: muestra el estado que los agentes ya dejaron escrito en disco.
# No genera contenido ni interpreta nada: solo concatena. Por eso no puede
# quedar desincronizado ni depende de que ningun agente lo mantenga.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 0

echo "=== ESTADO DE DESPACHO ==="
python scripts/state.py || echo "(scripts/state.py fallo)"

echo
echo "=== progress/current.md ==="
if [ -f progress/current.md ]; then cat progress/current.md; else echo "(no existe)"; fi

FEATURE="$(python scripts/state.py 2>/dev/null | python -c \
  'import json,sys; print(json.load(sys.stdin).get("feature",""))' 2>/dev/null || true)"
[ -z "$FEATURE" ] && exit 0

IT="$(ls -d "progress/$FEATURE"/IT* 2>/dev/null | sort -V | tail -1 || true)"
[ -z "$IT" ] && exit 0

echo
echo "=== Ultima iteracion: $IT ==="
for f in impl.md review.md security.md; do
  if [ -f "$IT/$f" ]; then echo "--- $f ---"; cat "$IT/$f"; fi
done

# evidence.md NO se muestra: el leader no lo lee nunca.
exit 0
