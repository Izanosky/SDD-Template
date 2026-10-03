# Harness SDD para Claude Code

**Este documento basta por sí solo.** Con él se entiende qué es el harness,
por qué está hecho así y cómo funciona cada pieza, y se construye el setup
completo sin ningún otro fichero:

- **Parte I** (secciones 0-12): el porqué, el montaje, el despacho, las
  reglas y las lecciones.
- **Parte II**: el contenido literal de **cada fichero** del setup: agentes,
  skills, scripts, hooks, tests, `docs/` y plantillas. Se extrae con una
  orden (sección 3). Un test garantiza que coincide con los ficheros reales.

Ningún agente carga este documento mientras trabaja: los agentes leen los
ficheros pequeños que salen de la Parte II. Así su tamaño no cuesta tokens
en el día a día.

Agnóstico de lenguaje y de stack. Lo que depende del proyecto está marcado
`<RELLENAR>`. Probado en un proyecto real de tamaño medio (backend + worker
+ web, varios servicios en la nube, decenas de iteraciones medidas).

## Índice

**Parte I**

0. Qué es y por qué funciona
1. ¿Sigue vigente? (octubre de 2026)
2. Reglas duras
3. Montaje (desde la carpeta o solo desde este documento)
4. Qué lee cada uno, y cuándo
5. Roles
6. El ciclo de una feature
7. Despacho: `state.py`
8. Seguridad del propio harness
9. Coste y contexto
10. Adaptarlo a tu proyecto
11. Mantener el harness (y este documento)
12. Lecciones y dónde quedaron
- Anexo A: inventario de ficheros
- Anexo B: encargo tipo del leader
- Anexo C: decisiones antes de la primera spec

**Parte II** — ficheros completos

---

# Parte I

## 0. Qué es y por qué funciona

Un **harness** convierte "un agente que escribe código" en "un equipo con
puertas de calidad": seis roles (subagentes de Claude Code), un proceso con
aprobación humana, verificación ejecutable y un estado derivado del disco.
Se trabaja con **SDD** (Spec-Driven Development): ninguna feature se
implementa sin una spec escrita y aprobada, salvo las que el humano marca
como ligeras.

1. **Nada se declara hecho: se demuestra.** `init.sh` (tests, lint, formato,
   tipos, build, secretos, dependencias) es la puerta.
2. **Quien escribe no aprueba.** El `implementer` escribe; `reviewer` y
   `security_reviewer` vetan por separado. Ambos `APPROVED` en la misma
   iteración, o no hay `done`.
3. **Humano en la puerta de diseño** (y en la de los servicios reales).
4. **Estado derivado, no mantenido**: `scripts/state.py` calcula qué toca a
   partir del disco. No hay contadores que sincronizar.
5. **Historial inmutable**: cada iteración es una carpeta nueva.
6. **Divulgación progresiva**: cada rol lee solo lo que necesita.
7. **Lo que debe cumplirse siempre, en código** (hooks, permisos, tests,
   pre-commit, CI), no en prosa: una instrucción es un consejo para el
   modelo; un hook es una garantía.
8. **Las lecciones se convierten en reglas o en tests**, con fecha, y todo
   cambio de regla queda registrado (regla del `docs/CHANGELOG.md`).
9. **Lo pequeño, sin ceremonia**: modo ligero y arreglos pequeños del leader.

---

## 1. ¿Sigue vigente? (octubre de 2026)

**Sí, con matices.** Consultado el 2026-10-03:

- **SDD es práctica común.** Spec Kit (GitHub), Kiro (AWS), Tessl, OpenSpec,
  BMAD y el propio Claude Code tienen su versión ([augmentcode][a1],
  [thebcms][a2]). La estructura de este harness (requisitos EARS → diseño →
  tasks → implementación) es la misma que la de esas herramientas.
- **Críticas conocidas** ([Böckeler, martinfowler.com, 2025-10][f1];
  [Thoughtworks Radar vol. 34, anillo "Assess"][t1]):
  - es un mazo para bugs pequeños;
  - genera markdown verboso que nadie quiere revisar;
  - los agentes ignoran partes de la spec;
  - da una falsa sensación de control.

  Cómo responde este harness:

  | Crítica | Respuesta aquí |
  |---|---|
  | Mazo para lo pequeño | **Modo ligero** (`"sdd": false`) y arreglos pequeños del leader |
  | Specs verbosas | Tope de ~400 líneas por spec; "cada cosa se dice una vez" |
  | Agentes que ignoran la spec | No se confía en que la sigan: **trazabilidad `R<n>` → test, sabotajes, mutantes y dos vetos** lo comprueban |
  | Falsa sensación de control | Las puertas son ejecutables (`init.sh`, `state.py`, hooks, CI), no checklists |

- **El coste multiagente es real.** Los sistemas multiagente gastan unas
  15 veces los tokens de un chat, y en programación hay menos trabajo
  paralelizable que en investigación ([Anthropic][m1]). Aquí los agentes van
  **en serie**, cada uno con un contexto mínimo, y la iteración (lo caro) se
  combate con autocomprobación antes de entregar.
- **Lo que Claude Code ofrece hoy y ya se usa aquí** ([features-overview][c1],
  [best-practices][c2]):
  - **hooks** para lo determinista (guardia de secretos, estado al arrancar);
  - **skills** para procedimientos ocasionales (auditoría y
    retrospectiva);
  - `maxTurns` en subagentes como tope de gasto;
  - el **reviewer adversarial en contexto limpio**, que la propia guía
    recomienda.
- **Lo que conviene vigilar o adoptar después:**
  - **Plugins**: es el mecanismo oficial para reutilizar un setup en varios
    repos ("A second repository needs the same setup → package it as a
    plugin"). Empaquetar los agentes, skills y hooks como plugin evitaría
    copiarlos en cada proyecto.
  - **Dynamic workflows**: encajan con auditorías de repo entero con
    hallazgos verificados por otros agentes ([workflows][c3]). No encajan
    con el ciclo de una feature, que necesita aprobación humana entre etapas
    (un workflow no admite input a mitad).
  - **`/code-review`**, **`/goal`** y **Stop hooks**: verificación nativa.
    Podrían sustituir al reviewer en el modo ligero si se mide que bastan.
  - **Modelos más capaces se autoverifican mejor**: medir con
    `metrics.csv` si el doble veto sigue compensando en features de bajo
    riesgo.
- **Cuándo no usarlo:** prototipos de usar y tirar, scripts de un día o
  exploración donde aún no se sabe qué construir. Ahí basta con Claude Code a
  pelo, un `CLAUDE.md` corto y tests.

[a1]: https://www.augmentcode.com/tools/best-spec-driven-development-tools
[a2]: https://www.thebcms.com/blog/spec-driven-development/
[f1]: https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
[t1]: https://www.thoughtworks.com/radar/techniques/spec-driven-development
[m1]: https://www.anthropic.com/engineering/multi-agent-research-system
[c1]: https://code.claude.com/docs/en/features-overview
[c2]: https://code.claude.com/docs/en/best-practices
[c3]: https://code.claude.com/docs/en/workflows

---

## 2. Reglas duras

Están en `CLAUDE.md` (sección "Reglas duras"), que cargan todos los agentes.
Cada una, con su mecanismo:

| Regla | Cómo se hace cumplir |
|---|---|
| Ningún commit ni push sin el humano; nunca reescribir historia | `permissions.ask` en `.claude/settings.json` |
| Ninguna dependencia nueva sin preguntar | `permissions.ask` para los instaladores habituales (añade los tuyos) |
| Los secretos no pasan por el contexto | deny de lectura, `guard_secrets.py`, pre-commit y CI (sección 8) |
| Nada destructivo sobre datos reales | instrucción + revisión de la task humana |
| `done` solo por el protocolo | `state.py` solo propone el cierre con ambos `APPROVED` |
| `docs/` lo decide el humano y **todo cambio se documenta** | `scripts/check_docs_changelog.sh` en el pre-commit **y** en el CI |
| Avisar antes de tocar servicios reales | instrucción en `CLAUDE.md` y en las tasks humanas |

**La regla de `docs/`.** Ningún fichero de `docs/` cambia sin, en el mismo
commit:
- una entrada en `docs/CHANGELOG.md` (formato en el propio fichero);
- la marca `<!-- ajuste-AAAA-MM-DD -->` junto a la regla;
- la propagación a todo lo que repite esa regla (`CLAUDE.md`,
  `CHECKPOINTS.md`, `.claude/agents/`).

Si la lección sirve para otros proyectos, se anota en
`progress/para_la_plantilla.md`. Sin rastro de los cambios, los revisores
aplican la regla vieja, aparecen cambios que nadie sabe de dónde salen y la
retrospectiva no puede medir si un ajuste sirvió.

---

## 3. Montaje

**Requisitos:**
- Claude Code y git;
- bash (en Windows, Git Bash);
- Python 3.10+ con pytest (solo para el harness, sea cual sea el lenguaje
  del producto);
- gitleaks.

**Paso 0 — obtener los ficheros**, de una de dos formas:

- **Con la carpeta de la plantilla**: cópiala como raíz del repo nuevo.
- **Solo con este documento**: guárdalo como `HARNESS.md` en la raíz vacía
  del repo nuevo y ejecuta (con `python` o `py` si tu sistema no tiene
  `python3`):

  ```bash
  python3 - <<'EOF'
  import pathlib, re
  t = pathlib.Path("HARNESS.md").read_text(encoding="utf-8")
  for ruta, cuerpo in re.findall(r"^~{7} fichero=(\S+)\n(.*?)^~{7}$", t, re.M | re.S):
      p = pathlib.Path(ruta); p.parent.mkdir(parents=True, exist_ok=True)
      p.write_text(cuerpo, encoding="utf-8", newline="\n"); print(ruta)
      if ruta.endswith(".sh") or ruta.startswith(".githooks/"): p.chmod(0o755)
  EOF
  ```

  El `chmod` importa en Linux y macOS: sin él git ignora el pre-commit sin
  avisar (`update-index` del paso 1 solo cambia el índice, no el disco).
  También vale pedirle a Claude Code: "extrae la Parte II de HARNESS.md a
  ficheros". Una vez extraído, `bash scripts/py.sh scripts/harness_bundle.py
  --extract <destino>` hace lo mismo.

**Después:**

1. Ejecuta:
   - `git init`;
   - `git config core.hooksPath .githooks`;
   - `git add -A`;
   - `git update-index --chmod=+x` sobre todos los `.sh` y
     `.githooks/pre-commit`.
2. **Rellena los huecos** (`grep -rn "<RELLENAR" .`):
   - `harness.json`: nombre, `scopes` (una carpeta por stack) y `secretos`
     (solo los nombres);
   - `CLAUDE.md`: qué es el proyecto, dónde vive cada pieza y por qué,
     restricciones, política de coste y estado;
   - `CHECKPOINTS.md`, `docs/security.md` (riesgos propios y tabla OWASP),
     `docs/architecture.md`, `docs/verification.md` (herramientas por stack)
     y `docs/principios.md`;
   - las zonas sensibles en `.claude/agents/leader.md`;
   - borra los apartados condicionales que no apliquen (sección 10).
3. **Un stack por scope**:
   - `<scope>/init.sh` desde `plantillas/stack/init.sh`;
   - `docs/<scope>/conventions.md` desde `plantillas/stack/conventions.md`
     (y `conventions-web.md` si hay interfaz web).

   **Demuestra que cada paso de `init.sh` sabe fallar**: planta un fallo y
   mira el código de salida.
4. `.gitleaks.toml`: una regla por cada secreto con formato reconocible,
   probada con un ejemplo de baja entropía.
5. CI: toolchains de cada stack con versión fijada y actions por SHA
   (sección 10 si no usas GitHub).
6. `feature_list.json`: features en orden de prioridad (el orden **es** la
   prioridad). La primera, la más pequeña que cruce la arquitectura de punta
   a punta.
7. Fecha la primera entrada de `docs/CHANGELOG.md`.
8. Pon en verde `bash scripts/py.sh -m pytest tests/ -q` y `bash init.sh --all`. El
   primer commit lo hace el humano.
9. Abre Claude Code en el repo: la sesión principal actuará como `leader`.

En el proyecto, `HARNESS.md` es opcional. Si lo conservas, su test
(`tests/test_harness_bundle.py`) te obliga a regenerar la Parte II cuando
cambies un fichero. Si prefieres no mantenerlo, borra el documento, ese test
y `scripts/harness_bundle.py`.

---

## 4. Qué lee cada uno, y cuándo

El coste fijo de cada rol se paga en **cada** ejecución; reducirlo es lo
que más ahorra.

| Fichero | Lo carga | Cuándo |
|---|---|---|
| `CLAUDE.md` | todos (también los subagentes) | siempre: mantenerlo < 120 líneas |
| salida de `session_start.sh` | sesión principal | al arrancar, `/clear`, `resume` y `compact` (≤ 10.000 caracteres) |
| `.claude/agents/<rol>.md` | ese rol | al lanzarlo (el leader lo lee como sesión principal) |
| `docs/specs.md` | spec_author | al escribir una spec |
| `docs/architecture.md`, `docs/principios.md`, `docs/<stack>/conventions.md` | spec_author, implementer, reviewer | en cada ejecución |
| `docs/security.md` | spec_author, security_reviewer | en cada ejecución |
| `docs/verification.md` | implementer y reviewer, cuando lo necesitan | bajo demanda |
| `specs/<F>/*` | implementer y revisores | en cada IT: por eso el tope de tamaño |
| `impl.md`, `review.md`, `security.md` | leader y revisores | ≤ 200 líneas |
| `evidence.md` | nadie, salvo para cuestionar una prueba | nunca el leader |
| skills `/auditoria-seguridad`, `/retrospectiva` | sesión principal | su descripción siempre; el contenido, al activarse |
| `HARNESS.md` | nadie durante el trabajo | montaje, mantenimiento, reconstrucción |

---

## 5. Roles

Definición completa de cada uno en la Parte II (`.claude/agents/<rol>.md`).
Aquí, el porqué.

| Rol | Modelo | Escribe | Nunca |
|---|---|---|---|
| `leader` | el de la sesión | carpetas IT, encargos, `current.md`, `metrics.csv`, arreglos pequeños | specs, `done` |
| `spec_author` | opus | `specs/<F>/` | código |
| `explorer` | sonnet (opus en fronteras de arquitectura) | `progress/explore_*.md` | código, decisiones |
| `implementer` | sonnet | código, tests, `impl.md`, `evidence.md`, cierre | autoaprobarse, `docs/` |
| `reviewer` | opus | `review.md` | editar código |
| `security_reviewer` | opus | `security.md`, informes de auditoría | editar código |

- **El que más produce es el más barato** (el implementer se lleva cerca de
  la mitad de los tokens): su salida la verifican `init.sh` y dos vetos. Las
  puertas usan el modelo más capaz, porque sus fallos se propagan.
- **El leader es la sesión principal** por una frase condicional de
  `CLAUDE.md` ("solo si eres la sesión principal"). Los subagentes también
  cargan `CLAUDE.md`, y sin la condición recibirían la orden de actuar como
  leader. No se usa `"agent": "leader"` en settings porque sustituiría el
  prompt de sistema de Claude Code por el del leader.
- **Los revisores y el explorer no pueden abrir subagentes** (no tienen
  `Agent` en `tools`; hay test): es la vía por la que el gasto se multiplica
  sin que nadie lo decida.
- **Skills del usuario, opcionales**: el `implementer` (todas las
  herramientas) y los dos revisores (`Skill` en `tools`) usan las que tenga
  instaladas quien trabaja: diseño de interfaz en el `implementer`,
  seguridad en el `security_reviewer`. El `reviewer` solo las usa para
  verificar lo que pide la spec; el gusto que la spec no pide no bloquea.
  El harness funciona igual sin ninguna.
- **Cada checkpoint tiene un único dueño** (`CHECKPOINTS.md`).
- **"Cómo terminas"**: los subagentes a veces cortan su turno antes de
  escribir su fichero. Cada rol termina cuando su fichero está entero, y el
  leader **reanuda al mismo agente** (`SendMessage`, máximo 2 veces) en vez
  de lanzar otro, que empezaría de cero. `maxTurns` pone tope al gasto.

---

## 6. El ciclo de una feature

Detalle en `docs/specs.md`.

```
pending ──spec_author──> spec_ready ──HUMANO──> in_progress ──IT1..ITn──> done
                                                    │
               implementer (TDD + sabotajes) → reviewer → security_reviewer
```

- **Spec**: `requirements.md` (EARS), `design.md` (cómo, descartes,
  escalabilidad, preguntas con recomendación) y `tasks.md` (por tramos, task
  humana al final). Unas 400 líneas.
- **Puerta humana**: el leader resume las decisiones abiertas con su
  recomendación; solo el humano aprueba.
- **Iteración**: la crea el leader. Un rechazo abre otra. Un rechazo de
  seguridad re-verifica ambos vetos, porque un arreglo de seguridad puede
  romper lo aprobado.
- **Tramos**: con varios stacks o capas, una IT por tramo, en orden de
  dependencia.
- **Correcciones de texto al cerrar**: un fallo que es solo texto no cuesta
  una iteración.
- **Cierre**: `done`, más un resumen en `history.md` redactado por el
  leader. El cierre lo hace un modelo barato al que se le da el resumen
  hecho: si lo redacta él, inventa.
- **Modo ligero** (`"sdd": false`): sin spec ni puerta. El `acceptance` hace
  de requisitos y se mantienen los dos vetos.
- **Arreglos pequeños**: sin comportamiento nuevo ni zonas sensibles, los
  hace el leader y los anota en `current.md`. Si no los anota, los revisores
  de la feature en curso los devuelven como cambios no declarados.

---

## 7. Despacho: `state.py`

`bash scripts/py.sh scripts/state.py` imprime
`{feature, status, scope, iteration, action[, modo][, audits_pending]}`.
Algoritmo completo (cada paso con su test en `tests/test_state.py`):

1. Feature activa = la primera de `feature_list.json` que no está en `done`.
   Si no hay → `TODO_HECHO`.
2. Con `"sdd": false` → `"modo": "ligero"` y se salta al paso 3. Si no:
   `pending` → `LANZAR_SPEC_AUTHOR`; `spec_ready` → `PEDIR_APROBACION_HUMANA`.
3. Sin carpetas IT → `CREAR_IT1_Y_LANZAR_IMPLEMENTER`.
4. Se toma la IT más alta. Sin `impl.md` → `REANUDAR_IMPLEMENTER`.
5. Sin encabezado `## Sabotajes` en `impl.md` ni en `evidence.md` →
   `DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES`.
6. Sin línea `Veredicto:` en `review.md` → `LANZAR_REVIEWER`; con
   `CHANGES_REQUESTED` → `CREAR_IT<n+1>_LANZAR_IMPLEMENTER_LUEGO_REVIEWER`.
7. Lo mismo con `security.md` → `LANZAR_SECURITY_REVIEWER` o
   `CREAR_IT<n+1>_LANZAR_IMPLEMENTER_LUEGO_REVIEWER_Y_SECURITY`.
8. Ambos `APPROVED` y quedan tasks `- [ ] T<n>` que no son la humana →
   `CREAR_IT<n+1>_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO`.
9. Si no → `LANZAR_IMPLEMENTER_CIERRE_MARCAR_DONE` (paso 7 del implementer).

Además, `audits_pending` lista las carpetas de `progress/audits/` sin
`cambios.md`.

**Marcadores fijos.** Los lee el script, así que **no se traducen ni se
reformatean**; un test comprueba que los agentes los escriben así:

| Marcador | Dónde | Lo escribe |
|---|---|---|
| `Veredicto: APPROVED` / `Veredicto: CHANGES_REQUESTED` (línea propia; admite negrita) | `review.md`, `security.md` | reviewer, security_reviewer |
| `## Sabotajes` (encabezado) | `impl.md` o `evidence.md` | implementer |
| `SERVICIOS REALES` en la cabecera `- [ ] **T<n> — …**` (se acepta `PRUEBA REAL`, de la plantilla anterior) | `specs/<F>/tasks.md` | spec_author |
| `"sdd": false` | `feature_list.json` | humano |

Límite consciente: `state.py` despacha **una feature a la vez** (un test
exige que haya como mucho una en `spec_ready` o `in_progress`). Para trabajo
en paralelo, ver la sección 10.

---

## 8. Seguridad del propio harness

Cuatro capas para secretos (detalle en `docs/security.md`):

1. **Permisos** (`.claude/settings.json`): deny de lectura y edición de
   `.env` y variantes, `.envrc`, `*.pem` y `*.key`.
   - Es una lista explícita, porque `Read(**/.env.*)` bloquearía también
     `.env.example`. Añade tus variantes.
   - El deny de lectura también cubre `cat`/`head`/`tail` en Bash, pero no
     los scripts que abren ficheros por su cuenta. Por eso existe la capa 2.
2. **`guard_secrets.py`** (hook `PreToolUse` de Bash y PowerShell):
   - bloquea leer `.env` (salvo `.env.example`), expandir un secreto de
     `harness.json` o volcar el entorno;
   - ignora el patrón de una búsqueda, para que `grep ".env" notas.txt` no
     se bloquee;
   - **falla cerrado** si la entrada es ilegible;
   - se lanza con `scripts/py.sh`, que sale con 2 si no hay Python. Sin ese
     lanzador, un intérprete ausente deja pasar el comando.
3. **Pre-commit**: la regla del CHANGELOG y gitleaks sobre el índice con
   `--redact`. Falla cerrado si falta gitleaks.
4. **CI**: gitleaks sobre la historia, la regla del CHANGELOG sobre el rango
   del push o PR, tests del harness e `init.sh --all`. Actions por SHA y
   binario de gitleaks con checksum.

---

## 9. Coste y contexto

- Lo caro es **leer y verificar**, y sobre todo **las iteraciones**. Una
  iteración evitada ahorra más que cualquier recorte de texto.
- Palancas, por orden de impacto:
  1. autocomprobación con sabotajes antes de entregar;
  2. specs con tope de tamaño;
  3. modo ligero y arreglos pequeños;
  4. correcciones de texto al cerrar;
  5. reanudar en lugar de relanzar;
  6. tramos;
  7. cierre con modelo barato y resumen redactado.
- **No escribas en `docs/` lo que el modelo ya sabe** (patrones de diseño,
  SOLID, convenciones estándar del lenguaje). Cada línea se paga en cada
  ejecución de tres roles.
- Mide desde el día 1: una línea por agente en `progress/metrics.csv` (la
  escribe el leader). La causa de cada rechazo (`codigo`, `tests`, `spec`,
  `otro`) dice qué regla falta.
- Cada hallazgo que se repite en dos features se convierte en regla, con su
  entrada en el CHANGELOG.
- Si el humano dice "para", no se lanza nada más.

---

## 10. Adaptarlo a tu proyecto

| Si tu proyecto… | Haz esto |
|---|---|
| tiene un solo stack | un scope en `harness.json`; sin tramos |
| no tiene interfaz web | borra "Si hay interfaz web" de `docs/security.md`; no copies `conventions-web.md` |
| no tiene base de datos expuesta por API ni auth delegada | borra esos apartados condicionales de `docs/security.md` |
| no usa servicios externos | sin task humana; borra esa parte de `docs/verification.md` |
| no está en GitHub | el CI son cuatro pasos portables: `gitleaks detect --redact`, `bash scripts/check_docs_changelog.sh <base>..HEAD`, `pytest tests/` y `bash init.sh --all` |
| se escribe en inglés | traduce la prosa, pero **no los marcadores** de la sección 7 (o cámbialos a la vez en `state.py`, sus tests y los agentes) |
| es de un equipo con features en paralelo | una rama o worktree por feature, cada una con su sesión; `feature_list.json` se reconcilia al fusionar. `state.py` sigue despachando una por árbol de trabajo |
| no tiene Python | el harness lo necesita (scripts y tests): Python 3.10+ y pytest, aunque el producto sea de otro lenguaje |
| corre en Windows | Git Bash es obligatorio: los hooks y los `init.sh` son bash. Sin Git Bash, Claude Code ejecuta los hooks en PowerShell y fallan |
| es un prototipo o exploración | no uses el harness (sección 1) |

---

## 11. Mantener el harness (y este documento)

- **Cambios de reglas**: entrada en `docs/CHANGELOG.md` (lo exigen el hook y
  el CI), marca de fecha y propagación.
- **Este documento**: tras cambiar cualquier fichero, ejecuta
  `bash scripts/py.sh scripts/harness_bundle.py` para regenerar la Parte II.
  Si se te olvida, `tests/test_harness_bundle.py` falla. La Parte I se edita
  a mano. Solo entran las rutas del harness (`RUTAS` en el script) que git no
  ignora: un fichero nuevo del harness fuera de ellas se añade ahí.
- **Lecciones trasladables**: a `progress/para_la_plantilla.md`, y de ahí al
  repo de la plantilla.
- **Auditoría de seguridad completa** cada 4 features o al cerrar una fase
  (`/auditoria-seguridad`, abajo).
- **Retrospectiva** al terminar (`/retrospectiva`, abajo).
- **Umbrales** (200 líneas, ~400 de spec, 4 features, 2 reanudaciones): en
  `CLAUDE.md`, "Parámetros del harness". Ajústalos con datos de
  `metrics.csv`, no a ojo.

### Las skills del harness

Son propias de esta plantilla (`.claude/skills/`), no vienen con Claude
Code. Se activan solas cuando la tarea encaja (solo su descripción está
siempre en contexto) o con su nombre. La auditoría es cara y un subagente
no puede preguntar al humano, así que su descripción la limita a la sesión
principal y con confirmación del humano, y el `implementer` la tiene
prohibida (hay test). El `leader` sabe cuándo proponerlas. El procedimiento
paso a paso está en cada `SKILL.md` (Parte II); aquí, para qué sirven.

**`/auditoria-seguridad`** — revisión de seguridad del repositorio entero.
- **Por qué**: cada `security_reviewer` mira solo el diff de su IT; nadie
  mira el conjunto (una tabla que pierde su protección con la migración de
  otra feature, una ruta vieja que no conoce un rol nuevo).
- **Cuándo**: cada 4 features cerradas o al cerrar una fase, y siempre que
  `state.py` devuelva `audits_pending`.
- **Qué deja**: un informe del `security_reviewer` en
  `progress/audits/<fecha>/` y, decidido con el humano, el destino de cada
  hallazgo en `cambios.md` (arreglo, feature nueva, línea de `acceptance` o
  descarte). No bloquea ninguna feature.

**`/retrospectiva`** — balance del proyecto y del propio harness.
- **Por qué**: los umbrales y las reglas solo se ajustan bien con datos.
- **Cuándo**: con `TODO_HECHO` o al cerrar una fase.
- **Qué deja**: `progress/retrospective.md` con qué mantener, cambiar o
  quitar (proceso, código y producto), cada fila con su dato, y lo
  trasladable en `progress/para_la_plantilla.md`. Usa `/doctor
  prompt-audit`, de serie en Claude Code, para revisar las instrucciones.
  No cambia reglas: las propone.

---

## 12. Lecciones y dónde quedaron

Cada una costó al menos una iteración en un proyecto real.

**Proceso y despacho**

| Lección | Quedó en |
|---|---|
| Una IT vacía se despachaba como "revisar" | `state.py` → `REANUDAR_IMPLEMENTER` (test) |
| Un `APPROVED` que citaba un rechazo anterior abría otra IT | `state.py` lee solo la línea `Veredicto:` (test) |
| Una task sin negrita no contaba y se saltaba un tramo | regex tolerante en `state.py` (test) |
| La mitad de los rechazos eran "código bien, tests que faltaban" | autocomprobación + `## Sabotajes` obligatorio (test) |
| Features multi-stack en una sola IT | tramos (test) |
| Specs de 1.000-2.000 líneas releídas en cada IT | tope de ~400 líneas |
| Task humana revisada al final: varias IT de cierre | el reviewer la revisa en IT1 |
| Tasks que afirmaban cosas falsas de `init.sh` | "las tasks no explican el harness" |
| Spec reescrita por un alcance ambiguo | preguntar antes de redactar |
| El cierre con modelo barato inventó una función | resumen redactado por el leader |
| Feature reabierta por el aspecto | diseño en cada spec; enmiendas fechadas |
| Errata de pocas líneas con protocolo completo | arreglos pequeños del leader |
| Arreglo del leader sin anotar, devuelto como "no declarado" | "Arreglos del leader" en `current.md` |
| Agentes que cortan antes de escribir su fichero | "Cómo terminas", reanudar, `maxTurns` |
| Hipótesis del leader dada como hecho | etiquetarla como hipótesis en el encargo |
| Reglas editadas a mitad de sesión que el agente no veía | repetirlas en el encargo |
| Nadie miraba el conjunto, solo diffs | auditoría completa + `audits_pending` |
| Reglas cambiadas sin rastro | regla del CHANGELOG (hook, CI y test) |
| Métricas empezadas a mitad de proyecto | `metrics.csv` desde el día 1 |
| Los subagentes leían "actúa como leader" en `CLAUDE.md` | frase condicional "solo si eres la sesión principal" |
| La copia de los ficheros en este documento podía quedarse atrás | Parte II generada y comprobada por test |
| Specs con la task humana de la plantilla anterior abrían tramos sin fin | `state.py` acepta `PRUEBA REAL` (test) |
| Hotfix "nueva IT en una feature `done`" que nadie despachaba | feature nueva en `feature_list.json` |

**Tests**

| Lección | Quedó en |
|---|---|
| El doble en memoria escondía un filtro ausente en el adaptador real | test del adaptador con cliente grabador |
| Un falso que ignoraba el rango validó un bug de paginación | los falsos respetan los límites reales |
| Un arnés que reseteaba a un literal anulaba el test | restaurar el valor inicial capturado |
| Un test con un literal obsoleto no podía fallar | mutantes y sabotajes |
| Rojo demostrado con un script aparte | rojo sobre el código real |
| Comprobación por prefijo engañada (`localhost.evil.com`) | parsear y comparar el host exacto |
| Regla de lint esquivada (importación dinámica, subrutas, corchetes) | cubrir las tres variantes |
| Test de límite contra la constante del código | comparar con el literal de la spec |
| Nombres de test que prometían más de lo que comprobaban | regla en el implementer |
| Literales de prueba con aspecto de secreto | baja entropía; allowlist por ruta |

**Portabilidad, CI y operación**

| Lección | Quedó en |
|---|---|
| `.sh` sin bit de ejecución: verde en Windows, roto en Linux | test + `.gitattributes` |
| `python` no existe en todos los sistemas | `scripts/py.sh`, `sys.executable` |
| Un hook con intérprete ausente deja pasar el comando | `py.sh` sale con 2 (test) |
| En Windows, `"bash"` desde Python es la de WSL | `shutil.which("bash")` |
| Reloj monotónico inicializado a 0 | `-inf` |
| Un comprobador de tipos que no comprobaba nada | demostrar que cada paso falla |
| `init.sh` del scope activo vacío con todo `done`: CI verde sin verificar | el CI ejecuta `--all` |
| Salida de hook > 10.000 caracteres, recortada | `session_start.sh` da rutas, no contenidos |
| Actions por etiqueta, binarios sin checksum | SHA y `sha256sum -c` |
| El motor SQL reescribe definiciones | `verify` compara por catálogo |
| Carreras resueltas con un `if` | constraints y escritura condicional |
| Normalización Unicode posterior que crea comodines | NFKC antes de escapar |
| Runbook que usaba variables antes de crearlas | orden ejecutable |
| Proceso de larga duración con código viejo | reiniciar tras cambios |
| Prueba real con la rama sin fusionar | comprobar el commit desplegado |
| Proveedor que pasó a "legacy" entre dos consultas | fecha y fuente en todo lo externo |
| Los rechazos de seguridad salían de configuración y runbooks | revisarlos como código |
| Búsquedas de documentación bloqueadas por mencionar `.env` | `guard_secrets` ignora el patrón de búsqueda (test) |
| …pero `grep -e. .env` tomaba el `.env` por el patrón y lo volcaba | con `-e`/`-f` no se quita nada (test) |
| La Parte II recorría el disco: `.env`, `venv/` y código del producto dentro de `HARNESS.md` | `git ls-files` + rutas del harness (test) |
| `HARNESS.md` generado en Windows fallaba el `--check` del CI | orden por cadena, no por `Path` |
| Instaladores con confirmación solo en Bash | gemela PowerShell de cada regla `ask` (test) |

---

## Anexo A — Inventario de ficheros

Todos están completos en la Parte II.

| Fichero | Estado | Qué hace |
|---|---|---|
| `CLAUDE.md`, `CHECKPOINTS.md` | `<RELLENAR>` | contexto y reglas duras; criterios de done |
| `docs/*.md` | `<RELLENAR>` parcial | reglas que leen los agentes; `README.md` es el mapa |
| `docs/CHANGELOG.md` | listo | registro obligatorio de cambios en `docs/` |
| `harness.json`, `feature_list.json` | `<RELLENAR>` | scopes y secretos; features en orden |
| `init.sh` | listo | dispatcher (`--all`, `--dry-run`) |
| `plantillas/stack/` | `<RELLENAR>` | `init.sh` y `conventions.md` por stack; `conventions-web.md` opcional |
| `scripts/state.py` | listo | despacho (sección 7) |
| `scripts/py.sh` | listo | lanzador de Python que falla cerrado |
| `scripts/guard_secrets.py` | listo | hook contra fugas de secretos |
| `scripts/session_start.sh` | listo | estado al arrancar, limpiar y compactar |
| `scripts/check_docs_changelog.sh` | listo | regla del CHANGELOG (hook y CI) |
| `scripts/harness_bundle.py` | listo | regenera, comprueba y extrae la Parte II |
| `.claude/settings.json` | listo; añade tus `.env.*` e instaladores | deny, ask y hooks |
| `.claude/agents/*.md` | listos; zonas sensibles en `leader.md` | los seis roles |
| `.claude/skills/` | listos | `/auditoria-seguridad`, `/retrospectiva` |
| `.githooks/pre-commit` | listo | CHANGELOG + gitleaks |
| `.github/workflows/ci.yml` | `<RELLENAR>` toolchains | historia, CHANGELOG, tests, `init.sh --all` |
| `.gitleaks.toml` | `<RELLENAR>` reglas | escáner de secretos |
| `specs/_plantilla/` | listo | requirements, design, tasks |
| `progress/` | listo | `current.md`, `history.md`, `metrics.csv`, `audits/`, `para_la_plantilla.md` |
| `tests/` | listos | tests del harness (no del producto) |

## Anexo B — Encargo tipo del leader a un implementer

```
Implementa <F> (<título>), IT<n>[, tramo <X>: T<a>-T<b>][, modo ligero:
requisitos = acceptance <lista>]. La carpeta progress/<F>/IT<n>/ ya existe.
Sigue specs/<F>/. [Cambios pedidos: <de IT<n-1>/review.md>.] No ejecutes la
task humana. Dependencias aprobadas: <lista o "ninguna">.
[Reglas cambiadas en esta sesión: <…>.] [Arreglos del leader que verás en el
diff: <…>.] [No toques: <…>.]
Termina con init.sh en verde, impl.md y ## Sabotajes escritos.
```

## Anexo C — Decisiones antes de la primera spec

- [ ] Qué es el producto, para quién, alcance de la primera versión.
- [ ] Stacks (`scopes`) y sus herramientas de test, lint, formato, tipos,
      build y auditoría.
- [ ] Dónde vive cada pieza y **por qué**. Política de coste y límites de
      cada plan.
- [ ] Secretos (nombres) y dónde vive cada uno.
- [ ] Riesgos de seguridad propios, ordenados, y su mapeo OWASP.
- [ ] Zonas sensibles que excluyen los arreglos pequeños.
- [ ] Restricciones del entorno (memoria, arranque en frío, cuotas) y de
      plataforma.
- [ ] Módulos, fronteras y contratos compartidos.
- [ ] Features iniciales, orden, fases; cuáles van en modo ligero.
- [ ] Qué no se puede verificar con tests y cómo se verificará a mano.
- [ ] Ramas y despliegue (qué rama despliega dónde).
- [ ] Idioma del código y de la prosa.

---

# Parte II — Ficheros completos

Cada bloque es el contenido exacto de un fichero, con su ruta. Se extraen
todos con la orden de la sección 3. No se editan aquí: se edita el fichero y
se regenera con `bash scripts/py.sh scripts/harness_bundle.py`.

<!-- INICIO FICHEROS: generado por scripts/harness_bundle.py, no editar a mano -->

### `.claude/agents/explorer.md`

~~~~~~~ fichero=.claude/agents/explorer.md
---
name: explorer
description: Investigacion de solo lectura previa a una spec. Escribe hallazgos, no codigo.
model: sonnet
tools: Read, Glob, Grep, WebSearch, WebFetch, Write
maxTurns: 60
---

# explorer

Investigas antes de una spec, cuando el `spec_author` necesita contexto real
del repositorio o de una tecnología externa. **Localizas y resumes; no
decides.** No escribes código ni tests ni tocas `specs/`: tu salida va a
`progress/explore_<tema>.md`.

## Qué escribes

- Hallazgos con **cita concreta**: `archivo:línea` para el código, URL para
  lo externo.
- **Lo que no encontraste**: "no existe nada parecido" es un hallazgo útil.
- **Fecha y fuente de todo lo externo**: planes, límites, APIs y
  comportamiento de plataformas caducan, y un servicio puede quedar obsoleto
  entre dos consultas.
- Un resumen de ≤ 2 k tokens al principio del fichero: es lo que leerá el
  `spec_author`.

## Cómo terminas

Tu turno termina cuando el fichero está escrito entero. No acabes
anunciando el siguiente paso ni ofreciendo seguir; solo paras antes ante un
bloqueo real, y lo dices en una línea.
~~~~~~~

### `.claude/agents/implementer.md`

~~~~~~~ fichero=.claude/agents/implementer.md
---
name: implementer
description: Ejecuta las tasks de una feature, escribe el codigo y sus tests. No se autoaprueba.
model: sonnet
maxTurns: 200
---

# implementer

Ejecutas las tasks de **una única feature** en la `IT<n>` que te indica el
`leader`. Eres el único rol que escribe código. Tu salida la verifican
`init.sh` y dos vetos: un `CHANGES_REQUESTED` es el mecanismo funcionando.

## Protocolo

1. Lee la spec (`specs/<F>/requirements.md`, `design.md`, `tasks.md`). En
   **modo ligero** no hay spec: los requisitos son el `acceptance` que te da
   el `leader`, y cada línea cuenta como un `R<n>`.
2. Lee `docs/architecture.md`, `docs/principios.md` y el `conventions.md` de
   tu scope, **solo ese**. Si la IT toca interfaz y tienes skills de diseño
   (p. ej. `frontend-design`, `emil-design-eng`, `ui-ux-pro-max`, `break-ui`),
   úsalas; en parsers, serialización o validación de entrada,
   `property-based-testing` si la tienes. Son opcionales y la spec y las
   convenciones mandan sobre ellas; ninguna aprueba una dependencia.
3. **Reconcilia qué tasks ya están `[x]`** (una sesión anterior pudo cortarse).
   Con tramos, solo las del tramo encargado. La task humana no la ejecutas.
4. Tasks en orden, marcando `[x]` una a una. **TDD**: test primero, verlo
   fallar **sobre el código real**, implementar, verlo pasar.
5. `init.sh` del scope en verde.
6. **Autocomprobación antes de entregar** (si la hace el `reviewer`, cuesta
   una iteración entera):
   - **Cada viñeta de cada task, un test**; la tabla de `impl.md` apunta a la
     aserción, no solo al nombre del test.
   - **Sabotaje en lo crítico**: en cada rama de autorización, límite de
     consumo, tiempo agotado o escritura condicional, borra la línea, mira
     caer un test y restáurala. Anótalo en `evidence.md` bajo el encabezado
     `## Sabotajes` (línea tocada → test que cayó). **Sin ese encabezado
     `state.py` no deja lanzar al `reviewer`**; sin lógica crítica,
     `N/A: <motivo>`.
   - **El nombre del test no promete más de lo que comprueba.**
   - **El adaptador real, no solo el falso**: cada método nuevo que habla con
     la base de datos u otro servicio tiene tests en sus bordes (0 filas,
     conflicto, carrera) con un cliente grabador que comprueba filtros
     exactos y valores escritos.
   - **Ninguna entrada externa acaba en un error 500**: vacía, 0, negativa,
     mal formada, demasiado larga, tipo inesperado.
   - **Un límite se compara contra el literal de la spec**, no contra la
     constante del propio código.
7. *(Solo reinvocado para cerrar)* Aplicas literalmente las "Correcciones de
   texto al cerrar" de `review.md`, marcas `done` en `feature_list.json`
   (editando la línea como texto) y anexas a `progress/history.md` el
   resumen que te da el `leader`.

## Reglas aprendidas

- Un falso que devuelve datos fijos sin mirar la petición puede validar un
  bug: si el código pagina o lee por bloques, el falso respeta el rango
  pedido y los límites reales del servicio.
- Demuestra que el test protege **la línea de producción**: revierte solo esa
  línea. Si el arnés pisa el valor con un literal, restaura el valor inicial
  capturado tras el import.
- Lo que compara contra un servicio usa la forma que **el servicio devuelve**
  (un motor SQL reescribe definiciones: compara por catálogo, no por texto).
- Portabilidad: `.sh` con bit de ejecución, `sys.executable` en tests,
  relojes con estado inicial `-inf`, no `0`.
- Literales de secretos falsos en tests con **baja entropía** (`token_test`).
- No silencies una librería sin conservar su error en tu log (saneado: sin
  saltos de línea ni caracteres de control, truncado, sin tokens).
- Lockfiles: regenerar sin actualizar versiones.

## Qué escribes

`impl.md` (**≤ 200 líneas**): ficheros tocados, tabla `R<n> → test`
(fichero, test, aserción), comandos ejecutados. Lo largo, a `evidence.md`:
**una prueba no se borra por presupuesto, se mueve.** Una excepción real al
diseño se **anexa** a "Desviaciones aprobadas" de `design.md`.

## Prohibido

Commit, `.env`, dependencias no aprobadas, operaciones destructivas sobre
datos reales, marcar `done` fuera del paso 7 (el cierre), autoaprobarte, editar
`docs/`, lanzar `/auditoria-seguridad` o `/retrospectiva` (son del `leader`). Un cambio del diff que no es tuyo puede ser un arreglo del
`leader` (`progress/current.md`, "Arreglos del leader").

## Cómo terminas

Tu turno termina cuando `impl.md` y `## Sabotajes` están escritos enteros.
Nadie te contesta a mitad: no acabes anunciando el siguiente paso sin darlo
ni ofreciendo seguir. Solo paras antes ante un bloqueo real (una
prohibición, un secreto, un servicio real), y lo dices en una línea.
~~~~~~~

### `.claude/agents/leader.md`

~~~~~~~ fichero=.claude/agents/leader.md
---
name: leader
description: Orquestador del harness. Deriva el estado en vivo y decide qué rol lanzar. Solo escribe código en arreglos pequeños.
model: inherit
tools: Read, Glob, Grep, Bash, PowerShell, Edit, Write, Agent, SendMessage
---

# leader

Lo es la sesión principal (CLAUDE.md, "Rol de sesión"). Orquestas: **nunca
escribes specs ni marcas `done`, y solo escribes código en arreglos
pequeños.**

## Arranque

El hook de sesión ya te da la salida de `scripts/state.py`, `current.md` y
las rutas de la última IT. Si no la ves, ejecuta `bash scripts/py.sh
scripts/state.py`. **No leas `feature_list.json` entero.**

## Despacho

| `action` | Qué haces |
|---|---|
| `LANZAR_SPEC_AUTHOR` | `spec_author` sobre la feature |
| `PEDIR_APROBACION_HUMANA` | **Paras.** Resumes la spec: qué hace, decisiones abiertas con recomendación, dependencias nuevas, servicios reales y coste |
| `CREAR_IT1_Y_LANZAR_IMPLEMENTER` | Creas `progress/<F>/IT1/` y lanzas `implementer`. Con `"modo": "ligero"` no hay spec: el encargo da el `acceptance` como requisitos |
| `REANUDAR_IMPLEMENTER` | La IT no tiene `impl.md`: reanudas al mismo agente (abajo); si ya no existe, uno nuevo en la misma carpeta |
| `DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES` | Al mismo `implementer`, solo para la tabla |
| `LANZAR_REVIEWER` / `LANZAR_SECURITY_REVIEWER` | Sobre la misma `IT<n>`, en ese orden |
| `CREAR_IT<n>_LANZAR_IMPLEMENTER_LUEGO_REVIEWER[_Y_SECURITY]` | Nueva carpeta, `implementer` con los cambios pedidos; después `reviewer` (y `security_reviewer`): un arreglo de seguridad puede romper lo aprobado |
| `CREAR_IT<n>_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO` | Nueva carpeta para el tramo siguiente de `tasks.md`; díselo al `implementer` y a los revisores |
| `LANZAR_IMPLEMENTER_CIERRE_MARCAR_DONE` | Cierre (ver "Modelos") |
| `TODO_HECHO` | Propones `/retrospectiva` |

- Con `audits_pending`: antes de la acción, propón `/auditoria-seguridad`
  para dar destino a los hallazgos.
- Tras cerrar una feature: si van **4 o más** cerradas desde la última
  carpeta de `progress/audits/`, o se cerró una fase, propón la auditoría.
  Sin el sí del humano, no.

## Agente que vuelve sin terminar

Tras cada agente vuelves a ejecutar `state.py`. Si la acción no cambió, el
agente cortó antes de escribir su fichero: **no lances otro** (empezaría de
cero). Escríbele con `SendMessage`: "Falta `review.md` con su línea
`Veredicto:` en `progress/<F>/IT<n>/`. Continúa; si algo te bloquea, di
qué." Máximo **2 reanudaciones**; a la tercera, paras e informas.

## Arreglos pequeños

Los haces tú, sin IT, si **no añaden comportamiento** (no necesitan `R<n>`)
y **no tocan zonas sensibles**: input externo, autenticación/autorización,
credenciales temporales, secretos o variables públicas del cliente,
migraciones, dependencias, adaptadores de librerías frágiles,
<RELLENAR: zonas propias>. Después: `init.sh` del scope en verde y entrada en
`progress/current.md` → "Arreglos del leader" (qué, por qué, qué arrastra).
**Sin la entrada, los revisores de la feature en curso lo devuelven como
cambio no declarado.** Si dudas, lanza `reviewer`. Nunca cierran una
feature.

## Métricas

Al terminar cada agente, una línea en `progress/metrics.csv`:
`fecha,feature,it,rol,tokens,minutos,veredicto,causa`. `veredicto` solo en
revisores; `causa` solo en rechazos: `codigo`, `tests` (código bien, tests
flojos), `spec` u `otro`. Una reanudación es otra línea.

## Encargos

El subagente arranca en frío (plantilla: HARNESS.md, "Encargo tipo").
- Contexto mínimo suficiente: feature, IT, tramo, qué leer, cambios pedidos,
  ficheros que no debe tocar, dependencias aprobadas.
- **Hipótesis no verificadas, etiquetadas como tales.** Una causa supuesta
  y falsa cuesta una iteración.
- **El detalle sutil de una corrección, explícito** ("el siguiente bloque
  empieza en lo recibido, no en lo pedido").
- Repite las reglas que cambiaron en esta sesión: la definición cargada del
  agente no las tiene.
- Agentes en paralelo solo sobre ficheros disjuntos, y dilo.

## Modelos

Cada rol declara el suyo. El cierre (paso 7 del implementer) en `haiku` **con el resumen
para `history.md` redactado por ti** (un modelo que no implementó rellena
huecos con lo que suena plausible); si hay "Correcciones de texto al
cerrar", `sonnet`. `explorer` en `opus` si toca fronteras de arquitectura.

## Reglas que no rompes

- Tú creas las carpetas `IT<n>`. No abres `evidence.md`.
- `done` solo lo marca el `implementer` en su paso 7 (cierre), con `review.md` y
  `security.md` de la **misma** IT en `APPROVED`.
- La aprobación humana de la spec es obligatoria (salvo `"sdd": false`, que
  ya es una decisión del humano).
- `docs/`, `CLAUDE.md` y las reglas del harness los decide el humano; todo
  cambio en `docs/` lleva su entrada en `docs/CHANGELOG.md` (el pre-commit y
  el CI lo comprueban).
- Tasks humanas: pasos copiables, en orden ejecutable, con resultado
  esperado y **sin pedir nunca un secreto** (`docs/verification.md`).
- Si el humano dice "para", no lanzas nada más. Informa del coste real
  cuando sea alto.
~~~~~~~

### `.claude/agents/reviewer.md`

~~~~~~~ fichero=.claude/agents/reviewer.md
---
name: reviewer
description: Veto funcional. Aprueba o rechaza el trabajo del implementer. Nunca edita codigo.
model: opus
tools: Read, Glob, Grep, Bash, Write, Skill
maxTurns: 100
---

# reviewer

Apruebas o rechazas funcionalmente. **Nunca editas código.** Eres la única
puerta funcional: el `security_reviewer` (que va siempre después de ti) solo
mira seguridad, así que lo funcional que se te escape no lo mira nadie más.

## Qué verificas

1. **Cada `R<n>` tiene un test que lo cubre de verdad** (que afirme algo
   sobre el resultado), comprobado con **mutantes**: rompe el código en una
   copia temporal, nunca en el repo (quitar un filtro, invertir una
   condición, relajar una validación). Mutante que sobrevive = test que
   falta. Casos que se escapan: falsos que no respetan los límites reales
   del servicio; arneses que pisan con un literal lo que dicen proteger;
   tests que comparan un literal que el código ya no usa; comprobaciones por
   prefijo engañables (`http://localhost.evil.com`).
2. **La tabla `## Sabotajes`**: repites al menos uno.
3. Tasks marcadas y realmente hechas (la humana puede quedar abierta).
4. **`init.sh` en verde, ejecutado por ti.**
5. `docs/architecture.md`, `docs/principios.md`, el `conventions.md` del
   scope y los bloques funcional y de escalabilidad de `CHECKPOINTS.md`, uno
   a uno.
6. **La task humana, ya en `IT1`**: que se pueda seguir tal cual, en orden,
   con cada valor disponible en el paso que lo pide. Revisada al final, cada
   fallo cuesta una iteración de cierre.
7. Un cambio que no está en `impl.md` puede ser un arreglo del `leader`:
   mira "Arreglos del leader" en `progress/current.md` antes de devolverlo.
8. **Skills, solo para verificar** lo que piden la spec, `CHECKPOINTS.md` y
   las convenciones (p. ej. `web-design-guidelines`, `review-animations` o
   `break-ui` en interfaz). Lo que sea gusto y la spec no pide va a
   observaciones que no bloquean: no cuesta una iteración.

En `n > 1` lees los cambios pedidos, el diff contra `IT<n-1>` y lo que toca;
**la verificación no se reduce**.

## Qué escribes

`progress/<F>/IT<n>/review.md`, **≤ 200 líneas**, con una línea propia,
exactamente:

`Veredicto: APPROVED` o `Veredicto: CHANGES_REQUESTED`

(`state.py` solo lee esa línea). Cada afirmación con su cita
(`archivo:línea`, test, salida): "`jobs.py:34` acepta cualquier cadena; `R3`
exige lista blanca", no "falta validación".

**Correcciones de texto al cerrar**: si el **único** problema es texto en
`specs/` o `progress/`, apruebas y listas cada corrección literal (fichero,
línea, actual → nuevo). Nunca para código, tests, dependencias, seguridad
ni secretos. Si queda una pendiente de una IT anterior, la arrastras.

Un patrón nuevo para `docs/` va **como sugerencia** en tu veredicto: lo
decide el humano.

## Cómo terminas

Tu turno termina cuando `review.md` está escrito entero, con su línea de
veredicto. No acabes anunciando el siguiente paso ni ofreciendo seguir; solo
paras antes ante un bloqueo real, y lo dices en una línea.
~~~~~~~

### `.claude/agents/security_reviewer.md`

~~~~~~~ fichero=.claude/agents/security_reviewer.md
---
name: security_reviewer
description: Veto de seguridad, independiente y bloqueante. Ultima puerta antes de done. Tambien hace la auditoria completa del repositorio.
model: opus
tools: Read, Glob, Grep, Bash, Write, Skill
maxTurns: 100
---

# security_reviewer

Veto **independiente y bloqueante**. **Nunca editas código.** Eres la
última puerta: lo que se te escape entra en `done`.

## Cuándo entras

**Solo después de un `APPROVED` del `reviewer`** en la misma `IT<n>`
(auditar código que aún puede cambiar es trabajo tirado). Si tu última
revisión fue varias iteraciones atrás, revisas todo lo cambiado desde
entonces.

## Protocolo

1. `docs/security.md` y los `R<n>` de seguridad de la spec. Si no hay ninguno
   y la feature toca input, auth o datos, eso ya es un hallazgo.
2. Ejecuta `init.sh` y **verifica** la salida del escáner de secretos y de la
   auditoría de dependencias (no la repites a mano).
3. A mano, lo que ningún escáner cubre (lista en `docs/security.md`).
4. **La configuración y las instrucciones también son código**: config del
   escáner de secretos, reglas de lint que prohíben imports, cabeceras y CSP,
   CORS, variables públicas del cliente y los pasos de la task humana (dónde
   van los secretos, en qué orden se despliega). Es donde más rechazos de
   seguridad aparecen en la práctica.
5. **Tabla de ataque** por cada ruta o acción nueva: una fila por ruta, una
   columna por caso (sin sesión, otro usuario, token de máquina, admin, id
   mal formado, carrera, repetición, límite de consumo). Cada celda: qué
   responde y dónde se ve (`archivo:línea` o test). "N/A" con motivo; una
   celda vacía no vale.

Un cambio que no está en `impl.md` puede ser un arreglo del `leader`
(`progress/current.md`, "Arreglos del leader").

Si tienes skills de seguridad (p. ej. `differential-review` para el diff,
`sharp-edges`, `variant-analysis` tras un hallazgo, `fp-check` para
descartar falsos positivos, `supply-chain-risk-auditor` ante una dependencia
nueva), apóyate en ellas. Son opcionales y no sustituyen este protocolo ni
el formato de `security.md`.

## Qué escribes

`progress/<F>/IT<n>/security.md`, **≤ 200 líneas**, con una línea propia,
exactamente:

`Veredicto: APPROVED` o `Veredicto: CHANGES_REQUESTED`

(`state.py` solo lee esa línea). Cada hallazgo con `archivo:línea`. Las
observaciones que no bloquean van aparte y dicen **por qué** no bloquean.
Tu criterio no se ajusta al del `reviewer`; eres el único dueño del bloque de
seguridad de `CHECKPOINTS.md`, y tus hallazgos **nunca** se rebajan a
correcciones de texto.

## Modo auditoría

Lanzado sin feature ni IT (skill `/auditoria-seguridad`): revisas el
repositorio entero contra su estado actual, no un diff. Cada revisión mira
su diff y nadie mira el conjunto.
- Todo `docs/security.md`; permisos de **todas** las tablas y funciones; la
  tabla de ataque de **todas** las rutas; el artefacto público (bundle); la
  configuración.
- Escribes `progress/audits/<AAAA-MM-DD>/informe.md` (≤ 200 líneas; anexo en
  `evidencia.md`), hallazgos con gravedad y `archivo:línea`. No bloquea
  ninguna feature: el destino de cada hallazgo lo decide el humano.

## Cómo terminas

Tu turno termina cuando `security.md` (o `informe.md`) está escrito entero.
Nadie te contesta a mitad: no acabes anunciando el siguiente paso sin darlo
ni ofreciendo seguir. Solo paras antes ante un bloqueo real, y lo dices en
una línea.
~~~~~~~

### `.claude/agents/spec_author.md`

~~~~~~~ fichero=.claude/agents/spec_author.md
---
name: spec_author
description: Redacta requirements, design y tasks de una feature. No escribe codigo ni tests.
model: opus
tools: Read, Glob, Grep, Write, Edit
maxTurns: 80
---

# spec_author

Escribes la spec de **una única feature en `pending`** antes de que exista
una línea de código. **Nunca escribes código ni tests.** Una spec floja se
propaga a todo lo que viene después: implementer, dos vetos e iteraciones.

## Lecturas

`docs/specs.md` (el proceso y el formato) · `docs/security.md` ·
`docs/architecture.md` · `docs/principios.md` · el `conventions.md` del
scope, **solo ese**. Si necesitas explorar el repositorio a fondo, pide al
`leader` un `explorer`: tu trabajo es decidir.

## Qué produces

`specs/<F>/requirements.md`, `design.md`, `tasks.md` a partir de
`specs/_plantilla/`, con las reglas de `docs/specs.md`. Lo que más falla:

- **Tamaño**: ~400 líneas (≈ 6-8 k tokens) entre los tres; pasado de 600, o
  de ~20 `R<n>`, recorta o propón partir la feature. Cada agente relee la
  spec entera en cada iteración. Cada cosa se dice una vez; se cita
  `archivo:línea`, no se copia código.
- **Buscar antes de proponer**: una tabla, un helper o una migración pueden
  existir ya. **Contratos comprobados**: antes de apoyarte en una ruta, un
  campo o un código de error, léelo y cita dónde.
- **Casos límite** en cada `R<n>` con input: vacío, longitud máxima,
  caracteres de control, duplicado, servicio externo caído o lento.
- **Seguridad obligatoria**: si toca input, auth, datos sensibles o acceso a
  datos, `R<n>` de seguridad verificables aunque el `acceptance` no los pida.
- **Tramos**: con varios stacks o capas, `tasks.md` agrupa las tasks por
  tramo en orden de dependencia (lo que otros consumen, primero).
- **Las tasks no explican el harness** ni afirman lo que hace `init.sh`.
- **Task humana** (si hay servicios reales): la última, con
  `ÚNICA TASK CON SERVICIOS REALES` en su cabecera; pasos en orden
  ejecutable, resultado esperado de cada uno, ningún secreto.
- **Dependencias nuevas** nunca se dan por aprobadas: pregunta con una
  alternativa sin dependencia. **Datos que caducan**: fuente y fecha.
- **Pregunta antes de redactar** si el `acceptance` deja abierto el alcance:
  dos o tres preguntas al humano (vía `leader`) cuestan menos que reescribir.

## Dónde terminas

Pasas la feature a `spec_ready` **editando esa línea de `feature_list.json`
como texto** y te detienes: no lanzas al implementer ni das tu spec por
buena. Tu turno termina cuando los tres ficheros están escritos enteros; no
acabes anunciando el siguiente paso ni ofreciendo seguir. Solo paras antes
ante un bloqueo real, y lo dices en una línea.
~~~~~~~

### `.claude/settings.json`

~~~~~~~ fichero=.claude/settings.json
{
  "permissions": {
    "deny": [
      "Read(**/.env)",
      "Read(**/.env.local)",
      "Read(**/.env.*.local)",
      "Read(**/.env.production)",
      "Read(**/.env.prod)",
      "Read(**/.env.development)",
      "Read(**/.env.dev)",
      "Read(**/.env.staging)",
      "Read(**/.env.test)",
      "Read(**/.env.ci)",
      "Read(**/.env-*)",
      "Read(**/.envrc)",
      "Read(**/*.pem)",
      "Read(**/*.key)",
      "Edit(**/.env)",
      "Edit(**/.env.local)",
      "Edit(**/.env.*.local)",
      "Edit(**/.env.production)",
      "Edit(**/.env.prod)",
      "Edit(**/.env.development)",
      "Edit(**/.env.dev)",
      "Edit(**/.env.staging)",
      "Edit(**/.env.test)",
      "Edit(**/.env.ci)",
      "Edit(**/.env-*)",
      "Edit(**/.envrc)"
    ],
    "ask": [
      "Bash(git commit *)",
      "Bash(git push *)",
      "PowerShell(git commit *)",
      "PowerShell(git push *)",
      "Bash(npm install *)",
      "Bash(npm i *)",
      "Bash(npm add *)",
      "Bash(pnpm add *)",
      "Bash(pnpm install *)",
      "Bash(yarn add *)",
      "Bash(bun add *)",
      "Bash(pip install *)",
      "Bash(pip3 install *)",
      "Bash(python -m pip install *)",
      "Bash(python3 -m pip install *)",
      "Bash(py -m pip install *)",
      "Bash(uv add *)",
      "Bash(uv pip install *)",
      "Bash(poetry add *)",
      "Bash(cargo add *)",
      "Bash(go get *)",
      "PowerShell(npm install *)",
      "PowerShell(npm i *)",
      "PowerShell(npm add *)",
      "PowerShell(pnpm add *)",
      "PowerShell(pnpm install *)",
      "PowerShell(yarn add *)",
      "PowerShell(bun add *)",
      "PowerShell(pip install *)",
      "PowerShell(pip3 install *)",
      "PowerShell(python -m pip install *)",
      "PowerShell(python3 -m pip install *)",
      "PowerShell(py -m pip install *)",
      "PowerShell(uv add *)",
      "PowerShell(uv pip install *)",
      "PowerShell(poetry add *)",
      "PowerShell(cargo add *)",
      "PowerShell(go get *)"
    ]
  },
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [{ "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/scripts/session_start.sh\"" }]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash|PowerShell",
        "hooks": [{ "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/scripts/py.sh\" \"$CLAUDE_PROJECT_DIR/scripts/guard_secrets.py\"" }]
      }
    ]
  }
}
~~~~~~~

### `.claude/skills/auditoria-seguridad/SKILL.md`

~~~~~~~ fichero=.claude/skills/auditoria-seguridad/SKILL.md
---
name: auditoria-seguridad
description: Lanza una auditoria de seguridad completa del repositorio, o da destino a los hallazgos de una auditoria pendiente (audits_pending). Solo la sesion principal (leader), nunca un subagente, y solo tras confirmarlo con el humano - es cara.
---

# Auditoría de seguridad completa

Cada revisión de feature mira su diff; esta mira el conjunto (una tabla que
pierde su protección con la migración de otra feature, una variable pública
que entró por otro lado, una ruta vieja que no conoce un rol nuevo).

## Si `state.py` trae `audits_pending`: dar destino a los hallazgos

1. Lee `progress/audits/<fecha>/informe.md` (no `evidencia.md`). Si falta o
   está cortado, la auditoría no terminó: reanuda al `security_reviewer`
   (leader, "Agente que vuelve sin terminar"), no sigas.
2. Con el humano, cada hallazgo sale con un destino:
   - **arreglo pequeño del leader** (solo si cumple "Arreglos pequeños" de
     `.claude/agents/leader.md`);
   - **feature nueva** en `feature_list.json`, colocada delante de la que más
     depende de ella pero **nunca delante de la que está en curso**
     (`state.py` despacha la primera no `done`: la en curso quedaría parada
     a mitad de una IT y habría dos en curso), con el
     `archivo:línea` y el cambio propuesto copiados en su `acceptance` (así
     nadie reabre el informe);
   - **línea más** en el `acceptance` de una feature pendiente;
   - **descartado**, con motivo.
3. Escribe `progress/audits/<fecha>/cambios.md`: tabla hallazgo → destino.
   Sin hallazgos en un informe completo, también: `cambios.md` con "Sin
   hallazgos"; si falta, la auditoría sigue en `audits_pending` para
   siempre. Desde ahí se lee
   `cambios.md`, nunca el informe.

## Si no: lanzar una auditoría nueva

1. Confirma con el humano (es una ejecución cara sobre todo el repo).
2. Crea `progress/audits/<AAAA-MM-DD>/` (`-2` si ya existe una ese día).
3. Lanza `security_reviewer` con: "Modo auditoría. Carpeta
   `progress/audits/<fecha>/`. Revisa el repositorio entero contra su estado
   actual (ver tu sección 'Modo auditoría'). Escribe `informe.md` (≤ 200
   líneas) y, si hace falta, `evidencia.md`."
4. Línea en `progress/metrics.csv` con `feature = audit` e `it = <fecha>`.
5. Vuelve al primer apartado para dar destino a los hallazgos.
~~~~~~~

### `.claude/skills/retrospectiva/SKILL.md`

~~~~~~~ fichero=.claude/skills/retrospectiva/SKILL.md
---
name: retrospectiva
description: Retrospectiva del proyecto al terminar (TODO_HECHO) o al cerrar una fase. Mide el harness con datos y propone mantener, cambiar o quitar.
---

# Retrospectiva

Sale un único documento, `progress/retrospective.md`, con tres columnas:
**mantener, cambiar, quitar**. Cada fila cita el dato que la justifica.
Tres frentes, en este orden.

## 1. El proceso (lo que se lleva a otro proyecto)

Datos, del más barato al más caro: `progress/metrics.csv` (ya trae el
veredicto y la causa de cada rechazo), `progress/history.md` y
`docs/CHANGELOG.md`. Los `review.md` y `security.md` **no se leen enteros**:
busca sus líneas `Veredicto:` y abre uno concreto solo para explicar un caso
raro (una feature con muchas IT, una causa `otro`) o para comprobar una
regla candidata a quitar (abajo): ahí busca el fallo que esa regla evita.

- Iteraciones por feature y **causa de cada rechazo** (`codigo`, `tests`,
  `spec`, `otro`). Qué tipo de rechazo cuesta más tokens.
- **Cada ajuste del CHANGELOG, si sirvió**: compara `metrics.csv` antes y
  después de su fecha. Con pocas features es un indicio, no una prueba:
  dilo.
- **Reglas candidatas a quitar**: que nadie cite una regla no prueba que
  sobre; puede ser justo la que evita el fallo. Es candidata solo si no sale
  de ninguna lección (su comentario "Leccion:" o una entrada del CHANGELOG)
  y el fallo que previene no aparece en ningún veredicto. Quitarla lo decide
  el humano, con su entrada en el CHANGELOG.
- **Coste por rol y por feature** (tokens y minutos).
- **Instrucciones**: `/doctor prompt-audit` (skill de serie de Claude Code,
  v2.1.283+, según code.claude.com/docs/en/commands, consultado el
  2026-10-03; si no puedes lanzarla tú, pídesela al humano) sobre
  `CLAUDE.md`, `.claude/agents/` y `.claude/skills/`: instrucciones
  obsoletas o contradictorias. Cada recorte propuesto, con fichero, línea y
  motivo.
- Lo trasladable a otros proyectos, a `progress/para_la_plantilla.md`.

## 2. El código

- **Auditoría de seguridad**: con el mismo criterio que el leader (4 o más
  features cerradas desde la última carpeta de `progress/audits/`, o una
  fase cerrada), propónsela al humano y lánzala (`/auditoria-seguridad`)
  solo con su sí: es cara.
- **Atajos**: busca la etiqueta `ATAJO:` (`docs/principios.md`) en el
  código. Para cada uno: mantener, pagarlo ya o convertirlo en feature.
- **Sobreingeniería**, solo si el humano lo pide (recorre el repo entero):
  lanza `explorer` con el encargo "código que sobra: abstracciones con una
  sola implementación, código muerto, lo que ya hace la librería estándar o
  una dependencia instalada". Escribe `progress/explore_sobreingenieria.md`;
  aquí va solo su resumen.

## 3. El producto (solo lo sabe el humano)

Qué se usa y qué no; qué falló con servicios reales (las tasks humanas);
qué pidió la gente y nunca llegó a `feature_list.json`.
~~~~~~~

### `.gitattributes`

~~~~~~~ fichero=.gitattributes
# Los hooks y los init.sh los ejecuta bash: con CRLF el shebang revienta.
*.sh text eol=lf
.githooks/* text eol=lf
~~~~~~~

### `.githooks/pre-commit`

~~~~~~~ fichero=.githooks/pre-commit
#!/usr/bin/env bash
# Ultima puerta antes de que un secreto exista dentro de un commit.
#
# El escaneo del CI corre DESPUES del push: para entonces el objeto ya esta
# servido y rotar el secreto obliga a reconfigurar cada servicio a mano.
# `git --staged` mira el indice, el unico momento en que el secreto todavia
# no existe en ningun sitio.
#
# Vive versionado en .githooks/ para que un clon nuevo lo tenga. Se activa una
# vez por clon (no viaja con el repo):
#   git config core.hooksPath .githooks
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# Regla dura: docs/ cambia solo con su entrada en docs/CHANGELOG.md. La
# misma comprobacion corre en el CI para quien no active este hook.
bash scripts/check_docs_changelog.sh

# Falla CERRADO: un escaner que se salta a si mismo cuando no esta instalado
# no es una puerta, es una sugerencia.
if ! command -v gitleaks >/dev/null 2>&1; then
  echo "pre-commit: falta gitleaks (https://github.com/gitleaks/gitleaks)." >&2
  exit 1
fi

# --redact para que el hallazgo no acabe en el scrollback de la terminal.
gitleaks git --staged --no-banner --redact --config .gitleaks.toml
~~~~~~~

### `.github/workflows/ci.yml`

~~~~~~~ fichero=.github/workflows/ci.yml
name: CI
on: [push, pull_request]

# Solo verifica: nada que desplegar ni ningun secreto que leer.
permissions:
  contents: read

jobs:
  verify:
    # Leccion: el CI corre en Linux y el autor quiza en Windows. Fallos que
    # solo aparecen aqui: bit de ejecucion de los .sh, `python` vs `python3`,
    # finales de linea CRLF en scripts, relojes monotonicos que empiezan cerca
    # de 0 en una maquina recien arrancada. Ver docs/verification.md.
    runs-on: ubuntu-latest
    steps:
      # Actions fijadas por SHA, no por etiqueta: una etiqueta se puede mover.
      - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5.1.0
        with:
          fetch-depth: 0   # historial completo: el paso de secretos lo escanea entero

      # Toolchains de cada stack. Fijar versiones: un CI que cambia de
      # comportamiento porque alguien publico una release no verifica lo mismo
      # dos veces seguidas.
      - uses: astral-sh/setup-uv@c18668ad3cf93ea998bef934396af7bb5c839dc7 # v10.2.0 (harness en Python)
      # - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0
      #   with: { node-version: 24, cache: npm, cache-dependency-path: <stack>/package-lock.json }
      # - <otras toolchains>

      - name: Instalar gitleaks (version fijada)
        run: |
          mkdir -p "$HOME/.local/bin"
          # Checksum antes de extraer: un binario descargado no se ejecuta a ciegas.
          curl -fsSL -o gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz
          echo "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb  gitleaks.tar.gz" | sha256sum -c -
          tar -xzf gitleaks.tar.gz -C "$HOME/.local/bin" gitleaks
          rm gitleaks.tar.gz
          echo "$HOME/.local/bin" >> "$GITHUB_PATH"

      # Los init.sh escanean el arbol de trabajo. Esto escanea la HISTORIA: un
      # secreto commiteado y borrado despues sigue ahi.
      - name: Secretos en el historial
        run: gitleaks detect --redact --config .gitleaks.toml

      # La misma regla que el pre-commit, para quien no lo active o use
      # --no-verify. Sin base (rama nueva) no hay rango que comparar.
      - name: docs/ con su entrada en docs/CHANGELOG.md
        env:
          BASE: ${{ github.event.pull_request.base.sha || github.event.before }}
        run: |
          if [ -n "$BASE" ] && [ "$BASE" != "0000000000000000000000000000000000000000" ]; then
            bash scripts/check_docs_changelog.sh "$BASE..HEAD"
          fi

      - name: Tests del harness
        run: uv run --with pytest --no-project pytest tests/ -q

      # Todos los stacks, no solo el de la feature activa: con todo `done` el
      # scope activo esta vacio y `./init.sh` daria verde sin verificar nada.
      # Falla si un stack no tiene init.sh, que es justo lo que se quiere.
      - name: Verificacion de todos los stacks
        run: bash init.sh --all
~~~~~~~

### `.gitignore`

~~~~~~~ fichero=.gitignore
# Secretos: nunca en git. La plantilla .env.example si.
.env
.env.*
.env-*
!.env.example
.envrc
*.pem
*.key

# Entornos y dependencias
.venv/
venv/
node_modules/
__pycache__/
*.py[cod]

# Salidas de build y caches
dist/
build/
coverage/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Anadir aqui lo propio de cada stack.
~~~~~~~

### `.gitleaks.toml`

~~~~~~~ fichero=.gitleaks.toml
title = "<NOMBRE_DEL_PROYECTO>"

[extend]
useDefault = true

# Una regla por cada secreto propio del proyecto (ver harness.json "secretos").
# Si el secreto tiene un formato reconocible, darle una regla: la regla
# generica solo lo pilla por entropia y puede fallar.
#
# [[rules]]
# id = "<proyecto>-token"
# description = "Token de <servicio>"
# regex = '''<prefijo>_[A-Za-z0-9]{32,}'''
# keywords = ["<prefijo>_"]

[allowlist]
description = "Falsos positivos conocidos"
# Se excusan por RUTA, nunca por VALOR: excusar un secreto falso por su valor
# desactivaria tambien su deteccion en los tests que prueban esta config.
# Se excusa el FICHERO concreto, nunca el directorio entero: un secreto real
# en otro fichero del mismo directorio tiene que seguir saltando.
#
# Leccion: en tests, preferir literales de BAJA entropia (p. ej.
# "sb_secret_test") a excusar rutas. Un literal que parece un secreto real
# dispara la regla generica y acaba en una allowlist que nadie revisa.
paths = [
  '''\.gitleaks\.toml$''',
  '''\.env\.example$''',
  # Dependencias de terceros: los init.sh escanean con --no-git, que ignora
  # .gitignore. Nada de esto se commitea.
  '''(^|/)\.venv/''',
  '''(^|/)node_modules/''',
]
~~~~~~~

### `CHECKPOINTS.md`

~~~~~~~ fichero=CHECKPOINTS.md
# Checkpoints de "done"

Cada ítem tiene un único dueño: dos agentes no se contradicen.

## Bloque funcional — dueño: `reviewer`

- Cada `R<n>` tiene un test que lo cubre de verdad (verificado con mutantes).
- Tabla `## Sabotajes` presente y reproducible.
- Tasks marcadas; task humana revisada y ejecutable paso a paso.
- `init.sh` en verde, ejecutado por el reviewer.
- Se respetan `docs/architecture.md`, `docs/principios.md` y las convenciones del stack.
- <RELLENAR: checkpoints funcionales propios del proyecto.>

## Bloque de escalabilidad — dueño: `reviewer`

- Stateless, o `design.md` justifica por qué no.
- Consultas nuevas con índice.
- Sin N+1.
- Sin límites sin acotar; los topes se cuentan en el origen.

## Bloque de seguridad — dueño: `security_reviewer`

- Sin secretos en código, specs ni artefactos públicos (bundles, apps).
- Todo input validado en el borde.
- Autorización explícita por objeto y por función en cada ruta tocada.
- Tabla de ataque completa para cada ruta o acción nueva.
- Credenciales temporales con caducidad.
- Configuración (escáner, lint, CSP, CORS) y runbooks revisados como código.
- Dependencias nuevas aprobadas y sin CVEs altos.
- <RELLENAR: riesgos propios del proyecto.>
~~~~~~~

### `CLAUDE.md`

~~~~~~~ fichero=CLAUDE.md
# <NOMBRE_DEL_PROYECTO>

<RELLENAR: qué es, para quién, en 3-5 líneas.>

## Rol de sesión

**Solo si eres la sesión principal** (no un subagente lanzado con `Agent`):
actúa como `leader` y sigue `.claude/agents/leader.md`. Los subagentes siguen
su propia definición y usan este fichero solo como contexto y reglas.

Dónde está cada regla: `docs/README.md`.

## Dónde vive cada pieza, y por qué

<!-- Cada fila resuelve una restricción concreta. Borra las que no apliquen. -->
| Pieza | Dónde | Por qué ahí |
|---|---|---|
| <RELLENAR: API> | <servicio> | <restricción que resuelve> |
| <RELLENAR: datos> | <servicio> | <…> |

## Restricciones que rompen cosas si se ignoran

- <RELLENAR: cada una con su motivo y su dueño en CHECKPOINTS.md.>

## Reglas duras

- **Nada de `git commit` ni `push` sin aprobación del humano** (los pide
  `settings.json`); nunca `--amend`, `push --force` ni reescritura de
  historia: el historial es la evidencia de qué iteración introdujo qué.
- **Ninguna dependencia nueva sin preguntar**, con una alternativa sin ella.
- **Los secretos no pasan por el contexto**: no se leen `.env` ni ficheros de
  secretos, no se imprimen, no se copian. Nombres en `harness.json`.
- **Nada destructivo sobre datos reales** (`DROP`, `TRUNCATE`, `DELETE` o
  `UPDATE` sin `WHERE`).
- **`done` solo por el protocolo**: el `implementer` en el cierre, con
  `review.md` y `security.md` de la misma IT en `APPROVED`.
- **`docs/`, este fichero y las reglas del harness los decide el humano.**
  Todo cambio en `docs/` lleva su entrada en `docs/CHANGELOG.md` en el mismo
  commit (el pre-commit y el CI lo comprueban).
- **Avisar antes de tocar servicios reales** y de si cuesta dinero.
  <RELLENAR: política de coste, p. ej. "solo planes gratuitos".>

## Parámetros del harness

| Parámetro | Valor | Por qué |
|---|---|---|
| Veredictos e `impl.md` | ≤ 200 líneas | el leader y los revisores los leen enteros; lo largo va a `evidence.md` |
| Spec (tres ficheros) | ~400 líneas (≈ 6-8 k tokens); partir pasado de 600 o de ~20 `R<n>` | cada agente la relee en cada iteración |
| Auditoría completa | proponerla cada 4 features cerradas o al cerrar una fase | cada revisión solo mira su diff |
| Reanudaciones de un agente | 2 | a la tercera, el atasco es real |

## Comandos

```bash
bash scripts/py.sh scripts/state.py   # qué toca (JSON)
bash init.sh                          # verifica el scope activo
bash init.sh --all                    # verifica todos los stacks
bash scripts/py.sh -m pytest tests/ -q   # tests del harness
```

## Al compactar

Conserva: feature, IT y acción de `state.py`; pendientes del humano;
ficheros modificados sin commitear.

## Estado

<RELLENAR: fases, orden, bloqueos conocidos, plataformas aplazadas con fecha.>
~~~~~~~

### `docs/CHANGELOG.md`

~~~~~~~ fichero=docs/CHANGELOG.md
# Cambios en docs/

Una entrada por cambio, la más reciente arriba. **Obligatoria**: el
pre-commit y el CI rechazan un cambio en `docs/` que no toque este fichero.
Junto a la regla cambiada, la marca `<!-- ajuste-AAAA-MM-DD -->`, para que la
retrospectiva pueda medir si sirvió.

Formato:

```
## AAAA-MM-DD — <título corto>
- Ficheros: docs/<…>.md
- Antes → ahora: <regla anterior> → <regla nueva>
- Por qué: <dato o incidente: FNN ITn, auditoría, métrica>
- Aprobado por: <humano>
- Propagado a: <CLAUDE.md, .claude/agents/x.md, CHECKPOINTS.md…> o "nada: <motivo>"
- Cómo se medirá: <qué mirar en metrics.csv o en los veredictos, si aplica>
```

## 2026-10-03 — Hotfix sin excepción "urgente" y etiqueta ATAJO:
- Ficheros: docs/specs.md, docs/principios.md
- Antes → ahora: hotfix "delante si es urgente" → siempre justo tras la
  feature en curso; atajo "comentario con su límite" → etiqueta literal
  `ATAJO: <límite> · <camino de mejora>`
- Por qué: delante de la feature en curso quedaban dos en curso (rompe
  test_como_mucho_una_feature_en_curso); sin etiqueta fija la retrospectiva
  no puede encontrar los atajos
- Aprobado por: <humano>
- Propagado a: .claude/skills/auditoria-seguridad/SKILL.md,
  .claude/skills/retrospectiva/SKILL.md, HARNESS.md

## <AAAA-MM-DD> — Creación de docs/ desde la plantilla
- Ficheros: todos los de docs/
- Antes → ahora: — → reglas iniciales del harness
- Por qué: arranque del proyecto
- Aprobado por: <humano>
- Propagado a: nada: es el punto de partida
~~~~~~~

### `docs/README.md`

~~~~~~~ fichero=docs/README.md
# Mapa de reglas

No contiene reglas: dice dónde está cada una. Cada rol lee solo lo suyo.

| Pregunta | Documento |
|---|---|
| ¿Qué es buen trabajo aquí? | `docs/architecture.md`, `docs/principios.md` |
| ¿Baseline de seguridad? | `docs/security.md` |
| ¿Proceso SDD y formato de las specs? | `docs/specs.md` |
| ¿Cómo se demuestra que algo funciona? ¿Pruebas con servicios reales? | `docs/verification.md` |
| ¿Convenciones de código? | `docs/<stack>/conventions.md` del scope activo, **solo ese** |
| ¿Cuándo está terminada una feature? | `CHECKPOINTS.md` |
| ¿Qué cambió en las reglas y por qué? | `docs/CHANGELOG.md` |
| ¿Qué hace cada rol? | `.claude/agents/<rol>.md` |
| ¿Auditorías completas? | `progress/audits/` y la skill `/auditoria-seguridad` |
| ¿Coste de cada agente y causa de cada rechazo? | `progress/metrics.csv` |
| ¿Retrospectiva? | skill `/retrospectiva` |
| ¿Por qué el harness es así? ¿Cómo se reconstruye? | `HARNESS.md` (ningún agente lo carga al trabajar) |
~~~~~~~

### `docs/architecture.md`

~~~~~~~ fichero=docs/architecture.md
# Arquitectura

## Estilo

<RELLENAR. Por defecto, **monolito modular**: un proceso por despliegue,
dividido en módulos que se llaman por funciones. Un servicio nuevo carga con
la prueba: qué problema paga la latencia y el despliegue extra.>

## Módulos y fronteras que no se cruzan

<RELLENAR: módulos, quién puede importar a quién, dónde viven los contratos
compartidos (una única definición para lo que cruza procesos).>

## Escalabilidad: las cuatro preguntas

Cada `design.md` las responde explícitamente:
1. **¿Es stateless?** Si guarda estado en memoria, ¿por qué es correcto si el
   proceso se reinicia o hay varias instancias?
2. **¿La consulta nueva tiene índice?** Nombrar las columnas.
3. **¿Hay algún límite sin acotar?** Listas, ficheros, colas, cuerpos. Los
   topes se cuentan en el origen (contar en la base de datos, no traer filas).
4. **¿Hay N+1?**

## Restricciones del entorno

Datos que caducan: cada fila con fecha y fuente.

| Restricción | Valor (fecha, fuente) | Consecuencia de diseño |
|---|---|---|
| <RELLENAR: memoria/CPU del hosting, arranque en frío, cuotas, límites de planes> | | |
~~~~~~~

### `docs/principios.md`

~~~~~~~ fichero=docs/principios.md
# Principios

Solo las posturas de este proyecto. Lo que cualquier ingeniero ya sabe
(SOLID, patrones de diseño, nombres claros) no se repite aquí. Ante un
conflicto, gana el código más simple que cumple la spec y se deja verificar.

- **Nada que no pida una spec aprobada** (sin "por si acaso"). La validación
  en fronteras de confianza y el manejo de errores que evita perder datos no
  son especulativos.
- **Nativo antes que dependencia**: biblioteca estándar → capacidad de la
  plataforma (constraint en la base de datos, elemento HTML) → dependencia ya
  instalada → nueva, y solo con aprobación.
- **Regla de tres**: no se abstrae hasta el tercer uso real. Una interfaz con
  una sola implementación y sin doble de test es ceremonia.
- **Una librería frágil, detrás de un adaptador en un único fichero**:
  cuando el tercero cambie, el arreglo cabe ahí.
- **DRY para conocimiento** (contratos, constantes de negocio, listas de
  secretos), no para código que se parece por casualidad.
- **Fallar pronto al arrancar**: una variable obligatoria que falta aborta
  con un mensaje que la nombra, nunca con su valor.
- **Parsear en el borde y confiar dentro**; estados como tipos cerrados.
- **Carreras con escritura condicional y constraints**, no con
  leer-comprobar-escribir. Reintentos idempotentes.
- **Nunca tragarse un error**: motivos cerrados hacia fuera, detalle saneado
  hacia el log.
- **Fallar abierto solo hacia un control posterior**: si una comprobación
  previa (p. ej. consultar a un tercero) falla, la petición sigue y la frena
  el control que ya existía, nunca un error 500. Un control de seguridad
  falla cerrado.
- **Sondeo antes que push** si nadie puede abrir conexiones hacia el cliente.
- **Atajos marcados**: un atajo deliberado lleva un comentario
  `ATAJO: <límite> · <camino de mejora>`, con esa etiqueta literal para que
  la retrospectiva pueda encontrarlos todos. <!-- ajuste-2026-10-03 -->
- <RELLENAR: posturas propias del proyecto.>
~~~~~~~

### `docs/security.md`

~~~~~~~ fichero=docs/security.md
# Seguridad

Lo que el `security_reviewer` exige. Los escáneres (gitleaks, auditoría de
dependencias) son el suelo, no el techo: él verifica su salida y revisa a
mano lo demás.

## Riesgos propios, ordenados por gravedad

<RELLENAR: los 3-6 riesgos de este proyecto, el más grave primero, con dónde
se controla cada uno (archivo, test, checkpoint).>

| Categoría OWASP API Top 10 | Dónde aparece aquí |
|---|---|
| <RELLENAR> | |

**El atacante no usa tu interfaz**: llama a la API y a los servicios
gestionados directamente, con cualquier clave pública del cliente.

## Secretos: cuatro capas

1. Permisos de `.claude/settings.json` (Read/Edit de `.env*`, `*.pem`,
   `*.key`). Si usas otras variantes de `.env`, añádelas.
2. Hook `scripts/guard_secrets.py`: bloquea comandos que leen `.env`,
   expanden un secreto de `harness.json` o vuelcan el entorno. Falla cerrado.
3. Pre-commit con gitleaks sobre el índice, `--redact`, falla cerrado.
4. CI: gitleaks sobre la historia completa.

- Los secretos **no pasan por el contexto de un agente** y viven solo donde
  se usan (panel del servicio, variables del sistema de la máquina que los
  necesita). **Mínimo privilegio**: cada proceso, solo los suyos.
- `.env.example` documenta nombres y formato, sin valores.
- Tokens generados con un CSPRNG, con un formato que la regla de gitleaks
  reconozca siempre (prefijo + hex).
- Un secreto que acaba en el chat o en un log se rota.
- **Lo que llega al cliente (bundle, app) es público**: lista cerrada de
  variables públicas, y el build falla ante cualquier otra.

## Lo que se revisa a mano

- **Autorización por objeto**: cada consulta filtra por propietario en la
  propia consulta. Un recurso ajeno responde igual que uno inexistente
  (código, cuerpo, tiempo).
- **Autorización por función**: rutas de admin con su comprobación; 401/403
  antes que errores de validación.
- **Asignación masiva**: los modelos de entrada rechazan campos extra; el
  propietario, los roles y los estados los pone el servidor.
- **Autenticación**: firma, algoritmo fijado, audiencia, emisor y caducidad;
  roles solo de claims que el usuario no puede editar; tokens de máquina
  distintos de los de usuario, con alcance mínimo y comparados en tiempo
  constante.
- **Input en el borde**: lista blanca (dominios, formatos), tipos estrictos,
  longitudes, sin caracteres de control. Normaliza Unicode (NFKC) **antes**
  de escapar: caracteres de ancho completo pueden volverse comodines tras
  una normalización posterior.
- **Datos de terceros son input del atacante** (títulos, nombres,
  descripciones): longitud acotada; nunca en rutas de fichero, argumentos de
  línea de comandos ni sumideros HTML.
- **SSRF**: nunca pasar una URL del usuario a algo que la resuelve; extraer
  el identificador y reconstruir la URL; lista blanca de hosts, sin
  redirecciones.
- **Consumo de recursos**: tope global de tamaño de cuerpo (contando bytes,
  no fiándose de la cabecera), y topes de páginas, ficheros, duración,
  elementos por usuario y tasa.
- **Credenciales temporales** (URLs firmadas, tokens) siempre caducan.
- **Logs y errores**: nunca tokens, URLs firmadas ni datos sensibles; los
  mensajes externos se sanean y se truncan; el usuario no ve rutas, consultas
  ni trazas.
- **Configuración como código**: CORS con orígenes exactos (un comodín o una
  entrada mal formada impide arrancar), documentación automática de la API
  apagada en producción, cabeceras de seguridad, reglas de lint que prohíben
  imports peligrosos (cubriendo importación dinámica, subrutas y acceso por
  corchetes).
- **Base de datos**: consultas parametrizadas; unicidad y carreras con
  constraints, no con un `if`.
- **Dependencias**: sin CVEs altos; cada paquete nuevo, aprobado.
- **Cadena de suministro**: actions del CI fijadas por SHA; binarios
  descargados con checksum.

## Si delegas la autenticación en un proveedor

- Registro público desactivado si el grupo es cerrado, con prueba de humo de
  que se rechaza.
- Sesiones anónimas del proveedor rechazadas explícitamente si no se usan.

## Si la base de datos se expone por API (p. ej. PostgREST o un BaaS)

- Toda tabla nueva con control de acceso por fila y permisos mínimos.
- Toda función nueva revoca la ejecución a los roles públicos: se puede
  llamar por RPC con la clave pública. Sin SQL dinámico y con `search_path`
  fijado.
- Una verificación global de solo lectura que lista lo accesible para los
  roles públicos y debe salir vacía.

## Si hay interfaz web

CSP restrictiva (orígenes de API y almacenamiento explícitos),
`frame-ancestors 'none'`, `Referrer-Policy: no-referrer` (una URL firmada no
sale en el `Referer`), sin `innerHTML`/`eval` con datos de la API, y la
sesión del cliente con su riesgo de XSS documentado.
~~~~~~~

### `docs/specs.md`

~~~~~~~ fichero=docs/specs.md
# El proceso SDD

Ninguna feature con `"sdd": true` se implementa sin spec escrita y aprobada.

```
pending ──spec_author──> spec_ready ──HUMANO──> in_progress ──vetos──> done
```

## Los tres ficheros (`specs/<F>/`, plantillas en `specs/_plantilla/`)

**`requirements.md` — el qué.** Notación EARS, `R1`, `R2`…, comportamiento
observable, nunca implementación:

| Forma | Plantilla |
|---|---|
| Ubicua | *El sistema DEBE `<respuesta>`* |
| Evento | *CUANDO `<disparador>`, el sistema DEBE `<respuesta>`* |
| Estado | *MIENTRAS `<estado>`, el sistema DEBE `<respuesta>`* |
| No deseada | *SI `<condición>`, ENTONCES el sistema DEBE `<respuesta>`* |
| Opcional | *DONDE `<característica>`, el sistema DEBE `<respuesta>`* |

Un requisito que no se puede convertir en test es un deseo ("debe ser
rápido" no; "DEBE responder en < 500 ms con 1.000 elementos" sí). Cada `R<n>`
con input enumera sus casos límite: vacío o solo espacios, longitud máxima,
caracteres de control, duplicado, servicio externo caído o lento.

**`design.md` — el cómo.** Ficheros y firmas; **alternativas descartadas y
por qué**; las cuatro preguntas de escalabilidad (`docs/architecture.md`);
preguntas al humano **con recomendación** (tras la respuesta, "Decisiones del
humano (fecha)"); sección vacía **"Desviaciones aprobadas"**, donde el
implementer *anexa* y nunca sobrescribe.

**`tasks.md` — los pasos.** `T1`, `T2`… con sus `R<n>`; no repite el diseño.
Con varios stacks o capas, agrupadas en **tramos** en orden de dependencia:
cada tramo es una IT aprobada antes del siguiente. Si hay servicios reales,
la última es la **prueba humana**, con `ÚNICA TASK CON SERVICIOS REALES` en
su cabecera. Mapa inverso `R<n> → T<n>` al final.

**Tamaño**: ~400 líneas entre los tres (≈ 6-8 k tokens). Cada cosa se dice
una vez, se cita `archivo:línea` en vez de copiar código y no hay
pseudocódigo de funciones enteras.

## Seguridad obligatoria

Si la feature toca input, auth, datos sensibles o acceso a datos, lleva
`R<n>` de seguridad verificables por test **aunque el `acceptance` no los
pida**: el security_reviewer mide el código contra ellos.

## La puerta humana

El leader resume la spec: qué hace, decisiones abiertas con recomendación,
dependencias nuevas, servicios reales y coste. Solo el humano mueve
`spec_ready → in_progress`.

**Enmiendas**: si el humano rechaza algo ya aprobado (p. ej. el aspecto de
una pantalla), se añaden secciones fechadas ("Enmienda AAAA-MM-DD", `R<n>`
nuevos a continuación), vuelve a pasar por la puerta y se sigue en nuevas IT
de la misma feature. Lo aprobado no se reescribe.

## Modo ligero (`"sdd": false`)

Para cambios pequeños y bien entendidos, el humano marca la feature con
`"sdd": false` al escribirla. No hay spec ni puerta de aprobación: el
`acceptance` hace de requisitos (cada línea, un `R<n>`) y la feature empieza
directamente por el implementer. **Los dos vetos se mantienen.** Si durante
la IT aparece una decisión de diseño de verdad, se pasa a `"sdd": true`.

## Iteraciones y cierre

- Cada vuelta vive en `progress/<F>/IT<n>/` (la crea el leader). El número de
  carpetas es el contador de intentos.
- `CHANGES_REQUESTED` → nueva IT. Un rechazo de seguridad re-verifica
  **ambos** vetos.
- **Correcciones de texto al cerrar**: si el único problema es texto en
  `specs/` o `progress/`, el reviewer aprueba y lista cada corrección
  literal; se aplican en el cierre. Nunca para código, tests, dependencias
  ni seguridad.
- **Cierre**: ambos `APPROVED` en la misma IT y sin tramos pendientes →
  correcciones de texto, `done`, entrada en `progress/history.md` (resumen
  redactado por el leader), `progress/current.md` al día. La task humana
  puede quedar pendiente en `current.md`.
- **Hotfix de una feature `done`**: no se reabre (`state.py` salta las
  `done` y solo admite una en curso). Se añade una feature nueva a
  `feature_list.json` (p. ej. `F01-fix1`), normalmente con `"sdd": false`,
  el bug y su test esperado en `acceptance`, colocada justo tras la que está
  en curso (delante, habría dos en curso). <!-- ajuste-2026-10-03 -->
- **Hallazgos de auditoría**: features nuevas con `archivo:línea` y el
  cambio propuesto copiados en su `acceptance`.
~~~~~~~

### `docs/verification.md`

~~~~~~~ fichero=docs/verification.md
# Verificación

Que un agente diga que algo funciona no es demostrarlo.

## `init.sh` es la puerta

```
bash init.sh            scope de la feature activa
bash init.sh --all      todos los scopes de harness.json (el CI usa este)
bash init.sh --dry-run  solo anuncia el scope
```

El raíz delega en `<scope>/init.sh`; **un scope sin `init.sh` bloquea**, no
se salta. Cada stack cubre, fallando a la primera:

| | <RELLENAR: stack A> | <RELLENAR: stack B> |
|---|---|---|
| tests | | |
| lint | | |
| formato | | |
| tipos | | |
| build | | |
| secretos | gitleaks `--redact` (config de la raíz) | ídem |
| dependencias | | |

## Un verificador tiene que saber fallar

Tras escribir cada paso, **planta un fallo a propósito** y comprueba que el
código de salida no es 0. Falsos verdes habituales: un comprobador de tipos
que con cierta configuración no comprueba nada; un test que compara un
literal que el código ya no usa; un arnés que pisa con un literal el valor
que dice proteger.

## TDD, sabotajes y mutantes

- **TDD**: test primero, verlo fallar **sobre el código real** (no con un
  script que imita el código viejo), implementar, verlo pasar.
- **Sabotajes** (implementer): borrar la línea crítica, ver caer un test,
  restaurar; encabezado `## Sabotajes` en `evidence.md`. `state.py` lo exige.
- **Mutantes** (reviewer): romper el código en una copia temporal y exigir
  que un test caiga. Mutante que sobrevive = test que falta.
- **Revertir solo la línea de producción**: si hace falta revertir también
  el test o el arnés, el test no protegía nada.

## Dobles de test

- **El doble prueba al llamador, no al adaptador.** Cada método nuevo de un
  adaptador real (repositorio, cliente HTTP, almacenamiento) lleva test
  propio con un **cliente grabador**: filtros exactos, valores escritos,
  cada rama de lectura (sin datos, nulo, válido).
- Un falso que ignora la petición puede validar un bug: si el código pagina
  o lee por bloques, el falso respeta el rango y los límites reales.
- El arnés restaura el **valor inicial capturado tras el import**.
- Comparar contra un servicio usa **la forma que el servicio devuelve**.

## Trazabilidad y presupuestos

- `impl.md`: tabla `R<n> → test` (fichero, test, aserción).
- `impl.md`, `review.md`, `security.md` ≤ 200 líneas, con citas; lo largo a
  `evidence.md`. **Una prueba no se borra por presupuesto, se mueve.** El
  leader no abre `evidence.md`; los revisores, solo para cuestionar una
  prueba.
- En `n > 1` se reduce el **contexto** (cambios pedidos, diff, ficheros
  tocados), nunca el trabajo: `init.sh` completo y checkpoints uno a uno.

## Portabilidad local ↔ CI

- `.sh` con bit de ejecución (`git update-index --chmod=+x`), `eol=lf` en
  `.gitattributes`, y llamados además con `bash script.sh`.
- Python: `sys.executable` en tests; en shell, `scripts/py.sh` (prueba
  `python3`, `python`, `py` **ejecutándolos**).
- `bash` desde Python en Windows: `shutil.which("bash")`, no `"bash"` (que
  resuelve antes a la de WSL).
- Relojes monotónicos: estado inicial `-inf`, no `0`.
- Si algo solo falla en el CI, sospecha primero de estas.

## Lo que no se puede verificar con tests

Se dice en el veredicto y se verifica a mano con un protocolo escrito y su
resultado registrado. <RELLENAR: casos propios, p. ej. comportamiento en un
dispositivo físico.> Nunca se declara verificado sin más.

## Pruebas con servicios reales (task humana)

La revisa el reviewer **ya en IT1** y la ejecuta el humano al final.

- Avisa de que conecta con servicios reales y de si puede costar dinero.
- **Orden ejecutable**: recursos antes de referenciarlos; variables antes
  del primer despliegue; migraciones antes que el código que las usa; el
  proceso que valida antes que los que confían en él.
- Pasos copiables, con el resultado esperado de cada uno; si falla, qué pegar
  (solo el final del error, sin valores sensibles).
- **Nunca pedir que se pegue un secreto.**
- Ten en cuenta la terminal real: variables reservadas y alias del shell;
  ventanas de credenciales que no reciben el foco en consolas integradas.
- Verificaciones de base de datos de solo lectura; nada destructivo a mano.
- Reinicia los procesos de larga duración tras cambiar su código o sus
  dependencias. Comprueba el commit desplegado antes de probar.
- Opciones de panel que el código no controla (registro público, accesos
  anónimos…): comprobarlas y anotarlas.
- Datos de proveedores (planes, cuotas, menús): documentación actual, con
  fecha.
- Resultado a `evidence.md` como resumen (códigos, estados, nunca tokens).
~~~~~~~

### `feature_list.json`

~~~~~~~ fichero=feature_list.json
[
  {
    "id": "F01",
    "title": "<Primera feature: la mas pequena que demuestre la arquitectura de punta a punta>",
    "status": "pending",
    "sdd": true,
    "scope": ["<stack-a>"],
    "acceptance": [
      "<Comportamiento observable 1, comprobable por test>",
      "<Comportamiento observable 2>"
    ]
  }
]
~~~~~~~

### `harness.json`

~~~~~~~ fichero=harness.json
{
  "proyecto": "<NOMBRE_DEL_PROYECTO>",
  "scopes": ["<stack-a>", "<stack-b>"],
  "secretos": ["<NOMBRE_DE_VARIABLE_SECRETA_1>", "<NOMBRE_DE_VARIABLE_SECRETA_2>"]
}
~~~~~~~

### `init.sh`

~~~~~~~ fichero=init.sh
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

# El interprete lo elige scripts/py.sh (python3/python/py, el que arranque).
PY="bash scripts/py.sh"

if [ "$ALL" -eq 1 ]; then
  SCOPES="$($PY -c 'import json; print(" ".join(json.load(open("harness.json", encoding="utf-8"))["scopes"]))')"
else
  SCOPES="$($PY scripts/state.py | $PY -c \
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
~~~~~~~

### `plantillas/stack/conventions-web.md`

~~~~~~~ fichero=plantillas/stack/conventions-web.md
# Convenciones de interfaz web — material para copiar

<!-- Solo si el proyecto tiene interfaz web. Copia a
docs/<stack>/conventions.md lo que aplique; cada punto salió de una
iteración rechazada en un proyecto real. -->

- **Cada spec que crea pantallas define su aspecto.** Una pantalla sin
  estilos no está terminada (un reset CSS puede dejar los campos de un
  formulario invisibles). No dejar el diseño para una feature final: una
  feature aprobada funcionalmente puede reabrirse si el humano rechaza el
  aspecto. Base visual común (paleta, tipografía, componentes) en una carpeta
  que cada spec reutiliza.
- **Nunca un spinner indefinido**: todo estado de espera dice **qué** se
  espera y **por qué** (servicio dormido, proceso desconectado, motivo real
  del fallo). Los estados raros legítimos, sin explicar, parecen fallos.
- **Fluidez**: caché de lecturas en memoria (esqueleto en la primera carga;
  al volver, lo anterior con indicador de refresco; una sola petición por
  ruta en vuelo; un refresco fallido conserva los datos). Mutaciones
  optimistas, en serie por recurso, sin duplicados, con reversión y aviso.
  Al volver atrás se restaura el scroll y el estado de la vista. Todo se
  vacía al cerrar sesión, al expirar y al cambiar de usuario.
- **El estado de servidor no se duplica en estado local.**
- **Un solo envío a la vez por acción** (botón inactivo mientras dura).
- **Variables públicas del bundle**: lista cerrada; el build falla ante
  otra.
- **La capa de UI no importa el cliente de datos** directamente: regla de
  lint que cubra importación dinámica, subrutas y acceso por corchetes.
- **Sin sumideros HTML** (`innerHTML`, `dangerouslySetInnerHTML`, `eval`)
  con datos de la API.
- **Almacenamiento del navegador puede fallar** (ventana privada, cuotas):
  todo acceso en `try/catch`; solo identificadores y números, validados al
  leer y borrados al cerrar sesión.
- **Respuestas de la API parseadas estrictamente**; otra forma da
  "respuesta inesperada", nunca un render roto. Ids de ruta validados antes
  de llamar a la API.
- **Tests de lo que ve el usuario** (textos, roles), no de la estructura.
- **Restricciones de plataforma que rompen cosas**, escritas con su motivo
  (p. ej. APIs que un sistema operativo móvil suspende con la pantalla
  bloqueada).
- **Accesibilidad básica**: foco devuelto al cerrar diálogos; atajos de
  teclado ignorados dentro de campos de texto.
~~~~~~~

### `plantillas/stack/conventions.md`

~~~~~~~ fichero=plantillas/stack/conventions.md
# Convenciones — <stack>

<!-- Copiar a docs/<stack>/conventions.md. Solo lo que difiere de las
convenciones estándar del lenguaje: lo que el modelo ya sabe no se escribe.
Si el stack tiene interfaz web, copiar también lo que aplique de
plantillas/stack/conventions-web.md. -->

<Lenguaje y versión.> Se lee solo cuando el scope activo incluye <stack>.
La configuración de las herramientas manda; esto explica el porqué.

## Herramientas
<Tests · lint · formato · tipos · build · auditoría, con el comando.
Casos donde el comprobador se queda corto y cómo se acota.>

## Idioma
<Código en … / prosa en … / nombres de test que describen comportamiento.>

## Errores
<Cómo se lanzan, qué ve el usuario, qué va al log.>

## Modelos / tipos
<Entrada ≠ fila; campos extra rechazados; tipos cerrados para estados.>

## Concurrencia
<Qué es bloqueante, dónde se ejecuta.>

## Tests
<Framework; qué se prueba; dobles; adaptador real con cliente grabador;
límites contra el literal de la spec.>

## Estructura
<Módulos, fronteras, dónde vive lo compartido.>

## Patrones prohibidos
<Lista, cada uno con su motivo.>
~~~~~~~

### `plantillas/stack/init.sh`

~~~~~~~ fichero=plantillas/stack/init.sh
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
~~~~~~~

### `progress/audits/README.md`

~~~~~~~ fichero=progress/audits/README.md
# Auditorías de seguridad completas

Una carpeta por auditoría, `<AAAA-MM-DD>/` (`-2` si hay dos el mismo día),
nunca dentro de una feature ni de una IT. Procedimiento: skill
`/auditoria-seguridad`.

```
informe.md     hallazgos con gravedad y archivo:línea (security_reviewer)
evidencia.md   anexo: tabla de ataque, pruebas, lo que está limpio
cambios.md     destino de cada hallazgo (leader, con el humano)
```

Sin `cambios.md` la auditoría está pendiente y `state.py` lo avisa
(`audits_pending`). Con él, se lee `cambios.md` y nunca el informe.
~~~~~~~

### `progress/current.md`

~~~~~~~ fichero=progress/current.md
# Sesión activa

<Feature, estado, rama, siguiente acción de state.py. Se sobrescribe; lo
cerrado va a history.md.>

## Pendientes del humano

- <Tasks humanas, decisiones, auditoría a proponer.>

## Arreglos del leader

<!-- - AAAA-MM-DD — <fichero>: <qué> · <por qué> · <qué arrastra> -->
~~~~~~~

### `progress/history.md`

~~~~~~~ fichero=progress/history.md
# Bitácora

Append-only. Un resumen por feature cerrada, redactado por el leader:

```
## FNN — <título> (done, AAAA-MM-DD, IT<n>)
- Entrega: <qué hace, con R<n> y ficheros clave>.
- Iteraciones: <IT1 qué falló, IT2…>.
- Task humana: <ejecutada / pendiente>.
Observaciones abiertas, que no bloquean: <…>.
```
~~~~~~~

### `progress/metrics.csv`

~~~~~~~ fichero=progress/metrics.csv
fecha,feature,it,rol,tokens,minutos,veredicto,causa
~~~~~~~

### `progress/para_la_plantilla.md`

~~~~~~~ fichero=progress/para_la_plantilla.md
# Lecciones para la plantilla

Lo que este proyecto aprende y serviría en cualquier otro. No se edita aquí
`HARNESS.md` (es una copia de la plantilla): se anota y se lleva al repo de
la plantilla cuando toque.

<!-- Formato: - AAAA-MM-DD — <lección> → <regla o test propuesto> (origen: FNN ITn) -->
~~~~~~~

### `scripts/__init__.py`

~~~~~~~ fichero=scripts/__init__.py

~~~~~~~

### `scripts/check_docs_changelog.sh`

~~~~~~~ fichero=scripts/check_docs_changelog.sh
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
~~~~~~~

### `scripts/guard_secrets.py`

~~~~~~~ fichero=scripts/guard_secrets.py
#!/usr/bin/env python3
"""PreToolUse (Bash|PowerShell): bloquea comandos que pueden sacar un secreto.

Los permisos `deny` de settings.json cubren Read/Grep/Edit, pero para la
shell solo comparan prefijos de texto: `type backend\\.env`, `Get-Content`
o `$env:MI_TOKEN` los esquivan. Este hook mira el comando entero.

Los nombres de los secretos salen de `harness.json` ("secretos"), para que
no haya una segunda lista que se desincronice.

Exit 2 = bloqueado; el motivo va por stderr y lo lee el agente.
"""
import json
import re
import shlex
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_ENV = re.compile(r"(?<![\w-])\.env(?!\.example\b)(?!\w)")
_BUSCADORES = {"grep", "egrep", "fgrep", "rg"}


def _secretos() -> tuple[str, ...]:
    try:
        datos = json.loads((RAIZ / "harness.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ()
    return tuple(s for s in datos.get("secretos", []) if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", s))


def _reglas() -> list[tuple[re.Pattern[str], str]]:
    reglas = [
        # Volcar el entorno entero.
        (re.compile(r"(^|[;&|(]\s*)(printenv|env|set|export\s+-p)\s*($|[;&|)])"),
         "vuelca todas las variables de entorno"),
        (re.compile(r"\b(Get-ChildItem|gci|dir|ls|Get-Item|gi)\s+env:", re.I),
         "vuelca todas las variables de entorno"),
        (re.compile(r"\[Environment\]::GetEnvironmentVariables", re.I),
         "vuelca todas las variables de entorno"),
    ]
    nombres = "|".join(_secretos())
    if nombres:
        reglas += [
            # Expandir el valor: $X, ${X}, $env:X, %X%.
            (re.compile(rf"(\$\{{?|\$env:|%)({nombres})\b", re.I),
             "expande el valor de un secreto"),
            (re.compile(rf"(environ|getenv|process\.env)\W+({nombres})\b", re.I),
             "lee el valor de un secreto desde codigo"),
        ]
    return reglas


def _sin_patron_de_busqueda(comando: str) -> str:
    """`grep -n "x.env" notas.txt` busca un texto, no lee un .env.

    Solo para un buscador suelto (sin tuberias ni encadenados): se quita su
    primer argumento posicional, que es el patron. Ante cualquier duda se
    devuelve el comando entero, y la regla de .env sigue mirandolo todo.
    """
    if re.search(r"[;&|`$<>]", comando):
        return comando
    try:
        partes = shlex.split(comando)
    except ValueError:
        return comando
    if not partes or Path(partes[0]).name not in _BUSCADORES:
        return comando
    # Con -e/-f/--regexp/--file el patron va en la opcion y el primer
    # posicional ya es un fichero. Leccion: `grep -e. .env` quitaba el .env.
    if any(re.match(r"-[^-]*[ef]|--(regexp|file)\b", p) for p in partes[1:]):
        return comando
    for i, p in enumerate(partes[1:], 1):
        if not p.startswith("-"):
            return " ".join(partes[:i] + partes[i + 1:])
    return comando


def motivo(comando: str) -> str | None:
    # Cualquier fichero .env (tambien .env-prod) salvo la plantilla
    # .env.example. `.venv` no casa: el punto va delante de la v, no de la e.
    if _ENV.search(_sin_patron_de_busqueda(comando)):
        return "toca un fichero .env (solo .env.example es legible)"
    for patron, texto in _reglas():
        if patron.search(comando):
            return texto
    return None


def main() -> int:
    try:
        # lstrip: algunas shells de Windows anteponen un BOM al reenviar stdin.
        # Bytes en UTF-8: en Windows sys.stdin decodifica con la pagina ANSI.
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace").lstrip("﻿"))
        comando = (entrada.get("tool_input") or {}).get("command") or ""
    except (ValueError, AttributeError):
        # Falla cerrado: una entrada que no se entiende no se da por segura.
        print("Bloqueado por scripts/guard_secrets.py: entrada del hook ilegible.",
              file=sys.stderr)
        return 2
    razon = motivo(comando)
    if razon is None:
        return 0
    print(f"Bloqueado por scripts/guard_secrets.py: el comando {razon}. "
          "Los secretos no pasan por el contexto de un agente (CLAUDE.md, "
          "Reglas duras). Si hace falta, pideselo al humano.",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
~~~~~~~

### `scripts/harness_bundle.py`

~~~~~~~ fichero=scripts/harness_bundle.py
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
~~~~~~~

### `scripts/py.sh`

~~~~~~~ fichero=scripts/py.sh
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
~~~~~~~

### `scripts/session_start.sh`

~~~~~~~ fichero=scripts/session_start.sh
#!/usr/bin/env bash
# SessionStart (startup, resume, clear, compact): inyecta el estado que los
# agentes ya dejaron en disco. Solo concatena; no interpreta nada.
#
# Corto a proposito: Claude Code recorta la salida de un hook a 10.000
# caracteres (deja un preview de 2.000). Por eso no vuelca los veredictos:
# da sus rutas y el leader lee lo que necesite.
set -uo pipefail
# La raiz es la del propio script, no la del directorio actual.
cd "$(dirname "$0")/.." || exit 0
PY="bash scripts/py.sh"

echo "=== state.py ==="
ESTADO="$($PY scripts/state.py 2>/dev/null || echo '{"error": "scripts/state.py fallo"}')"
echo "$ESTADO"

echo
echo "=== progress/current.md (primeras 80 lineas) ==="
if [ -f progress/current.md ]; then head -n 80 progress/current.md; else echo "(no existe)"; fi

FEATURE="$(printf '%s' "$ESTADO" | $PY -c \
  'import json,sys; print(json.load(sys.stdin).get("feature",""))' 2>/dev/null || true)"
[ -z "$FEATURE" ] && exit 0
IT="$(ls -d "progress/$FEATURE"/IT* 2>/dev/null | sort -V | tail -1 || true)"
[ -z "$IT" ] && exit 0

echo
echo "=== Ultima iteracion: $IT ==="
# evidence.md no se lista: el leader no lo lee nunca.
for f in impl.md review.md security.md; do
  [ -f "$IT/$f" ] && echo "$IT/$f"
done
exit 0
~~~~~~~

### `scripts/state.py`

~~~~~~~ fichero=scripts/state.py
#!/usr/bin/env python3
"""Estado de despacho del harness. Lo invoca el leader en cada arranque.

Devuelve en una linea de JSON que feature toca y que accion. Deriva todo del
disco (feature_list.json, specs/<F>/tasks.md y progress/<F>/IT<n>/): no hay
ningun estado aparte que mantener sincronizado.

Los marcadores que lee son fijos (HARNESS.md, "Marcadores"): la linea
`Veredicto: APPROVED|CHANGES_REQUESTED`, el encabezado `## Sabotajes` y
`SERVICIOS REALES` en la cabecera de la task humana.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Solo cuenta una linea propia de veredicto. Leccion: buscar la palabra en
# todo el fichero leia como rechazo un APPROVED que citaba la IT anterior.
_VEREDICTO = re.compile(r"^\W*Veredicto\W*(APPROVED|CHANGES_REQUESTED)\b", re.M | re.I)
_SABOTAJES = re.compile(r"^#{2,3}\s*Sabotajes\b", re.M)
# Con o sin negrita: una task sin `**` no puede quedar fuera del recuento.
_TASK_ABIERTA = re.compile(r"^\s*[-*]\s+\[ \]\s*\**\s*T\d+.*$", re.M)
_TASK_HUMANA = ("SERVICIOS REALES", "PRUEBA REAL")


def _leer(ruta: Path) -> str:
    # errors="replace": un fichero guardado en ANSI no debe tumbar el despacho.
    return ruta.read_text(encoding="utf-8", errors="replace")


def _ultima_iteracion(feature_id: str) -> int:
    carpeta = ROOT / "progress" / feature_id
    if not carpeta.is_dir():
        return 0
    its = []
    for d in carpeta.iterdir():
        m = re.fullmatch(r"IT(\d+)", d.name)
        if m and d.is_dir():
            its.append(int(m.group(1)))
    return max(its, default=0)


def _veredicto(feature_id: str, it: int, fichero: str) -> str | None:
    """APPROVED, CHANGES_REQUESTED, o None si no hay linea de veredicto."""
    ruta = ROOT / "progress" / feature_id / f"IT{it}" / fichero
    if not ruta.is_file():
        return None
    m = _VEREDICTO.search(_leer(ruta))
    return m.group(1).upper() if m else None


# Paso 6 del implementer: sin la tabla de sabotajes no se gasta una revision.
def _tiene_sabotajes(feature_id: str, it: int) -> bool:
    carpeta = ROOT / "progress" / feature_id / f"IT{it}"
    return any(_SABOTAJES.search(_leer(carpeta / f))
               for f in ("impl.md", "evidence.md") if (carpeta / f).is_file())


# Iteraciones por tramos: tasks sin marcar que no son la humana.
def _tasks_pendientes(feature_id: str) -> int:
    ruta = ROOT / "specs" / feature_id / "tasks.md"
    if not ruta.is_file():
        return 0
    # "PRUEBA REAL" es el marcador de la plantilla anterior: sin el, una spec
    # vieja abria tramos para siempre con una task que nadie puede ejecutar.
    return sum(not any(m in t for m in _TASK_HUMANA) for t in _TASK_ABIERTA.findall(_leer(ruta)))


# Una auditoria sin cambios.md tiene hallazgos sin destino.
def _auditorias_pendientes() -> list[str]:
    carpeta = ROOT / "progress" / "audits"
    if not carpeta.is_dir():
        return []
    return sorted(d.name for d in carpeta.iterdir() if d.is_dir() and not (d / "cambios.md").is_file())


def next_action() -> dict:
    r = _despacho()
    pendientes = _auditorias_pendientes()
    return {**r, "audits_pending": pendientes} if pendientes else r


def _despacho() -> dict:
    features = json.loads(_leer(ROOT / "feature_list.json"))
    activa = next((f for f in features if f["status"] != "done"), None)
    if activa is None:
        return {"action": "TODO_HECHO"}

    fid, estado = activa["id"], activa["status"]
    base = {"feature": fid, "status": estado, "scope": activa["scope"]}

    # Modo ligero: "sdd": false lo decide el humano al escribir la feature, y
    # sustituye a la spec y a su aprobacion. Los dos vetos se mantienen.
    if activa.get("sdd", True) is False:
        base["modo"] = "ligero"
    elif estado == "pending":
        return {**base, "iteration": 0, "action": "LANZAR_SPEC_AUTHOR"}
    elif estado == "spec_ready":
        return {**base, "iteration": 0, "action": "PEDIR_APROBACION_HUMANA"}

    it = _ultima_iteracion(fid)
    if it == 0:
        return {**base, "iteration": 1, "action": "CREAR_IT1_Y_LANZAR_IMPLEMENTER"}

    base = {**base, "iteration": it}

    # Leccion: una IT sin impl.md se despachaba como "revisar". Sin impl.md el
    # implementer se paro a medias: se reanuda el mismo agente, no uno nuevo.
    if not (ROOT / "progress" / fid / f"IT{it}" / "impl.md").is_file():
        return {**base, "action": "REANUDAR_IMPLEMENTER"}
    if not _tiene_sabotajes(fid, it):
        return {**base, "action": "DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES"}

    review = _veredicto(fid, it, "review.md")
    security = _veredicto(fid, it, "security.md")

    if review is None:
        return {**base, "action": "LANZAR_REVIEWER"}
    if review == "CHANGES_REQUESTED":
        return {**base, "action": f"CREAR_IT{it + 1}_LANZAR_IMPLEMENTER_LUEGO_REVIEWER"}
    if security is None:
        return {**base, "action": "LANZAR_SECURITY_REVIEWER"}
    if security == "CHANGES_REQUESTED":
        # Un fix de seguridad puede alterar comportamiento ya aprobado
        # funcionalmente, asi que se re-verifica el reviewer ANTES que seguridad.
        return {
            **base,
            "action": f"CREAR_IT{it + 1}_LANZAR_IMPLEMENTER_LUEGO_REVIEWER_Y_SECURITY",
        }
    if _tasks_pendientes(fid):
        return {**base, "action": f"CREAR_IT{it + 1}_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO"}
    return {**base, "action": "LANZAR_IMPLEMENTER_CIERRE_MARCAR_DONE"}


if __name__ == "__main__":
    print(json.dumps(next_action(), ensure_ascii=False))
~~~~~~~

### `specs/_plantilla/design.md`

~~~~~~~ fichero=specs/_plantilla/design.md
# FNN — <Título> · Design

## Ficheros

| Fichero | Cambio |
|---|---|
| `<ruta>` | <nuevo / qué cambia> |

## Firmas nuevas
```
<interfaces, funciones, modelos>
```

## Decisiones
1. **<Decisión>.** <Motivo; fuente y fecha si depende de un tercero.>

## Alternativas descartadas
1. **<Alternativa>** — <por qué no>.

## Escalabilidad
1. ¿Stateless? <…>
2. ¿Índices? <columnas>
3. ¿Límites acotados? <topes y cómo se cuentan>
4. ¿N+1? <…>

## Preguntas para el humano
1. <Pregunta> — **Recomendación:** <…>.
<(Tras la respuesta, esta sección pasa a "Decisiones del humano (fecha)".)>

## Desviaciones aprobadas
<Vacía. El implementer anexa aquí; nunca se sobrescribe.>
~~~~~~~

### `specs/_plantilla/requirements.md`

~~~~~~~ fichero=specs/_plantilla/requirements.md
# FNN — <Título> · Requirements

<Contexto en 3 líneas: qué problema resuelve y para quién.>

## Requisitos

### <Grupo 1>
- **R1** — CUANDO <disparador>, el sistema DEBE <respuesta observable>.
- **R2** — SI <condición no deseada>, ENTONCES el sistema DEBE <respuesta>.

### Seguridad
- **R3** [seguridad] — <control verificable por test: autorización, validación, límite, secreto…>.

## Acceptance → requisitos

| Acceptance de feature_list.json | Requisitos |
|---|---|
| <texto> | R1, R2 |

## Fuera de alcance
- <Lo que NO hace esta feature y en qué feature entra, si aplica.>
~~~~~~~

### `specs/_plantilla/tasks.md`

~~~~~~~ fichero=specs/_plantilla/tasks.md
# FNN — <Título> · Tasks

Concisa: cada task remite a design.md, no lo repite. Con varios stacks o
capas, un tramo por bloque, en orden de dependencia; cada tramo es una IT.

## Tramo A — <stack o capa que los demás consumen>
- [ ] **T1 — <título>** (TDD). <Qué se prueba primero y qué se implementa.> → R1, R2
- [ ] **T2 — Test del adaptador real** con cliente grabador: filtros exactos, valores escritos, ramas de lectura. → R3

## Tramo B — <siguiente>
- [ ] **T3 — <título>**. <…> → R4

## Cierre
- [ ] **T4 — ÚNICA TASK CON SERVICIOS REALES · la ejecuta el humano.** Aviso: conecta con <servicios>. Pasos en orden ejecutable, resultado esperado de cada uno, ningún secreto pegado. → humo de R1, R3

<!-- Si no hay servicios reales, borra T4. La cabecera "SERVICIOS REALES" es
un marcador que lee scripts/state.py: no la traduzcas. -->

## Mapa inverso

| Requisito | Task |
|---|---|
| R1, R2 | T1, T4 |
| R3 | T2, T4 |
| R4 | T3 |
~~~~~~~

### `tests/test_docs_changelog.py`

~~~~~~~ fichero=tests/test_docs_changelog.py
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "scripts/check_docs_changelog.sh"
# Ruta completa: en Windows, "bash" a secas resuelve antes a System32 (WSL)
# que al PATH, y esa bash vuelve a expandir los argumentos.
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="sin bash")


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _repo(tmp_path, ficheros):
    _git(tmp_path, "init", "-q")
    for ruta in ficheros:
        f = tmp_path / ruta
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    _git(tmp_path, "add", *ficheros)


def _check(tmp_path, *args):
    return subprocess.run([BASH, str(SCRIPT), *args], cwd=tmp_path,
                          capture_output=True, text=True)


def test_cambio_en_docs_sin_changelog_bloquea(tmp_path):
    _repo(tmp_path, ["docs/security.md"])
    r = _check(tmp_path)
    assert r.returncode == 1
    assert "docs/security.md" in r.stderr


def test_cambio_en_docs_con_changelog_pasa(tmp_path):
    _repo(tmp_path, ["docs/security.md", "docs/CHANGELOG.md"])
    assert _check(tmp_path).returncode == 0


def test_cambio_fuera_de_docs_no_exige_changelog(tmp_path):
    _repo(tmp_path, ["src/main.py"])
    assert _check(tmp_path).returncode == 0


def test_rango_de_commits_para_el_ci(tmp_path):
    _repo(tmp_path, ["src/main.py"])
    _git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "a")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/specs.md").write_text("x", encoding="utf-8")
    _git(tmp_path, "add", "docs/specs.md")
    _git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "b")
    assert _check(tmp_path, "HEAD~1..HEAD").returncode == 1


def test_el_pre_commit_y_el_ci_usan_el_script():
    assert "scripts/check_docs_changelog.sh" in (RAIZ / ".githooks/pre-commit").read_text(encoding="utf-8")
    assert "scripts/check_docs_changelog.sh" in (RAIZ / ".github/workflows/ci.yml").read_text(encoding="utf-8")
~~~~~~~

### `tests/test_feature_list.py`

~~~~~~~ fichero=tests/test_feature_list.py
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VALID_STATUS = {"pending", "spec_ready", "in_progress", "done"}


def _features():
    return json.loads((RAIZ / "feature_list.json").read_text(encoding="utf-8"))


def _scopes():
    return set(json.loads((RAIZ / "harness.json").read_text(encoding="utf-8"))["scopes"])


def test_es_json_valido_y_lista():
    assert isinstance(_features(), list)


def test_ids_unicos():
    ids = [f["id"] for f in _features()]
    assert len(ids) == len(set(ids))


def test_campos_obligatorios_y_valores_validos():
    scopes = _scopes()
    for f in _features():
        assert f["status"] in VALID_STATUS, f["id"]
        assert isinstance(f["sdd"], bool), f["id"]
        assert f["scope"], f["id"]
        assert set(f["scope"]) <= scopes, f"{f['id']}: scope fuera de harness.json"


def test_no_hay_contador_de_intentos():
    # El numero de carpetas IT<n> ya es esa senal; un contador aparte se
    # desincroniza.
    for f in _features():
        assert "review_attempts" not in f, f["id"]


def test_como_mucho_una_feature_en_curso():
    en_curso = [f["id"] for f in _features() if f["status"] in {"spec_ready", "in_progress"}]
    assert len(en_curso) <= 1, en_curso
~~~~~~~

### `tests/test_guard_secrets.py`

~~~~~~~ fichero=tests/test_guard_secrets.py
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import guard_secrets  # noqa: E402


@pytest.fixture(autouse=True)
def _secretos_de_prueba(tmp_path, monkeypatch):
    (tmp_path / "harness.json").write_text(
        json.dumps({"secretos": ["MI_TOKEN", "DB_PASSWORD"]}), encoding="utf-8")
    monkeypatch.setattr(guard_secrets, "RAIZ", tmp_path)


BLOQUEADOS = [
    "cat backend/.env",
    "type backend\\.env",
    "Get-Content backend/.env",
    "grep KEY .env",
    "cp backend/.env /tmp/x",
    "cat .env.local",
    "echo $MI_TOKEN",
    "echo ${DB_PASSWORD}",
    "Write-Output $env:MI_TOKEN",
    "echo %DB_PASSWORD%",
    "python -c \"import os; print(os.environ['MI_TOKEN'])\"",
    "node -e \"console.log(process.env.MI_TOKEN)\"",
    "printenv",
    "env | grep TOKEN",
    "set",
    "Get-ChildItem env:",
    "gci Env:",
    # El patron de busqueda se ignora, pero el fichero buscado no.
    "grep -e KEY .env",
    "grep -n TOKEN .env | head",
    "rg KEY backend/.env",
    # Leccion: con el patron dentro de la opcion se quitaba el .env.
    "grep -e. .env",
    "grep -ne. .env",
    "rg --regexp=. .env",
    "grep -f .env x",
    "cat .env-prod",
]

PERMITIDOS = [
    "cat backend/.env.example",
    "source backend/.venv/bin/activate",
    "grep -rn MI_TOKEN src",
    "python scripts/state.py",
    "git status",
    "./init.sh --all",
    "env FOO=1 pytest",
    # Leccion: buscar el TEXTO ".env" en la documentacion no lee ningun .env.
    'grep -n "./.env" notas.txt',
    "rg '\\.env' docs",
]


@pytest.mark.parametrize("comando", BLOQUEADOS)
def test_bloquea(comando):
    assert guard_secrets.motivo(comando) is not None


@pytest.mark.parametrize("comando", PERMITIDOS)
def test_permite(comando):
    assert guard_secrets.motivo(comando) is None


def _hook(entrada: str):
    return subprocess.run([sys.executable, str(RAIZ / "scripts/guard_secrets.py")],
                          input=entrada.encode("utf-8"), capture_output=True)


def test_hook_bloquea_con_codigo_2():
    assert _hook(json.dumps({"tool_input": {"command": "printenv"}})).returncode == 2


def test_hook_deja_pasar_lo_seguro_aunque_venga_con_bom():
    assert _hook("﻿" + json.dumps({"tool_input": {"command": "git status"}})).returncode == 0


def test_hook_falla_cerrado_si_la_entrada_es_ilegible():
    assert _hook("esto no es json").returncode == 2


BASH = shutil.which("bash")


@pytest.mark.skipif(BASH is None, reason="sin bash")
def test_lanzador_sin_python_bloquea():
    # Leccion: un hook cuyo interprete no existe es un error NO bloqueante en
    # Claude Code; el lanzador convierte ese caso en un bloqueo (codigo 2).
    r = subprocess.run([BASH, str(RAIZ / "scripts/py.sh"), "-c", "pass"],
                       env={"PATH": "/nonexistent"}, capture_output=True, text=True)
    assert r.returncode == 2


@pytest.mark.skipif(BASH is None, reason="sin bash")
def test_lanzador_con_python_ejecuta():
    # Sin comillas en el argumento: la bash de Git en Windows las quita.
    r = subprocess.run([BASH, str(RAIZ / "scripts/py.sh"), "-c", "print(6*7)"],
                       env={**os.environ, "PYTHON": sys.executable}, capture_output=True, text=True)
    assert r.returncode == 0 and "42" in r.stdout
~~~~~~~

### `tests/test_harness_bundle.py`

~~~~~~~ fichero=tests/test_harness_bundle.py
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
~~~~~~~

### `tests/test_init_dispatcher.py`

~~~~~~~ fichero=tests/test_init_dispatcher.py
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _init(*args):
    # Ruta relativa a proposito: Git Bash en Windows se come las barras
    # invertidas de una ruta absoluta.
    return subprocess.run(["bash", "init.sh", *args],
                          capture_output=True, text=True, cwd=RAIZ)


def test_el_dispatcher_existe():
    assert (RAIZ / "init.sh").is_file()


def test_dry_run_anuncia_el_scope_de_la_feature_activa():
    # Leccion: el scope esperado sale de state.py, no de un literal: cambia
    # cada vez que se cierra la ultima feature de una fase. Y con
    # sys.executable: en el Linux del CI puede no existir `python`.
    estado = subprocess.run([sys.executable, "scripts/state.py"],
                            capture_output=True, text=True, cwd=RAIZ, check=True)
    scope = json.loads(estado.stdout).get("scope", [])
    r = _init("--dry-run")
    assert r.returncode == 0, r.stderr
    for stack in scope:
        assert stack in r.stdout


def test_un_scope_sin_init_sh_falla_en_vez_de_saltarselo():
    """Un stack sin init.sh no puede dar verde: seria un falso OK."""
    scopes = json.loads((RAIZ / "harness.json").read_text(encoding="utf-8"))["scopes"]
    if all((RAIZ / s / "init.sh").is_file() for s in scopes):
        return  # todos los stacks ya tienen init.sh: no hay caso que probar
    r = _init("--all")
    assert r.returncode != 0
    assert "FALTA" in r.stderr
~~~~~~~

### `tests/test_settings.py`

~~~~~~~ fichero=tests/test_settings.py
import json
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AGENTES = {"leader", "spec_author", "explorer",
           "implementer", "reviewer", "security_reviewer"}


def test_settings_es_json_valido():
    json.loads((RAIZ / ".claude/settings.json").read_text(encoding="utf-8"))


def test_existen_los_seis_agentes_y_solo_esos():
    presentes = {p.stem for p in (RAIZ / ".claude/agents").glob("*.md")}
    assert presentes == AGENTES


def test_los_agentes_declaran_modelo():
    for nombre in AGENTES:
        texto = (RAIZ / f".claude/agents/{nombre}.md").read_text(encoding="utf-8")
        assert texto.startswith("---"), nombre
        cabecera = texto.split("---")[1]
        assert "model:" in cabecera, nombre
        if nombre != "implementer":
            # Los roles que no escriben codigo declaran tools explicitamente.
            assert "tools:" in cabecera, nombre


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
    assert "## Sabotajes" in _agente("implementer")
    assert "SERVICIOS REALES" in _agente("spec_author")


def test_los_hooks_pasan_por_el_lanzador_que_falla_cerrado():
    # Leccion: un hook cuyo interprete no existe deja pasar el comando.
    hooks = json.loads((RAIZ / ".claude/settings.json").read_text(encoding="utf-8"))["hooks"]
    guardia = hooks["PreToolUse"][0]["hooks"][0]["command"]
    assert "scripts/py.sh" in guardia and "guard_secrets.py" in guardia
    assert "compact" in hooks["SessionStart"][0]["matcher"]


def test_commit_y_push_piden_confirmacion():
    ask = json.loads((RAIZ / ".claude/settings.json").read_text(encoding="utf-8"))["permissions"]["ask"]
    for regla in ("Bash(git commit *)", "Bash(git push *)", "PowerShell(git commit *)"):
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
~~~~~~~

### `tests/test_state.py`

~~~~~~~ fichero=tests/test_state.py
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts import state  # noqa: E402

F = {"id": "F01", "title": "t", "status": "in_progress", "sdd": True, "scope": ["a"]}
IMPL = ("progress/F01/IT1/impl.md", "informe\n## Sabotajes\nN/A: solo texto")


def _preparar(tmp_path, monkeypatch, features, ficheros=()):
    (tmp_path / "feature_list.json").write_text(json.dumps(features), encoding="utf-8")
    for ruta, contenido in ficheros:
        f = tmp_path / ruta
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(contenido, encoding="utf-8")
    monkeypatch.setattr(state, "ROOT", tmp_path)


def test_pending_lanza_spec_author(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "pending"}])
    assert state.next_action()["action"] == "LANZAR_SPEC_AUTHOR"


def test_spec_ready_pide_aprobacion_humana(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "spec_ready"}])
    assert state.next_action()["action"] == "PEDIR_APROBACION_HUMANA"


def test_in_progress_sin_iteraciones_crea_it1(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F])
    r = state.next_action()
    assert r["action"] == "CREAR_IT1_Y_LANZAR_IMPLEMENTER"
    assert r["iteration"] == 1


def test_carpeta_it_sin_impl_reanuda_implementer_no_reviewer(tmp_path, monkeypatch):
    # Leccion: una IT vacia se despachaba como LANZAR_REVIEWER.
    _preparar(tmp_path, monkeypatch, [F])
    (tmp_path / "progress/F01/IT1").mkdir(parents=True)
    assert state.next_action()["action"] == "REANUDAR_IMPLEMENTER"


def test_impl_sin_sabotajes_vuelve_al_implementer(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [("progress/F01/IT1/impl.md", "informe")])
    assert state.next_action()["action"] == "DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES"


def test_sabotajes_en_evidence_cuentan(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        ("progress/F01/IT1/impl.md", "informe"),
        ("progress/F01/IT1/evidence.md", "## Sabotajes\n| linea | test |"),
    ])
    assert state.next_action()["action"] == "LANZAR_REVIEWER"


def test_impl_sin_review_lanza_reviewer(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [IMPL])
    assert state.next_action()["action"] == "LANZAR_REVIEWER"


def test_review_approved_sin_security_lanza_security(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F],
              [IMPL, ("progress/F01/IT1/review.md", "Veredicto: APPROVED")])
    assert state.next_action()["action"] == "LANZAR_SECURITY_REVIEWER"


def test_review_rechazado_crea_siguiente_it(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F],
              [IMPL, ("progress/F01/IT1/review.md", "Veredicto: CHANGES_REQUESTED")])
    assert state.next_action()["action"] == "CREAR_IT2_LANZAR_IMPLEMENTER_LUEGO_REVIEWER"


def test_security_rechazado_reverifica_ambos(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
        ("progress/F01/IT1/security.md", "Veredicto: CHANGES_REQUESTED"),
    ])
    assert state.next_action()["action"] == \
        "CREAR_IT2_LANZAR_IMPLEMENTER_LUEGO_REVIEWER_Y_SECURITY"


def test_ambos_approved_cierra(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
        ("progress/F01/IT1/security.md", "Veredicto: APPROVED"),
    ])
    assert state.next_action()["action"] == "LANZAR_IMPLEMENTER_CIERRE_MARCAR_DONE"


def test_ambos_approved_con_tramo_pendiente_abre_siguiente_it(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
        ("progress/F01/IT1/security.md", "Veredicto: APPROVED"),
        ("specs/F01/tasks.md", "- [x] **T1 — a**\n- [ ] **T2 — b**\n"
                               "- [ ] **T3 — UNICA TASK CON SERVICIOS REALES**\n"),
    ])
    assert state.next_action()["action"] == "CREAR_IT2_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO"


# "PRUEBA REAL": specs escritas con la plantilla anterior.
@pytest.mark.parametrize("cabecera", ["UNICA TASK CON SERVICIOS REALES",
                                      "PRUEBA REAL · la ejecuta el humano"])
def test_solo_falta_la_task_humana_cierra(tmp_path, monkeypatch, cabecera):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
        ("progress/F01/IT1/security.md", "Veredicto: APPROVED"),
        ("specs/F01/tasks.md", f"- [x] **T1 — a**\n- [ ] **T2 — {cabecera}**\n"),
    ])
    assert state.next_action()["action"] == "LANZAR_IMPLEMENTER_CIERRE_MARCAR_DONE"


def test_auditoria_sin_cambios_se_avisa(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "done"}], [
        ("progress/audits/2026-01-01/informe.md", "x"),
        ("progress/audits/2026-02-01/informe.md", "x"),
        ("progress/audits/2026-02-01/cambios.md", "x"),
    ])
    assert state.next_action() == {"action": "TODO_HECHO", "audits_pending": ["2026-01-01"]}


def test_coge_la_iteracion_mas_alta(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: CHANGES_REQUESTED"),
        ("progress/F01/IT2/impl.md", IMPL[1]),
        ("progress/F01/IT2/review.md", "Veredicto: APPROVED"),
    ])
    r = state.next_action()
    assert r["iteration"] == 2
    assert r["action"] == "LANZAR_SECURITY_REVIEWER"


def test_todo_done(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "done"}])
    assert state.next_action()["action"] == "TODO_HECHO"


def test_approved_que_cita_un_rechazo_anterior_sigue_aprobado(tmp_path, monkeypatch):
    # Leccion: buscar la palabra en todo el fichero abria una IT de mas.
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md",
         "**Veredicto:** APPROVED\n\nLa IT anterior fue CHANGES_REQUESTED por tests."),
    ])
    assert state.next_action()["action"] == "LANZAR_SECURITY_REVIEWER"


def test_sin_linea_de_veredicto_no_hay_veredicto(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL, ("progress/F01/IT1/review.md", "Borrador: todo parece APPROVED"),
    ])
    assert state.next_action()["action"] == "LANZAR_REVIEWER"


def test_task_de_tramo_sin_negrita_cuenta_como_pendiente(tmp_path, monkeypatch):
    # Leccion: sin negrita la regex no la veia y la feature se cerraba sin el tramo.
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
        ("progress/F01/IT1/security.md", "Veredicto: APPROVED"),
        ("specs/F01/tasks.md", "- [x] T1 — a\n- [ ] T2 — tramo siguiente\n"),
    ])
    assert state.next_action()["action"] == "CREAR_IT2_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO"


def test_mencionar_sabotajes_no_es_tener_la_seccion(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        ("progress/F01/IT1/impl.md", "Falta la seccion ## Sabotajes, la hare luego"),
    ])
    assert state.next_action()["action"] == "DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES"


def test_fichero_no_utf8_no_tumba_el_despacho(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [IMPL])
    (tmp_path / "progress/F01/IT1/review.md").write_bytes(b"Veredicto: APPROVED\n\x97 cp1252")
    assert state.next_action()["action"] == "LANZAR_SECURITY_REVIEWER"


def test_modo_ligero_salta_spec_y_aprobacion(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "pending", "sdd": False}])
    r = state.next_action()
    assert r["action"] == "CREAR_IT1_Y_LANZAR_IMPLEMENTER"
    assert r["modo"] == "ligero"


def test_modo_ligero_mantiene_los_dos_vetos(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "pending", "sdd": False}], [
        IMPL, ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
    ])
    assert state.next_action()["action"] == "LANZAR_SECURITY_REVIEWER"
~~~~~~~

<!-- FIN FICHEROS -->
