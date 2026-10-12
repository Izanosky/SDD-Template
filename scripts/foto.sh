#!/usr/bin/env bash
# Foto del arbol de trabajo: imprime el SHA de un arbol de git con todo lo que
# hay ahora (tambien lo no seguido; nunca lo ignorado), sin tocar el indice
# ni crear commits.
#
#   bash scripts/foto.sh > progress/<F>/IT<n>/base     (leader, al crear la IT)
#   git diff "$(cat progress/<F>/IT<n>/base)" "$(bash scripts/foto.sh)"
#                                                       (revisores: que cambio)
#
# Leccion del piloto: las IT no se commitean (el commit es del humano), asi que
# "el diff contra la IT anterior" no existia, y la base de la feature
# (`git rev-parse HEAD`) arrastraba la feature anterior sin commitear o fallaba
# en un repo sin commits.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
indice="$(mktemp)"
trap 'rm -f "$indice"' EXIT
# Partir del indice real solo acelera (reutiliza su cache); no lo modifica.
cp "$(git rev-parse --git-path index)" "$indice" 2>/dev/null || rm -f "$indice"
GIT_INDEX_FILE="$indice" git -c core.safecrlf=false add -A
GIT_INDEX_FILE="$indice" git write-tree
