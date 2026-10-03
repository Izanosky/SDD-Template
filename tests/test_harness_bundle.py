import os
import subprocess
import sys
import textwrap
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import harness_bundle  # noqa: E402


def test_harness_md_contiene_cada_fichero_tal_cual():
    # HARNESS.md debe bastar para construir el setup: su copia de cada fichero
    # no puede quedarse atras. Si falla: bash scripts/py.sh scripts/harness_bundle.py
    assert harness_bundle.main(["--check"]) == 0


def test_extraer_reconstruye_el_setup_identico(tmp_path):
    guia = (RAIZ / "HARNESS.md").read_text(encoding="utf-8")
    escritos = harness_bundle.extraer(guia, tmp_path)
    esperados = [p.relative_to(RAIZ).as_posix() for p in harness_bundle.ficheros()]
    assert sorted(escritos) == sorted(esperados)
    for ruta in esperados:
        original = harness_bundle._normal((RAIZ / ruta).read_text(encoding="utf-8"))
        assert (tmp_path / ruta).read_text(encoding="utf-8") == original, ruta


def test_un_cambio_sin_regenerar_se_detecta(tmp_path, monkeypatch):
    copia = tmp_path / "HARNESS.md"
    copia.write_text((RAIZ / "HARNESS.md").read_text(encoding="utf-8")
                     .replace("fichero=CLAUDE.md\n", "fichero=CLAUDE.md\nlinea vieja\n", 1),
                     encoding="utf-8")
    monkeypatch.setattr(harness_bundle, "GUIA", copia)
    assert harness_bundle.main(["--check"]) == 1


def test_solo_entra_el_harness_y_nunca_lo_ignorado(tmp_path, monkeypatch):
    # Leccion: recorrer el disco metia secretos ignorados y codigo del
    # producto en HARNESS.md, que se commitea.
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitignore").write_text("ignorado.md\n", encoding="utf-8")
    for ruta in ("docs/regla.md", "docs/ignorado.md", "src/app.py"):
        (tmp_path / ruta).parent.mkdir(exist_ok=True)
        (tmp_path / ruta).write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(harness_bundle, "RAIZ", tmp_path)
    rutas = [p.relative_to(tmp_path).as_posix() for p in harness_bundle.ficheros()]
    assert rutas == [".gitignore", "docs/regla.md"]


def test_el_extractor_del_paso_0_reconstruye_el_setup(tmp_path):
    # Es la via "solo con este documento": se ejecuta tal cual esta en la
    # seccion 3. Leccion: sin chmod, en Linux/macOS git ignoraba el pre-commit.
    guia = (RAIZ / "HARNESS.md").read_text(encoding="utf-8")
    codigo = textwrap.dedent(guia.split("python3 - <<'EOF'\n", 1)[1].split("  EOF\n", 1)[0])
    (tmp_path / "HARNESS.md").write_text(guia, encoding="utf-8")
    subprocess.run([sys.executable, "-c", codigo], cwd=tmp_path, check=True,
                   capture_output=True)
    for p in harness_bundle.ficheros():
        assert (tmp_path / p.relative_to(RAIZ)).is_file(), p
    if os.name != "nt":  # en Windows no hay bit de ejecucion que mirar
        assert os.access(tmp_path / ".githooks/pre-commit", os.X_OK)
