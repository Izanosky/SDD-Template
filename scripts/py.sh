#!/usr/bin/env bash
# Lanza un script Python del harness con el primer interprete que ARRANQUE.
#   bash scripts/py.sh scripts/guard_secrets.py
#
# Por que existe: un hook cuyo interprete no existe (`python` en macOS/Linux
# suele faltar; en Windows `python3` puede ser un stub de la tienda) es un
# error NO bloqueante para Claude Code, asi que el comando que debia vigilar
# pasa. Aqui, sin interprete, se sale con 2: en un hook PreToolUse, 2 bloquea.
for c in "${PYTHON:-}" python3 python py; do
  [ -n "$c" ] || continue
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys" >/dev/null 2>&1; then
    exec "$c" "$@"
  fi
done
echo "scripts/py.sh: no hay un interprete de Python que arranque; se bloquea por seguridad." >&2
exit 2
