# Plantilla de harness SDD

Plantilla para desarrollar un proyecto con **Claude Code como equipo de
agentes con puertas de calidad**, siguiendo *Spec-Driven Development* (SDD):
ninguna feature se implementa sin una spec aprobada por un humano, nada se da
por hecho sin verificación ejecutable y quien escribe el código no lo aprueba.

Es agnóstica de lenguaje y stack. Todo lo que depende del proyecto está
marcado como `<RELLENAR>` o `<...>`.

> La guía completa (principios, proceso, seguridad, lecciones aprendidas y
> plantillas de texto) está en **[HARNESS.md](HARNESS.md)**. Este README es el
> resumen práctico para ponerla en marcha.

---

## Cómo funciona, en una imagen

```
feature_list.json          specs/<F>/                 progress/<F>/IT<n>/
   (qué hacer)       (requirements, design, tasks)   (impl, review, security)

 pending ──spec_author──> spec_ready ──HUMANO──> in_progress ──vetos──> done
                                        aprueba     │
                                                    ├─ implementer  → impl.md + evidence.md
                                                    ├─ reviewer     → review.md   (APPROVED / CHANGES_REQUESTED)
                                                    └─ security_rev → security.md (APPROVED / CHANGES_REQUESTED)
```

- **`leader`** (la sesión principal de Claude Code) orquesta: ejecuta
  `python scripts/state.py`, que dice qué feature toca y qué acción, y lanza
  el subagente correspondiente. Nunca escribe código.
- El **estado se deriva del disco** (`feature_list.json` + carpetas
  `progress/<F>/IT<n>/`), no se mantiene a mano.
- Si un revisor rechaza, se crea una nueva iteración `IT<n+1>`. Una feature
  solo pasa a `done` cuando `review.md` y `security.md` de la **misma**
  iteración son `APPROVED`.
- `./init.sh` (tests, lint, formato, tipos, build, secretos, dependencias) es
  la puerta: "funciona" solo cuenta si `init.sh` sale en verde.

### Los seis roles (`.claude/agents/`)

| Rol | Modelo | Qué hace | Nunca |
|---|---|---|---|
| `leader` | sonnet | Decide qué rol lanzar, crea las carpetas `IT<n>` | Escribir código o specs, marcar `done` |
| `spec_author` | opus | Escribe `specs/<F>/` | Escribir código o tests |
| `explorer` | sonnet | Investiga y deja hallazgos en `progress/explore_*.md` | Decidir, escribir código |
| `implementer` | sonnet | Código, tests (TDD), `impl.md`, `evidence.md`, cierre | Aprobarse a sí mismo |
| `reviewer` | opus | Veto funcional (con mutantes) | Editar código |
| `security_reviewer` | opus | Veto de seguridad, última puerta | Editar código |

---

## Requisitos

- [Claude Code](https://claude.com/claude-code)
- Git y **bash** (en Windows, Git Bash)
- Python 3.10+ con `pytest`
- [gitleaks](https://github.com/gitleaks/gitleaks) (lo exige el hook de
  pre-commit y los `init.sh` de cada stack)
- Las toolchains de tus stacks

---

## Puesta en marcha

### 1. Copiar la plantilla y crear el repo

```bash
cp -r harness-sdd-template mi-proyecto && cd mi-proyecto
git init
git config core.hooksPath .githooks        # activa el pre-commit (una vez por clon)
git add -A
git update-index --chmod=+x init.sh scripts/session_start.sh .githooks/pre-commit plantillas/stack/init.sh
```

### 2. Rellenar lo específico del proyecto

| Fichero | Qué poner |
|---|---|
| `harness.json` | `proyecto`, `scopes` (una carpeta por stack: `backend`, `frontend`…) y `secretos` (**nombres** de las variables secretas, nunca valores) |
| `feature_list.json` | Features en orden de prioridad (el orden **es** la prioridad). La primera, la más pequeña que cruce toda la arquitectura |
| `<scope>/init.sh` | Uno por stack, copiado de `plantillas/stack/init.sh`, con los comandos reales. Comprueba que cada paso **sabe fallar** |
| `CLAUDE.md`, `AGENTS.md`, `CHECKPOINTS.md` | Desde las plantillas del Anexo B de `HARNESS.md` |
| `docs/` | `specs.md`, `verification.md`, `security.md`, `principios.md`, `architecture.md` y `docs/<stack>/conventions.md` (tabla en la sección 1 de `HARNESS.md`) |
| `.gitleaks.toml` | Una regla por cada secreto con formato reconocible |
| `.github/workflows/ci.yml` | Toolchains de cada stack con versión fijada |

La checklist completa y el orden recomendado están en la **sección 1 de
`HARNESS.md`**; las decisiones que conviene tomar antes de la primera spec,
en el **Anexo C**.

> Atajo: abre Claude Code en el repo y pídele *"Monta el harness siguiendo
> HARNESS.md"*.

### 3. Comprobar que todo está en verde y hacer el primer commit

```bash
python -m pytest tests/ -q     # tests del propio harness
./init.sh --all                # verificación de todos los stacks
git commit -m "chore: harness inicial"
```

Mientras un scope de `harness.json` no tenga su `<scope>/init.sh`,
`./init.sh` falla con `FALTA ./<scope>/init.sh`: es intencionado (un stack
sin verificar no puede dar verde).

---

## Uso diario

1. Abre Claude Code en la raíz del repo. Por `CLAUDE.md` actúa como `leader`
   y lo primero que hace es `python scripts/state.py`.
2. Dile que continúe. El leader lanzará el rol que toque según la acción:

   | `action` de `state.py` | Qué pasa |
   |---|---|
   | `LANZAR_SPEC_AUTHOR` | Se escribe la spec de la feature |
   | `PEDIR_APROBACION_HUMANA` | **Te toca a ti**: el leader resume la spec y sus decisiones abiertas con recomendación |
   | `CREAR_IT1_Y_LANZAR_IMPLEMENTER` | Empieza la implementación |
   | `LANZAR_IMPLEMENTER_EN_IT<n>` | Retoma una iteración interrumpida |
   | `LANZAR_REVIEWER` / `LANZAR_SECURITY_REVIEWER` | Vetos, en ese orden |
   | `CREAR_IT<n>_…` | Rechazo: nueva iteración con los cambios pedidos |
   | `LANZAR_IMPLEMENTER_PASO_8_MARCAR_DONE` | Cierre: `done`, `history.md`, `current.md` |
   | `TODO_HECHO` | No queda nada pendiente |

3. **Tus puntos de intervención:**
   - Aprobar (o corregir) cada spec en `spec_ready`. Tras aprobarla, la
     feature pasa a `in_progress`.
   - Aprobar dependencias nuevas y cambios en `docs/` o en las reglas del
     harness.
   - Ejecutar las tasks de prueba con servicios reales (última task de la
     spec, con pasos copiables).
   - Hacer los commits: los agentes no hacen `git commit`.

Pendientes y contexto de la sesión: `progress/current.md`. Historial de
features cerradas: `progress/history.md`.

---

## Comandos

```bash
python scripts/state.py      # qué feature toca y qué acción (JSON)
./init.sh                    # verifica el scope de la feature activa
./init.sh --all              # verifica todos los scopes de harness.json
./init.sh --dry-run          # solo muestra el scope activo
python -m pytest tests/ -q   # tests del harness
bash scripts/session_start.sh  # estado + current.md + última iteración
```

---

## Qué hay en la plantilla

```
.
├── HARNESS.md                guía completa (léela)
├── harness.json              proyecto, scopes y nombres de secretos   <RELLENAR>
├── feature_list.json         features: id, title, status, sdd, scope, acceptance   <RELLENAR>
├── init.sh                   dispatcher: delega en <scope>/init.sh
├── plantillas/stack/init.sh  plantilla de verificación por stack   <RELLENAR>
├── specs/_plantilla/         requirements.md, design.md, tasks.md
├── progress/                 current.md (estado vivo), history.md (append-only)
├── scripts/
│   ├── state.py              tabla de despacho
│   ├── session_start.sh      hook: muestra el estado tras /clear
│   └── guard_secrets.py      hook: bloquea comandos de shell que sacan secretos
├── tests/                    tests DEL HARNESS (no del producto)
├── .claude/
│   ├── settings.json         deny de .env/*.pem/*.key + hooks
│   └── agents/               los seis roles
├── .githooks/pre-commit      gitleaks sobre el índice (falla si falta gitleaks)
├── .github/workflows/ci.yml  secretos en el historial + tests + init.sh   <RELLENAR toolchains>
├── .gitleaks.toml            reglas de secretos   <RELLENAR>
└── .gitignore, .gitattributes
```

## Seguridad de secretos

Cuatro capas para que un secreto nunca pase por el contexto de un agente ni
llegue a un commit:

1. **Permisos** en `.claude/settings.json`: los agentes no pueden leer ni
   editar `.env*`, `*.pem` ni `*.key`.
2. **Hook `guard_secrets.py`**: bloquea comandos que leen `.env`, expanden un
   secreto de `harness.json` (`$X`, `$env:X`, `%X%`, `os.environ`,
   `process.env`) o vuelcan el entorno (`env`, `printenv`, `set`…).
3. **Pre-commit** con gitleaks sobre lo que vas a commitear.
4. **CI** escanea el historial completo.

Los secretos viven en el panel de variables de cada servicio o en variables
de entorno del sistema, nunca en el repo. Documenta sus nombres en
`.env.example`, sin valores.
