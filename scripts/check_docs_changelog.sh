#!/usr/bin/env bash
# Regla dura: todo cambio en docs/ se documenta en docs/CHANGELOG.md.
#   bash scripts/check_docs_changelog.sh            lo preparado para commit (pre-commit)
#   bash scripts/check_docs_changelog.sh A..B       un rango de commits (CI)
# Sin la entrada, nadie sabe que una regla cambio ni por que, y los agentes
# siguen trabajando con la vieja.
set -euo pipefail
if [ $# -gt 0 ]; then
  cambios="$(git diff --name-only "$1")"
else
  cambios="$(git diff --cached --name-only)"
fi
docs="$(printf '%s\n' "$cambios" | grep '^docs/' | grep -vx 'docs/CHANGELOG\.md' || true)"
if [ -n "$docs" ] && ! printf '%s\n' "$cambios" | grep -qx 'docs/CHANGELOG\.md'; then
  echo "Cambios en docs/ sin entrada en docs/CHANGELOG.md:" >&2
  echo "$docs" >&2
  exit 1
fi
