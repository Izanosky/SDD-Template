#!/usr/bin/env python3
"""Mantiene la Parte II de HARNESS.md: el contenido literal de cada fichero.

HARNESS.md tiene que bastar para construir todo el setup sin el resto del
repositorio. Para que esa copia no se desincronice, se genera desde los
ficheros reales y un test (tests/test_harness_bundle.py) falla si difieren.

    bash scripts/py.sh scripts/harness_bundle.py            regenera la Parte II
    bash scripts/py.sh scripts/harness_bundle.py --check    sale con 1 si esta desfasada
    bash scripts/py.sh scripts/harness_bundle.py --extract DESTINO
                                                escribe todos los ficheros
"""
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GUIA = RAIZ / "HARNESS.md"
INICIO = "<!-- INICIO FICHEROS: generado por scripts/harness_bundle.py, no editar a mano -->"
FIN = "<!-- FIN FICHEROS -->"
VALLA = "~" * 7
# Solo el setup del harness. Leccion: recorrer el disco entero metia en este
# documento (que se commitea) los secretos, venv/ y el codigo del producto.
RUTAS = (
    ".claude/agents/", ".claude/skills/", ".claude/settings.json",
    ".gitattributes", ".githooks/", ".github/workflows/ci.yml", ".gitignore",
    ".gitleaks.toml", "CHECKPOINTS.md", "CLAUDE.md", "docs/",
    "feature_list.json", "harness.json", "init.sh", "plantillas/",
    "progress/audits/README.md", "progress/current.md", "progress/history.md",
    "progress/metrics.csv", "progress/para_la_plantilla.md", "scripts/",
    "specs/_plantilla/", "tests/",
)
BLOQUE = re.compile(rf"^{VALLA} fichero=(\S+)\n(.*?)^{VALLA}$", re.M | re.S)


def _normal(texto: str) -> str:
    return texto if texto.endswith("\n") else texto + "\n"


def ficheros() -> list[Path]:
    # git respeta .gitignore: lo ignorado (secretos, caches) nunca entra.
    # Orden por cadena, no por Path: en Windows Path ordena sin distinguir
    # mayusculas y en el CI Linux si, y el --check fallaria alli.
    salida = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=RAIZ, capture_output=True, encoding="utf-8", check=True).stdout
    rutas = {r for r in salida.split("\0") if r.startswith(RUTAS) and (RAIZ / r).is_file()}
    return [RAIZ / r for r in sorted(rutas)]


def parte_ii() -> str:
    trozos = [INICIO, ""]
    for p in ficheros():
        ruta = p.relative_to(RAIZ).as_posix()
        contenido = _normal(p.read_text(encoding="utf-8"))
        trozos += [f"### `{ruta}`", "", f"{VALLA} fichero={ruta}", contenido + VALLA, ""]
    trozos.append(FIN)
    return "\n".join(trozos)


def _guia_con(parte: str) -> str:
    texto = GUIA.read_text(encoding="utf-8")
    # El primer INICIO y el ULTIMO FIN: este mismo script va dentro de la
    # Parte II y contiene ambos marcadores en su texto.
    antes, _, resto = texto.partition(INICIO)
    _, _, despues = resto.rpartition(FIN)
    return antes + parte + despues


def extraer(guia: str, destino: Path) -> list[str]:
    escritos = []
    for ruta, cuerpo in BLOQUE.findall(guia):
        f = destino / ruta
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(cuerpo, encoding="utf-8", newline="\n")
        if ruta.endswith(".sh") or ruta.startswith(".githooks/"):
            f.chmod(0o755)
        escritos.append(ruta)
    return escritos


def main(args: list[str]) -> int:
    if args[:1] == ["--extract"] and len(args) == 2:
        for ruta in extraer(GUIA.read_text(encoding="utf-8"), Path(args[1])):
            print(ruta)
        return 0
    nueva = _guia_con(parte_ii())
    if args == ["--check"]:
        if nueva != GUIA.read_text(encoding="utf-8"):
            print("HARNESS.md desfasado: bash scripts/py.sh scripts/harness_bundle.py", file=sys.stderr)
            return 1
        return 0
    GUIA.write_text(nueva, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
