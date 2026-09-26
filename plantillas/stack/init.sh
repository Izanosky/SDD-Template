#!/usr/bin/env bash
# Verificacion ejecutable de UN stack. Copiar a <scope>/init.sh y rellenar.
# Falla a la primera (set -e). Cada paso DEBE poder fallar: tras escribirlo,
# plantar un fallo a proposito y comprobar que el codigo de salida no es 0.
#
# Recordatorios (lecciones reales):
#  - Versionar con bit de ejecucion: `git update-index --chmod=+x <scope>/init.sh`.
#    En Windows no se nota; en el CI Linux da "Permission denied".
#  - Instalar dependencias desde el LOCKFILE si faltan, para que un clon limpio
#    y el runner de CI funcionen igual que la maquina del autor.
#  - Comprobar que el comprobador de tipos comprueba DE VERDAD (ej.: en TS con
#    tsconfig "solution style", `tsc --noEmit` a secas no mira nada; hace falta
#    `tsc -b --noEmit`). Se demuestra inyectando un error de tipos.
#  - Escaneo de secretos con la config de la RAIZ y --redact.
set -euo pipefail
cd "$(dirname "$0")"
RAIZ="$(git rev-parse --show-toplevel)"

# 0. Dependencias desde el lockfile si faltan (clon limpio / CI).
# [ -d node_modules ] || npm ci            # ejemplo JS
# uv sync --frozen                          # ejemplo Python

echo "==> tests";        echo "<COMANDO_DE_TESTS>"         ; false  # sustituir y quitar `false`
echo "==> lint";         echo "<COMANDO_DE_LINT>"
echo "==> formato";      echo "<COMANDO_DE_FORMATO_EN_MODO_CHECK>"
echo "==> tipos";        echo "<COMANDO_DE_TIPOS_QUE_FALLE_DE_VERDAD>"
echo "==> build";        echo "<COMANDO_DE_BUILD_SI_APLICA>"
echo "==> secretos";     gitleaks detect --no-git --redact --config "$RAIZ/.gitleaks.toml" --source .
echo "==> dependencias"; echo "<AUDITORIA_DE_DEPENDENCIAS_CON_UMBRAL>"
echo "STACK OK"
