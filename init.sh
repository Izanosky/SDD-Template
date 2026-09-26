#!/usr/bin/env bash
# Dispatcher: lee el scope de la feature activa y delega en <scope>/init.sh.
#   ./init.sh            el scope de la feature activa (scripts/state.py)
#   ./init.sh --all      todos los scopes de harness.json
#   ./init.sh --dry-run  solo anuncia el scope
set -euo pipefail
cd "$(dirname "$0")"

DRY=0
ALL=0
case "${1:-}" in
  --dry-run) DRY=1 ;;
  --all)     ALL=1 ;;
esac

# El nombre del interprete cambia entre sistemas: Git Bash tiene `python`, un
# Linux normalmente solo `python3`. Se prueba cada candidato EJECUTANDOLO, no
# solo mirando el PATH: en Windows `python3` suele ser el stub de la Microsoft
# Store, que esta en el PATH y no arranca nada.
PY=""
for c in "${PYTHON:-}" python python3 py; do
  [ -n "$c" ] || continue
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys" >/dev/null 2>&1; then
    PY="$c"; break
  fi
done
[ -n "$PY" ] || { echo "No encuentro un interprete de Python en el PATH." >&2; exit 1; }

if [ "$ALL" -eq 1 ]; then
  SCOPES="$("$PY" -c 'import json; print(" ".join(json.load(open("harness.json", encoding="utf-8"))["scopes"]))')"
else
  SCOPES="$("$PY" scripts/state.py | "$PY" -c \
    'import json,sys; print(" ".join(json.load(sys.stdin).get("scope", [])))')"
fi

if [ -z "$SCOPES" ]; then
  echo "No hay feature activa con scope. Usa --all para verificar todo."
  exit 0
fi

echo "Scope activo: $SCOPES"
[ "$DRY" -eq 1 ] && exit 0

# Un stack sin init.sh se BLOQUEA, no se salta. Saltarlo daria un "TODO OK"
# que afirma que ese stack esta verificado cuando nadie lo ha comprobado.
for s in $SCOPES; do
  if [ ! -f "./$s/init.sh" ]; then
    echo "FALTA ./$s/init.sh — ese stack no se puede verificar todavia." >&2
    exit 1
  fi
done

for s in $SCOPES; do
  echo "=========== $s ==========="
  # `bash` explicito: no depende del bit de ejecucion (que en Windows no se
  # nota y en el CI Linux da "Permission denied"). Aun asi, ver
  # docs/verification.md: los .sh se versionan con +x.
  bash "./$s/init.sh"
done
echo "TODO OK"
