import json
import sys
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AGENTES = {"leader", "spec_author", "explorer",
           "implementer", "implementer_ui", "reviewer", "security_reviewer"}


def test_settings_es_json_valido():
    json.loads((RAIZ / ".claude/settings.json").read_text(encoding="utf-8"))


def test_existen_los_siete_agentes_y_solo_esos():
    presentes = {p.stem for p in (RAIZ / ".claude/agents").glob("*.md")}
    assert presentes == AGENTES


def test_los_agentes_declaran_modelo():
    for nombre in AGENTES:
        texto = (RAIZ / f".claude/agents/{nombre}.md").read_text(encoding="utf-8")
        assert texto.startswith("---"), nombre
        cabecera = texto.split("---")[1]
        assert "model:" in cabecera, nombre
        if nombre not in {"implementer", "implementer_ui"}:
            # Los roles que no escriben codigo declaran tools explicitamente.
            assert "tools:" in cabecera, nombre


def test_ponytail_no_se_inyecta_en_los_roles_del_harness():
    # Leccion: su hook SubagentStart metia "un solo check, nada de suites" en
    # revisores y spec_author, y duplicaba la precarga del implementer.
    import re
    patron = json.loads((RAIZ / ".claude/settings.json").read_text(encoding="utf-8")
                        )["env"]["PONYTAIL_SUBAGENT_MATCHER"]
    for rol in AGENTES - {"leader"}:
        assert not re.search(patron, rol, re.I), rol
    assert re.search(patron, "Explore", re.I)


def test_los_revisores_no_pueden_abrir_subagentes():
    # Cierra la unica ruta por la que el gasto podia multiplicarse sin que el
    # leader lo decidiera.
    for nombre in {"reviewer", "security_reviewer", "explorer"}:
        cabecera = (RAIZ / f".claude/agents/{nombre}.md").read_text(
            encoding="utf-8").split("---")[1]
        assert "Agent" not in cabecera, f"{nombre} puede multiplicar el gasto"


def _agente(nombre):
    return (RAIZ / f".claude/agents/{nombre}.md").read_text(encoding="utf-8")


def test_los_agentes_escriben_los_marcadores_que_lee_state_py():
    # state.py solo entiende estas cadenas: si un agente las cambia, el
    # despacho se rompe en silencio.
    for revisor in ("reviewer", "security_reviewer"):
        assert "Veredicto: APPROVED" in _agente(revisor), revisor
        assert "Veredicto: CHANGES_REQUESTED" in _agente(revisor), revisor
        assert "`Causa: codigo`" in _agente(revisor), revisor  # la lee metricas.py
    assert "## Sabotajes" in _agente("implementer")
    assert "SERVICIOS REALES" in _agente("spec_author")
    assert "Estado: APROBADO" in (RAIZ / ".claude/skills/arranque/SKILL.md").read_text(encoding="utf-8")
    assert "Aprobada por el humano: AAAA-MM-DD" in _agente("leader")


def test_los_hooks_pasan_por_el_lanzador_que_falla_cerrado():
    # Leccion: un hook cuyo interprete no existe deja pasar el comando.
    hooks = json.loads((RAIZ / ".claude/settings.json").read_text(encoding="utf-8"))["hooks"]
    guardia = hooks["PreToolUse"][0]["hooks"][0]["command"]
    assert "scripts/py.sh" in guardia and "guard_secrets.py" in guardia
    assert "compact" in hooks["SessionStart"][0]["matcher"]
    config = next(h for h in hooks["PreToolUse"] if "Edit" in h["matcher"])
    assert "scripts/py.sh" in config["hooks"][0]["command"]
    assert "guard_config.py" in config["hooks"][0]["command"]


def test_commit_y_push_piden_confirmacion():
    ask = json.loads((RAIZ / ".claude/settings.json").read_text(encoding="utf-8"))["permissions"]["ask"]
    # `git push` a secas tambien publica; `git push *` quiza no lo cubra.
    for regla in ("Bash(git commit *)", "Bash(git push *)", "Bash(git push)",
                  "PowerShell(git commit *)"):
        assert regla in ask


def test_cada_regla_ask_de_bash_tiene_su_gemela_en_powershell():
    # Leccion: los instaladores solo estaban completos para Bash, y en Windows
    # entraba una dependencia sin preguntar.
    ask = json.loads((RAIZ / ".claude/settings.json").read_text(encoding="utf-8"))["permissions"]["ask"]
    for regla in ask:
        if regla.startswith("Bash("):
            assert "PowerShell(" + regla[len("Bash("):] in ask, regla


def test_la_auditoria_automatica_exige_leader_y_confirmacion():
    # Las skills se activan solas; la auditoria es cara y un subagente no
    # puede preguntar al humano, asi que su descripcion pone el freno.
    cabecera = (RAIZ / ".claude/skills/auditoria-seguridad/SKILL.md").read_text(
        encoding="utf-8").split("---")[1]
    assert "humano" in cabecera and "subagente" in cabecera
    assert "/auditoria-seguridad" in _agente("implementer")


def test_los_sh_versionados_son_ejecutables():
    # Leccion: en Windows no se nota; en el CI Linux da "Permission denied".
    r = subprocess.run(["git", "ls-files", "-s"], capture_output=True, text=True, cwd=RAIZ)
    if r.returncode != 0:
        return  # aun no es un repo git
    for linea in r.stdout.splitlines():
        modo, *_, ruta = linea.split()
        if ruta.endswith(".sh") or ruta.startswith(".githooks/"):
            assert modo == "100755", f"{ruta} sin bit de ejecucion (git update-index --chmod=+x)"


def test_ninguna_skill_precargada_esta_oculta_del_todo():
    # Leccion (comprobado 2026-10-10): con "user-invocable-only" u "off" en
    # skillOverrides la precarga deja de funcionar en silencio; "name-only"
    # recorta el listado y la conserva.
    sys.path.insert(0, str(RAIZ / "scripts"))
    import skills
    overrides = json.loads((RAIZ / ".claude/settings.json").read_text(encoding="utf-8")).get(
        "skillOverrides", {})
    for skill in skills.precargadas():
        assert overrides.get(skill, "on") in {"on", "name-only"}, skill


def test_implementer_ui_remite_al_implementer_y_hace_capturas():
    ui = _agente("implementer_ui")
    assert ".claude/agents/implementer.md" in ui and "## Capturas" in ui
    assert "Capturas" in _agente("reviewer")
    assert "implementer_ui" in _agente("leader")
