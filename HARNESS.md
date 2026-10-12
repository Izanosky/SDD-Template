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
2. Reglas duras y valores por defecto
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
puertas de calidad": siete roles (subagentes de Claude Code), un proceso con
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
  **en serie**, cada uno
  con un contexto mínimo, y la iteración (lo caro) se combate con
  autocomprobación antes de entregar.
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
  - **Piezas de ECC (affaan-m/ECC) estudiadas y no adoptadas** (2026-10-11):
    `pr-test-analyzer` (autorevisión de tests antes de entregar) cuesta un
    agente por IT y lo cubre el mismo comando de mutantes del implementer;
    se reconsidera si `metrics.csv` sigue dando rechazos con causa `tests`.
    Los hooks `post-edit-format` y `post-edit-typecheck` añaden segundos y
    salida a cada `Edit` de cada agente y dependen del stack; lo cubre
    `init.sh --rapido`. `skill-comply` mide si se siguen skills y reglas
    con ejecuciones `claude -p`: herramienta de mantenimiento de la
    plantilla, no del proyecto; la columna `skills` de `metrics.csv` da lo
    esencial. Adoptados: `config-protection` (`guard_config.py`),
    `block-no-verify` y `safety-guard` (`guard_secrets.py`).
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

## 2. Reglas duras y valores por defecto

El harness sirve al humano, no al revés. Las **reglas duras** protegen lo
que no tiene vuelta atrás y no se relajan. Todo lo demás son **valores por
defecto**: el humano los cambia cuando estorben, y el leader debe proponerlo
cuando lo vea (`leader.md`, "El harness se adapta al proyecto"). Ambas
listas están en `CLAUDE.md`, que cargan todos los agentes.

| Regla dura | Cómo se hace cumplir |
|---|---|
| Ningún commit ni push sin el humano; nunca reescribir historia | `permissions.ask` en `.claude/settings.json`; `guard_secrets.py` bloquea `--amend`, `push --force`, `rebase` y `filter-branch` |
| Ninguna dependencia nueva sin preguntar | `permissions.ask` para los instaladores habituales (añade los tuyos) |
| Los secretos no pasan por el contexto | deny de lectura, `guard_secrets.py`, pre-commit y CI si lo hay (sección 8) |
| Nada destructivo sobre datos reales | instrucción + revisión de la task humana |
| Avisar antes de tocar servicios reales | instrucción en `CLAUDE.md` y en las tasks humanas |

| Por defecto | Cómo se aplica |
|---|---|
| `done` solo por el protocolo | `state.py` solo propone el cierre con ambos `APPROVED` |
| `docs/` lo decide el humano y **cada cambio se documenta** | `scripts/check_docs_changelog.sh` en el pre-commit (y en el CI): **avisa, no bloquea** |
| Perfil, CI, spec formal, mutantes, cadencia de auditorías | los fija `/arranque` según el perfil del proyecto (personal, compartido, producción) |

**La costumbre de `docs/`.** Cada cambio en `docs/` lleva, en el mismo
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
   - `git status --short`: lo personal que ya hubiera en la carpeta (hojas
     de cálculo, PDFs, exportaciones) va a `.gitignore` **antes** del
     siguiente paso (lección: un Excel con la nómina entró en el índice);
   - `git add -A`;
   - `git update-index --chmod=+x` sobre todos los `.sh` y
     `.githooks/pre-commit`.
2. **Rellena los huecos** (`grep -rn "<RELLENAR" .`). Lo más cómodo es
   abrir Claude Code y ejecutar `/arranque`: fija el perfil del proyecto,
   te entrevista con una recomendación en cada pregunta, trae los temas que
   un equipo profesional se plantearía (`catalogo.md`) y rellena lo que
   sigue.
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
5. CI, **si el perfil lo lleva** (si no, borra `.github/workflows/ci.yml`):
   toolchains de cada stack con versión fijada y actions por SHA (sección 10
   si no usas GitHub). Un rojo avisa, pero no bloquea el trabajo.
6. `feature_list.json`: features en orden de prioridad (el orden **es** la
   prioridad). La primera, la más pequeña que cruce la arquitectura de punta
   a punta.
7. Fecha la primera entrada de `docs/CHANGELOG.md`.
8. Pon en verde `bash scripts/py.sh -m pytest tests/ -q` y `bash init.sh --all`. El
   primer commit lo hace el humano.
9. Abre Claude Code en el repo: la sesión principal actuará como `leader`.

**En el proyecto, `HARNESS.md` sobra**: `/arranque` propone borrarlo en su
paso 0, junto con `tests/test_harness_bundle.py` y
`scripts/harness_bundle.py`. Es la guía de la plantilla, no del proyecto, y
su test falla en cuanto el proyecto adapta un fichero (lección del piloto:
ponía el CI en rojo sin que nada del producto fallara). El proyecto adapta
sus ficheros pequeños con libertad, y lo que sirva para otros proyectos va a
`progress/para_la_plantilla.md`.

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
| `docs/<stack>/direccion-visual.md` | spec_author, implementer_ui, reviewer | en tramos de interfaz |
| skills precargadas (`skills:` del rol) | ese rol | enteras, en cada ejecución |
| listado de skills instaladas | todos | en cada turno: nombre y descripción, salvo las recortadas con `skillOverrides` |
| skills del harness (`/arranque`, `/direccion-visual`, `/auditoria-seguridad`, `/retrospectiva`) | sesión principal | su descripción siempre; el contenido, al activarse |
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
| `implementer_ui` | sonnet | lo mismo en tramos `(interfaz)`, más las capturas | lo mismo; cerrar la feature |
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
- **Skills precargadas, no "opcionales"**: cada rol declara las suyas en
  `skills:` y Claude Code inyecta su contenido entero al lanzarlo.
  Lección del piloto: dadas como opcionales, o nombradas en el encargo, los
  subagentes no las invocaban (0 de las de diseño en 110 ejecuciones del
  implementer) y anotaban "criterio aplicado a mano". Las que no están
  instaladas se saltan sin error; `scripts/skills.py` lo avisa en el hook
  de sesión, igual que las instaladas que ningún rol usa todavía (el
  leader propone dónde van). Son criterio, no protocolo: la spec, las
  convenciones y la definición del rol mandan. Lista en el README ("Skills
  opcionales"). El harness funciona igual sin ninguna.
- **`implementer_ui`**: el `implementer` de los tramos `(interfaz)`, con
  criterio de diseño precargado y la obligación de mirar lo que construye
  (capturas en claro/oscuro y dos anchos, con datos normales y de peor
  caso). Su definición remite a la del `implementer` para no duplicarla.
  Lección: los tests de jsdom no veían un diálogo vacío ni una columna
  desalineada; los encontraba el humano.
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
   tramo intermedio:  implementer (mutantes en zonas críticas) → reviewer
   último tramo:      implementer → reviewer → (si aprueba) security_reviewer
```

- **Spec**: `requirements.md` (EARS), `design.md` (cómo, descartes,
  escalabilidad, preguntas con recomendación) y `tasks.md` (por tramos, task
  humana al final). Unas 400 líneas.
- **Puerta humana**: el leader resume las decisiones abiertas con su
  recomendación; solo el humano aprueba, con un sí explícito («sigue» no
  vale). Con él, el leader anota sus decisiones en `design.md` y pasa la
  feature a `in_progress`.
- **Iteración**: la crea el leader, con una **foto** del árbol de trabajo
  (`scripts/foto.sh` → `IT<n>/base`): las IT no se commitean, y la foto es
  lo que permite a los revisores ver qué cambió en cada una y al
  security_reviewer la feature entera. Un rechazo, de cualquiera, abre otra
  que vuelve a pasar por el reviewer (y en el último tramo por seguridad):
  un arreglo puede romper lo aprobado; si solo toca tests, las revisiones
  son acotadas.
- **Tramos**: con varios stacks o capas, una IT por tramo, en orden de
  dependencia, **dos como mucho**. En los intermedios solo veta el
  reviewer; el security_reviewer revisa la feature entera en el último,
  solo sobre una IT que el reviewer ya aprobó. Lecciones del piloto:
  pasaba en cada tramo (47 veces) y rechazó 2; y en paralelo revisaba IT
  que el reviewer rechazaba (el 51 %, unos 61 k tokens por pasada) para
  ganar unos 3 minutos.
- **Mutantes con el mismo criterio**: en las zonas críticas (las fija
  `/arranque`), el implementer pasa la herramienta de mutantes del stack
  antes de entregar y el reviewer repite el mismo comando; fuera de ellas,
  tests de comportamiento y un test flojo es una observación. Lección: 42
  de 44 primeras entregas rechazadas, casi todas por un mutante que el
  implementer no había probado; las IT de corrección fueron el 37 % del
  tiempo y el 41 % de los tokens.
- **Correcciones de texto al cerrar**: un fallo que es solo texto no cuesta
  una iteración.
- **Cierre**: `done`, más un resumen en `history.md` redactado por el
  leader, que después propone el commit (lo confirma el humano) y `/clear`. El cierre lo hace un modelo barato al que se le da el resumen
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

0. Sin la línea `Estado: APROBADO` en `progress/arranque.md` → `ARRANQUE`:
   de ahí salen los documentos que guían todo, y no se escribe ninguna spec
   sin ellos.
1. Feature activa = la primera de `feature_list.json` que no está en `done`.
   Si no hay → `TODO_HECHO`.
2. Con `"sdd": false` → `"modo": "ligero"` y se salta al paso 3. Si no:
   `pending` → `LANZAR_SPEC_AUTHOR`; `spec_ready` sin la marca
   `Aprobada por el humano` en `design.md` → `PEDIR_APROBACION_HUMANA`.
3. Sin carpetas IT → `CREAR_IT1_Y_LANZAR_IMPLEMENTER`.
4. Se toma la IT más alta. Con `descartada.md` (el humano cambió de stack
   o de rumbo con ella sin revisar) cuenta como rechazada y se salta al
   paso 6. Sin `impl.md` → `REANUDAR_IMPLEMENTER`.
5. Sin encabezado `## Sabotajes` en `impl.md` ni en `evidence.md` →
   `DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES`.
6. Sin `Veredicto:` en `review.md` → `LANZAR_REVIEWER`. Algún
   `CHANGES_REQUESTED` (de `review.md` o `security.md`) →
   `CREAR_IT<n+1>_LANZAR_IMPLEMENTER_LUEGO_REVIEWER`.
7. **Tramo intermedio** (quedan tasks `- [ ] T<n>` que no son la humana)
   con el reviewer en `APPROVED` → `CREAR_IT<n+1>_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO`.
8. **Último tramo** (o modo ligero): sin `security.md` →
   `LANZAR_SECURITY_REVIEWER`; los dos `APPROVED` →
   `LANZAR_IMPLEMENTER_CIERRE_MARCAR_DONE` (paso 7 del implementer).

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
| `Estado: APROBADO` (línea propia) | `progress/arranque.md` | leader, con el sí del humano al final de `/arranque` |
| `Aprobada por el humano: AAAA-MM-DD` (línea propia) | `specs/<F>/design.md` | leader, con el sí del humano a la spec |

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
     se bloquee, y el cuerpo de un heredoc para el volcado del entorno
     (código que se escribe, no comandos);
   - bloquea también lo que no tiene vuelta atrás: matar procesos por
     nombre (`taskkill /IM`, `pkill`, `Stop-Process -Name`), reescribir
     la historia y descartar cambios sin commitear (`checkout -- `,
     `restore`, `reset --hard`, `clean -f`, `stash drop`): el trabajo de
     todas las IT vive sin commitear hasta que el humano commitea;
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
  1. el mismo criterio de mutantes para implementer y reviewer, solo en
     zonas críticas (y re-revisión acotada si el arreglo solo toca tests);
  2. specs con tope de tamaño;
  3. modo ligero y arreglos pequeños;
  4. correcciones de texto al cerrar;
  5. reanudar en lugar de relanzar;
  6. tramos;
  7. cierre con modelo barato y resumen redactado;
  8. security_reviewer una vez por feature, tras el reviewer;
  9. `init.sh --rapido` en las vueltas de implementer y reviewer;
  10. `/clear` tras cerrar cada feature (el estado está en disco) y métricas
      escritas por un hook, no por la sesión principal.
- **No escribas en `docs/` lo que el modelo ya sabe** (patrones de diseño,
  SOLID, convenciones estándar del lenguaje). Cada línea se paga en cada
  ejecución de tres roles.
- **El listado de skills se paga en cada turno de cada agente**: en el
  piloto, 46 skills instaladas sumaban ~3,6 k tokens de descripciones,
  releídos en cada paso. `skillOverrides` en `.claude/settings.json` deja
  en `name-only` las que el harness usa por nombre (comprobado: la precarga
  sigue funcionando; con `user-invocable-only` deja de funcionar) y en
  `user-invocable-only` las que no usa. Las de plugin no admiten
  `skillOverrides`: se desactiva el plugin para el proyecto o se acepta su
  coste. Los servidores MCP llegan diferidos (solo el nombre) y cuestan poco.
- Mide desde el día 1: una línea por agente en `progress/metrics.csv` (la
  escribe el hook `SubagentStop`, `scripts/metricas.py`, con el consumo que
  lee `scripts/agent_tokens.py` del transcript: tokens nuevos, relecturas de
  caché, minutos y skills invocadas).
- **Plugins del usuario que se inyectan solos**: ponytail mete sus reglas
  en cada subagente con un hook `SubagentStart`. `settings.json` lo limita
  (`PONYTAIL_SUBAGENT_MATCHER`) a los subagentes ajenos al harness: en los
  revisores y el `spec_author` choca con "un test por viñeta", y el
  implementer ya lo precarga. El reviewer lleva en su lugar
  `ponytail-review`, cuyo hallazgo va a observaciones que no bloquean.
  Revisa los hooks de cada plugin nuevo. La causa
  de cada rechazo (`codigo`, `tests`, `spec`, `otro`) dice qué regla falta.
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
| es solo para ti y pequeño | perfil **personal** en `/arranque`: sin CI ni preguntas de escala, spec formal solo donde importa |
| es un prototipo de un rato | no uses el harness (sección 1) |

---

## 11. Mantener el harness (y este documento)

- **Cambios de reglas**: entrada en `docs/CHANGELOG.md` (el hook avisa si
  falta), marca de fecha y propagación.
- **Este documento** (solo en el repo de la plantilla): tras cambiar cualquier fichero, ejecuta
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

**`/arranque`** — primer uso del harness en un proyecto.
- **Por qué**: de aquí salen los documentos que guían todo lo demás. En el
  piloto, una sola ronda con todas las decisiones acababa en "sigue", el
  stack se decidió sin pesar la ambición visual (cambio de framework a mitad
  de F01) y nadie preguntó por el móvil.
- **Cuándo**: siempre primero; `state.py` devuelve `ARRANQUE` y no despacha
  ninguna feature hasta que `progress/arranque.md` dice `Estado: APROBADO`.
- **Cómo**: guiado por el humano. Tras el producto, un **mapa de todas las
  decisiones técnicas** (plataforma, arquitectura, backend, datos,
  seguridad, frontend con sus librerías, calidad, operación), cada una con
  propuesta y modo: obvia (se acepta en bloque), a elegir (2-3 opciones) o a
  investigar. El humano ajusta el mapa y aprueba qué se investiga
  (`explorer`, `/deep-research`, una prueba mínima, `council`) antes de
  gastar nada. Se decide bloque a bloque en orden de dependencia, con
  comprobación de coherencia.
- **Qué deja**: ADR en `docs/adr/`, "Stack y librerías" en
  `docs/architecture.md` (la lista de dependencias aprobadas), el resto de
  documentos, las skills del stack asignadas y `F00` completa. Sustituye al
  Anexo C. El mapa vive en `progress/arranque.md` (desde
  `plantillas/arranque.md`) y se propone `/clear` al cerrar cada bloque.
- **`F00`, andamiaje en modo ligero**, siempre la primera feature: generador
  oficial, `init.sh` que sabe fallar, CI en verde, un "hola mundo" de punta
  a punta y una prueba de cada **supuesto de riesgo** del mapa. Lección: en
  el piloto la primera feature cargó con el toolchain y el cambio de stack
  (11 IT); un supuesto falso se descubre aquí con casi nada construido.

**`/direccion-visual`** — la dirección visual del proyecto.
- **Por qué**: sin ella, la paleta sale de los valores por defecto
  (índigo, Inter, tarjetas iguales) y queda congelada en los `R<n>`; y con
  "evita lo genérico" como único criterio sale algo distinto pero amateur.
- **Cuándo**: tras F00 y antes de la primera feature con pantallas, o para
  rediseñar.
- **Cómo**: el humano aporta 3-6 referencias reales (Refero, apps que usa),
  que fijan el listón; se generan tres direcciones distintas (a mano en
  Google Stitch o como miniaturas) y elige él. Ahí se deciden también las
  librerías de interfaz.
- **Qué deja**: los tokens en un único sitio del stack,
  `docs/<stack>/direccion-visual.md` (referencias, tono, tipografía,
  layout, movimiento y lo prohibido) y las capturas aprobadas.

**`/auditoria-seguridad`** — revisión de seguridad del repositorio entero.
- **Por qué**: cada `security_reviewer` mira solo el diff de su IT; nadie
  mira el conjunto (una tabla que pierde su protección con la migración de
  otra feature, una ruta vieja que no conoce un rol nuevo).
- **Cuándo**: cada 4 features cerradas o al cerrar una fase, y siempre que
  `state.py` devuelva `audits_pending`.
- **Qué deja**: un informe en `progress/audits/<fecha>/` y, decidido con el
  humano, el destino de cada hallazgo en `cambios.md` (arreglo, feature
  nueva, línea de `acceptance` o descarte). No bloquea ninguna feature.
- **Motor**: el `security_reviewer` en modo auditoría, o, si están
  instaladas, `security-audit` de Cloudflare (varias fases con verificadores
  que intentan refutar cada hallazgo) y `/insecure-defaults:audit` de Trail
  of Bits. Las dos últimas orquestan muchos agentes: solo desde la sesión
  principal y con el presupuesto acordado.

**`/retrospectiva`** — balance del proyecto y del propio harness.
- **Por qué**: los umbrales y las reglas solo se ajustan bien con datos.
- **Cuándo**: con `TODO_HECHO` o al cerrar una fase.
- **Qué deja**: `progress/retrospective.md` con qué mantener, cambiar o
  quitar (proceso, código y producto), cada fila con su dato, y lo
  trasladable en `progress/para_la_plantilla.md`. Usa `/doctor
  prompt-audit`, de serie en Claude Code, para revisar las instrucciones;
  si están instaladas, `/ponytail:ponytail-audit` para la sobreingeniería y, al
  cerrar una fase y con el sí del humano, `spec-to-code-compliance` para
  comparar el código con sus specs. No cambia reglas: las propone.

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
| Interfaces "hechas con IA" (paleta por defecto congelada como `R<n>`) y fallos visuales que solo veía el humano | `/direccion-visual`, `implementer_ui` con capturas, el reviewer las mira |
| Skills de diseño nunca invocadas; nombradas en el encargo, "aplicadas a mano" | `skills:` precargadas por rol; `skills.py` avisa de las nuevas y las ausentes |
| La línea "Skills usadas" no distinguía invocar de aplicar a mano | columna `skills` de `metrics.csv` desde el transcript (`agent_tokens.py`) |
| `subagent_tokens` sumado contaba varias veces lo mismo | `agent_tokens.py` lee el consumo real por ejecución |
| El leader escribía cada línea de métricas en su contexto caro | hook `SubagentStop` (`metricas.py`) |
| 42 de 44 primeras entregas rechazadas por mutantes que el implementer no había probado | mismo comando de mutantes del stack para los dos, solo en zonas críticas |
| Security en cada tramo, después del reviewer: 47 pasadas, 2 rechazos | solo en el último tramo (test) |
| Security en paralelo con el reviewer: revisaba IT que este rechazaba (51 %) | en serie, solo tras su `APPROVED` (test) |
| `init.sh` completo (build, auditorías con red) varias veces por IT | `init.sh --rapido` (test) |
| Tests intermitentes anotados y nunca arreglados | se arreglan en la siguiente IT |
| Tasks humanas para mirar la interfaz, nunca ejecutadas | solo con servicios reales; lo visual, capturas |
| Una ronda con todas las decisiones acababa en "sigue" | `/arranque` en rondas: producto, técnica, diseño |
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
| Cambio de stack con una IT sin revisar: el despacho pedía revisarla | `descartada.md` cuenta como rechazo (test) |
| «Sigue con la spec» tomado como aprobación de todas las recomendaciones | el leader exige un sí explícito y repregunta |
| Ampliar el alcance al cerrar llevó una spec a 699 líneas | feature nueva, no enmienda |
| La línea de métricas del cierre caía en la feature siguiente | `metricas.py` usa la IT escrita más reciente (test) |
| ponytail (plugin del usuario) se inyectaba en revisores y `spec_author` | `PONYTAIL_SUBAGENT_MATCHER` en `settings.json` (test) |
| Skills de *dirección* de diseño precargadas en quien implementa | solo en `/direccion-visual`; `implementer_ui`, las de oficio |
| Dirección visual "distinta" pero amateur: el único criterio era evitar lo genérico | referencias reales que aporta el humano y tres direcciones (Stitch) para elegir |
| La librería de componentes se instalaba antes de mirar ninguna referencia | se decide en `/direccion-visual`, tras F00 |
| Sin commits por IT, "el diff contra la IT anterior" no existía | foto del árbol por IT (`scripts/foto.sh`, test) |
| "Restaurar de HEAD" para un sabotaje borra el trabajo sin commitear | el hook bloquea descartar cambios (test) |
| Nadie tenía la orden de pasar una spec aprobada a `in_progress` | marca `Aprobada por el humano: AAAA-MM-DD` en `design.md`, que lee `state.py` (test) |
| El `spec_author` debía preguntar pero no podía esperar respuesta | termina con las preguntas y se le reanuda |
| Una IT descartada dejaba sus tasks en `[x]`: el despacho daba el tramo por hecho | el leader las desmarca al descartarla |
| `git push` a secas quizá no lo cubría `Bash(git push *)` | regla exacta además del comodín (test) |
| El experimento de modelos no se podía medir: `metrics.csv` no guardaba el modelo | columna `modelo` y `comparar.py` (test) |
| `mutmut` no funciona en Windows nativo (y quitó `--paths-to-mutate`) | `cosmic-ray` en Windows, en una copia (`plantillas/stack/conventions.md`) |

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
| `git add -A` del montaje metió un Excel personal en el índice | `git status` y `.gitignore` antes |
| `setup-uv` sin `version` instalaba el último uv | versión fijada en el CI |
| `guard_secrets` leía el código de un heredoc como volcado del entorno | ignora el cuerpo del heredoc para esa regla (test) |
| `taskkill /IM node.exe` mató todos los `node` de la máquina | el hook bloquea matar por nombre (test) |
| El scratchpad compartido: un agente corrió la lista de mutantes de otro | una carpeta por agente e IT |
| `rm -rf` de una copia con *junction* a `node_modules` casi vacía el real | copias sin enlaces, o se quita antes |
| `HARNESS.md` desfasado tras cada línea de `metrics.csv` | semillas fijas para lo vivo de `progress/` (test) |

---

## Anexo A — Inventario de ficheros

Todos están completos en la Parte II.

| Fichero | Estado | Qué hace |
|---|---|---|
| `CLAUDE.md`, `CHECKPOINTS.md` | `<RELLENAR>` | contexto y reglas duras; criterios de done |
| `docs/*.md` | `<RELLENAR>` parcial | reglas que leen los agentes; `README.md` es el mapa |
| `docs/CHANGELOG.md` | listo | registro obligatorio de cambios en `docs/` |
| `harness.json`, `feature_list.json` | `<RELLENAR>` | scopes y secretos; features en orden |
| `init.sh` | listo | dispatcher (`--all`, `--dry-run`, `--rapido`) |
| `plantillas/stack/` | `<RELLENAR>` | `init.sh` y `conventions.md` por stack; `conventions-web.md` opcional |
| `scripts/state.py` | listo | despacho (sección 7) |
| `scripts/py.sh` | listo | lanzador de Python que falla cerrado |
| `scripts/guard_secrets.py` | listo | hook contra fugas de secretos, saltos del pre-commit, historia reescrita y procesos matados por nombre |
| `scripts/guard_config.py` | listo | pide confirmación antes de tocar configuración de lint, tipos o del harness |
| `scripts/skills.py` | listo | skills instaladas sin clasificar y precargadas que faltan |
| `scripts/agent_tokens.py` | listo | consumo real de un subagente leído de su transcript |
| `scripts/metricas.py` | listo | hook `SubagentStop`: escribe `metrics.csv` (con el modelo de cada ejecución) |
| `scripts/comparar.py` | listo | compara dos `metrics.csv`: ¿surtió efecto un cambio? |
| `scripts/session_start.sh` | listo | estado al arrancar, limpiar y compactar |
| `scripts/foto.sh` | listo | foto del árbol de trabajo (base de cada IT) sin commits ni tocar el índice |
| `scripts/check_docs_changelog.sh` | listo | regla del CHANGELOG (hook y CI) |
| `scripts/harness_bundle.py` | listo | regenera, comprueba y extrae la Parte II |
| `.claude/settings.json` | listo; añade tus `.env.*` e instaladores | deny, ask, hooks y `skillOverrides` |
| `.claude/agents/*.md` | listos; zonas sensibles en `leader.md` | los siete roles |
| `.claude/skills/` | listos | `/arranque`, `/direccion-visual`, `/auditoria-seguridad`, `/retrospectiva` |
| `.githooks/pre-commit` | listo | CHANGELOG + gitleaks |
| `.github/workflows/ci.yml` | `<RELLENAR>` toolchains | historia, CHANGELOG, tests, `init.sh --all` |
| `.gitleaks.toml` | `<RELLENAR>` reglas | escáner de secretos |
| `specs/_plantilla/` | listo | requirements, design, tasks |
| `plantillas/arranque.md` | listo | mapa de decisiones de `/arranque` (se copia a `progress/`) |
| `progress/` | listo | `current.md`, `history.md`, `metrics.csv`, `audits/`, `para_la_plantilla.md` |
| `tests/` | listos | tests del harness (no del producto) |

## Anexo B — Encargo tipo del leader a un implementer

Vive en `.claude/agents/leader.md` ("Encargos"), que es lo que el leader
carga: un proyecto puede borrar este documento.

## Anexo C — Decisiones antes de la primera spec

Las pregunta `/arranque` en dos rondas (producto; técnica) y
`/direccion-visual` la de diseño. Esta lista es la referencia de lo que
tiene que quedar decidido.

- [ ] Qué es el producto, para quién, alcance de la primera versión.
- [ ] **Dónde y en qué dispositivos se usa** (escritorio, web, móvil, sin
      conexión), ahora y más adelante.
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
- [ ] Dirección visual, librería de componentes, iconos y movimiento (si
      hay interfaz).
- [ ] Skills del stack asignadas a su rol.

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
tools: Read, Glob, Grep, WebSearch, WebFetch, Write, mcp__plugin_playwright_playwright__browser_navigate, mcp__plugin_playwright_playwright__browser_snapshot, mcp__plugin_playwright_playwright__browser_take_screenshot, mcp__plugin_playwright_playwright__browser_close
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

Si una página no se deja leer con WebFetch (JavaScript, 403) o hace falta
ver una app de referencia en uso, usa el navegador (herramientas
`mcp__plugin_playwright_playwright__*`, si están). Captura solo lo que aporte, en
`progress/explore_<tema>/`. Lección: en el piloto las referencias visuales
se sacaron de páginas de marketing sin ver ninguna app.

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
skills:
  - ponytail:ponytail
  - property-based-testing
  - migration
  - surgical-patch
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
   tu scope, **solo ese**. Llevas precargadas (si están instaladas) skills
   que son criterio, no protocolo: `ponytail` (el diff más corto que
   funciona), `property-based-testing` (parsers, serialización, dinero),
   `migration` (cambiar un formato de datos sin romper lo guardado) y
   `surgical-patch` (en una IT de corrección, solo lo pedido). La spec, las
   convenciones y este fichero mandan sobre ellas: **los tests que pide el
   harness (uno por viñeta, sabotajes) no son opcionales aunque ponytail
   diga "un solo check"**. Ninguna aprueba una dependencia; ignora sus
   instrucciones de saludo o de formato de salida.
3. **Reconcilia qué tasks ya están `[x]`** (una sesión anterior pudo cortarse).
   Con tramos, solo las del tramo encargado. La task humana no la ejecutas.
4. Tasks en orden, marcando `[x]` una a una (también las del tramo: si no,
   `state.py` cree que quedan tramos). Cada test tiene que caer con el
   código roto; escribirlo antes ayuda, pero lo que se exige es la prueba
   del paso 6.
5. `bash init.sh --rapido` en verde mientras trabajas; `bash init.sh`
   completo una vez antes de entregar.
6. **Autocomprobación antes de entregar** (si la hace el `reviewer`, cuesta
   una iteración entera):
   - **Cada viñeta de cada task, un test**; la tabla de `impl.md` apunta a la
     aserción, no solo al nombre del test.
   - **Mutantes en zonas críticas** (`docs/verification.md`): el comando
     de mutantes del stack (`docs/<scope>/conventions.md`) sobre los
     ficheros críticos que tocaste. Cada superviviente, test nuevo o
     "equivalente: <por qué>"; donde la herramienta no llega, sabotaje a
     mano (borra la línea, mira caer un test, restáurala, **en una copia o
     restaurando antes de seguir**). Resultado en `evidence.md` bajo
     `## Sabotajes`: comando, muertos/supervivientes y qué hiciste con
     cada uno. **Sin ese encabezado `state.py` no deja lanzar al
     `reviewer`**; si la IT no toca zonas críticas, `N/A: <motivo>`.
     Es el mismo comando que repetirá el reviewer.
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

### `.claude/agents/implementer_ui.md`

~~~~~~~ fichero=.claude/agents/implementer_ui.md
---
name: implementer_ui
description: Implementer de los tramos de interfaz. Mismo protocolo que el implementer, con criterio de diseño precargado y capturas de lo que construye.
model: sonnet
maxTurns: 200
skills:
  - ponytail:ponytail
  - property-based-testing
  - migration
  - surgical-patch
  - make-interfaces-feel-better
  - web-design-guidelines
---

# implementer_ui

Eres el `implementer` de un tramo de interfaz. **Primero lee
`.claude/agents/implementer.md` y síguelo entero**: protocolo, reglas
aprendidas, qué escribes, prohibido y cómo terminas. Aquí solo va lo que
añade la interfaz.

Lección del piloto: las pantallas "se notaban hechas con IA" (paleta índigo
por defecto, todo en tarjetas iguales) y los fallos visuales los encontraba
el humano, porque nadie miraba la app renderizada.

## La dirección visual manda

- Lee `docs/<scope>/direccion-visual.md`. Manda sobre tus skills de diseño
  (`make-interfaces-feel-better`, `web-design-guidelines`): son oficio
  para lo que la dirección no fija, no una dirección nueva. Ignora sus
  instrucciones de saludo o de formato de salida. Las skills que *proponen*
  una dirección (`frontend-design`, `frontend-design-direction`) son de
  `/direccion-visual`, no tuyas: aquí empujarían a reinventar el aspecto
  pantalla a pantalla.
- **Tokens**: todo color, tamaño, espaciado, radio, sombra y duración sale
  de los tokens (la dirección visual dice dónde viven); nada de valores
  sueltos.
- Si el tramo crea pantallas y ese fichero no existe, **para** y dilo en una
  línea: el `leader` propone `/direccion-visual` al humano. (F00 no
  cuenta: su "hola mundo" va antes de la dirección visual.)
- Movimiento, solo el que fija la dirección visual. No añadas animaciones
  por pulir: en el piloto fueron la mayor fuente de iteraciones.

## Capturas

Antes de entregar, mira lo que has construido:

1. Arranca la interfaz con el **modo de datos falsos** del scope (comando en
   `docs/<scope>/conventions.md`), con datos normales y con el juego de
   **peor caso** (nombres largos, cero elementos, cifras enormes, texto en
   otro idioma).
2. Con el navegador (herramientas `mcp__plugin_playwright_playwright__*` o
   equivalentes; cárgalas con ToolSearch; si el MCP no arranca porque busca
   otro navegador, mira `conventions.md`) captura cada pantalla que toca el
   tramo: tema claro y oscuro si existen, ancho 1280 y 390, datos normales y
   peor caso. **Como mucho ~8 capturas**: prioriza lo nuevo.
3. Guárdalas en `progress/<F>/IT<n>/capturas/<pantalla>-<tema>-<ancho>-<datos>.png`
   (si la herramienta las deja en otra carpeta, cópialas).
4. Ábrelas junto a las capturas aprobadas de `/direccion-visual` y arregla
   lo que veas: texto cortado o solapado, desalineado, contraste pobre,
   estados rotos con el peor caso, lo que se aparte de la dirección
   visual.
5. Cierra el navegador y para **solo tu servidor** (por su PID; nunca matar
   todos los procesos de `node` o `python` de la máquina).

En `impl.md`, una sección `## Capturas` con la lista de ficheros y lo que
corregiste al verlas. Sin navegador disponible: `## Capturas` con
`no disponibles: <motivo>`, y el `reviewer` decide.
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
redactas specs ni marcas `done`, y solo escribes código en arreglos
pequeños.**

## Arranque

El hook de sesión ya te da la salida de `scripts/state.py`, `current.md` y
las rutas de la última IT. Si no la ves, ejecuta `bash scripts/py.sh
scripts/state.py`. **No leas `feature_list.json` entero.**

- La siguiente feature crea pantallas y no existe
  `docs/<scope>/direccion-visual.md`: propón `/direccion-visual` antes de
  su spec (después de F00, que solo monta el framework).

## Despacho

| `action` | Qué haces |
|---|---|
| `ARRANQUE` | `/arranque` con el humano (o lo retomas donde diga `progress/arranque.md`). Nada más hasta que lo apruebe |
| `LANZAR_SPEC_AUTHOR` | `spec_author` sobre la feature |
| `PEDIR_APROBACION_HUMANA` | **Paras.** Resumes la spec: qué hace, decisiones abiertas con recomendación, dependencias nuevas, servicios reales y coste. Solo vale un sí explícito a la spec y a cada decisión (o "las recomendadas"); «sigue» o «vale» no (en el piloto aprobaron cuatro specs así): repregunta. **Con el sí**: anexas a `design.md` "Decisiones del humano (fecha)" con sus respuestas tal cual y la línea `Aprobada por el humano: AAAA-MM-DD` (la marca que lee `state.py`), y pasas la feature a `in_progress` |
| `CREAR_IT1_Y_LANZAR_IMPLEMENTER` | Creas `progress/<F>/IT1/` con su foto (abajo; el security_reviewer revisa la feature desde ella) y lanzas `implementer`. Con `"modo": "ligero"` no hay spec: el encargo da el `acceptance` como requisitos |
| `REANUDAR_IMPLEMENTER` | La IT no tiene `impl.md`: reanudas al mismo agente (abajo); si ya no existe, uno nuevo en la misma carpeta |
| `DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES` | Al mismo `implementer`, solo para la tabla |
| `LANZAR_REVIEWER` | Sobre la misma `IT<n>` |
| `LANZAR_SECURITY_REVIEWER` | Último tramo, sobre la `IT<n>` que el reviewer ya aprobó |
| `CREAR_IT<n>_LANZAR_IMPLEMENTER_LUEGO_REVIEWER` | Rechazo del reviewer o de seguridad: nueva carpeta, `implementer` con los cambios pedidos (de `review.md` o `security.md`); después `reviewer`, y `state.py` traerá a seguridad cuando apruebe. Si el arreglo solo toca tests, díselo a los revisores: su revisión es acotada |
| `CREAR_IT<n>_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO` | Nueva carpeta para el tramo siguiente de `tasks.md`; díselo al `implementer` y a los revisores |
| `LANZAR_IMPLEMENTER_CIERRE_MARCAR_DONE` | Cierre (ver "Modelos") |
| `TODO_HECHO` | Propones `/retrospectiva` |

- **Tramo de interfaz** (cabecera con `(interfaz)` en `tasks.md`, o en modo
  ligero un `acceptance` que cambia pantallas): donde la tabla dice
  `implementer`, lanzas `implementer_ui`. El cierre sigue siendo del
  `implementer`.
- **Cada carpeta `IT<n>` nace con su foto**: `mkdir -p progress/<F>/IT<n>
  && bash scripts/foto.sh > progress/<F>/IT<n>/base` (el árbol de trabajo
  sin commits; de ahí sacan los revisores el diff de la IT, y de la de `IT1`
  el de la feature). Tus arreglos pequeños, después de crearla.
- Con `audits_pending`: antes de la acción, propón `/auditoria-seguridad`
  para dar destino a los hallazgos.
- Tras cerrar una feature: **propón el commit** con un mensaje redactado
  (lo confirma el humano); propón la auditoría cuando toque según "Auditoría
  completa" en `CLAUDE.md` (cuenta las features cerradas desde la última
  carpeta de `progress/audits/`); y
  **propón `/clear`** (el estado está en disco; en el piloto la sesión
  principal acumulaba 16-24 M de lecturas de caché).
- Un test intermitente visto por cualquier agente: lo apuntas en
  `current.md` y va en el encargo de la siguiente IT (arreglarlo o ponerlo
  en cuarentena con su motivo).

## El harness se adapta al proyecto

Si una regla, un paso o una comprobación estorba en este proyecto (no
compensa para su perfil, repite trabajo o falla por algo que no es del
producto), **díselo al humano con una propuesta concreta**: quitarla,
relajarla o cambiarla. Decide él; con su sí, lo editas y lo dejas anotado
(`docs/CHANGELOG.md` si es `docs/`, y `progress/para_la_plantilla.md` si
sirve para otros proyectos). Las reglas duras de `CLAUDE.md` quedan fuera.

- **Un CI en rojo es un aviso**, no un bloqueo: di la causa y propón el
  arreglo, pero el despacho sigue.

## Agente que vuelve sin terminar

Tras cada agente vuelves a ejecutar `state.py`. Si la acción no cambió, el
agente cortó antes de escribir su fichero: **no lances otro** (empezaría de
cero). Escríbele con `SendMessage`: "Falta `review.md` con su línea
`Veredicto:` en `progress/<F>/IT<n>/`. Continúa; si algo te bloquea, di
qué." Máximo **2 reanudaciones**; a la tercera, paras e informas.

- **`spec_author` que vuelve con preguntas** de alcance (sin los tres
  ficheros): no es un corte. Llévaselas al humano y reanúdalo con las
  respuestas; no cuenta como reanudación.

## Cambios de rumbo

Solo con el sí del humano:

- **Descartar una IT** (cambia el stack o el rumbo con la IT sin revisar):
  escribe `progress/<F>/IT<n>/descartada.md` con el motivo y quién lo
  decidió; `state.py` la da por rechazada y abre la siguiente. **Desmarca
  en `tasks.md` las tasks que marcó** (si no, `state.py` cree hecho ese
  tramo y lanza los vetos finales). El encargo de la siguiente dice qué
  código de la descartada se quita y qué se conserva. No borres la carpeta.
- **Reabrir una feature `done`** o **ampliar el alcance al cerrar**: no;
  feature nueva con los cambios como `acceptance`, justo **tras** la activa
  (`docs/specs.md`, "Hotfix"). Si el humano la quiere ya, delante solo en
  modo ligero (nunca pasa a `in_progress`), y di a los revisores de la
  activa qué parte del diff es suya.

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

Las escribe el hook `SubagentStop` (`scripts/metricas.py`) en
`progress/metrics.csv`, una línea por ejecución. **No las escribes tú**;
solo corriges una mal atribuida. Nunca uses el `subagent_tokens` del
resultado de Agent: es el tamaño del contexto, no lo gastado. Para comparar
con otro proyecto o con antes de un cambio: `scripts/comparar.py`.

## Skills

Cada rol precarga las suyas (`skills:` en su definición): **no nombres
skills en los encargos**. Lección: nombradas en el encargo, los agentes las
"aplicaban a mano" sin cargarlas.

- El hook trae `=== skills.py ===` con skills **nuevas**: para cada una
  propón al humano, con una línea de por qué, precargarla en un rol
  (`skills:` del agente y `"name-only"` en `skillOverrides` de
  `.claude/settings.json`) o descartarla (`"user-invocable-only"`; las de
  plugin, a `skills_revisadas` de `harness.json`). Con su sí, lo editas.
- Skills **ausentes**: avisa al humano; ese rol trabaja sin ellas.
- Tests intermitentes o un fallo sin causa clara: `investigate-first`
  antes de tocar código.
- El humano toma o cambia una decisión de arquitectura (stack, plataforma,
  almacenamiento, despliegue): **para la feature en curso**, propón
  investigarla como en `/arranque` (ronda 2; `council` si está disputada)
  y déjala como ADR (`architecture-decision-records`) antes de seguir.
  Lección: un cambio de framework a mitad de feature tiró una IT entera.

## Encargos

El subagente arranca en frío. Encargo tipo al implementer:

```
Implementa <F> (<título>), IT<n>[, tramo <X>: T<a>-T<b>][, modo ligero:
requisitos = acceptance <lista>]. La carpeta progress/<F>/IT<n>/ ya existe.
Sigue specs/<F>/. [Cambios pedidos: <de IT<n-1>/review.md>.] No ejecutes la
task humana. Dependencias aprobadas: <lista o "ninguna">.
[Reglas cambiadas en esta sesión: <…>.] [Arreglos del leader que verás en el
diff: <…>.] [No toques: <…>.]
Termina con init.sh en verde, impl.md y ## Sabotajes escritos.
```

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

Cada rol declara el suyo. El cierre (paso 7 del implementer) en `haiku`
**con el resumen para `history.md` redactado por ti** (un modelo que no implementó rellena
huecos con lo que suena plausible); si hay "Correcciones de texto al
cerrar", `sonnet`. `explorer` en `opus` si toca fronteras de arquitectura.

## Reglas que no rompes

- Tú creas las carpetas `IT<n>`, cada una con su `base`. No abres
  `evidence.md`.
- En `specs/` solo escribes "Decisiones del humano", tal cual las dijo.
- `done` solo lo marca el `implementer` en su paso 7 (cierre), con `review.md` y
  `security.md` de la **misma** IT en `APPROVED`.
- La aprobación humana de la spec es obligatoria (salvo `"sdd": false`, que
  ya es una decisión del humano).
- `docs/`, `CLAUDE.md` y las reglas del harness los decide el humano; todo
  cambio en `docs/` lleva su entrada en `docs/CHANGELOG.md` (el pre-commit
  avisa si falta).
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
skills:
  - property-based-testing
  - web-design-guidelines
  - ponytail:ponytail-review
---

# reviewer

Apruebas o rechazas funcionalmente. **Nunca editas código.** Eres la única
puerta funcional: el `security_reviewer` (solo en el último tramo, después
de tu `APPROVED`) solo mira seguridad, así que lo funcional que se te escape no lo mira nadie más.

## Qué verificas

1. **Cada `R<n>` tiene un test que lo cubre de verdad** (que afirme algo
   sobre el resultado).
2. **Zonas críticas** (`docs/verification.md`): repites **el mismo comando
   de mutantes** que dejó el implementer en `## Sabotajes` y juzgas cada
   superviviente (test que falta, o equivalente de verdad). Añade a mano,
   en una copia y nunca en el repo, solo lo que la herramienta no puede
   mutar: un filtro de consulta, una comprobación por prefijo engañable
   (`http://localhost.evil.com`), un falso que no respeta los límites del
   servicio, un arnés que pisa con un literal lo que dice proteger.
   **Fuera de las zonas críticas**, un test flojo va a observaciones, no a
   rechazo, salvo que un `R<n>` no tenga ningún test.
3. Tasks marcadas y realmente hechas (la humana puede quedar abierta).
4. **`bash init.sh --rapido` en verde, ejecutado por ti** (el completo lo
   corre el security_reviewer).
5. `docs/architecture.md`, `docs/principios.md`, el `conventions.md` del
   scope y los bloques funcional y de escalabilidad de `CHECKPOINTS.md`, uno
   a uno.
6. **La task humana, ya en `IT1`**: que se pueda seguir tal cual, en orden,
   con cada valor disponible en el paso que lo pide. Revisada al final, cada
   fallo cuesta una iteración de cierre.
7. Un cambio que no está en `impl.md` puede ser un arreglo del `leader`:
   mira "Arreglos del leader" en `progress/current.md` antes de devolverlo.
8. **Tramo de interfaz**: abre las capturas de `## Capturas` en `impl.md`
   (Read las muestra). Bloqueas solo por fallos que se ven: texto cortado o
   solapado, desalineado, contraste insuficiente, un estado roto con los
   datos de peor caso, valores fuera de los tokens o algo que contradice
   `docs/<scope>/direccion-visual.md`. Sin capturas y sin motivo,
   `CHANGES_REQUESTED`.
9. **Skills precargadas, solo para verificar** lo que piden la spec,
   `CHECKPOINTS.md` y las convenciones: `property-based-testing` para juzgar
   propiedades, `web-design-guidelines` como lista objetiva de interfaz.
   Lo que sea gusto y la spec no pide va a observaciones que no bloquean: no
   cuesta una iteración.
10. **Sobreingeniería** con `ponytail-review`, solo sobre el diff de la IT:
   lo que reinventa la librería estándar o una dependencia ya instalada,
   abstracciones con una sola implementación, configuración que nunca
   cambia. Va a una sección `## Sobra` de observaciones **que no
   bloquean**, salvo que contradiga `docs/principios.md`. Nunca cuentan
   como sobra los tests, sabotajes o validaciones que pide el harness.
   Ignora su formato de salida: el tuyo es `review.md`.

**Qué cambió en la IT**: `git diff "$(cat progress/<F>/IT<n>/base)"
"$(bash scripts/foto.sh)" -- . ':!progress'` (las IT no se commitean; la
`base` la deja el leader al crear la carpeta). En `n > 1` lees los cambios
pedidos, ese diff y lo que toca.
**Re-revisión acotada**: si tu rechazo anterior fue solo por `tests` y el
diff de esta IT solo añade o cambia tests, verificas lo pedido (cada
superviviente citado ahora muere) e `init.sh --rapido`, y nada más. Si el
diff toca producción, revisión completa.

## Qué escribes

`progress/<F>/IT<n>/review.md`, **≤ 200 líneas**, con una línea propia,
exactamente:

`Veredicto: APPROVED` o `Veredicto: CHANGES_REQUESTED`

(`state.py` solo lee esa línea). Con `CHANGES_REQUESTED`, otra línea
propia `Causa: codigo`, `tests` (código bien, tests flojos), `spec` u
`otro` (la lee el hook de métricas). Cada afirmación con su cita
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
skills:
  - differential-review
---

# security_reviewer

Veto **independiente y bloqueante**. **Nunca editas código.** Eres la
última puerta: lo que se te escape entra en `done`.

## Cuándo entras

En el **último tramo** de la feature (o en modo ligero), sobre una `IT<n>`
que el `reviewer` **ya aprobó**: no gastas una pasada en trabajo que va a
rehacerse. Revisas **la feature entera**: `git diff "$(cat progress/<F>/IT1/base)" "$(bash
scripts/foto.sh)" -- . ':!progress'` (la foto del árbol al empezar la
feature; incluye los ficheros nuevos sin seguimiento). Sin `IT1/base`
(feature empezada antes de esta regla), desde la `Base de <F>` de
`progress/current.md`. Lecciones del piloto: pasabas en cada tramo (47
veces) y rechazaste 2; y en paralelo con el reviewer revisabas IT que él
rechazaba (el 51 %).

En `n > 1`, si el diff de la IT solo cambia tests, lo confirmas en pocas
líneas (sigue sin tocar producción, `init.sh` completo en verde) y
apruebas; si toca producción, revisas lo cambiado desde tu última
revisión.

## Protocolo

1. `docs/security.md` y los `R<n>` de seguridad de la spec. Si no hay ninguno
   y la feature toca input, auth o datos, eso ya es un hallazgo.
2. Ejecuta `bash init.sh` **completo** (eres el único rol que lo hace en
   cada IT final) y **verifica** la salida del escáner de secretos y de la
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

Llevas precargada `differential-review` (si está instalada): es tu método
para revisar el diff. Además, con la herramienta `Skill`:
- si el diff toca un lockfile o un manifiesto de dependencias, invoca
  `supply-chain-risk-auditor`;
- tras un hallazgo, invoca `variant-analysis` para buscar el mismo fallo en
  el resto del repositorio.

No sustituyen este protocolo ni el formato de `security.md`.

## Qué escribes

`progress/<F>/IT<n>/security.md`, **≤ 200 líneas**, con una línea propia,
exactamente:

`Veredicto: APPROVED` o `Veredicto: CHANGES_REQUESTED`

(`state.py` solo lee esa línea). Con `CHANGES_REQUESTED`, otra línea
propia `Causa: codigo` u `otro` (la lee el hook de métricas). Cada hallazgo
con `archivo:línea`. Las
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
  configuración, con `sharp-edges` (invócala) para las APIs y opciones que
  invitan al error.
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
  Si llevas precargada `prd-securability-enhancement` (la añade `/arranque`
  en proyectos con usuarios o servidor), úsala para elegirlos contra ASVS.
- **Tramos**: con varios stacks o capas, `tasks.md` agrupa las tasks por
  tramo en orden de dependencia (lo que otros consumen, primero). **Dos
  como mucho** (lógica y datos; interfaz) salvo que haya más stacks: cada
  tramo es otro ciclo de implementación y revisión. El tramo
  que crea o cambia pantallas lleva `(interfaz)` en su cabecera: lo hace el
  `implementer_ui`.
- **El aspecto no va en `R<n>`**: colores, tipografía y componentes salen de
  `docs/<scope>/direccion-visual.md`; la spec la cita y solo añade lo propio
  de sus pantallas. Lección: con los tokens congelados como requisito, el
  diseño no podía mejorar sin enmendar specs.
- **Las tasks no explican el harness** ni afirman lo que hace `init.sh`.
- **Task humana**, solo si hay servicios reales (mirar la interfaz no lo
  es: lo cubren las capturas): la última, con
  `ÚNICA TASK CON SERVICIOS REALES` en su cabecera; pasos en orden
  ejecutable, resultado esperado de cada uno, ningún secreto.
- **Dependencias nuevas** nunca se dan por aprobadas: pregunta con una
  alternativa sin dependencia. **Datos que caducan**: fuente y fecha.
- **Pregunta antes de redactar** si el `acceptance` deja abierto el alcance:
  dos o tres preguntas al humano cuestan menos que reescribir. No puedes
  esperar respuesta a mitad: terminas tu turno solo con las preguntas
  (cada una con tu recomendación) y el `leader` te reanuda con las
  respuestas. Lo que no sea alcance no para: va a `design.md` como
  pregunta con recomendación.

## Dónde terminas

Pasas la feature a `spec_ready` **editando esa línea de `feature_list.json`
como texto** y te detienes: no lanzas al implementer ni das tu spec por
buena. Tu turno termina cuando los tres ficheros están escritos enteros; no
acabes anunciando el siguiente paso ni ofreciendo seguir. Solo paras antes
ante un bloqueo real o con las preguntas de alcance (arriba).
~~~~~~~

### `.claude/settings.json`

~~~~~~~ fichero=.claude/settings.json
{
  "env": {
    "PONYTAIL_SUBAGENT_MATCHER": "^(?!(implementer|implementer_ui|reviewer|security_reviewer|spec_author|explorer)$)"
  },
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
      "Bash(git push)",
      "PowerShell(git commit *)",
      "PowerShell(git push *)",
      "PowerShell(git push)",
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
    "SubagentStop": [
      {
        "hooks": [{ "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/scripts/py.sh\" \"$CLAUDE_PROJECT_DIR/scripts/metricas.py\" || true" }]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash|PowerShell",
        "hooks": [{ "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/scripts/py.sh\" \"$CLAUDE_PROJECT_DIR/scripts/guard_secrets.py\"" }]
      },
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [{ "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/scripts/py.sh\" \"$CLAUDE_PROJECT_DIR/scripts/guard_config.py\"" }]
      }
    ]
  },
  "skillOverrides": {
    "differential-review": "name-only",
    "property-based-testing": "name-only",
    "web-design-guidelines": "name-only",
    "migration": "name-only",
    "surgical-patch": "name-only",
    "frontend-design-direction": "user-invocable-only",
    "make-interfaces-feel-better": "name-only",
    "supply-chain-risk-auditor": "name-only",
    "variant-analysis": "name-only",
    "sharp-edges": "name-only",
    "ui-ux-pro-max": "name-only",
    "redesign-existing-projects": "name-only",
    "pick-ui-library": "name-only",
    "investigate-first": "name-only",
    "security-audit": "name-only",
    "prd-securability-enhancement": "name-only",
    "vercel-react-best-practices": "name-only",
    "vercel-composition-patterns": "name-only",
    "vercel-react-view-transitions": "name-only",
    "modern-python": "name-only",
    "council": "name-only",
    "architecture-decision-records": "name-only",
    "emil-design-eng": "user-invocable-only",
    "review-animations": "user-invocable-only",
    "break-ui": "user-invocable-only",
    "fp-check": "user-invocable-only",
    "agent-browser": "user-invocable-only",
    "lean-build": "user-invocable-only",
    "safe-refactor": "user-invocable-only",
    "verify-and-stop": "user-invocable-only",
    "grill-me": "user-invocable-only",
    "prompt-master": "user-invocable-only",
    "cavecrew": "user-invocable-only",
    "caveman": "user-invocable-only",
    "caveman-commit": "user-invocable-only",
    "caveman-compress": "user-invocable-only",
    "caveman-discover": "user-invocable-only",
    "caveman-evidence-review": "user-invocable-only",
    "caveman-explore": "user-invocable-only",
    "caveman-help": "user-invocable-only",
    "caveman-learn": "user-invocable-only",
    "caveman-manage": "user-invocable-only",
    "caveman-optimize": "user-invocable-only",
    "caveman-review": "user-invocable-only",
    "caveman-setup": "user-invocable-only",
    "caveman-stats": "user-invocable-only"
  }
}
~~~~~~~

### `.claude/skills/arranque/SKILL.md`

~~~~~~~ fichero=.claude/skills/arranque/SKILL.md
---
name: arranque
description: Primer uso del harness en un proyecto - entrevista guiada que fija el perfil del proyecto (personal, compartido, produccion) y con el producto, arquitectura, stack y librerias; trae los temas profesionales que el humano no conoce (cache, escalado, observabilidad...) con propuesta y porque, decide el humano, y lo deja escrito. Solo la sesion principal (leader), nunca un subagente.
---

# Arranque

**De aquí salen los documentos que guían todo el proyecto**: cada spec,
cada encargo y cada revisión se miden contra ellos. Por eso nada empieza
hasta que esté todo claro: `state.py` devuelve `ARRANQUE` (y no despacha
ninguna feature) mientras `progress/arranque.md` no tenga la línea
`Estado: APROBADO`, que solo se escribe con el sí del humano al final.

Lecciones del piloto:

- una sola ronda con todo acababa en respuestas de "sigue";
- el stack se eligió sin pesar la ambición visual del producto, y hubo que
  cambiar de framework a mitad de la primera feature (una IT tirada, dos
  investigaciones, una enmienda de ~360 líneas);
- nadie preguntó en qué dispositivos se usaría: el deseo de usarla en el
  móvil llegó con la arquitectura de escritorio ya construida;
- las librerías de interfaz (componentes, animación, gráficos) se fueron
  eligiendo feature a feature, cada una con su investigación.

## Principios del flujo

- **Manda el humano.** Tú preparas, propones y recomiendas; él decide qué se
  decide, cómo y con cuánta investigación. **No investigues nada que no
  haya aprobado**, y antes di qué harías y su coste aproximado.
- **Entrevista, no formulario** <!-- ajuste-2026-10-12 -->: sigue una rama
  del árbol de decisiones hasta cerrarla antes de abrir otra, y cada
  pregunta lleva **tu respuesta recomendada y su porqué**. Las preguntas
  abiertas (las del producto), de una en una. Si una respuesta abre otra
  pregunta, haz esa primero.
- **Aportas lo que el humano no sabe.** "No lo sé" es una respuesta válida.
  Explica en dos líneas qué está en juego, recomienda y apunta la decisión
  como "por recomendación", que la deja revisable. Los temas que un equipo
  profesional se plantearía los traes tú (`catalogo.md`), aunque nadie los
  haya mencionado.
- **Proporcional al proyecto**: el perfil (paso 0) decide cuánto se
  pregunta y qué piezas del harness se instalan. Un proyecto personal no
  carga con CI ni con preguntas de escalado.
- **Nada se queda sin decidir por omisión**: el mapa de decisiones (paso 2)
  cubre todo el proyecto, y cada fila acaba decidida, aplazada con
  disparador o descartada por no aplicar.
- **En orden de dependencia**: lo que condiciona a lo demás, primero
  (plataforma → arquitectura → backend → frontend → calidad y operación).
  Una decisión no se pregunta antes que aquellas de las que depende.
- **Pocas interrupciones**: las preguntas cerradas, en tandas de hasta 4 con
  `AskUserQuestion` (si está), con la recomendada primero y su porqué. Lo
  obvio se propone en bloque para aceptarlo de una vez.
- **Lo que ya dice el repositorio** no se pregunta: se lee y se confirma.
  **Con código existente**, el mapa del paso 2 sale prerrellenado de las
  dependencias, la configuración y la estructura (lo que hay es la
  decisión tomada); el humano confirma o corrige, y solo las filas sin
  código detrás siguen el flujo normal.
- **Reanudable y barato**: el estado vive en `progress/arranque.md` (copia
  de `plantillas/arranque.md`), que se actualiza tras cada tanda. **Al
  cerrar cada bloque, propón `/clear`**: ese fichero basta para seguir, y
  las investigaciones no se arrastran en el contexto de la sesión.
- Sin commits: el primero lo hace el humano, al final (paso 6).

## 0. Soltar la plantilla y fijar el perfil

**Primero, con el sí del humano**, borra lo que solo sirve en el repo de la
plantilla: `HARNESS.md`, `scripts/harness_bundle.py`,
`tests/test_harness_bundle.py` y, si vinieron con la copia, `AUDITORIA.md`
y `PILOTO_PENDIENTE.md`. `HARNESS.md` guarda una copia de cada fichero y su
test falla en cuanto el proyecto adapta uno. Desde aquí, el harness del
proyecto son sus ficheros pequeños: se cambian cuando haga falta, y lo que
sirva para otros proyectos se apunta en `progress/para_la_plantilla.md`.

Después, **el perfil**. Pregunta, de una en una y con tu recomendación:
para quién es (solo para el humano, para personas conocidas o abierto al
público), qué pasa si falla o pierde datos, si mueve dinero o datos
sensibles de otros y qué quiere sacar el humano (aprender, tenerlo
funcionando, un producto). Propón el perfil con esta tabla y deja que el
humano cambie cualquier casilla:

| | personal | compartido | producción |
|---|---|---|---|
| Arranque | producto y las filas imprescindibles del mapa | mapa completo | mapa completo y `catalogo.md` entero |
| Spec formal | solo en features grandes o con zonas críticas; el resto, `"sdd": false` | todas salvo las triviales | todas salvo las triviales |
| Zonas críticas y mutantes | normalmente ninguna | las que haya | las que haya |
| CI | no | recomendado | sí |
| Auditoría de seguridad completa | cuando la pida el humano | cada 4 features | cada 4 features o al cerrar una fase |

Copia `plantillas/arranque.md` a `progress/arranque.md` y apunta ahí el
perfil y sus casillas, y también en "Parámetros del harness" de
`CLAUDE.md`, que es lo que lee el leader después. El perfil
se puede cambiar más adelante: se vuelve a esta tabla.

## 1. Producto

Primera tanda, abierta. Como mínimo debe quedar claro (y sigue tirando del
hilo cuando una respuesta abre otra):

- qué es, para quién, qué problema resuelve; qué entra en la primera
  versión y **qué no**;
- **dónde y en qué dispositivos se usa**, ahora y más adelante (escritorio,
  web, móvil, sin conexión);
- qué datos maneja, dónde deben vivir, si son sensibles, quién los ve (uno
  o varios usuarios) y cuánto costaría perderlos;
- **cuánto pesa la interfaz** (austera, pulida, con animaciones): condiciona
  el stack;
- volumen y crecimiento, presupuesto (gratis, de pago y cuánto), plazos;
- **preferencias y vetos del humano**: lenguajes que conoce o quiere
  aprender, servicios que ya usa, cosas que no quiere.

Escribe `CLAUDE.md` (qué es, para quién; "Estado") y `feature_list.json`:
`F00` (andamiaje, ya en la plantilla; se completa en el paso 4) y después
las features de producto en orden, la primera la más pequeña que aporte
valor.

## 2. Mapa de decisiones

Con el producto, rellena en `progress/arranque.md` la tabla de **todas** las
decisiones técnicas que aplican (borra las que no), en orden de
dependencia. Con perfil **personal**, solo las que el producto no puede
dejar sin decidir. Con **compartido** o **producción**, lee también
`catalogo.md` y añade una fila por cada tema que aplique (bloque
"Escala"), cada una con qué es en una línea y si se decide ahora o se
aplaza con disparador.

| Bloque | Decisiones |
|---|---|
| Plataforma | tipo de app (web, escritorio, móvil, CLI, servicio), empaquetado y distribución, sin conexión |
| Arquitectura | forma (monolito, cliente-servidor, local-first, serverless…), capas y fronteras, dónde vive cada pieza |
| Backend | lenguaje y versión, framework, estilo de API y contratos, validación, errores, tareas en segundo plano |
| Datos | almacenamiento o base de datos, ORM o acceso, migraciones y versionado de formatos, copias de seguridad |
| Seguridad | autenticación y autorización, secretos, riesgos propios y zonas sensibles |
| Frontend | framework, enrutado, estado y caché de datos, formularios, i18n, accesibilidad. Librería de componentes, estilos, iconos, animación, gráficos y fuentes: solo una propuesta; se deciden en `/direccion-visual`, con referencias delante |
| Calidad | tests por capa (unidad, integración, extremo a extremo), lint, formato, tipos, auditoría de dependencias, **zonas críticas** (dinero, datos, permisos, parsers…) y la **herramienta de mutantes** del stack para ellas |
| Operación | build, CI (según el perfil), despliegue y ramas, entornos, logs y errores, coste |
| Escala | las filas que salgan de `catalogo.md` (perfil compartido o producción) |

Cada fila con una **propuesta** y un **modo**:

- **obvia**: hay una opción claramente mejor para este producto (dilo y
  por qué); se acepta en bloque;
- **a elegir**: 2-3 opciones conocidas con sus pros y contras; decide el
  humano;
- **a investigar**: hay hechos que no sabes con seguridad (versión,
  mantenimiento, licencia, límites de un plan, soporte de una plataforma)
  o una apuesta arriesgada.

Cierra el mapa con los **2-3 supuestos de riesgo**: lo que, si resulta
falso, obliga a cambiar una decisión de base (que un puente entre procesos
funcione con la CSP, que una librería corra en la plataforma, que un plan
gratuito aguante el volumen). Los comprobará `F00` antes de escribir
producto.

Enseña el mapa y deja que el humano lo ajuste: cambiar el modo de una
fila, decidir alguna él directamente, marcar qué investigar y con cuánto
esfuerzo. **Solo entonces** se pasa al paso 3.

## 3. Decidir, bloque a bloque

Por bloque y en orden:

1. Las **obvias**, en una sola pregunta para aceptarlas o abrir alguna.
2. Las **a investigar** que el humano aprobó, todas las del bloque a la
   vez y en paralelo:
   - `explorer` para preguntas acotadas (una librería, un plan, un límite);
   - `/deep-research` (workflow de serie de Claude Code) para una pregunta
     amplia que necesita fuentes cruzadas; es el más caro;
   - una **prueba mínima** en el scratchpad si una opción depende de algo
     sin comprobar (que un puente entre procesos funcione, que una
     librería corra en la plataforma);
   - `council` si, tras investigar, sigue habiendo varias buenas sin
     ganadora y el humano quiere contraste.
   Cada hecho con fuente y fecha. Las librerías, con licencia, último
   release y si cumplen la política de dependencias.
3. Las **a elegir**, con las opciones y la recomendación (ya con lo
   investigado).
4. Antes de cerrar el bloque, **coherencia** con lo ya decidido (versiones
   compatibles, licencias, plataforma, CSP, coste) y **qué la haría
   revisable**: cada decisión se marca fija o revisable con su disparador
   ("app móvil: revisar al cerrar la fase 2").

Actualiza `progress/arranque.md` al cerrar cada bloque.

## 4. Lo que queda escrito

- **ADR** en `docs/adr/` para cada decisión de arquitectura, plataforma,
  datos o framework principal (skill `architecture-decision-records`:
  contexto, decisión, alternativas y por qué no, consecuencias, cuándo
  revisarla).
- `docs/architecture.md`, sección "Stack y librerías": cada pieza con
  versión, para qué, alternativa descartada y su ADR si lo tiene. Es la
  lista de dependencias aprobadas: lo que no esté ahí sigue pidiendo
  permiso.
- `F00` en `feature_list.json` con sus scopes reales y una línea de
  `acceptance` por supuesto de riesgo. Va en modo ligero: andamiaje con el
  generador oficial, `init.sh` que sabe fallar, CI en verde (si el perfil
  lo lleva) y un "hola mundo" de punta a punta. Quita las líneas de
  `acceptance` que el perfil no lleve (CI, mutantes).
- **CI**: si el perfil lo lleva, `.github/workflows/ci.yml` con la
  toolchain de cada stack, con versión fijada y actions fijadas por SHA. Si
  no, borra el fichero. Un CI en rojo avisa, pero no bloquea el trabajo. Lección: en el piloto la primera feature cargó
  con el toolchain y el cambio de stack, y necesitó 11 IT.
- `harness.json` (scopes, secretos), el resto de `CLAUDE.md` (la tabla
  "Dónde vive cada pieza" enlaza a los ADR), `docs/security.md`,
  `docs/verification.md` (con las zonas críticas), `docs/<scope>/conventions.md` y
  `<scope>/init.sh` desde `plantillas/stack/`, las zonas sensibles de
  `.claude/agents/leader.md` y la entrada de `docs/CHANGELOG.md`.
- **Skills según el stack**, propuestas al humano; con su sí, en `skills:`
  del agente y `"name-only"` en `skillOverrides` de `.claude/settings.json`:

| Si el proyecto… | Skill | Agente |
|---|---|---|
| usa React | `vercel-react-best-practices`, `vercel-composition-patterns` | `implementer_ui` |
| usa la API View Transitions | `vercel-react-view-transitions` | `implementer_ui` |
| usa Python | `modern-python` | `implementer` |
| tiene usuarios o servidor | `prd-securability-enhancement` | `spec_author` |
| usa una plataforma con skills propias (Supabase, Cloudflare…) | las suyas, si están instaladas | el que las use |

  Lo que no esté instalado se apunta en `README.md` ("Skills opcionales") y
  se le dice al humano cómo instalarlo.

## 5. Diseño

Si hay interfaz, `/direccion-visual` **después de F00** y antes de la
primera feature con pantallas: ahí se eligen, con referencias reales que
aporta el humano, las librerías de interfaz (componentes, iconos,
animación, fuentes) y el aspecto, y los tokens se escriben ya en el
stack. F00 instala solo el framework. Lección del banco de pruebas: con la librería
de componentes decidida en el arranque, quedó instalada antes de mirar
ninguna referencia.

## 6. Aprobación final

Antes de pedirla, comprueba:

- ninguna fila abierta en `progress/arranque.md` (decidida, aplazada con
  disparador, o "no aplica");
- ningún hueco por rellenar (`grep -rn "<RELLENAR" .`; `README.md` y
  `plantillas/` citan la marca sin ser huecos);
- los documentos no se contradicen entre sí (lo que dice `CLAUDE.md`,
  los ADR, "Stack y librerías", las convenciones y `init.sh`);
- `F00` tiene sus supuestos de riesgo y la primera feature de producto se
  puede especificar con lo decidido, sin preguntas de arquitectura
  pendientes.

Enseña al humano un resumen de una pantalla: decisiones por bloque (con las
revisables y su disparador), documentos escritos y lo que le queda al
humano: instalar gitleaks y `git config core.hooksPath .githooks`, el CI si
lo hay, demostrar que cada paso de `init.sh` sabe fallar y el primer
commit. **Con su sí explícito**, añade
`Estado: APROBADO` (fecha) a `progress/arranque.md`; desde ahí `state.py`
despacha la primera feature. Si luego cambia una decisión de base, se
vuelve a su fila del mapa y a su ADR (leader, "Skills").
~~~~~~~

### `.claude/skills/arranque/catalogo.md`

~~~~~~~ fichero=.claude/skills/arranque/catalogo.md
# Catálogo: lo que se plantearía un equipo profesional

Se lee en el paso 2 de `/arranque` con perfil **compartido** o
**producción**. No es una lista que cumplir: sirve para que nada importante
se quede sin pensar por no saber que existía. El humano no tiene por qué
conocer estos temas; tú los traes.

Por cada tema que aplique: qué es en una línea, por qué importa **en este
producto** y tu propuesta (**ahora**, **más adelante** con su disparador o
**no aplica**). El criterio para elegir:

- **Si es caro cambiarlo después, se decide ahora.** Son cosas que quedan
  repartidas por todo el código o por los datos.
- **Si es barato añadirlo después, se aplaza** hasta que aparezca la señal
  (YAGNI). Hasta entonces, con la opción simple.

Faltan temas seguro: añade los que pida el producto (pagos, tiempo real,
IA, mapas, ficheros grandes…). Si no sabes cómo lo resuelven productos
parecidos, propón investigarlo (modo **investigar**, con su coste).

## Caro de cambiar después: se decide en el arranque

| Tema | Qué es | Señal de que aplica | Por defecto sensato |
|---|---|---|---|
| Forma de la arquitectura | monolito, monolito modular o servicios separados | casi siempre | monolito modular; se parte solo con un motivo medido |
| Servidor sin estado | nada de sesiones ni ficheros en la memoria o el disco de una instancia | más de una instancia, autoescalado, serverless | sesión en token o en un almacén compartido; ficheros en almacenamiento de objetos |
| Varios clientes u organizaciones (multi-tenant) | cómo se separan los datos de cada cliente | "empresas", "equipos", "cuentas" | columna de tenant y autorización en la capa de datos (RLS o equivalente) |
| Autenticación y autorización | quién eres y qué puedes hacer: proveedor o propia, roles | más de un usuario | un proveedor probado; contraseñas propias solo con motivo |
| Identificadores | autoincremental o UUID/ULID | IDs en URLs, sincronización, fusión de datos | no adivinables en lo que se expone |
| Dinero | importes, redondeo, moneda, cobros | cualquier cobro | enteros en céntimos o decimal; tarjetas solo a través del proveedor de pagos |
| Idempotencia | repetir una operación no la duplica | pagos, webhooks, colas, reintentos del cliente | clave de idempotencia en las escrituras que cobran o notifican |
| Fechas, idioma y región | UTC en los datos, textos traducibles, formatos locales | usuarios en varios países o idiomas | UTC siempre; textos fuera del código si hay más de un idioma previsto |
| Datos personales (RGPD) | qué se guarda, cuánto tiempo, cómo se exporta y se borra | datos de personas, usuarios de la UE | lo mínimo; borrado real; dónde viven los datos |
| Contratos de API y versiones | que un cliente antiguo siga funcionando | app móvil (no se actualiza a la vez), terceros que consumen la API | versionar desde el principio si hay clientes que no controlas |
| Migraciones del esquema | cambiar la base de datos sin parar ni perder datos | cualquier BD que vaya a evolucionar | herramienta de migraciones desde el día 1; expandir antes de contraer |
| Accesibilidad | teclado, contraste, lector de pantalla | interfaz para el público | desde el principio: añadirla al final es rehacer pantallas |
| Coste que crece con el uso | qué se paga por usuario, petición o GB | proveedores de pago o con límites gratuitos | alerta de presupuesto en cada proveedor desde el día 1 |

## Barato después: se aplaza con su disparador

| Tema | Qué es | Disparador para hacerlo | Mientras tanto |
|---|---|---|---|
| Caché | guardar resultados caros para no recalcularlos (memoria, Redis, CDN, cabeceras HTTP). Lo difícil es invalidarla | lecturas repetidas con latencia medida alta, o coste de una API externa | sin caché; cabeceras HTTP en los estáticos |
| Pool de conexiones a la BD | reutilizar conexiones en vez de abrir una por petición | errores "too many connections", mucha concurrencia. **En serverless, ahora**: cada instancia abre las suyas | el pool del driver o del ORM; en serverless, el pooler del proveedor |
| Escalado horizontal | más instancias detrás de un balanceador (requiere servidor sin estado) | CPU o latencia al límite con una instancia | una instancia y el autoescalado del proveedor |
| Colas y segundo plano | sacar lo lento de la petición (correos, procesar ficheros, llamadas externas) | peticiones de más de 1-2 s, trabajo que hay que reintentar | cola del proveedor o tabla en la BD; nunca hilos sueltos |
| Límites de uso (rate limiting) | que nadie tumbe el servicio ni pruebe contraseñas a fuerza bruta | API pública, mucho tráfico | **en login y registro, ahora**; en el resto, con tráfico |
| Paginación y topes | ninguna lista ni subida sin tamaño máximo | listas que crecen con los usuarios | tope en todo desde el principio (es una convención, no infraestructura) |
| Observabilidad | logs estructurados, errores con contexto (tipo Sentry), métricas, alertas | usuarios que no eres tú: no te contarán qué falla | logs estructurados y captura de errores en la primera versión pública; métricas y trazas con varios servicios |
| Copias y restauración | copias automáticas y **una restauración probada** | datos que no se pueden regenerar | copias del proveedor; probar una restauración antes de abrir al público |
| Entornos | local, pruebas (staging) y producción, con datos y secretos separados | usuarios a los que no puedes romper nada | local y producción |
| Despliegue y vuelta atrás | desplegar sin cortar y volver a la versión anterior en minutos | despliegues frecuentes, usuarios que pagan | el del proveedor con rollback; feature flags si se despliega más de lo que se publica |
| Disponibilidad (SLO) | cuánto tiempo caído es aceptable; decide la redundancia | clientes que pagan, contratos | sin objetivo formal |
| CDN | servir estáticos e imágenes desde cerca del usuario | usuarios lejos del servidor, imágenes pesadas | la del hosting |
| Búsqueda | texto completo, filtros, relevancia | la de la BD se queda corta o lenta | la búsqueda de texto de la BD |
| Ficheros subidos | almacenamiento de objetos, tipo y tamaño máximos, URLs firmadas | subidas de usuarios | almacenamiento del proveedor con límites |
| Correo y notificaciones | proveedor transaccional, plantillas, bajas | correos a usuarios | proveedor transaccional; nunca SMTP propio |
| Tiempo real | websockets o SSE, reconexión, presencia | chat, colaboración, paneles en vivo | sondeo periódico |
| Registro de acciones | quién hizo qué y cuándo | varios administradores, dinero, B2B | logs de aplicación |
| Pruebas de carga | medir antes de optimizar | lanzamiento con fecha, pico previsto | nada |
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

1. Confirma con el humano (es una ejecución cara sobre todo el repo) y elige
   con él el motor; los dos primeros orquestan muchos agentes y solo
   funcionan desde la sesión principal, nunca desde un subagente:
   - **`security-audit`** (Cloudflare), si está instalada: modo auditoría
     completa, perfil `quick` o `standard` y presupuesto de agentes
     acordados con el humano. Su salida va fuera del repo
     (`~/security-audit-skill/<repo>/run-<N>`, déjala ahí).
   - **`/insecure-defaults:audit`** (Trail of Bits), si está instalado: más
     barato y acotado a configuraciones inseguras por defecto (secretos de
     respaldo, credenciales por defecto, modos que fallan abiertos, CORS
     `*`, debug). Puede acompañar a cualquiera de los otros dos.
   - **`security_reviewer` en modo auditoría**: el de siempre, si no hay
     ninguna de las anteriores o el humano prefiere un solo agente.
2. Crea `progress/audits/<AAAA-MM-DD>/` (`-2` si ya existe una ese día).
3. Con `security_reviewer`, lánzalo con: "Modo auditoría. Carpeta
   `progress/audits/<fecha>/`. Revisa el repositorio entero contra su estado
   actual (ver tu sección 'Modo auditoría'). Escribe `informe.md` (≤ 200
   líneas) y, si hace falta, `evidencia.md`." Con las otras, escribe tú
   `informe.md` (≤ 200 líneas) a partir de su informe: hallazgos
   confirmados con gravedad y `archivo:línea`, los pendientes de validar
   aparte, y la ruta del informe original en `evidencia.md`.
4. La línea de `progress/metrics.csv` la escribe el hook de métricas con
   `feature = audit`; con los motores de la sesión principal no hay
   subagente que la dispare: apúntala tú (`it = <fecha>`).
5. Vuelve al primer apartado para dar destino a los hallazgos.
~~~~~~~

### `.claude/skills/direccion-visual/SKILL.md`

~~~~~~~ fichero=.claude/skills/direccion-visual/SKILL.md
---
name: direccion-visual
description: Decide con el humano la direccion visual del proyecto (librerias de interfaz, tokens, tipografia, movimiento) a partir de referencias reales que aporta el humano y de tres direcciones comparadas, y deja docs/<scope>/direccion-visual.md, los tokens en el stack y las capturas aprobadas. Tras F00 y antes de la primera feature con pantallas, o para redisenar. Solo la sesion principal (leader).
---

# Dirección visual

Lecciones:
- Piloto: la paleta salió de páginas de marketing y de los valores por
  defecto (índigo, Inter, tarjetas iguales) y las pantallas "se notaban
  hechas con IA".
- Banco de pruebas (2026-10-11): con "evita lo genérico" como único
  criterio salió una propuesta distinta pero amateur (fuente rara en todo,
  cifras en monoespaciada, fondo tintado, muchos colores saturados).
  Faltaban un listón y opciones entre las que elegir.

Va **después de F00** (el framework ya está instalado) y antes de la
primera feature con pantallas; se repite solo para rediseñar. Objetivo:
**profesional antes que original**. Lo distintivo, en uno o dos detalles;
el resto, contención.

## 1. Contexto, primero para el humano

Lee `CLAUDE.md`, `progress/arranque.md` y el `acceptance` de la primera
feature con interfaz. **Antes de preguntar**, cuéntale en 3-4 líneas qué es
el producto, qué pantallas vienen y qué queda fuera. Si ya hay interfaz,
captúrala.

## 2. Referencias: las aporta el humano

**Sin referencias no se propone nada.** Pídele 3-6 capturas de productos
reales que le parezcan profesionales y del mismo tipo (sector, plataforma,
densidad): de Refero, Mobbin o apps que use. Las guarda en
`docs/<scope>/direccion-visual/referencias/`. Si el MCP de Refero está
conectado, puedes proponerle candidatas, pero elige él.

De cada una, una línea: qué se toma (escala tipográfica, espaciado, cuánto
color y dónde, cómo muestra cifras y listas, densidad) y qué no.

## 3. Preguntas, pocas y con recomendación

Tono, claro/oscuro, densidad, cuánto movimiento y las **librerías de
interfaz**: componentes, iconos, animación y fuentes (licencia; servidas en
local si hay CSP). El arranque fijó el framework; estas se eligen aquí, con
las referencias delante (`pick-ui-library`). Cada dependencia, con el sí
del humano y a "Stack y librerías" de `docs/architecture.md`.

## 4. Tres direcciones, y elige el humano

- **Con Google Stitch** (stitch.withgoogle.com, a mano, lo maneja el
  humano): redacta un prompt por dirección para la pantalla principal, con
  contenido real (normal y peor caso), las referencias como imágenes y las
  restricciones. Tres direcciones de verdad distintas (densidad, jerarquía,
  uso del color), no tres paletas. El humano elige y guarda en
  `docs/<scope>/direccion-visual/stitch/` las capturas y el `DESIGN.md` de
  la elegida. El HTML que exporta es referencia, no código del producto.
- **Sin Stitch**: las haces tú como miniaturas HTML
  (`frontend-design:frontend-design`, `ui-ux-pro-max` para paletas y
  fuentes) y se las enseñas juntas.

Antes de enseñarlas, descarta lo que tenga **señales de amateur**: fuente
"con personalidad" en todo el texto, fondo de página tintado, muchos colores
saturados, cifras en monoespaciada en lugar de números tabulares, dos
fuentes expresivas compitiendo, insignias repetidas en cada fila.

## 5. Qué deja escrito

- **Los tokens, en un único sitio y en la forma nativa del stack** (tema de
  la librería de componentes, variables CSS, configuración de Tailwind…):
  colores claro/oscuro con su contraste, tipografía y escala, espaciado,
  radios, sombras y duraciones. Las pantallas no usan valores sueltos.
- `docs/<scope>/direccion-visual.md` (≤ 120 líneas), que leen
  `spec_author`, `implementer_ui` y `reviewer`: propósito y tono, las
  referencias y qué se toma de cada una, dónde viven los tokens y el papel
  de cada uno (los valores no se copian), tipografía, layout y densidad,
  reglas de componentes, movimiento (qué, cuándo, duraciones) y lo
  prohibido.
- Las capturas aprobadas de la pantalla principal (claro y oscuro, 1280 y
  390 px, normal y peor caso) en `docs/<scope>/direccion-visual/`.
- En `docs/<scope>/conventions.md`, el comando del modo de datos falsos con
  su peor caso.
- Si el MCP del navegador no arranca (p. ej. busca Chrome y solo hay Edge),
  configúralo para el navegador instalado (Playwright: `--browser msedge`)
  y anótalo en `conventions.md`.
- Entrada en `docs/CHANGELOG.md`, con el "Aprobado por" del humano.
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

- **Contra una línea base** (otro proyecto, o el mismo antes de un cambio):
  `bash scripts/py.sh scripts/comparar.py <base.csv>` da primeras entregas
  aprobadas, rechazos por causa, peso de las IT de corrección, pasadas del
  security_reviewer, coste por feature y el implementer por modelo.
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
- **Skills**: la columna `skills` de `metrics.csv` dice cuáles se
  invocaron de verdad. Una precargada que nunca cambia nada en los
  veredictos es candidata a quitar; una que se invoca a menudo, a precargar.
- **Coste fijo del contexto** (método de `context-budget` de ECC): cada
  turno de cada agente relee las definiciones, las skills precargadas, el
  listado de skills (`skillOverrides` de `.claude/settings.json` lo
  recorta) y los esquemas de herramientas MCP no diferidas. Estímalo
  (palabras × 1,3) y propón recortes con su ahorro.
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
- **Decisiones revisables**: en `docs/adr/`, las que dicen "revisable"
  con su disparador. Si el disparador ya se cumplió (la fase cerró, el
  volumen llegó), propón al humano revisarla.
- **Atajos**: busca la etiqueta `ATAJO:` (`docs/principios.md`) en el
  código. Para cada uno: mantener, pagarlo ya o convertirlo en feature.
- **Sobreingeniería**, solo si el humano lo pide (recorre el repo entero):
  `/ponytail:ponytail-audit` si está instalada (devuelve una lista ordenada de qué
  borrar o simplificar); si no, lanza `explorer` con el encargo "código que
  sobra: abstracciones con una sola implementación, código muerto, lo que
  ya hace la librería estándar o una dependencia instalada". El resultado va
  a `progress/explore_sobreingenieria.md`; aquí, solo su resumen.
- **Código frente a specs**, al cerrar una fase y solo con el sí del humano
  (lanza un agente por requisito: es cara):
  `/spec-to-code-compliance:spec-to-code-compliance` sobre las specs de la fase. Sus
  divergencias confirmadas se tratan como hallazgos de auditoría (feature
  nueva o línea de `acceptance`).

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

# docs/ cambia con su entrada en docs/CHANGELOG.md. Avisa, no bloquea: es
# costumbre del harness, no una regla dura (CLAUDE.md).
bash scripts/check_docs_changelog.sh || echo "pre-commit: aviso, falta la entrada en docs/CHANGELOG.md (el commit sigue)." >&2

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

# Opcional: /arranque lo deja o lo borra segun el perfil del proyecto. Un
# rojo aqui avisa al humano; no bloquea el trabajo del harness.

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
      # Sin `version`, la action instala el ultimo uv publicado (leccion del
      # piloto: choco con la politica de antiguedad de dependencias).
      - uses: astral-sh/setup-uv@c18668ad3cf93ea998bef934396af7bb5c839dc7 # v10.2.0 (harness en Python)
        with: { version: "0.11.21" }
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

      # Lo mismo que el pre-commit, y como alli solo avisa: es costumbre del
      # harness, no una regla dura. Sin base (rama nueva) no hay rango.
      - name: docs/ con su entrada en docs/CHANGELOG.md
        continue-on-error: true
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

# Salidas de las herramientas de mutantes (docs/verification.md): copias del
# codigo que no se commitean ni deben recoger los tests ni el lint.
mutants/
.mutmut-cache
.stryker-tmp/
reports/mutation/
mutants.out*/

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

- Cada `R<n>` tiene un test que lo cubre de verdad (en zonas críticas, verificado con mutantes).
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

<!-- Cada fila resuelve una restricción concreta. Borra las que no apliquen.
Alternativas descartadas y cuándo revisar cada decisión: docs/adr/. -->
| Pieza | Dónde | Por qué ahí |
|---|---|---|
| <RELLENAR: API> | <servicio> | <restricción que resuelve> |
| <RELLENAR: datos> | <servicio> | <…> |

## Restricciones que rompen cosas si se ignoran

- <RELLENAR: cada una con su motivo y su dueño en CHECKPOINTS.md.>

## Reglas duras

Protegen lo que no tiene vuelta atrás; no se relajan.

- **Nada de `git commit` ni `push` sin aprobación del humano** (los pide
  `settings.json`); nunca `--amend`, `push --force` ni reescritura de
  historia: el historial es la evidencia de qué iteración introdujo qué.
- **Ninguna dependencia nueva sin preguntar**, con una alternativa sin ella.
- **Los secretos no pasan por el contexto**: no se leen `.env` ni ficheros de
  secretos, no se imprimen, no se copian. Nombres en `harness.json`.
- **Nada destructivo sobre datos reales** (`DROP`, `TRUNCATE`, `DELETE` o
  `UPDATE` sin `WHERE`).
- **Avisar antes de tocar servicios reales** y de si cuesta dinero.
  <RELLENAR: política de coste, p. ej. "solo planes gratuitos".>

## Por defecto, y el humano manda

El resto del harness es una forma de trabajar, no una atadura. Las
decisiones son del humano, y el leader debe proponer quitar o relajar lo
que estorbe en este proyecto.

- **`docs/`, este fichero y las reglas del harness los decide el humano**;
  los agentes no los cambian por su cuenta. Cada cambio en `docs/` lleva su
  entrada en `docs/CHANGELOG.md` (el pre-commit avisa si falta).
- **`done` solo por el protocolo**: el `implementer` en el cierre, con
  `review.md` y `security.md` de la misma IT en `APPROVED`.

## Parámetros del harness

| Parámetro | Valor | Por qué |
|---|---|---|
| Perfil | <RELLENAR: personal / compartido / producción (lo fija `/arranque`)> | decide cuánto proceso compensa |
| CI | <RELLENAR: sí / no> | si lo hay, un rojo avisa pero no bloquea |
| Veredictos e `impl.md` | ≤ 200 líneas | el leader y los revisores los leen enteros; lo largo va a `evidence.md` |
| Spec (tres ficheros) | ~400 líneas (≈ 6-8 k tokens); partir pasado de 600 o de ~20 `R<n>` | cada agente la relee en cada iteración |
| Auditoría completa | <RELLENAR: según el perfil: cada 4 features cerradas o al cerrar una fase / cuando la pida el humano> | cada revisión solo mira su diff |
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

Una entrada por cambio, la más reciente arriba. El pre-commit (y el CI, si
lo hay) avisa de un cambio en `docs/` que no toque este fichero.
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

## 2026-10-12 — Perfil del proyecto, CI opcional y el harness al servicio del humano
- Ficheros: docs/CHANGELOG.md, docs/security.md, docs/README.md
- Antes → ahora: HARNESS.md y su test viajaban al proyecto y ponían el CI
  en rojo cada vez que se adaptaba un fichero → `/arranque` los borra en el
  paso 0. El CI era obligatorio → lo decide el perfil (personal, compartido,
  producción) y un rojo avisa sin bloquear. El CHANGELOG de `docs/` lo
  exigían el pre-commit y el CI → avisan. `CLAUDE.md` separa las reglas
  duras (no se relajan) de lo que es "por defecto" (lo cambia el humano, y
  el leader propone cambiarlo cuando estorba). `/arranque` pasa a ser una
  entrevista con recomendación en cada pregunta y trae `catalogo.md`
  (caché, pooling, escalado, observabilidad…) para los perfiles compartido
  y producción
- Por qué: en el piloto el CI fallaba por HARNESS.md desfasado, y el
  harness se vivía como una atadura en lugar de como una ayuda
- Aprobado por: humano (2026-10-12)
- Propagado a: CLAUDE.md, .claude/agents/leader.md,
  .claude/skills/arranque/ (SKILL.md, catalogo.md), plantillas/arranque.md,
  .githooks/pre-commit, .github/workflows/ci.yml, feature_list.json,
  tests/test_docs_changelog.py, HARNESS.md
- Cómo se medirá: en el próximo proyecto, número de fallos de CI o del
  pre-commit que no fueran del producto, y preguntas del arranque que el
  humano respondió con "no lo sé" (tienen que salir con recomendación)

## 2026-10-11 — Seguridad en serie, tras el reviewer
- Ficheros: docs/specs.md
- Antes → ahora: en el último tramo, reviewer y security_reviewer en
  paralelo sobre cada IT → primero el reviewer; el security_reviewer solo
  sobre una IT que el reviewer aprobó (sigue siendo solo en el último
  tramo). Cualquier rechazo abre una IT que vuelve a pasar por el reviewer
- Por qué: en el piloto el reviewer rechazó 49 de 96 revisiones; en
  paralelo, la mitad de las pasadas de seguridad (~61 k tokens cada una)
  caían en IT que iban a rehacerse, para ganar unos 3 minutos
- Aprobado por: autor de la plantilla
- Propagado a: scripts/state.py (y sus tests), .claude/agents/leader.md,
  reviewer.md, security_reviewer.md, plantillas/stack/conventions.md,
  HARNESS.md
- Cómo se medirá: `comparar.py`, "Pasadas del security_reviewer" por
  feature frente a la línea base

## 2026-10-11 — Foto del árbol por IT y quién ejecuta `init.sh` completo
- Ficheros: docs/specs.md, docs/verification.md
- Antes → ahora: el security_reviewer revisaba "desde su commit base"
  (`git rev-parse HEAD`) → desde la foto de `IT1` (`scripts/foto.sh`, un
  árbol de git con lo no seguido, sin commits); `init.sh` completo "en el
  security_reviewer, el cierre y el CI" → en el implementer antes de
  entregar (ya lo pedía su definición), el security_reviewer y el CI (el
  cierre solo edita texto)
- Por qué: las IT no se commitean, así que "el diff de la IT" no existía
  (piloto F08 IT4: el reviewer no pudo comparar con IT3); la base fallaba
  sin commits y arrastraba la feature anterior si no se había commiteado
- Aprobado por: autor de la plantilla
- Propagado a: .claude/agents/leader.md, reviewer.md, security_reviewer.md,
  CHECKPOINTS.md, init.sh, HARNESS.md
- Cómo se medirá: rechazos con causa `otro` por diffs mal leídos

## 2026-10-11 — Copias, procesos y cambios de rumbo sin pisar a nadie
- Ficheros: docs/verification.md
- Antes → ahora: sin regla sobre el scratchpad, las copias ni los procesos
  → cada agente en `<scratchpad>/<F>-IT<n>-<rol>/`, copias sin enlaces a
  `node_modules`/`.venv` (o el enlace se quita antes de borrar), procesos
  por PID (el hook bloquea matar por nombre y reescribir la historia).
  Fuera de docs/: IT descartable con `descartada.md` y reabrir una `done`
  como feature nueva (leader.md, state.py)
- Por qué: piloto (Gestor): `mut.py` pisado entre agentes (F13a IT2),
  junction a `node_modules` a un `rm -rf` de vaciarlo (F12 IT5),
  `taskkill` de todos los `node` (F03 IT6), IT de un framework abandonado
  sin forma de descartarla (F01 IT4), F13a reabierta a mano
- Aprobado por: autor de la plantilla
- Propagado a: .claude/agents/leader.md, scripts/guard_secrets.py,
  scripts/state.py, plantillas/stack/conventions.md (carpeta de trabajo de
  los mutantes fuera de tests y lint), .gitignore, HARNESS.md
- Cómo se medirá: en `para_la_plantilla.md`, ningún caso nuevo de esos

## 2026-10-10 — Menos iteraciones: mutantes por stack, vetos al final y en paralelo
- Ficheros: docs/verification.md, docs/specs.md
- Antes → ahora: mutantes a criterio de cada rol en todo el código → la
  herramienta de mutantes del stack, en zonas críticas, con el mismo comando
  para implementer y reviewer (fuera de ellas, un test flojo es una
  observación); TDD obligatorio → rojo demostrado por el mutante o el
  sabotaje; security_reviewer en cada tramo y después del reviewer → solo en
  el último tramo, en paralelo, sobre la feature entera; re-revisión
  completa siempre → acotada si el arreglo solo toca tests; `init.sh`
  completo en cada vuelta → `--rapido` para implementer y reviewer; tramos
  sin límite → dos como mucho; tests intermitentes anotados → se arreglan
  en la siguiente IT; task humana para mirar la interfaz → solo con
  servicios reales
- Por qué: piloto (Gestor): 42 de 44 primeras entregas rechazadas (31 por
  `tests`); IT de corrección = 37 % del tiempo y 41 % de los tokens;
  security 46 pasadas y 2 rechazos (131 min, 2,8 M tokens); 8 tests
  intermitentes sin arreglar; 9 features seguidas sin task humana
- Aprobado por: autor de la plantilla
- Propagado a: scripts/state.py (vetos por tramo), scripts/metricas.py
  (hook SubagentStop: el leader ya no escribe métricas), init.sh y
  plantillas/stack/ (--rapido, comando de mutantes), .claude/agents/
  (implementer, reviewer, security_reviewer, spec_author, leader),
  .claude/skills/arranque, plantillas/arranque.md, HARNESS.md
- Cómo se medirá: primeras entregas aprobadas, IT por feature y tokens por
  feature en metrics.csv frente al piloto

## 2026-10-10 — Interfaz con dirección visual y capturas; skills precargadas
- Ficheros: docs/specs.md, docs/verification.md, docs/README.md,
  docs/architecture.md, docs/adr/README.md (nuevo)
- Antes → ahora: decisiones de arquitectura repartidas en `CLAUDE.md` sin
  alternativas ni disparador de revisión, y la primera spec podía empezar
  con el stack a medio decidir → `/arranque` guiado por el humano (mapa de
  todas las decisiones técnicas, investigación solo la que él apruebe),
  ADR en `docs/adr/`, "Stack y librerías" en `docs/architecture.md` como
  lista de dependencias aprobadas, y `state.py` devuelve `ARRANQUE` hasta
  que el humano lo aprueba;
  el aspecto se fijaba como `R<n>` de cada spec y nadie veía
  la interfaz renderizada → dirección visual única en
  `docs/<scope>/direccion-visual.md` (skill `/direccion-visual`), tramos
  `(interfaz)` hechos por el `implementer_ui` con capturas que el `reviewer`
  revisa; skills precargadas por rol (`skills:`) en vez de "opcionales"
- Por qué: piloto (Gestor, 17 features): 0 invocaciones de skills de diseño
  en 110 ejecuciones del implementer, interfaces "hechas con IA" (paleta
  índigo y tarjetas por defecto) y fallos visuales encontrados por el humano
  (F03 T8, F09, InvestmentsPanel)
- Aprobado por: autor de la plantilla
- Propagado a: .claude/agents/ (implementer_ui nuevo, implementer,
  reviewer, security_reviewer, spec_author, explorer, leader),
  .claude/skills/ (arranque y direccion-visual nuevas, auditoria-seguridad,
  retrospectiva), .claude/settings.json (skillOverrides, guard_config),
  scripts/ (state.py, skills.py, agent_tokens.py, guard_config.py,
  guard_secrets.py),
  specs/_plantilla/tasks.md, plantillas/stack/conventions-web.md,
  harness.json, README.md, HARNESS.md
- Cómo se medirá: columna `skills` de metrics.csv; rechazos del reviewer
  por capturas frente a fallos visuales que encuentre el humano después

## 2026-10-03 — Hotfix sin excepción "urgente" y etiqueta ATAJO:
- Ficheros: docs/specs.md, docs/principios.md
- Antes → ahora: hotfix "delante si es urgente" → siempre justo tras la
  feature en curso; atajo "comentario con su límite" → etiqueta literal
  `ATAJO: <límite> · <camino de mejora>`
- Por qué: delante de la feature en curso quedaban dos en curso (rompe
  test_como_mucho_una_feature_en_curso); sin etiqueta fija la retrospectiva
  no puede encontrar los atajos
- Aprobado por: autor de la plantilla
- Propagado a: .claude/skills/auditoria-seguridad/SKILL.md,
  .claude/skills/retrospectiva/SKILL.md, HARNESS.md

## <RELLENAR: AAAA-MM-DD> — Creación de docs/ desde la plantilla
- Ficheros: todos los de docs/
- Antes → ahora: — → reglas iniciales del harness
- Por qué: arranque del proyecto
- Aprobado por: <RELLENAR: humano>
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
| ¿Por qué la arquitectura es así? ¿Cuándo se revisa? | `docs/adr/` |
| ¿Aspecto de la interfaz? | `docs/<stack>/direccion-visual.md` (skill `/direccion-visual`) |
| ¿Qué skills usa cada rol? | `skills:` de cada `.claude/agents/<rol>.md`; las nuevas o ausentes, `scripts/skills.py` |
| ¿Primer uso del harness? | skill `/arranque` |
| ¿Cuándo está terminada una feature? | `CHECKPOINTS.md` |
| ¿Qué cambió en las reglas y por qué? | `docs/CHANGELOG.md` |
| ¿Qué hace cada rol? | `.claude/agents/<rol>.md` |
| ¿Auditorías completas? | `progress/audits/` y la skill `/auditoria-seguridad` |
| ¿Coste de cada agente y causa de cada rechazo? | `progress/metrics.csv` |
| ¿Retrospectiva? | skill `/retrospectiva` |
| ¿Por qué el harness es así? ¿Cómo se reconstruye? | `HARNESS.md` del repo de la plantilla; en el proyecto lo borra `/arranque` (ningún agente lo carga al trabajar) |
~~~~~~~

### `docs/adr/README.md`

~~~~~~~ fichero=docs/adr/README.md
# Decisiones de arquitectura (ADR)

Una por decisión de arquitectura: contexto, decisión, alternativas
descartadas y por qué, consecuencias, y si es **fija** o **revisable** (con
su disparador). Las primeras las deja `/arranque`; las siguientes, la skill
`architecture-decision-records` cuando el humano cambia o toma una decisión
de ese calibre. Una decisión sustituida no se borra: pasa a "sustituida por
ADR-NNNN". Cada ADR nuevo o cambiado lleva su entrada en `docs/CHANGELOG.md`.

| ADR | Título | Estado | Revisable cuando | Fecha |
|-----|--------|--------|------------------|-------|
~~~~~~~

### `docs/architecture.md`

~~~~~~~ fichero=docs/architecture.md
# Arquitectura

## Estilo

<RELLENAR. Por defecto, **monolito modular**: un proceso por despliegue,
dividido en módulos que se llaman por funciones. Un servicio nuevo carga con
la prueba: qué problema paga la latencia y el despliegue extra.>

## Stack y librerías <!-- ajuste-2026-10-10 -->

La deja `/arranque`. Es la lista de dependencias aprobadas: lo que no esté
aquí pide permiso al humano. Las decisiones grandes, con su ADR en
`docs/adr/`.

| Pieza | Elección y versión | Para qué | Alternativa descartada | ADR |
|---|---|---|---|---|
| <RELLENAR> | | | | |

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
4. CI, si el perfil lo lleva: gitleaks sobre la historia completa. <!-- ajuste-2026-10-12 -->

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
cada tramo es una IT aprobada antes del siguiente. **Dos tramos como mucho**
(típicamente lógica y datos, después interfaz), salvo que haya más stacks:
cada tramo es otro ciclo de implementación y revisión. <!-- ajuste-2026-10-10 -->
El tramo que crea o
cambia pantallas lleva `(interfaz)` en su cabecera: lo hace el
`implementer_ui`, con capturas. <!-- ajuste-2026-10-10 --> Si hay servicios reales,
la última es la **prueba humana**, con `ÚNICA TASK CON SERVICIOS REALES` en
su cabecera. Mapa inverso `R<n> → T<n>` al final.

**El aspecto no es un `R<n>`**: colores, tipografía, componentes y
movimiento salen de `docs/<scope>/direccion-visual.md` (skill
`/direccion-visual`); la spec la cita y solo fija lo propio de sus
pantallas. <!-- ajuste-2026-10-10 -->

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
- **Los vetos**: primero el reviewer, siempre; en el último tramo (o en
  modo ligero), con su `APPROVED`, el security_reviewer, que revisa la
  feature entera desde la foto de su `IT1` (`scripts/foto.sh`). Lecciones
  del piloto: el security_reviewer pasó en cada tramo (47 veces) y rechazó
  2; y en paralelo con el reviewer revisaba IT que este rechazaba (el
  51 %). <!-- ajuste-2026-10-11 -->
- `CHANGES_REQUESTED` (de cualquiera) → nueva IT, que vuelve a pasar por el
  reviewer y, en el último tramo, por seguridad (acotados si el arreglo
  solo toca tests).
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

## Zonas críticas y mutantes <!-- ajuste-2026-10-10 -->

Lección del piloto: el reviewer rechazó 42 de 44 primeras entregas, casi
siempre por un mutante que sobrevivía en una línea que el implementer no
había saboteado; las IT de corrección fueron el 37 % del tiempo. Los dos
usaban criterios distintos, y el mismo rigor en dinero que en una animación.

**Zonas críticas** (las fija `/arranque`): <RELLENAR: p. ej. dinero y
cálculos, escritura de datos y migraciones, autenticación y permisos,
parsers y validación de entrada externa>.

- **En zonas críticas, la herramienta de mutantes del stack** (decidida en
  `/arranque`, comando en `docs/<scope>/conventions.md`) sobre los ficheros
  críticos tocados en la IT. La pasa el implementer antes de entregar y la
  repite el reviewer: **el mismo comando, el mismo criterio**. Cada
  superviviente acaba en un test nuevo o en "equivalente: <por qué>". Donde
  la herramienta no llega (una consulta, un filtro, configuración), un
  sabotaje a mano: borrar la línea, ver caer un test, restaurar.
- **Fuera de las zonas críticas**, un test de comportamiento por viñeta de
  cada task. Un test flojo ahí es una observación del reviewer, no un
  rechazo, salvo que un `R<n>` se quede sin ningún test.
- Resultado en `evidence.md`, encabezado `## Sabotajes` (`state.py` lo
  exige): comando, muertos/supervivientes y qué se hizo con cada
  superviviente; `N/A: <motivo>` si la IT no toca zonas críticas.
- **Rojo sobre el código real**: lo exigible es que el test caiga con el
  código roto, y eso lo demuestran el mutante o el sabotaje. Escribir el
  test antes es recomendable, no obligatorio (en el piloto no se cumplió y
  no era lo que protegía).
- **Revertir solo la línea de producción**: si hace falta revertir también
  el test o el arnés, el test no protegía nada.
- **Copias y sabotajes, cada agente en su carpeta**:
  `<scratchpad>/<F>-IT<n>-<rol>/`. El scratchpad es compartido; lección:
  el implementer pisó el `mut.py` del reviewer y este corrió la lista
  ajena. <!-- ajuste-2026-10-11 -->
- **Una copia no enlaza las dependencias del repo** (`node_modules`,
  `.venv`): un `rm -rf` de la copia puede atravesar el enlace y vaciar el
  original. Si enlazas, quita el enlace antes de borrar la copia.
- **Procesos, por su PID**: el hook bloquea matar por nombre (lección: un
  `taskkill /IM node.exe` mató todos los `node` de la máquina).

## Tests intermitentes

Un test que falla a veces es un fallo, no ruido: el leader lo apunta y se
arregla (o se pone en cuarentena con su motivo) en la siguiente IT de la
feature en curso. Lección: en el piloto se anotaron ocho y nadie los
arregló; cada uno costó repeticiones y desconfianza en los resultados.

## Interfaz: capturas <!-- ajuste-2026-10-10 -->

Los tests de interfaz (jsdom y similares) no ven el resultado: un texto
cortado, una columna desalineada o un diálogo vacío pasan en verde. En cada
tramo `(interfaz)`:

- el `implementer_ui` arranca el **modo de datos falsos** (normal y peor
  caso), captura cada pantalla tocada (claro/oscuro, 1280 y 390 px, ~8 como
  mucho) en `progress/<F>/IT<n>/capturas/` y las lista en `impl.md`
  (`## Capturas`);
- el `reviewer` las abre y bloquea **solo por fallos que se ven** (cortado,
  solapado, desalineado, contraste, peor caso roto, contradicción con
  `docs/<scope>/direccion-visual.md`). El gusto va a observaciones.

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
  tocados). **Re-revisión acotada**: si el rechazo anterior fue solo por
  `tests` y el diff de esta IT solo añade o cambia tests, se verifica lo
  pedido (cada superviviente citado ahora muere) y `init.sh --rapido`; si
  el diff toca producción, revisión completa.
  <!-- ajuste-2026-10-10 -->
- `init.sh --rapido` (tests, lint, formato, tipos) en las vueltas del
  implementer y del reviewer; `init.sh` completo (build, secretos,
  auditoría de dependencias) en el implementer antes de entregar, el security_reviewer y el CI.

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

Solo si la feature conecta con servicios reales (despliegue, pagos, correo,
APIs externas). Mirar la interfaz no es una task humana: lo cubren las
capturas. Lección: en el piloto, nueve features seguidas se cerraron sin
ejecutar su task humana, que el reviewer había revisado en cada IT1.
<!-- ajuste-2026-10-10 -->

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
    "id": "F00",
    "title": "Andamiaje y supuestos de riesgo (modo ligero)",
    "status": "pending",
    "sdd": false,
    "scope": ["<stack-a>", "<stack-b>"],
    "acceptance": [
      "Cada scope creado con el generador oficial de su framework y las versiones de 'Stack y librerias' (docs/architecture.md), sin dependencias fuera de esa lista",
      "<scope>/init.sh ejecuta tests, lint, formato, tipos, build, secretos y auditoria de dependencias, y se ha demostrado que cada paso sabe fallar (evidence.md)",
      "Un 'hola mundo' cruza la arquitectura de punta a punta (p. ej. interfaz -> API -> datos) y lo cubre un test",
      "<Cada supuesto de riesgo de progress/arranque.md, comprobado con una prueba minima; si alguno falla, se para y se vuelve a su fila del mapa>",
      "<Si hay zonas criticas: el comando de mutantes de docs/<scope>/conventions.md corre sobre un fichero de una de ellas>",
      "<Si el perfil lleva CI: el CI pasa con bash init.sh --all>"
    ]
  },
  {
    "id": "F01",
    "title": "<Primera feature de producto: la mas pequena que aporte valor sobre el andamiaje>",
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
  "secretos": ["<NOMBRE_DE_VARIABLE_SECRETA_1>", "<NOMBRE_DE_VARIABLE_SECRETA_2>"],
  "skills_revisadas": [
    "frontend-design:frontend-design",
    "ponytail:ponytail",
    "ponytail:ponytail-audit",
    "ponytail:ponytail-review",
    "ponytail:ponytail-debt",
    "ponytail:ponytail-gain",
    "ponytail:ponytail-help",
    "spec-to-code-compliance:spec-to-code-compliance",
    "skill-creator:skill-creator",
    "feature-dev:feature-dev",
    "code-review:code-review",
    "supabase:supabase",
    "supabase:supabase-postgres-best-practices"
  ]
}
~~~~~~~

### `init.sh`

~~~~~~~ fichero=init.sh
#!/usr/bin/env bash
# Dispatcher: lee el scope de la feature activa y delega en <scope>/init.sh.
#   ./init.sh            el scope de la feature activa (scripts/state.py)
#   ./init.sh --all      todos los scopes de harness.json
#   ./init.sh --dry-run  solo anuncia el scope
#   ./init.sh --rapido   tests, lint, formato y tipos; sin build, secretos ni
#                        auditoria de dependencias (combinable con --all)
set -euo pipefail
cd "$(dirname "$0")"

DRY=0
ALL=0
# Leccion: cada agente ejecutaba init.sh completo varias veces por IT, con
# install, build y auditorias que van a la red. Las vueltas del implementer
# y del reviewer usan --rapido; el completo, el implementer al entregar,
# el security_reviewer y el CI.
export HARNESS_RAPIDO=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --all)     ALL=1 ;;
    --rapido)  HARNESS_RAPIDO=1 ;;
  esac
done

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

echo "Scope activo: $SCOPES${HARNESS_RAPIDO:+ (rapido)}"
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

### `plantillas/arranque.md`

~~~~~~~ fichero=plantillas/arranque.md
# Arranque

<!-- Copiar a progress/arranque.md al empezar /arranque. state.py no
despacha ninguna feature hasta que la linea de estado diga APROBADO: no la
traduzcas ni la cambies de formato. -->

Estado: en curso

## Perfil

<personal | compartido | producción>, y las casillas que el humano cambió
de la tabla del paso 0 (spec formal, zonas críticas, CI, auditoría).

## Producto

<5-10 líneas: qué es, para quién, primera versión y lo que no entra,
dispositivos ahora y más adelante, datos y su sensibilidad, peso de la
interfaz, presupuesto, preferencias y vetos del humano.>

## Mapa de decisiones

Modo: **obvia** (se acepta en bloque) · **elegir** (2-3 opciones, decide el
humano) · **investigar** (solo con su sí y su coste dicho) · **no aplica**.
Borra las filas que no apliquen; añade las que falten.

| Bloque | Decisión | Propuesta | Modo | Decidido | Fija / revisable (cuándo) | ADR |
|---|---|---|---|---|---|---|
| Plataforma | tipo de app, empaquetado, sin conexión | | | | | |
| Arquitectura | forma, capas y fronteras, dónde vive cada pieza | | | | | |
| Backend | lenguaje y versión, framework, API y contratos, validación, errores, segundo plano | | | | | |
| Datos | almacenamiento, acceso u ORM, migraciones y formatos, copias | | | | | |
| Seguridad | autenticación y autorización, secretos, zonas sensibles | | | | | |
| Frontend | framework, enrutado, estado y caché, formularios, i18n, accesibilidad (componentes, estilos, iconos, animación, gráficos y fuentes: propuesta; se deciden en `/direccion-visual`) | | | | | |
| Calidad | tests por capa, lint, formato, tipos, auditoría de dependencias, **zonas críticas** y **herramienta de mutantes** para ellas | | | | | |
| Operación | build, CI (según el perfil), despliegue y ramas, entornos, logs, coste | | | | | |
| Escala | una fila por tema de `catalogo.md` que aplique (perfil compartido o producción) | | | | | |

## Supuestos de riesgo

Los 2-3 que, si fallan, obligan a cambiar una decisión de base. Los
comprueba F00 antes de escribir producto.

1. <supuesto> — cómo se comprueba — fila del mapa afectada

## Bloques cerrados

<Una línea por bloque al cerrarlo: fecha y qué se decidió. Tras cada uno se
puede hacer /clear: este fichero basta para seguir.>
~~~~~~~

### `plantillas/stack/conventions-web.md`

~~~~~~~ fichero=plantillas/stack/conventions-web.md
# Convenciones de interfaz web — material para copiar

<!-- Solo si el proyecto tiene interfaz web. Copia a
docs/<stack>/conventions.md lo que aplique; cada punto salió de una
iteración rechazada en un proyecto real. -->

- **La base visual vive en `docs/<stack>/direccion-visual.md`** (skill
  `/direccion-visual`, antes de la primera pantalla); cada spec la cita y
  define solo lo propio de sus pantallas. Una pantalla sin estilos no está
  terminada (un reset CSS puede dejar los campos de un formulario
  invisibles). No dejar el diseño para una feature final: una feature
  aprobada funcionalmente puede reabrirse si el humano rechaza el aspecto.
- **Modo de datos falsos**: un comando (`<RELLENAR: p. ej. pnpm dev:demo>`)
  arranca la interfaz sin backend ni datos reales, con dos juegos: normal y
  **peor caso** (nombres largos e irrompibles, lista vacía, un solo
  elemento, cifras enormes y negativas, texto en otro idioma). Con él hace
  sus capturas el `implementer_ui`. Lección: los fallos visuales los
  encontraba el humano con sus datos reales.
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
<Mutantes (zonas críticas, docs/verification.md): herramienta del stack y
el comando para unos ficheros concretos, p. ej. `npx stryker run --mutate
<ficheros>`, `cargo mutants --file <fichero>`; en Python, `mutmut run`
(3.x: ficheros en `[tool.mutmut] paths_to_mutate` de `pyproject.toml`) **no
funciona en Windows nativo** (comprobado 2026-10-11): ahí, `cosmic-ray`
(8.x: `cosmic-ray init cr.toml s.sqlite && cosmic-ray exec cr.toml s.sqlite
&& cr-report s.sqlite`), que muta el fichero en sitio mientras corre:
siempre en una copia del scope. Lo usan implementer y reviewer igual.
Su carpeta de trabajo (`mutants/`, `.stryker-tmp/`…) fuera de la recogida
de tests y del lint.>

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
# Con `init.sh --rapido` (HARNESS_RAPIDO=1) se para aqui: lo de abajo es lento
# o va a la red, y lo ejecutan el security_reviewer, el cierre y el CI.
if [ -n "${HARNESS_RAPIDO:-}" ]; then echo "STACK OK (rapido)"; exit 0; fi
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
fecha,feature,it,rol,tokens,cache_read,minutos,veredicto,causa,skills,modelo
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

### `scripts/agent_tokens.py`

~~~~~~~ fichero=scripts/agent_tokens.py
#!/usr/bin/env python3
"""Consumo real de un subagente, por ejecucion, leido de su transcript.

El `subagent_tokens` que devuelve la herramienta Agent es el tamano del
contexto al terminar, no lo gastado: en una reanudacion arrastra todo lo
anterior y no cuenta las relecturas de cache. Leccion: sumarlo daba un total
que no cuadraba con nada (piloto, 2026-10-03).

    bash scripts/py.sh scripts/agent_tokens.py <agent_id>
    bash scripts/py.sh scripts/agent_tokens.py <agent_id> --run 3
    bash scripts/py.sh scripts/agent_tokens.py --file <transcript.jsonl>

Una ejecucion termina en su llamada a SubagentHandback o cuando llega otro
mensaje al agente (el SendMessage que la reanuda): las versiones recientes
de Claude Code no escriben SubagentHandback en el transcript. Por cada ejecucion imprime `run,inicio,minutos,tokens,cache_read,skills`:
- tokens = input + cache_creation + output (lo nuevo de esa ejecucion);
- cache_read = relecturas de cache (la mayor parte del gasto real);
- skills = las invocadas con la herramienta Skill, separadas por `|`. Las
  precargadas (`skills:` del agente) no aparecen: no se invocan. Leccion:
  la linea "Skills usadas" que escribia cada agente mezclaba lo invocado con
  "criterio aplicado a mano" y no servia para medir.
Cada mensaje de la API se cuenta una vez (el transcript lo repite por bloque).
"""
import json
import sys
from datetime import datetime
from pathlib import Path


def _hora(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _usos_de_herramienta(entrada: dict, nombre: str) -> list[dict]:
    contenido = (entrada.get("message") or {}).get("content") or []
    if not isinstance(contenido, list):
        return []
    return [b for b in contenido if b.get("type") == "tool_use" and b.get("name") == nombre]


def _es_mensaje(entrada: dict) -> bool:
    """Texto que llega al agente (encargo, reanudacion), no un resultado de herramienta."""
    if entrada.get("type") == "assistant":
        return True  # sin mensaje previo visible, la ejecucion empieza al primer paso
    contenido = (entrada.get("message") or {}).get("content")
    if entrada.get("type") != "user" or contenido is None:
        return False
    return isinstance(contenido, str) or any(b.get("type") != "tool_result" for b in contenido)


def ejecuciones(lineas) -> list[dict]:
    """Agrupa el transcript en ejecuciones y suma su uso."""
    runs, usos, skills, inicio, fin, modelo = [], {}, {}, None, None, ""

    def cerrar():
        if usos:
            u = usos.values()
            runs.append({
                "inicio": inicio, "fin": fin,
                "tokens": sum(x.get("input_tokens", 0) + x.get("cache_creation_input_tokens", 0)
                              + x.get("output_tokens", 0) for x in u),
                "cache_read": sum(x.get("cache_read_input_tokens", 0) for x in u),
                "skills": list(skills.values()),
                # Lo pide el experimento de modelos: el leader puede cambiar el
                # de la definicion al lanzar, y solo el transcript lo sabe.
                "modelo": modelo,
            })

    for linea in lineas:
        try:
            e = json.loads(linea)
        except ValueError:
            continue
        ts = e.get("timestamp")
        m = e.get("message") or {}
        if e.get("type") == "user" and _es_mensaje(e) and usos:
            cerrar()  # mensaje nuevo tras trabajo ya hecho: otra ejecucion
            usos, skills, inicio, fin = {}, {}, None, None
        # Empieza en el encargo o el SendMessage, no en el resultado del
        # handback anterior: si no, los minutos cuentan la espera entre medias.
        if ts and not inicio and _es_mensaje(e):
            inicio = ts
        if ts and inicio:
            fin = ts
        if m.get("model"):
            modelo = m["model"]
        if m.get("usage"):
            usos[m.get("id") or len(usos)] = m["usage"]  # ultima entrada de cada mensaje
        for b in _usos_de_herramienta(e, "Skill"):
            skills[b.get("id") or len(skills)] = str((b.get("input") or {}).get("skill", "?"))
        if _usos_de_herramienta(e, "SubagentHandback"):
            cerrar()
            usos, skills, inicio, fin = {}, {}, None, None
    cerrar()  # ejecucion sin handback (cortada o en curso)
    return runs


def _transcript(agent_id: str) -> Path:
    raiz = Path.home() / ".claude" / "projects"
    hallados = sorted(raiz.glob(f"*/*/subagents/agent-{agent_id}*.jsonl"),
                      key=lambda p: p.stat().st_mtime)
    if not hallados:
        sys.exit(f"Sin transcript para agent-{agent_id} en {raiz}")
    return hallados[-1]


def main(argv: list[str]) -> int:
    run = int(argv[argv.index("--run") + 1]) if "--run" in argv else None
    ruta = Path(argv[argv.index("--file") + 1]) if "--file" in argv else _transcript(argv[0])
    print("run,inicio,minutos,tokens,cache_read,skills,modelo")
    for i, r in enumerate(ejecuciones(ruta.read_text(encoding="utf-8").splitlines()), 1):
        if run in (None, i):
            minutos = round((_hora(r["fin"]) - _hora(r["inicio"])).total_seconds() / 60)
            print(f"{i},{r['inicio'][:19]},{minutos},{r['tokens']},{r['cache_read']},"
                  f"{'|'.join(r['skills'])},{r['modelo']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
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

### `scripts/comparar.py`

~~~~~~~ fichero=scripts/comparar.py
#!/usr/bin/env python3
"""Compara dos progress/metrics.csv: ¿surtio efecto un cambio del harness?

    bash scripts/py.sh scripts/comparar.py BASE.csv [ACTUAL.csv]

ACTUAL es progress/metrics.csv si no se da. BASE suele ser la linea base de
otro proyecto o de antes del cambio (p. ej. la del piloto). Saca las cifras
que motivaron los cambios: primeras entregas aprobadas, rechazos por causa,
peso de las IT de correccion, pasadas del security_reviewer, coste por
feature y, con la columna `modelo`, el implementer por modelo.

Las columnas se leen por posicion: los ficheros antiguos (sin `skills` ni
`modelo`) valen igual. Con pocas features es un indicio, no una prueba.
"""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COLUMNAS = ("fecha", "feature", "it", "rol", "tokens", "cache_read", "minutos",
            "veredicto", "causa", "skills", "modelo")
IMPLEMENTERS = {"implementer", "implementer_ui"}


def leer(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8", newline="") as f:
        filas = list(csv.reader(f))
    datos = []
    for fila in filas[1:]:
        d = dict(zip(COLUMNAS, fila + [""] * (len(COLUMNAS) - len(fila))))
        if d["feature"] in {"-", "audit", ""} or not d["it"].isdigit():
            continue
        d["it"] = int(d["it"])
        for k in ("tokens", "cache_read", "minutos"):
            d[k] = int(d[k] or 0)
        datos.append(d)
    return datos


def _pct(a: float, b: float) -> str:
    return f"{100 * a / b:.0f} %" if b else "—"


def resumen(filas: list[dict]) -> dict[str, str]:
    # Ultimo veredicto de cada rol en cada IT (una reanudacion lo repite).
    veredictos = {(f["feature"], f["it"], f["rol"]): (f["veredicto"], f["causa"])
                  for f in filas if f["veredicto"]}
    rechazadas = {(fe, it) for (fe, it, _), (v, _) in veredictos.items()
                  if v == "CHANGES_REQUESTED"}
    revisadas = {(fe, it) for (fe, it, rol) in veredictos if rol == "reviewer"}
    # Primera entrega: IT revisada cuya anterior no fue rechazada (IT1 o un tramo nuevo).
    primeras = {k for k in revisadas if (k[0], k[1] - 1) not in rechazadas}
    correccion = {(f["feature"], f["it"]) for f in filas
                  if f["it"] >= 1 and (f["feature"], f["it"] - 1) in rechazadas}
    its = defaultdict(int)
    for f in filas:
        if f["rol"] in IMPLEMENTERS:
            its[f["feature"]] = max(its[f["feature"]], f["it"])
    n = len(its)
    causas = Counter(c or "sin causa" for (_, _, rol), (v, c) in veredictos.items()
                     if rol == "reviewer" and v == "CHANGES_REQUESTED")
    seguridad = [v for (_, _, rol), (v, _) in veredictos.items() if rol == "security_reviewer"]
    tokens = sum(f["tokens"] for f in filas)
    minutos = sum(f["minutos"] for f in filas)
    en_corr = [f for f in filas if (f["feature"], f["it"]) in correccion]
    r = {
        "Ejecuciones de agentes": str(len(filas)),
        "Features con implementación": str(n),
        "IT por feature (media)": f"{sum(its.values()) / n:.1f}" if n else "—",
        "Primeras entregas aprobadas por el reviewer":
            f"{len(primeras - rechazadas)}/{len(primeras)} ({_pct(len(primeras - rechazadas), len(primeras))})",
        "Rechazos del reviewer por causa":
            ", ".join(f"{c} {k}" for c, k in sorted(causas.items())) or "ninguno",
        "Pasadas del security_reviewer (rechazos)":
            f"{len(seguridad)} ({seguridad.count('CHANGES_REQUESTED')})",
        "Tokens nuevos por feature (media)": f"{tokens // n:,}".replace(",", ".") if n else "—",
        "Relecturas de caché por feature (media)":
            f"{sum(f['cache_read'] for f in filas) // n:,}".replace(",", ".") if n else "—",
        "Minutos por feature (media)": f"{minutos / n:.0f}" if n else "—",
        "Tokens en IT de corrección": _pct(sum(f["tokens"] for f in en_corr), tokens),
        "Minutos en IT de corrección": _pct(sum(f["minutos"] for f in en_corr), minutos),
    }
    # El implementer por modelo: primeras entregas que aprueba el reviewer.
    modelo_de = {(f["feature"], f["it"]): f["modelo"] or "sin dato"
                 for f in filas if f["rol"] in IMPLEMENTERS}
    for modelo in sorted(set(modelo_de.values())):
        suyas = {k for k in primeras if modelo_de.get(k) == modelo}
        ok = len(suyas - rechazadas)
        r[f"Implementer {modelo}: primeras aprobadas"] = f"{ok}/{len(suyas)} ({_pct(ok, len(suyas))})"
    return r


def tabla(base: dict[str, str], actual: dict[str, str]) -> str:
    lineas = ["| Métrica | Base | Actual |", "|---|---|---|"]
    for k in list(base) + [k for k in actual if k not in base]:
        lineas.append(f"| {k} | {base.get(k, '—')} | {actual.get(k, '—')} |")
    return "\n".join(lineas)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows no es UTF-8
    base = Path(argv[0])
    actual = Path(argv[1]) if len(argv) > 1 else RAIZ / "progress" / "metrics.csv"
    print(tabla(resumen(leer(base)), resumen(leer(actual))))
    print("\nCon pocas features, un indicio y no una prueba; mira también "
          "`Features con implementación`.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
~~~~~~~

### `scripts/foto.sh`

~~~~~~~ fichero=scripts/foto.sh
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
~~~~~~~

### `scripts/guard_config.py`

~~~~~~~ fichero=scripts/guard_config.py
#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit): pide confirmacion al humano antes de
cambiar la configuracion de lint, formato, tipos o del propio harness.

Un agente atascado en un check tiende a relajar la regla (un `ignore`, un
`strict: false`) en vez de arreglar el codigo, y el diff lo esconde entre
muchos cambios. Idea del hook config-protection de ECC; aqui no bloquea:
devuelve "ask", porque a veces el cambio es legitimo y lo aprueba el humano.

Crear un fichero nuevo no pregunta (el montaje los crea). Cambiar el texto
por la shell (sed, cat >) no pasa por aqui.
ATAJO: solo Edit/Write · si un agente lo esquiva por la shell, anadir esos
patrones a guard_secrets.py.

Si la entrada no se entiende, deja pasar: un fallo de este hook no debe
impedir editar codigo (el de secretos, en cambio, falla cerrado).
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_NOMBRES = re.compile(
    r"(\.?eslintrc(\.\w+)?|eslint\.config\.\w+|\.?prettierrc(\.\w+)?|prettier\.config\.\w+"
    r"|tsconfig(\.[\w-]+)?\.json|biome\.jsonc?|\.?ruff\.toml|\.?mypy\.ini|\.flake8|\.pylintrc"
    r"|pytest\.ini|setup\.cfg|\.golangci\.\w+|\.stylelintrc(\.\w+)?|\.gitleaks\.toml"
    r"|vitest\.config\.\w+|jest\.config\.\w+)", re.I)
# En pyproject.toml solo preocupa la configuracion de herramientas, no las
# dependencias ni la version.
_PYPROJECT = re.compile(r"\[tool\.|^\s*(ignore|extend-ignore|select|per-file-ignores|strict"
                        r"|disable_error_code|ignore_missing_imports|addopts|filterwarnings)\s*=",
                        re.M)


def _del_harness(ruta: Path) -> bool:
    try:
        rel = ruta.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return False
    return (rel.startswith((".githooks/", ".github/workflows/"))
            or rel in {".claude/settings.json", "init.sh"})


def motivo(entrada: dict) -> str | None:
    datos = entrada.get("tool_input") or {}
    ruta = Path(datos.get("file_path") or "")
    if not ruta.name or not ruta.is_file():
        return None
    if _del_harness(ruta):
        return "es configuracion del harness (la decide el humano)"
    if _NOMBRES.fullmatch(ruta.name):
        return "es configuracion de lint, formato, tipos o tests"
    if ruta.name == "pyproject.toml":
        texto = " ".join(str(datos.get(k, "")) for k in ("old_string", "new_string", "content"))
        texto += " ".join(str(e.get(k, "")) for e in datos.get("edits") or []
                          for k in ("old_string", "new_string"))
        if _PYPROJECT.search(texto):
            return "toca la configuracion de herramientas de pyproject.toml"
    return None


def main() -> int:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace").lstrip("﻿"))
    except ValueError:
        return 0
    razon = motivo(entrada) if isinstance(entrada, dict) else None
    if razon:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"scripts/guard_config.py: el fichero {razon}. Si un check falla, "
                "arregla el codigo; relajar la regla lo aprueba el humano."),
        }}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
~~~~~~~

### `scripts/guard_secrets.py`

~~~~~~~ fichero=scripts/guard_secrets.py
#!/usr/bin/env python3
"""PreToolUse (Bash|PowerShell): bloquea comandos que pueden sacar un secreto
o saltarse el pre-commit.

Los permisos `deny` de settings.json cubren Read/Grep/Edit, pero para la
shell solo comparan prefijos de texto: `type backend\\.env`, `Get-Content`
o `$env:MI_TOKEN` los esquivan. Este hook mira el comando entero.

Los nombres de los secretos salen de `harness.json` ("secretos"), para que
no haya una segunda lista que se desincronice.

El pre-commit es la ultima puerta antes de que un secreto exista en un
commit: `--no-verify`, `commit -n` o un `core.hooksPath` distinto de
`.githooks` lo apagan sin dejar rastro (idea del hook block-no-verify de ECC).

Y lo que no tiene vuelta atras (idea de safety-guard de ECC): reescribir la
historia (CLAUDE.md, Reglas duras) y matar procesos por nombre. Leccion del
piloto: un `taskkill /IM node.exe` mato todos los node de la maquina.

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


# El cuerpo de un heredoc es texto (codigo que se escribe o se pasa a un
# interprete), no comandos. Leccion: `print(fn(env))` o `; env |` dentro de
# un `python - <<EOF` se leian como volcado del entorno.
_HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1([^\n]*)\n.*?^\s*\2\s*$", re.M | re.S)

_VOLCADOS = [
    # Una linea nueva tambien separa comandos: `cd x\nenv` vuelca.
    re.compile(r"(^|[;&|(\n]\s*)(printenv|env|set|export\s+-p)\s*($|[;&|)\n])"),
    re.compile(r"\b(Get-ChildItem|gci|dir|ls|Get-Item|gi)\s+env:", re.I),
    re.compile(r"\[Environment\]::GetEnvironmentVariables", re.I),
]


def _reglas() -> list[tuple[re.Pattern[str], str]]:
    reglas = []
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
    # Con la marca sin comillas, bash expande $X dentro del heredoc: las
    # reglas de secretos siguen mirando el comando entero.
    sin_heredocs = _HEREDOC.sub(r"\3", comando)
    if any(p.search(sin_heredocs) for p in _VOLCADOS):
        return "vuelca todas las variables de entorno"
    for patron, texto in _reglas():
        if patron.search(comando):
            return texto
    return None


def _tramos(comando: str) -> list[list[str]] | None:
    """Por tokens, no por texto: un mensaje de commit que cite un comando pasa.

    None si hay comillas sin cerrar; quien llama mira el texto entero.
    """
    try:
        # La linea nueva separa comandos, salvo dentro de comillas.
        lexer = shlex.shlex(_HEREDOC.sub(r"\3", comando), posix=True,
                            punctuation_chars="();<>|&\n")
        lexer.whitespace = " \t\r"
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return None
    tramos, tramo = [], []
    for t in tokens + [";"]:
        if t and set(t) <= set(";&|()\n"):
            if tramo:
                tramos.append(tramo)
            tramo = []
        else:
            tramo.append(t)
    return tramos


def salta_el_pre_commit(comando: str) -> bool:
    tramos = _tramos(comando)
    if tramos is None:
        # Comillas sin cerrar: se mira el texto entero, aunque sobre-bloquee.
        return bool(re.search(r"--no-verify|core\.hookspath", comando, re.I))
    return any(_tramo_salta(t) for t in tramos)


def _es_git(tramo: list[str]) -> bool:
    return "git" in (Path(t).stem.lower() for t in tramo[:3])


def destructivo(comando: str) -> str | None:
    tramos = _tramos(comando)
    if tramos is None:
        tramos = [comando.split()]
    previo: list[str] = []
    for tramo in tramos:
        bajos = [t.lower() for t in tramo]
        orden = Path(bajos[0]).stem
        if (orden in ("pkill", "killall")
                or (orden == "taskkill" and "/im" in bajos)
                or (orden in ("stop-process", "spps") and "-name" in bajos)
                # `Get-Process node | Stop-Process`
                or (orden in ("stop-process", "spps", "kill") and previo
                    and Path(previo[0]).stem in ("get-process", "gps", "ps")
                    and "-id" not in previo)):
            return ("mata procesos por nombre (todos los de la maquina, no solo "
                    "los tuyos). Paralo por el PID que arrancaste")
        if _es_git(tramo) and (
                "--amend" in bajos
                or ("push" in bajos and any(t == "-f" or t.startswith("--force") for t in bajos))
                or any(t in ("rebase", "filter-branch", "filter-repo") for t in bajos)):
            return ("reescribe la historia de git (--amend, push --force, rebase, "
                    "filter-branch): el historial es la evidencia de cada iteracion")
        if _es_git(tramo) and _descarta_cambios(tramo):
            return ("descarta cambios sin commitear: el trabajo de todas las IT vive "
                    "sin commitear hasta que el humano commitea. Restaura desde tu copia")
        previo = bajos
    return None


def _descarta_cambios(tramo: list[str]) -> bool:
    """reset --hard, checkout/restore de ficheros, clean -f, stash drop/clear.

    Leccion del piloto: un agente comprobo un rojo "restaurando bridge.py de
    HEAD", que borra todo lo que las IT anteriores cambiaron en ese fichero.
    """
    t = tramo
    if "reset" in t and "--hard" in t:
        return True
    if "checkout" in t and ("--" in t or "." in t or "-f" in t or "--force" in t):
        return True
    if "restore" in t and ("--worktree" in t or "-W" in t
                           or not ("--staged" in t or "-S" in t)):
        return True
    if "clean" in t and any(re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*|--force", x) for x in t):
        return True
    return "stash" in t and ("drop" in t or "clear" in t)


def _tramo_salta(tramo: list[str]) -> bool:
    if not _es_git(tramo):
        return False
    bajos = [t.lower() for t in tramo]
    if "--no-verify" in bajos or ("commit" in bajos and "-n" in bajos):
        return True
    if "core.hookspath" in bajos and ("--unset" in bajos or "--unset-all" in bajos):
        return True
    for i, t in enumerate(bajos):
        valor = None
        if t.startswith("core.hookspath="):
            valor = t.split("=", 1)[1]
        elif t == "core.hookspath" and i + 1 < len(bajos):
            valor = bajos[i + 1]
        if valor is not None and valor.strip("/\\") != ".githooks":
            return True
    return False


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
    if salta_el_pre_commit(comando):
        print("Bloqueado por scripts/guard_secrets.py: el comando se salta el "
              "pre-commit (--no-verify, commit -n o core.hooksPath distinto de "
              ".githooks). Si un hook falla, arregla la causa; si sobra, lo "
              "decide el humano.", file=sys.stderr)
        return 2
    peligro = destructivo(comando)
    if peligro:
        print(f"Bloqueado por scripts/guard_secrets.py: el comando {peligro}. "
              "Si de verdad hace falta, lo ejecuta el humano.", file=sys.stderr)
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
# Los reescribe el proyecto tras cada agente: el documento guarda su semilla,
# no lo vivo. Leccion del piloto: un commit salio con HARNESS.md desfasado
# por una linea nueva de metrics.csv. Para cambiar una semilla, se edita aqui
# su bloque.
VOLATILES = ("progress/current.md", "progress/history.md",
             "progress/metrics.csv", "progress/para_la_plantilla.md")


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
    semillas = dict(BLOQUE.findall(GUIA.read_text(encoding="utf-8"))) if GUIA.is_file() else {}
    trozos = [INICIO, ""]
    for p in ficheros():
        ruta = p.relative_to(RAIZ).as_posix()
        if ruta in VOLATILES and ruta in semillas:
            contenido = semillas[ruta]
        else:
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

### `scripts/metricas.py`

~~~~~~~ fichero=scripts/metricas.py
#!/usr/bin/env python3
"""SubagentStop: anade a progress/metrics.csv la linea de la ejecucion que
acaba de terminar.

Antes la escribia el leader a mano tras cada agente: una llamada a
agent_tokens.py y una edicion por ejecucion, en el contexto mas caro de
todos (la sesion principal releia cada paso). Claude Code lanza este hook en
cada ejecucion de un subagente, tambien al reanudarlo con SendMessage, con
`agent_type` y `agent_transcript_path` (comprobado el 2026-10-10).

- feature e IT: las que despacha state.py (IT 0 para spec_author y
  explorer); con una auditoria pendiente, feature `audit`.
- veredicto y causa: las lineas `Veredicto:` y `Causa:` de review.md o
  security.md de esa IT.

Nunca falla hacia fuera: un SubagentStop con codigo 2 impediria que el
subagente terminara. Los errores van a stderr y el hook sale con 0.
"""
import csv
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import agent_tokens  # noqa: E402
import state  # noqa: E402

_CAUSA = re.compile(r"^\W*Causa\W*(codigo|tests|spec|otro)\b", re.M | re.I)
_REVISORES = {"reviewer": "review.md", "security_reviewer": "security.md"}


def _roles() -> set[str]:
    return {p.stem for p in (RAIZ / ".claude" / "agents").glob("*.md")} - {"leader"}


def _ultima_it_escrita() -> tuple[str, int] | None:
    its = [d for d in (RAIZ / "progress").glob("*/IT*")
           if d.is_dir() and re.fullmatch(r"IT\d+", d.name)]
    if not its:
        return None
    reciente = max(its, key=lambda d: max([f.stat().st_mtime for f in d.iterdir()]
                                          + [d.stat().st_mtime]))
    return reciente.parent.name, int(reciente.name[2:])


def fila(entrada: dict) -> list[str] | None:
    rol = entrada.get("agent_type") or ""
    transcript = Path(entrada.get("agent_transcript_path") or "")
    if rol not in _roles() or not transcript.is_file():
        return None
    runs = agent_tokens.ejecuciones(transcript.read_text(encoding="utf-8").splitlines())
    if not runs:
        return None
    r = runs[-1]
    estado = state.next_action()
    feature = estado.get("feature", "-")
    if estado.get("audits_pending") and rol == "security_reviewer":
        feature, it = "audit", estado["audits_pending"][-1]
    elif rol in {"spec_author", "explorer"}:
        it = 0
    else:
        # La IT que el agente acaba de escribir, no la que despacha state.py:
        # el cierre marca `done` y state.py ya apunta a la feature siguiente.
        feature, it = _ultima_it_escrita() or (feature, 0)
    veredicto = causa = ""
    if rol in _REVISORES and feature not in {"-", "audit"}:
        ruta = RAIZ / "progress" / feature / f"IT{it}" / _REVISORES[rol]
        texto = ruta.read_text(encoding="utf-8", errors="replace") if ruta.is_file() else ""
        m = state._VEREDICTO.search(texto)
        veredicto = m.group(1).upper() if m else ""
        c = _CAUSA.search(texto) if veredicto == "CHANGES_REQUESTED" else None
        causa = c.group(1).lower() if c else ""
    minutos = round((agent_tokens._hora(r["fin"]) - agent_tokens._hora(r["inicio"])).total_seconds() / 60)
    return [r["inicio"][:10], feature, str(it), rol, str(r["tokens"]), str(r["cache_read"]),
            str(minutos), veredicto, causa, "|".join(r["skills"]), r["modelo"]]


def main() -> int:
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace").lstrip("﻿"))
        linea = fila(entrada)
        if linea:
            with (RAIZ / "progress" / "metrics.csv").open("a", encoding="utf-8", newline="") as f:
                csv.writer(f, lineterminator="\n").writerow(linea)
    except Exception as e:  # noqa: BLE001 - un fallo aqui no debe bloquear al subagente
        print(f"metricas.py: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
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

# Solo si hay algo: una skill sin clasificar o una precargada que falta.
SKILLS="$($PY scripts/skills.py 2>/dev/null || true)"
if [ -n "$SKILLS" ]; then
  echo
  echo "=== skills.py ==="
  echo "$SKILLS"
fi

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

### `scripts/skills.py`

~~~~~~~ fichero=scripts/skills.py
#!/usr/bin/env python3
"""Skills instaladas que el harness aun no ha clasificado, y las que le faltan.

Una skill nueva no se usa sola: nadie la precarga y ningun agente sabe que
existe. Una precargada que falta tampoco avisa: Claude Code se la salta sin
error. Leccion: en el piloto ningun subagente invoco una skill bajo demanda
en 110 ejecuciones; solo la precarga (`skills:` del agente) es fiable.

    bash scripts/py.sh scripts/skills.py          # texto, vacio si no hay nada
    bash scripts/py.sh scripts/skills.py --json

Clasificada = la precarga algun agente, tiene estado en `skillOverrides` de
`.claude/settings.json` (o `settings.local.json`), o esta en
`skills_revisadas` de `harness.json`: las de plugin, a las que
`skillOverrides` no llega, tanto si las usa una skill del harness como si
se descartaron. Las de `.claude/skills/` del proyecto son del harness y no
cuentan.
"""
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _config() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def _json(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _nombre(skill_md: Path) -> str:
    try:
        cabecera = skill_md.read_text(encoding="utf-8").split("---")[1]
    except (OSError, IndexError, UnicodeDecodeError):
        return skill_md.parent.name
    m = re.search(r"^name:\s*(\S+)", cabecera, re.M)
    return m.group(1).strip("'\"") if m else skill_md.parent.name


def _de_plugin(raiz: Path, plugin: str) -> set[str]:
    return {f"{plugin}:{_nombre(p)}" for p in raiz.glob("skills/*/SKILL.md")}


def instaladas() -> set[str]:
    """Skills de usuario, plugins del directorio de skills y plugins activos."""
    config, nombres = _config(), set()
    for d in sorted((config / "skills").glob("*")):
        manifiesto = d / ".claude-plugin" / "plugin.json"
        if manifiesto.is_file():
            nombres |= _de_plugin(d, _json(manifiesto).get("name") or d.name)
        elif (d / "SKILL.md").is_file():
            nombres.add(_nombre(d / "SKILL.md"))
    activos = dict(_json(config / "settings.json").get("enabledPlugins") or {})
    for f in ("settings.json", "settings.local.json"):
        activos.update(_json(RAIZ / ".claude" / f).get("enabledPlugins") or {})
    instalados = _json(config / "plugins" / "installed_plugins.json").get("plugins") or {}
    for clave, entradas in instalados.items():
        if activos.get(clave) and entradas:
            ruta = Path(entradas[0].get("installPath", ""))
            nombres |= _de_plugin(ruta, clave.split("@")[0])
    return nombres


def precargadas() -> dict[str, set[str]]:
    """skill -> agentes que la precargan (lista `skills:` del frontmatter)."""
    usos: dict[str, set[str]] = {}
    for agente in (RAIZ / ".claude" / "agents").glob("*.md"):
        partes = agente.read_text(encoding="utf-8").split("---")
        bloque = re.search(r"^skills:\s*\n((?:[ \t]+-.*\n?)+)", partes[1] if len(partes) > 2 else "", re.M)
        for linea in (bloque.group(1).splitlines() if bloque else []):
            usos.setdefault(linea.strip().lstrip("-").strip().strip("'\""), set()).add(agente.stem)
    return usos


def clasificadas() -> set[str]:
    nombres = set(precargadas())
    for f in ("settings.json", "settings.local.json"):
        nombres |= set(_json(RAIZ / ".claude" / f).get("skillOverrides") or {})
    nombres |= set(_json(RAIZ / "harness.json").get("skills_revisadas") or [])
    nombres |= {_nombre(p) for p in (RAIZ / ".claude" / "skills").glob("*/SKILL.md")}
    return nombres


def informe() -> dict[str, list[str]]:
    hay = instaladas()
    return {
        "nuevas": sorted(hay - clasificadas()),
        "ausentes": sorted(f"{s} ({', '.join(sorted(a))})"
                           for s, a in precargadas().items() if s not in hay),
    }


def main(argv: list[str]) -> int:
    datos = informe()
    if "--json" in argv:
        print(json.dumps(datos, ensure_ascii=False))
        return 0
    if datos["nuevas"]:
        print("Skills nuevas sin clasificar (propon al humano un rol o descartarlas): "
              + ", ".join(datos["nuevas"]))
    if datos["ausentes"]:
        print("Skills precargadas que no estan instaladas (Claude Code las ignora): "
              + ", ".join(datos["ausentes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
~~~~~~~

### `scripts/state.py`

~~~~~~~ fichero=scripts/state.py
#!/usr/bin/env python3
"""Estado de despacho del harness. Lo invoca el leader en cada arranque.

Devuelve en una linea de JSON que feature toca y que accion. Deriva todo del
disco (feature_list.json, specs/<F>/tasks.md y progress/<F>/IT<n>/): no hay
ningun estado aparte que mantener sincronizado.

Los marcadores que lee son fijos (HARNESS.md, "Marcadores"): la linea
`Veredicto: APPROVED|CHANGES_REQUESTED`, el encabezado `## Sabotajes`,
`SERVICIOS REALES` en la cabecera de la task humana, `Estado: APROBADO` en
`progress/arranque.md` y `Aprobada por el humano: AAAA-MM-DD` en el
`design.md` de una spec.
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
_ARRANQUE_APROBADO = re.compile(r"^\W*Estado\W*APROBADO\b", re.M | re.I)
_SPEC_APROBADA = re.compile(r"^\W*Aprobada por el humano\W*\d{4}-\d{2}-\d{2}", re.M | re.I)


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


# La aprobacion es la marca del humano en design.md, no el campo status.
# Leccion: nadie tenia la orden de pasar la feature a in_progress y el
# despacho se quedaba pidiendo aprobacion para siempre.
def _spec_aprobada(feature_id: str) -> bool:
    ruta = ROOT / "specs" / feature_id / "design.md"
    return ruta.is_file() and bool(_SPEC_APROBADA.search(_leer(ruta)))


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
    # Del arranque salen los documentos que guian todo lo demas: sin el
    # aprobado no se escribe ninguna spec. Leccion: el stack decidido a
    # medias obligo a cambiar de framework a mitad de la primera feature.
    arranque = ROOT / "progress" / "arranque.md"
    if not (arranque.is_file() and _ARRANQUE_APROBADO.search(_leer(arranque))):
        return {"action": "ARRANQUE"}

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
    elif estado == "spec_ready" and not _spec_aprobada(fid):
        return {**base, "iteration": 0, "action": "PEDIR_APROBACION_HUMANA"}

    it = _ultima_iteracion(fid)
    if it == 0:
        return {**base, "iteration": 1, "action": "CREAR_IT1_Y_LANZAR_IMPLEMENTER"}

    base = {**base, "iteration": it}
    carpeta = ROOT / "progress" / fid / f"IT{it}"

    # Una IT descartada (el humano cambia de stack o de rumbo con ella sin
    # revisar) cuenta como rechazada: la siguiente parte de ahi. Leccion: el
    # despacho pedia revisar una IT de un framework ya abandonado.
    if (carpeta / "descartada.md").is_file():
        review = security = "CHANGES_REQUESTED"
    else:
        # Leccion: una IT sin impl.md se despachaba como "revisar". Sin
        # impl.md el implementer se paro a medias: se reanuda el mismo agente.
        if not (carpeta / "impl.md").is_file():
            return {**base, "action": "REANUDAR_IMPLEMENTER"}
        if not _tiene_sabotajes(fid, it):
            return {**base, "action": "DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES"}
        review = _veredicto(fid, it, "review.md")
        security = _veredicto(fid, it, "security.md")

    # Primero el veto funcional, siempre. Cualquier rechazo (tambien de
    # seguridad) abre otra IT que vuelve a pasar por el reviewer: un arreglo
    # puede romper lo que estaba aprobado.
    if review is None:
        return {**base, "action": "LANZAR_REVIEWER"}
    if "CHANGES_REQUESTED" in (review, security):
        return {**base, "action": f"CREAR_IT{it + 1}_LANZAR_IMPLEMENTER_LUEGO_REVIEWER"}
    if _tasks_pendientes(fid):
        return {**base, "action": f"CREAR_IT{it + 1}_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO"}

    # Ultimo tramo (o modo ligero): el security_reviewer, solo sobre una IT que
    # el reviewer ya aprobo, y una vez por feature salvo que rechace.
    # Lecciones del piloto: en cada tramo paso 47 veces y rechazo 2; y en
    # paralelo con el reviewer revisaba IT que este iba a rechazar (el 51 %,
    # ~61 k tokens por pasada) para ahorrar unos 3 minutos.
    if security is None:
        return {**base, "action": "LANZAR_SECURITY_REVIEWER"}
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
<(Tras la respuesta, esta sección pasa a "Decisiones del humano (fecha)",
con las respuestas tal cual y, en línea propia, `Aprobada por el humano:
AAAA-MM-DD`: es la marca que lee `state.py`.)>

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

## Tramo B — <siguiente> (interfaz)
- [ ] **T3 — <título>**. <…> → R4

<!-- "(interfaz)" en la cabecera de un tramo que crea o cambia pantallas: lo
hace el implementer_ui (capturas incluidas). Quítalo si el tramo no las toca. -->

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

### `tests/test_agent_tokens.py`

~~~~~~~ fichero=tests/test_agent_tokens.py
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import agent_tokens  # noqa: E402


def _l(**e):
    return json.dumps(e)


def _uso(msg_id, ts, entrada, cache, bloques=()):
    return _l(type="assistant", timestamp=ts, message={
        "id": msg_id, "content": list(bloques),
        "usage": {"input_tokens": entrada, "output_tokens": 1, "cache_read_input_tokens": cache}})


def test_separa_ejecuciones_y_cuenta_cada_mensaje_una_vez():
    lineas = [
        _l(type="user", timestamp="2026-10-10T10:00:00Z", message={"content": "encargo"}),
        _uso("a", "2026-10-10T10:01:00Z", 10, 100),
        # El transcript repite el mensaje por bloque: se cuenta una vez.
        _uso("a", "2026-10-10T10:01:00Z", 10, 100,
             [{"type": "tool_use", "id": "t1", "name": "Skill", "input": {"skill": "migration"}}]),
        _uso("b", "2026-10-10T10:05:00Z", 5, 50,
             [{"type": "tool_use", "id": "t2", "name": "SubagentHandback", "input": {}}]),
        _l(type="user", timestamp="2026-10-10T11:00:00Z", message={"content": "reanuda"}),
        _uso("c", "2026-10-10T11:02:00Z", 7, 70),
    ]
    r1, r2 = agent_tokens.ejecuciones(lineas)
    assert (r1["tokens"], r1["cache_read"], r1["skills"]) == (17, 150, ["migration"])
    assert (r2["tokens"], r2["cache_read"], r2["skills"]) == (8, 70, [])
    assert r2["inicio"] == "2026-10-10T11:00:00Z"


def test_sin_handback_un_mensaje_nuevo_abre_otra_ejecucion():
    # Leccion (2026-10-10): las versiones recientes no escriben
    # SubagentHandback; una reanudacion se sumaba a la ejecucion anterior.
    lineas = [
        _l(type="user", timestamp="2026-10-10T10:00:00Z", message={"content": "encargo"}),
        _uso("a", "2026-10-10T10:01:00Z", 10, 100),
        _l(type="user", timestamp="2026-10-10T10:01:30Z",
           message={"content": [{"type": "tool_result", "content": "ok"}]}),
        _uso("b", "2026-10-10T10:02:00Z", 5, 50),
        _l(type="user", timestamp="2026-10-10T10:30:00Z", message={"content": "reanuda"}),
        _uso("c", "2026-10-10T10:31:00Z", 7, 70),
    ]
    r1, r2 = agent_tokens.ejecuciones(lineas)
    assert (r1["tokens"], r1["cache_read"]) == (17, 150)
    assert (r2["tokens"], r2["inicio"]) == (8, "2026-10-10T10:30:00Z")
~~~~~~~

### `tests/test_comparar.py`

~~~~~~~ fichero=tests/test_comparar.py
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import comparar  # noqa: E402

# F01: IT1 rechazada por tests, IT2 (correccion) aprobada, IT3 tramo nuevo
# aprobado a la primera. Formato antiguo (9 columnas) mezclado con el nuevo.
CSV = """fecha,feature,it,rol,tokens,cache_read,minutos,veredicto,causa
d,F01,1,implementer,100,0,10,,,,claude-sonnet
d,F01,1,reviewer,50,0,5,CHANGES_REQUESTED,tests
d,F01,2,implementer,30,0,3,,,,claude-opus
d,F01,2,reviewer,10,0,1,APPROVED,
d,F01,3,implementer,60,0,6,,,,claude-opus
d,F01,3,reviewer,20,0,2,APPROVED,
d,F01,3,security_reviewer,30,0,3,APPROVED,
d,-,0,explorer,999,0,9,,
"""


def _resumen(tmp_path):
    ruta = tmp_path / "m.csv"
    ruta.write_text(CSV, encoding="utf-8")
    return comparar.resumen(comparar.leer(ruta))


def test_primeras_entregas_y_peso_de_la_correccion(tmp_path):
    r = _resumen(tmp_path)
    # Primeras entregas: IT1 (rechazada) e IT3 (aprobada); IT2 es correccion.
    assert r["Primeras entregas aprobadas por el reviewer"] == "1/2 (50 %)"
    assert r["Rechazos del reviewer por causa"] == "tests 1"
    assert r["Tokens en IT de corrección"] == "13 %"  # 40 de 300
    assert r["IT por feature (media)"] == "3.0"
    assert r["Ejecuciones de agentes"] == "7"  # el explorer sin feature no cuenta


def test_implementer_por_modelo(tmp_path):
    r = _resumen(tmp_path)
    assert r["Implementer claude-sonnet: primeras aprobadas"] == "0/1 (0 %)"
    assert r["Implementer claude-opus: primeras aprobadas"] == "1/1 (100 %)"
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
    ci = RAIZ / ".github/workflows/ci.yml"  # opcional: /arranque lo borra si el perfil no lo lleva
    if ci.is_file():
        assert "scripts/check_docs_changelog.sh" in ci.read_text(encoding="utf-8")


def test_el_pre_commit_avisa_sin_bloquear_por_el_changelog():
    # Es costumbre del harness, no regla dura: el humano no queda atado a ella.
    hook = (RAIZ / ".githooks/pre-commit").read_text(encoding="utf-8")
    assert "check_docs_changelog.sh ||" in hook
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

### `tests/test_foto.py`

~~~~~~~ fichero=tests/test_foto.py
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="sin bash")


def _git(cwd, *args):
    return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
                          cwd=cwd, check=True, capture_output=True, text=True).stdout


def _foto(cwd):
    return subprocess.run([BASH, str(RAIZ / "scripts/foto.sh")], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def test_la_foto_ve_lo_nuevo_sin_tocar_el_indice(tmp_path):
    # Leccion: sin commits por IT, el reviewer no tenia contra que comparar.
    _git(tmp_path, "init", "-q")
    (tmp_path / "a.txt").write_text("a\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("secreto\n", encoding="utf-8")
    base = _foto(tmp_path)  # funciona tambien sin ningun commit
    (tmp_path / "a.txt").write_text("a\nb\n", encoding="utf-8")
    (tmp_path / "nuevo.txt").write_text("n\n", encoding="utf-8")
    (tmp_path / "secreto").write_text("s\n", encoding="utf-8")
    cambios = _git(tmp_path, "diff", "--name-only", base, _foto(tmp_path)).split()
    assert cambios == ["a.txt", "nuevo.txt"]
    assert _git(tmp_path, "diff", "--cached", "--name-only") == ""
~~~~~~~

### `tests/test_guard_config.py`

~~~~~~~ fichero=tests/test_guard_config.py
import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import guard_config  # noqa: E402


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(guard_config, "RAIZ", tmp_path)
    for f in ("eslint.config.js", "web/tsconfig.app.json", "ruff.toml", "pyproject.toml",
              ".claude/settings.json", ".githooks/pre-commit", "src/app.py", "web/vite.config.ts"):
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f).write_text("x", encoding="utf-8")
    return tmp_path


def _entrada(ruta, **datos):
    return {"tool_name": "Edit", "tool_input": {"file_path": str(ruta), **datos}}


@pytest.mark.parametrize("fichero", ["eslint.config.js", "web/tsconfig.app.json", "ruff.toml",
                                     ".claude/settings.json", ".githooks/pre-commit"])
def test_pregunta_antes_de_tocar_configuracion(repo, fichero):
    assert guard_config.motivo(_entrada(repo / fichero)) is not None


@pytest.mark.parametrize("fichero", ["src/app.py", "web/vite.config.ts"])
def test_el_codigo_no_pregunta(repo, fichero):
    assert guard_config.motivo(_entrada(repo / fichero)) is None


def test_crear_un_fichero_nuevo_no_pregunta(repo):
    assert guard_config.motivo(_entrada(repo / "web" / "eslint.config.mjs")) is None


def test_pyproject_solo_pregunta_si_toca_herramientas(repo):
    py = repo / "pyproject.toml"
    assert guard_config.motivo(_entrada(py, old_string="version = \"1\"", new_string="version = \"2\"")) is None
    assert guard_config.motivo(_entrada(py, old_string="strict = true", new_string="strict = false"))
    assert guard_config.motivo(_entrada(py, edits=[{"old_string": "x", "new_string": "[tool.ruff]"}]))


def _hook(entrada: str):
    return subprocess.run([sys.executable, str(RAIZ / "scripts/guard_config.py")],
                          input=entrada.encode("utf-8"), capture_output=True, text=False)


def test_el_hook_devuelve_ask():
    r = _hook(json.dumps(_entrada(RAIZ / ".claude/settings.json")))
    salida = json.loads(r.stdout.decode("utf-8"))
    assert r.returncode == 0
    assert salida["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_el_hook_deja_pasar_si_la_entrada_es_ilegible():
    r = _hook("no es json")
    assert r.returncode == 0 and r.stdout == b""
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
    "cd app\nenv",
    "cat <<EOF; env\nx\nEOF",
    # Sin comillas en la marca, bash expande el secreto dentro del heredoc.
    "cat <<EOF\n$MI_TOKEN\nEOF",
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
    # Leccion del piloto: codigo dentro de un heredoc se leia como volcado.
    "python - <<'EOF'\nprint(fn(env))\nEOF",
    "cat >> t.py <<EOF\n    x = 1; env | 2\nset\nEOF",
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


SALTAN_EL_PRE_COMMIT = [
    "git commit --no-verify -m x",
    "git commit -n -m x",
    "git push --no-verify",
    "git -c core.hooksPath=/dev/null commit -m x",
    "git config core.hooksPath .git/hooks",
    "git config --unset core.hooksPath",
    "cd app && git commit --no-verify -m x",
    "git.exe commit --no-verify -m x",
]

RESPETAN_EL_PRE_COMMIT = [
    "git commit -m x",
    # Leccion: mirar el texto entero bloqueaba un mensaje que lo mencionaba.
    'git commit -m "docs: bloquear --no-verify"',
    "git config core.hooksPath .githooks",
    "git push -n",
    "git log -n 5",
    "echo --no-verify",
]


@pytest.mark.parametrize("comando", SALTAN_EL_PRE_COMMIT)
def test_bloquea_saltarse_el_pre_commit(comando):
    assert guard_secrets.salta_el_pre_commit(comando)


@pytest.mark.parametrize("comando", RESPETAN_EL_PRE_COMMIT)
def test_permite_git_normal(comando):
    assert not guard_secrets.salta_el_pre_commit(comando)


DESTRUCTIVOS = [
    # Leccion del piloto: mato todos los node de la maquina.
    "taskkill /F /IM node.exe",
    "cd app\ntaskkill /IM python.exe /F",
    "pkill node",
    "killall python3",
    "Stop-Process -Name node -Force",
    "Get-Process node | Stop-Process",
    "git commit --amend --no-edit",
    "git push --force origin main",
    "git push -f",
    "git push --force-with-lease",
    "git rebase main",
    "git filter-branch --tree-filter x",
    # Leccion del piloto: "restaurar de HEAD" borra el trabajo sin commitear.
    "git checkout HEAD -- app/bridge.py",
    "git checkout -- .",
    "git checkout .",
    "git restore app/bridge.py",
    "git restore --staged --worktree x",
    "git reset --hard",
    "git clean -fd",
    "git stash drop",
]

NO_DESTRUCTIVOS = [
    "taskkill /PID 4242 /F",
    "Stop-Process -Id 4242",
    "Get-Process -Id 4242 | Stop-Process",
    "kill 4242",
    "git push origin main",
    'git commit -m "docs: no usar taskkill /IM ni --amend"',
    "cat > notas.sh <<'EOF'\ngit rebase main\nEOF",
    "git checkout -b prueba",
    "git restore --staged x",
    "git reset HEAD x",
    "git clean -n",
    "git stash",
    "git diff HEAD -- app/bridge.py",
]


@pytest.mark.parametrize("comando", DESTRUCTIVOS)
def test_bloquea_lo_destructivo(comando):
    assert guard_secrets.destructivo(comando)


@pytest.mark.parametrize("comando", NO_DESTRUCTIVOS)
def test_permite_lo_acotado(comando):
    assert guard_secrets.destructivo(comando) is None


def test_hook_bloquea_no_verify_con_codigo_2():
    r = _hook(json.dumps({"tool_input": {"command": "git commit --no-verify -m x"}}))
    assert r.returncode == 2 and b"pre-commit" in r.stderr
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
        if ruta in harness_bundle.VOLATILES:
            continue
        original = harness_bundle._normal((RAIZ / ruta).read_text(encoding="utf-8"))
        assert (tmp_path / ruta).read_text(encoding="utf-8") == original, ruta


def test_un_cambio_sin_regenerar_se_detecta(tmp_path, monkeypatch):
    copia = tmp_path / "HARNESS.md"
    copia.write_text((RAIZ / "HARNESS.md").read_text(encoding="utf-8")
                     .replace("fichero=CLAUDE.md\n", "fichero=CLAUDE.md\nlinea vieja\n", 1),
                     encoding="utf-8")
    monkeypatch.setattr(harness_bundle, "GUIA", copia)
    assert harness_bundle.main(["--check"]) == 1


def test_lo_vivo_de_progress_no_desfasa_el_documento(tmp_path, monkeypatch):
    # Leccion del piloto: cada linea de metrics.csv dejaba HARNESS.md desfasado.
    # Un disco distinto de la semilla equivale a una semilla distinta del disco.
    copia = tmp_path / "HARNESS.md"
    copia.write_text((RAIZ / "HARNESS.md").read_text(encoding="utf-8")
                     .replace("fichero=progress/metrics.csv\n",
                              "fichero=progress/metrics.csv\nlinea de otro proyecto\n", 1),
                     encoding="utf-8")
    monkeypatch.setattr(harness_bundle, "GUIA", copia)
    assert harness_bundle.main(["--check"]) == 0


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


def test_rapido_se_anuncia_y_se_combina_con_dry_run():
    r = _init("--rapido", "--dry-run")
    assert r.returncode == 0, r.stderr
    if "Scope activo" in r.stdout:
        assert "(rapido)" in r.stdout


def test_la_plantilla_de_stack_corta_lo_lento_en_modo_rapido():
    texto = (RAIZ / "plantillas/stack/init.sh").read_text(encoding="utf-8")
    corte = texto.index("HARNESS_RAPIDO")
    for paso in ("==> build", "==> secretos", "==> dependencias"):
        assert texto.index(paso) > corte, paso
~~~~~~~

### `tests/test_metricas.py`

~~~~~~~ fichero=tests/test_metricas.py
import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import metricas  # noqa: E402
import state  # noqa: E402


def _transcript(ruta: Path) -> Path:
    lineas = [
        {"type": "user", "timestamp": "2026-10-10T10:00:00Z", "message": {"content": "encargo"}},
        {"type": "assistant", "timestamp": "2026-10-10T10:04:00Z", "message": {
            "id": "a", "model": "claude-opus-x", "content": [], "usage": {"input_tokens": 10, "output_tokens": 2,
                                                "cache_read_input_tokens": 300}}},
    ]
    ruta.write_text("\n".join(json.dumps(x) for x in lineas), encoding="utf-8")
    return ruta


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for rol in ("leader", "implementer", "reviewer", "spec_author"):
        (tmp_path / ".claude" / "agents").mkdir(parents=True, exist_ok=True)
        (tmp_path / ".claude" / "agents" / f"{rol}.md").write_text("---\n---\n", encoding="utf-8")
    (tmp_path / "progress" / "F01" / "IT2").mkdir(parents=True)
    (tmp_path / "progress" / "arranque.md").write_text("Estado: APROBADO\n", encoding="utf-8")
    (tmp_path / "feature_list.json").write_text(json.dumps([{
        "id": "F01", "status": "in_progress", "sdd": True, "scope": ["a"]}]), encoding="utf-8")
    monkeypatch.setattr(metricas, "RAIZ", tmp_path)
    monkeypatch.setattr(state, "ROOT", tmp_path)
    return tmp_path


def test_fila_del_reviewer_con_veredicto_y_causa(repo):
    (repo / "progress/F01/IT2/review.md").write_text(
        "Veredicto: CHANGES_REQUESTED\nCausa: tests\n", encoding="utf-8")
    fila = metricas.fila({"agent_type": "reviewer",
                          "agent_transcript_path": str(_transcript(repo / "t.jsonl"))})
    assert fila == ["2026-10-10", "F01", "2", "reviewer", "12", "300", "4",
                    "CHANGES_REQUESTED", "tests", "", "claude-opus-x"]


def test_el_cierre_cuenta_en_la_feature_cerrada(repo):
    # Leccion: el cierre marca done y state.py ya despacha la feature siguiente.
    (repo / "feature_list.json").write_text(json.dumps([
        {"id": "F01", "status": "done", "sdd": True, "scope": ["a"]},
        {"id": "F02", "status": "pending", "sdd": True, "scope": ["a"]}]), encoding="utf-8")
    fila = metricas.fila({"agent_type": "implementer",
                          "agent_transcript_path": str(_transcript(repo / "t.jsonl"))})
    assert fila[1:4] == ["F01", "2", "implementer"]


def test_spec_author_va_en_la_it_0(repo):
    fila = metricas.fila({"agent_type": "spec_author",
                          "agent_transcript_path": str(_transcript(repo / "t.jsonl"))})
    assert fila[1:4] == ["F01", "0", "spec_author"]


def test_agentes_ajenos_al_harness_no_se_apuntan(repo):
    assert metricas.fila({"agent_type": "Explore",
                          "agent_transcript_path": str(_transcript(repo / "t.jsonl"))}) is None


def test_el_hook_nunca_bloquea_al_subagente():
    # Un SubagentStop con codigo 2 impediria que el subagente terminara.
    r = subprocess.run([sys.executable, str(RAIZ / "scripts/metricas.py")],
                       input=b"no es json", capture_output=True)
    assert r.returncode == 0
~~~~~~~

### `tests/test_settings.py`

~~~~~~~ fichero=tests/test_settings.py
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
~~~~~~~

### `tests/test_skills.py`

~~~~~~~ fichero=tests/test_skills.py
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import skills  # noqa: E402


def _skill(carpeta: Path, nombre: str) -> None:
    carpeta.mkdir(parents=True)
    (carpeta / "SKILL.md").write_text(f"---\nname: {nombre}\ndescription: x\n---\n", encoding="utf-8")


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    config, proyecto = tmp_path / "config", tmp_path / "proyecto"
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(config))
    monkeypatch.setattr(skills, "RAIZ", proyecto)
    (proyecto / ".claude" / "agents").mkdir(parents=True)
    (proyecto / ".claude" / "agents" / "implementer.md").write_text(
        "---\nname: implementer\nmodel: sonnet\nskills:\n  - precargada\n  - falta\n---\n"
        "# implementer\n---\nskills:\n  - no-es-frontmatter\n", encoding="utf-8")
    (proyecto / ".claude" / "settings.json").write_text(
        json.dumps({"skillOverrides": {"oculta": "user-invocable-only"}}), encoding="utf-8")
    (proyecto / "harness.json").write_text(
        json.dumps({"skills_revisadas": ["plug:revisada"]}), encoding="utf-8")
    _skill(proyecto / ".claude" / "skills" / "arranque", "arranque")
    for nombre in ("precargada", "oculta", "nueva"):
        _skill(config / "skills" / nombre, nombre)
    # Carpeta con nombre distinto del de su SKILL.md: manda el `name:`.
    _skill(config / "skills" / "carpeta-rara", "con-nombre")
    # Plugin del directorio de skills.
    plugin_dir = config / "skills" / "mi-plugin"
    (plugin_dir / ".claude-plugin").mkdir(parents=True)
    (plugin_dir / ".claude-plugin" / "plugin.json").write_text('{"name": "mi-plugin"}', encoding="utf-8")
    _skill(plugin_dir / "skills" / "audita", "audita")
    # Plugins instalados: uno activo y otro no.
    for clave, nombre in (("plug@m", "revisada"), ("plug@m", "otra"), ("apagado@m", "x")):
        _skill(tmp_path / "cache" / clave.split("@")[0] / "skills" / nombre, nombre)
    (config / "plugins").mkdir(parents=True)
    (config / "plugins" / "installed_plugins.json").write_text(json.dumps({"plugins": {
        "plug@m": [{"installPath": str(tmp_path / "cache" / "plug")}],
        "apagado@m": [{"installPath": str(tmp_path / "cache" / "apagado")}],
    }}), encoding="utf-8")
    (config / "settings.json").write_text(
        json.dumps({"enabledPlugins": {"plug@m": True, "apagado@m": False}}), encoding="utf-8")
    return proyecto


def test_informa_de_las_nuevas_y_de_las_ausentes(entorno):
    datos = skills.informe()
    assert datos["nuevas"] == ["con-nombre", "mi-plugin:audita", "nueva", "plug:otra"]
    assert datos["ausentes"] == ["falta (implementer)"]


def test_solo_lee_las_skills_del_frontmatter(entorno):
    assert "no-es-frontmatter" not in skills.precargadas()


def test_un_plugin_desactivado_en_el_proyecto_no_cuenta(entorno):
    (entorno / ".claude" / "settings.json").write_text(
        json.dumps({"enabledPlugins": {"plug@m": False}}), encoding="utf-8")
    assert "plug:otra" not in skills.informe()["nuevas"]


def test_sin_nada_que_decir_no_imprime_nada(entorno, capsys):
    (entorno / "harness.json").write_text(json.dumps({"skills_revisadas": [
        "plug:revisada", "plug:otra", "mi-plugin:audita", "nueva", "con-nombre"]}), encoding="utf-8")
    (entorno / ".claude" / "agents" / "implementer.md").write_text(
        "---\nname: implementer\nskills:\n  - precargada\n---\n", encoding="utf-8")
    skills.main([])
    assert capsys.readouterr().out == ""


def test_la_plantilla_no_precarga_nada_raro():
    # Cada skill precargada en la plantilla figura en el README, que es donde
    # el usuario mira que instalar.
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    for skill in skills.precargadas():
        assert f"`{skill}`" in readme, skill
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


ARRANQUE = ("progress/arranque.md", "# Arranque\nEstado: APROBADO\n")


def _preparar(tmp_path, monkeypatch, features, ficheros=(), arranque=ARRANQUE):
    (tmp_path / "feature_list.json").write_text(json.dumps(features), encoding="utf-8")
    for ruta, contenido in ([arranque] if arranque else []) + list(ficheros):
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


def test_spec_aprobada_por_marca_avanza_aunque_siga_en_spec_ready(tmp_path, monkeypatch):
    # Leccion: nadie pasaba la feature a in_progress y el despacho se quedaba
    # pidiendo aprobacion. La marca del humano basta.
    _preparar(tmp_path, monkeypatch, [{**F, "status": "spec_ready"}], [
        ("specs/F01/design.md", "## Decisiones del humano (2026-10-11)\nP1: la recomendada\n"
                                "Aprobada por el humano: 2026-10-11\n")])
    assert state.next_action()["action"] == "CREAR_IT1_Y_LANZAR_IMPLEMENTER"


def test_spec_sin_marca_sigue_pidiendo_aprobacion(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "spec_ready"}], [
        ("specs/F01/design.md", "## Preguntas para el humano\nP1: recomiendo A\n")])
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


def test_it_descartada_sin_revisar_abre_la_siguiente(tmp_path, monkeypatch):
    # Leccion del piloto: con el stack cambiado, pedia revisar la IT vieja.
    _preparar(tmp_path, monkeypatch, [F], [
        ("progress/F01/IT1/descartada.md", "Motivo: cambio de framework (humano)")])
    assert state.next_action()["action"] == "CREAR_IT2_LANZAR_IMPLEMENTER_LUEGO_REVIEWER"


def test_impl_sin_sabotajes_vuelve_al_implementer(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [("progress/F01/IT1/impl.md", "informe")])
    assert state.next_action()["action"] == "DEVOLVER_AL_IMPLEMENTER_FALTAN_SABOTAJES"


def test_sabotajes_en_evidence_cuentan(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        ("progress/F01/IT1/impl.md", "informe"),
        ("progress/F01/IT1/evidence.md", "## Sabotajes\n| linea | test |"),
    ])
    assert state.next_action()["action"] == "LANZAR_REVIEWER"


def test_ultimo_tramo_empieza_por_el_reviewer(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [IMPL])
    assert state.next_action()["action"] == "LANZAR_REVIEWER"


def test_ultimo_tramo_con_security_hecho_lanza_solo_reviewer(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F],
              [IMPL, ("progress/F01/IT1/security.md", "Veredicto: APPROVED")])
    assert state.next_action()["action"] == "LANZAR_REVIEWER"


TRAMO_PENDIENTE = ("specs/F01/tasks.md", "- [x] **T1 — a**\n- [ ] **T2 — b**\n")


def test_tramo_intermedio_solo_reviewer(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [IMPL, TRAMO_PENDIENTE])
    assert state.next_action()["action"] == "LANZAR_REVIEWER"


def test_tramo_intermedio_aprobado_sigue_sin_security(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL, TRAMO_PENDIENTE, ("progress/F01/IT1/review.md", "Veredicto: APPROVED")])
    assert state.next_action()["action"] == "CREAR_IT2_LANZAR_IMPLEMENTER_SIGUIENTE_TRAMO"


def test_tramo_intermedio_rechazado_solo_reviewer(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL, TRAMO_PENDIENTE, ("progress/F01/IT1/review.md", "Veredicto: CHANGES_REQUESTED")])
    assert state.next_action()["action"] == "CREAR_IT2_LANZAR_IMPLEMENTER_LUEGO_REVIEWER"


def test_review_approved_sin_security_lanza_security(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F],
              [IMPL, ("progress/F01/IT1/review.md", "Veredicto: APPROVED")])
    assert state.next_action()["action"] == "LANZAR_SECURITY_REVIEWER"


def test_review_rechazado_no_gasta_una_pasada_de_seguridad(tmp_path, monkeypatch):
    # Leccion del piloto: en paralelo, seguridad revisaba IT que el reviewer
    # iba a rechazar (el 51 %).
    _preparar(tmp_path, monkeypatch, [F],
              [IMPL, ("progress/F01/IT1/review.md", "Veredicto: CHANGES_REQUESTED")])
    assert state.next_action()["action"] == "CREAR_IT2_LANZAR_IMPLEMENTER_LUEGO_REVIEWER"


def test_security_rechazado_vuelve_por_el_reviewer(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [F], [
        IMPL,
        ("progress/F01/IT1/review.md", "Veredicto: APPROVED"),
        ("progress/F01/IT1/security.md", "Veredicto: CHANGES_REQUESTED"),
    ])
    assert state.next_action()["action"] == "CREAR_IT2_LANZAR_IMPLEMENTER_LUEGO_REVIEWER"


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


@pytest.mark.parametrize("arranque", [None, ("progress/arranque.md", "Estado: en curso")])
def test_sin_arranque_aprobado_no_se_escribe_ninguna_spec(tmp_path, monkeypatch, arranque):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "pending"}], arranque=arranque)
    assert state.next_action()["action"] == "ARRANQUE"


def test_con_arranque_aprobado_se_despacha_normal(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch, [{**F, "status": "pending"}])
    assert state.next_action()["action"] == "LANZAR_SPEC_AUTHOR"
~~~~~~~

<!-- FIN FICHEROS -->
