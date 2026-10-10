# Plantilla de harness SDD para Claude Code

Plantilla para desarrollar un proyecto con **Claude Code como equipo de
agentes con puertas de calidad**, siguiendo *Spec-Driven Development* (SDD):
ninguna feature se implementa sin una spec aprobada por un humano (salvo las
marcadas como ligeras), nada se da por hecho sin verificación ejecutable y
quien escribe el código no lo aprueba.

Agnóstica de lenguaje y stack. Lo que depende del proyecto está marcado
`<RELLENAR>`.

> **[HARNESS.md](HARNESS.md) basta por sí solo**: explica el porqué de cada
> pieza (Parte I) y contiene el contenido literal de todos los ficheros
> (Parte II), extraíbles con una orden. Este README es el resumen.

## Cómo funciona

```
feature_list.json          specs/<F>/                 progress/<F>/IT<n>/
   (qué hacer)       (requirements, design, tasks)   (impl, review, security)

 pending ──spec_author──> spec_ready ──HUMANO──> in_progress ──vetos──> done
                                        aprueba     │
                                                    ├─ implementer  → impl.md + evidence.md (## Sabotajes)
                                                    ├─ reviewer     → review.md   (Veredicto: …)
                                                    └─ security_rev → security.md (Veredicto: …)
```

- La sesión principal de Claude Code actúa como **`leader`**. Ejecuta
  `scripts/state.py`, que dice qué feature toca y qué acción, y lanza el
  subagente que corresponde. Los arreglos pequeños (sin comportamiento nuevo
  ni zonas sensibles) los hace él mismo.
- El **estado se deriva del disco**. Un rechazo abre una iteración nueva, y
  solo hay `done` con ambos veredictos `APPROVED` en la misma iteración.
- **Modo ligero** (`"sdd": false`): sin spec ni aprobación previa; se
  mantienen los dos vetos.
- `init.sh` es la puerta: tests, lint, formato, tipos, build, secretos y
  dependencias.

| Rol | Modelo | Qué hace |
|---|---|---|
| `leader` | el de la sesión | despacha, crea las IT, arreglos pequeños, métricas |
| `spec_author` | opus | escribe `specs/<F>/` |
| `explorer` | sonnet | investiga y deja hallazgos citados |
| `implementer` | sonnet | código, tests (TDD + sabotajes), cierre |
| `implementer_ui` | sonnet | lo mismo en los tramos de interfaz, con criterio de diseño y capturas |
| `reviewer` | opus | veto funcional, con mutantes y revisión de capturas |
| `security_reviewer` | opus | veto de seguridad; auditoría completa |

## Requisitos

- Claude Code y git.
- bash (en Windows, Git Bash).
- Python 3.10+ con pytest, solo para el harness, sea cual sea el lenguaje del
  proyecto.
- [gitleaks](https://github.com/gitleaks/gitleaks).
- Las toolchains de tus stacks.

## Puesta en marcha

```bash
cp -r harness-sdd-template mi-proyecto && cd mi-proyecto   # o: extrae HARNESS.md (sección 3)
git init
git config core.hooksPath .githooks
git add -A
git update-index --chmod=+x init.sh scripts/*.sh .githooks/pre-commit plantillas/stack/init.sh
grep -rn "<RELLENAR" .      # lo que hay que rellenar
```

La lista completa de qué rellenar y en qué orden está en la sección 3 de
HARNESS.md. Las decisiones las toma `/arranque` contigo, y no se empieza
ninguna feature hasta que la apruebes (`state.py` devuelve `ARRANQUE`):
producto, un mapa de todas las decisiones técnicas (arquitectura, stack y
librerías de backend y frontend, calidad, operación) que tú ajustas, y
bloque a bloque las propuestas, investigando solo lo que tú marques. Si hay
interfaz, después va `/direccion-visual`.

## Uso diario

1. Abre Claude Code en la raíz. El hook de sesión inyecta el estado y la
   sesión actúa como `leader`.
2. Dile que continúe. Tus puntos de intervención:
   - aprobar cada spec;
   - aprobar dependencias nuevas y cambios en `docs/` (cada cambio, con su
     entrada en `docs/CHANGELOG.md`);
   - ejecutar las tasks con servicios reales;
   - hacer los commits (Claude Code te los pide confirmar).
3. Skills del harness: `/arranque` (primer uso), `/direccion-visual` (antes
   de la primera pantalla, o para rediseñar), `/auditoria-seguridad` (con tu
   confirmación: es cara) y `/retrospectiva`.

## Skills opcionales

Ninguna es obligatoria: si una no está instalada, Claude Code la ignora sin
avisar, y `scripts/skills.py` (lo ejecuta el hook de sesión) te lo dice.
Instálalas en `~/.claude/skills/<nombre>/` después de leerlas: una skill son
instrucciones que el agente sigue con tus permisos.

| Skill | Origen y licencia | Rol | Cómo |
|---|---|---|---|
| `ponytail:ponytail` | plugin [ponytail](https://github.com/DietrichGebert/ponytail), MIT | `implementer`, `implementer_ui` | precargada |
| `property-based-testing` | [trailofbits/skills](https://github.com/trailofbits/skills), CC BY-SA 4.0 | `implementer`, `implementer_ui`, `reviewer` | precargada |
| `migration`, `surgical-patch`, `investigate-first` | skills de usuario enlazadas desde `~/.agents/skills/` (origen sin registrar en un `ORIGEN.md`) | `implementer` (las dos primeras); `leader` la tercera | precargadas / bajo demanda |
| `frontend-design:frontend-design` | plugin oficial `frontend-design` (Anthropic) | `implementer_ui`, `/direccion-visual` | precargada |
| `frontend-design-direction`, `make-interfaces-feel-better` | [affaan-m/ECC](https://github.com/affaan-m/ECC), MIT | `implementer_ui`, `/direccion-visual` | precargadas |
| `web-design-guidelines` | [vercel-labs/web-interface-guidelines](https://github.com/vercel-labs/web-interface-guidelines), MIT | `implementer_ui`, `reviewer` | precargada |
| `ui-ux-pro-max`, `redesign-existing-projects`, `pick-ui-library` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill), [emilkowalski/skills](https://github.com/emilkowalski/skills); MIT | `/direccion-visual` | las invoca la skill |
| `differential-review` | trailofbits/skills, CC BY-SA 4.0 | `security_reviewer` | precargada |
| `supply-chain-risk-auditor`, `variant-analysis`, `sharp-edges` | trailofbits/skills, CC BY-SA 4.0 | `security_reviewer` | las invoca por regla (lockfile, tras un hallazgo, auditoría) |
| `security-audit` | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill), MIT | `/auditoria-seguridad` | motor opcional; muchos agentes |
| `insecure-defaults` | trailofbits/skills, CC BY-SA 4.0 (plugin con workflow) | `/auditoria-seguridad` | `/insecure-defaults:audit` |
| `spec-to-code-compliance` | trailofbits/skills, CC BY-SA 4.0 (plugin con workflow) | `/retrospectiva` | al cerrar una fase; caro |
| `ponytail:ponytail-audit` | plugin ponytail, MIT | `/retrospectiva` | sobreingeniería |
| `council`, `architecture-decision-records` | affaan-m/ECC, MIT | `/arranque` y `leader` | decisiones de arquitectura disputadas; ADR en `docs/adr/` |
| `/deep-research` | workflow de serie de Claude Code | `/arranque` | preguntas de arquitectura con fuentes cruzadas; caro |
| `prd-securability-enhancement` | [OWASP/secure-agent-playbook](https://github.com/OWASP/secure-agent-playbook), CC BY 4.0 | `spec_author` | la precarga `/arranque` si hay usuarios o servidor |
| `vercel-react-best-practices`, `vercel-composition-patterns`, `vercel-react-view-transitions` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills), MIT | `implementer_ui` | las precarga `/arranque` si el stack es React |
| `modern-python` | trailofbits/skills, CC BY-SA 4.0 (solo la skill, sin sus hooks) | `implementer` | la precarga `/arranque` si el stack es Python |

Navegador para las capturas y el `explorer`: el plugin oficial `playwright`
(MCP). Si tu servidor de Playwright tiene otro nombre, cambia los nombres
`mcp__plugin_playwright_playwright__*` de `.claude/agents/explorer.md`.

**Cada skill del listado ocupa contexto en cada turno de cada agente.**
`skillOverrides` de `.claude/settings.json` deja en `name-only` las que el
harness usa por nombre (la precarga sigue funcionando) y en
`user-invocable-only` las que no usa (siguen en tu menú `/`). Una skill de
plugin no admite esto: se apunta en `skills_revisadas` de `harness.json` o
se desactiva el plugin para el proyecto (`enabledPlugins`).

Revisión puntual de la configuración `.claude/`:
`npx ecc-agentshield@<versión fijada> scan` ([AgentShield](https://github.com/affaan-m/agentshield),
MIT); ejecuta código descargado, así que con versión de más de 7 días.

## Comandos

```bash
bash scripts/py.sh scripts/state.py   # qué feature toca y qué acción (JSON)
bash init.sh                          # verifica el scope de la feature activa
bash init.sh --all                    # verifica todos los stacks (lo usa el CI)
bash init.sh --rapido                 # solo tests, lint, formato y tipos (vueltas de trabajo)
bash scripts/py.sh scripts/skills.py  # skills sin clasificar o que faltan
bash scripts/py.sh scripts/agent_tokens.py <agent_id> --run <n>   # consumo real de un agente
bash scripts/py.sh -m pytest tests/ -q   # tests del harness
bash scripts/py.sh scripts/harness_bundle.py  # regenera la Parte II de HARNESS.md
```

## Mantener la plantilla

Tras cambiar cualquier fichero, ejecuta `bash scripts/py.sh scripts/harness_bundle.py`.
`tests/test_harness_bundle.py` falla si HARNESS.md no coincide con los
ficheros, así que la guía nunca se queda atrás.
