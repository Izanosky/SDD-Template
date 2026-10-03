# Auditoría de la plantilla harness-sdd-template — 2026-10-03

Alcance: todo el árbol versionado, incluidos los cambios sin commitear de la
sesión anterior. Fase 1, solo lectura (este fichero es lo único creado).
Tokens ≈ caracteres/4. Las pruebas de comportamiento de `state.py` se
hicieron en un directorio temporal, no en el repo.

## 1. Resumen

La plantilla funciona (56 tests en verde) y su proceso es sólido, pero tiene
**4 fallos de lógica comprobados**, **fugas de genericidad** (unas 25 menciones
del proyecto de origen solo en HARNESS.md) y un **problema de estructura** que
gasta tokens de más en cada sesión y en cada agente.

Los 5 más graves:
1. **H01** `state.py` lee mal un veredicto: un `review.md` con `APPROVED`
   que menciona `CHANGES_REQUESTED` (p. ej. de una IT anterior) abre una
   iteración nueva. Comprobado.
2. **H02** Una task de tramo escrita sin negrita no cuenta como pendiente:
   la feature se cierra sin hacer el tramo. Comprobado.
3. **H05** El hook `guard_secrets` **falla abierto**: si `python` no
   existe (macOS/Linux suelen tener solo `python3`), Claude Code lo trata
   como error no bloqueante y el comando pasa.
4. **H06** `Read` permite leer `.env.staging`, `.env.test` y otras variantes
   no listadas en `settings.json`.
5. **H10** HARNESS.md (20,5 k tokens) obliga a Claude a copiar secciones a
   `docs/` en el montaje. Es caro, se desincroniza y deja en `docs/`
   conocimiento genérico que todos los agentes releen en cada iteración.

Ahorro estimado aplicando todo:
- Montaje inicial: unos 25 k tokens (lectura y escritura).
- Cada ejecución de agente: entre 3 y 5 k tokens (−20/30 % del contexto
  fijo de cada rol).
- Por feature típica (~3,5 IT × 3 roles): entre 30 y 50 k tokens.

## 2. Hallazgos

Gravedad: A = alta, M = media, B = baja.

| ID | Cat | Grav | archivo:línea | Problema | Propuesta | Ahorro |
|---|---|---|---|---|---|---|
| H01 | B,C | A | scripts/state.py:27-37 | `_veredicto` busca la subcadena `CHANGES_REQUESTED` en todo el fichero. Un review aprobado que cita la IT anterior se lee como rechazo (comprobado: `CREAR_IT3_…`). Los revisores arrastran correcciones anteriores (reviewer.md:56), así que pasará. | Leer solo una línea `^Veredicto: (APPROVED\|CHANGES_REQUESTED)$`. Los agentes MUST escribir esa línea exacta. Test nuevo. **Cambia el algoritmo de despacho → decisión.** | — |
| H02 | B,C | A | scripts/state.py:48-53 | La regex exige `- [ ] **T<n>`. `- [ ] T2 — …` no cuenta y la feature pasa a cierre con un tramo sin hacer (comprobado). | Aceptar `^\s*- \[ \]\s*\**\s*T\d+`; test con y sin negrita. **Decisión (despacho).** | — |
| H03 | B | M | scripts/state.py:41-43 | Cualquier aparición de `## Sabotajes` en cualquier `.md` de la IT vale, incluido "falta ## Sabotajes" (comprobado: `LANZAR_REVIEWER`). | Regex de encabezado `^## Sabotajes\s*$` (re.M), solo en `impl.md`/`evidence.md`. **Decisión (despacho).** | — |
| H04 | C | B | scripts/state.py:32,43,52 | `read_text(encoding="utf-8")` revienta con un fichero ANSI (editor de Windows). Comprobado con cp1252. | `errors="replace"`. | — |
| H05 | C | A | .claude/settings.json:29-30 | `python "…/guard_secrets.py"`: sin `python` en el PATH el hook no arranca y Claude Code **deja pasar el comando** (doc. hooks: código ≠ 2 no bloquea; "interpreter not found" no bloquea). | Lanzador que pruebe `python3`/`python`/`py` y salga con 2 si no hay ninguno (falla cerrado), o declarar `"shell"` y documentar el requisito. Mismo arreglo en H07. | — |
| H06 | C | A | .claude/settings.json:3-17 | Deny solo para `.env`, `.env.local`, `.env.*.local`, `.env.production`, `.env.development`. `.env.staging`/`.env.test` se leen con Read (la doc. confirma que Read deny es por patrón). | `Read(**/.env.*)` + `Edit(**/.env.*)`. Coste: `.env.example` deja de ser legible por la herramienta Read (guard_secrets ya lo permite por shell) → **decisión**: o eso, o renombrar la plantilla a `env.example`. | — |
| H07 | C | M | scripts/session_start.sh:9,15 | Usa `python` (mismo problema que H05). Un fallo aquí no rompe nada, pero el estado no aparece. | Mismo lanzador que H05. | — |
| H08 | C,D | M | .claude/settings.json:23 + session_start.sh:21-25 | Solo `matcher: "clear"`: en `startup` y tras `compact` (justo cuando más falta) no se inyecta el estado. Además vuelca `impl.md`+`review.md`+`security.md` (hasta ~600 líneas): pasa el tope de 10.000 caracteres, se recorta a un preview de 2.000 y el resto se pierde. | `matcher: "startup\|clear\|compact\|resume"` e inyectar solo `state.py` + `current.md` + las rutas de la última IT (el leader lee lo que necesite). | ~2-5 k por arranque/clear |
| H09 | C,E | A | HARNESS.md:1424-1428 (plantilla B.1 CLAUDE.md) | "Al arrancar una sesión… actúa como `leader`… `python scripts/state.py`". Los subagentes **cargan CLAUDE.md** (la doc. de subagentes ofrece `omitClaudeMd` para evitarlo), así que el implementer y los revisores reciben la orden de actuar como leader. Riesgo de confusión de rol y de llamadas a `state.py` que sobran. | Opción 1: `"agent": "leader"` en `.claude/settings.json` (doc. sub-agents: "Running Main Session as Subagent") y quitar la orden de CLAUDE.md. Opción 2: "Solo si eres la sesión principal (no un subagente)…". **Decisión** (con la opción 1, el `model`/`tools` de leader.md pasan a aplicarse: ver H11). | ~0,1 k por subagente |
| H10 | E,D | A | HARNESS.md:170-181 (paso 5 de la checklist) | `docs/` se crea **copiando secciones** de HARNESS.md: Claude lee 20,5 k tokens y reescribe ~12 k. Las copias se desincronizan de la plantilla y nadie las versiona como plantilla. | Entregar `docs/*.md`, `CLAUDE.md`, `CHECKPOINTS.md`, mapa, `docs/CHANGELOG.md`, `progress/metrics.csv` y `progress/audits/README.md` como **ficheros reales** con `<RELLENAR>`. HARNESS.md pasa a ser la guía (por qué + checklist + índice) y deja de ser el depósito. | ~25 k en el montaje |
| H11 | B,F | M | HARNESS.md:266; leader.md:4-5 | La tabla dice "leader · sonnet", pero el leader es la sesión principal: su `model` y sus `tools` no se aplican salvo con `--agent`/`agent`. Si se aplicaran (H09), le faltan `Edit`/`Write` para arreglos pequeños, `current.md` y `metrics.csv`. | Si se adopta `agent`: `tools` + Edit, Write; si no, quitar `model`/`tools` de la tabla y decir "modelo de la sesión". | — |
| H12 | E,D | A | HARNESS.md:893-1068 → docs/principios.md | Secciones 9-12 (SOLID, GoF, estilos de arquitectura, antipatrones: ~2,5 k tokens) van a `docs/principios.md`, que leen spec_author, implementer y reviewer **en cada iteración**. La doc. oficial: excluir "standard conventions Claude already knows" y "self-evident practices". | `docs/principios.md` reducido a las **posturas propias** (nativo antes que dependencia, regla de tres, fallar abierto solo hacia un control posterior, atajos marcados, cuándo NO aplicar un patrón): ~0,6 k. El catálogo GoF queda en HARNESS.md como referencia humana o se elimina. | ~1,9 k por ejecución × 3 roles |
| H13 | D | M | HARNESS.md:262-490 vs .claude/agents/*.md | La sección 4 repite casi entera la definición de cada agente (~2,9 k). No cuesta en ejecución (no se cargan juntos), pero son dos fuentes de verdad: ya divergen en matices (p. ej. explorer sin "Cómo terminas"). | Sección 4 = tabla de roles + 1-2 líneas por rol + "definición canónica: `.claude/agents/<rol>.md`". | ~2,5 k en HARNESS |
| H14 | D | M | HARNESS.md:1272-1384 | El catálogo de 55 lecciones repite reglas ya escritas en las secciones 1, 6-8 y 14 (~1,6 k). | Una tabla "lección → dónde quedó como regla/test" en 1 línea cada una, o mover el catálogo a `docs/LECCIONES.md` (no lo lee ningún agente). | ~0,8 k |
| H15 | D | M | HARNESS.md:1415-1657 | El Anexo B (plantillas de texto, ~3 k) sobra si se aplica H10: las plantillas pasan a ser ficheros. | Eliminar el anexo, o dejar una tabla "fichero → propósito". | ~2,8 k |
| H16 | A | M | HARNESS.md:5-8 | Cabecera con cifras y fechas del origen ("18 features… septiembre-octubre 2026"). | "Probado en un proyecto real de tamaño medio" sin cifras, o cifras en un apartado de ejemplo. | ~0,05 k |
| H17 | A | M | HARNESS.md:1166-1193 | 17.1: tabla de tokens y rechazos del proyecto de origen, presentada como dato general. | Mover a "Ejemplo de lectura de metrics.csv" y marcarlo como ejemplo; quedarse con las conclusiones (más gasto en implementer; la iteración es lo caro). | ~0,3 k |
| H18 | A | M | HARNESS.md:146, 474, 629, 650, 887, 1008, 1110, 1170, 1243; security_reviewer.md:50; spec_author.md:57 | "En el proyecto de origen…", "PC de casa", "proveedor de vídeo", "iOS/Web Audio", "constante de 1200 a 300". | Reescribir como ejemplo genérico ("p. ej. un proceso que solo puede correr en una red concreta") o eliminar. Ningún agente necesita la anécdota: basta la regla y el motivo genérico. | ~0,5 k |
| H19 | A | M | HARNESS.md:842-846, 869-876, 1359-1362 | NFKC/`unaccent`, RLS, `search_path`, RPC con clave pública: específicos de Postgres/BaaS. | Agrupar en un apartado "Si usas una base de datos expuesta por API (p. ej. PostgREST/BaaS)". | — |
| H20 | A | M | HARNESS.md:833-838, 1157-1159, 1377 | Sesiones anónimas, registro público, panel del proveedor: supone un BaaS de auth. | Apartado condicional "Si delegas la autenticación en un proveedor". | — |
| H21 | A | M | HARNESS.md:1069-1115 | La sección 14 (frontend) se presenta como general y supone PWA/SPA ("prefetch", "localStorage", "Media Session"). | Título "Si tu proyecto tiene interfaz web"; sacar a `docs/frontend/conventions.md` de ejemplo. | — |
| H22 | A | M | HARNESS.md:362, 519, 624-631; spec_author.md:67-68 | "Tramos: backend primero" supone backend+frontend. | "Tramos por stack o por capa, en orden de dependencia (lo que otros consumen, primero)". | — |
| H23 | A,F | M | tests/test_feature_list.py:41-43 | "Como mucho una feature en curso" supone un solo desarrollador o agente. | Parámetro `max_en_curso` en `harness.json` (por defecto 1) y explicarlo en la guía. **Decisión.** | — |
| H24 | A,F | M | state.py (acciones), plantillas, `## Sabotajes`, `SERVICIOS REALES`, `Veredicto` | Idioma fijado en español en marcadores que lee un script. Un proyecto en inglés tiene que tocar código. | Documentar los marcadores como **tokens fijos** (no traducibles) en una tabla única, o leerlos de `harness.json`. **Decisión.** | — |
| H25 | A | B | .github/workflows/ci.yml | Solo GitHub Actions; sin guía para GitLab/otros. | Una línea en la guía: los cuatro pasos del CI son portables (historia gitleaks, pytest del harness, `init.sh`), con el comando de cada uno. | — |
| H26 | B | B | README.md:92, 96 | Remiten a "sección 1 de HARNESS.md" para la checklist; ahora es la 2. | Corregir referencias. | — |
| H27 | B | B | scripts/guard_secrets.py:72-73 | El mensaje cita "CLAUDE.md, Prohibiciones"; la plantilla B.1 la llama "Reglas duras". | Unificar el nombre. | — |
| H28 | B | B | spec_author.md:83-95 | Dos secciones de cierre seguidas ("Dónde terminas" y "Cómo terminas"). | Fusionar. | ~0,05 k por ejecución |
| H29 | B | B | explorer.md (completo) | Escribe un fichero y no tiene "Cómo terminas"; HARNESS.md:285-291 dice que todo rol que escribe la tiene. | Añadirla (2 líneas). | — |
| H30 | C | M | scripts/guard_secrets.py:33 | Falso positivo: cualquier comando que **mencione** `.env` se bloquea (p. ej. `grep -n "./.env" docs.txt`, visto durante esta auditoría). | Bloquear solo cuando `.env*` va en posición de fichero (argumento de `cat/type/Get-Content/cp/source…` o redirección), y añadir esos casos permitidos al test. | — |
| H31 | C,F | M | CLAUDE.md B.1 (reglas 1-2) | "No commit" y "no dependencias" solo están en prosa. La doc.: CLAUDE.md es "advisory"; para garantizar algo, permisos o hooks. | `permissions.ask`: `Bash(git commit *)`, `Bash(git push *)`, `PowerShell(git commit *)`, `PowerShell(git push *)` y los instaladores habituales (`npm install *`, `pip install *`, `uv add *`…, marcados `<RELLENAR>`). Límite documentado: `git -C . push` no casa. **Decisión** (con `ask`, el humano puede seguir aprobando). | — |
| H32 | C | M | .githooks/pre-commit:15-23 | La regla de `docs/CHANGELOG.md` solo vive en el hook local: un clon sin `core.hooksPath` o un `--no-verify` la saltan. | Paso de CI que compare el rango del push o PR (`git diff --name-only <base>..HEAD`) con la misma lógica, sacada a un script compartido. **Decisión** (GitHub). | — |
| H33 | F | B | specs/_plantilla/tasks.md + spec_author.md:57-63 | El tope de spec va en líneas (~400). Medido en el origen: una spec de unas 400-500 líneas son 7-10 k tokens. | Expresarlo en tokens aproximados (≈ 6-8 k) además de líneas; `wc -c`/4 como medida. | — |
| H34 | F | M | 200 líneas, ~400/600, 4 features, 2 reanudaciones (HARNESS.md:742-747, 360, 1219, 665) | Umbrales repartidos por cuatro ficheros, sin un sitio único donde ajustarlos. | Tabla "Parámetros del harness" en un solo sitio (CLAUDE.md o `harness.json` + docs), con el valor por defecto y su porqué; los agentes la citan. | — |
| H35 | F | M | feature_list.json `sdd` | El campo `sdd` existe y nadie lo usa (state.py lo ignora). Proyectos pequeños pagan spec + puerta humana + 2 vetos incluso para lo trivial. | **Modo ligero**: `"sdd": false` → `state.py` salta el spec_author y la puerta humana; el implementer trabaja desde `acceptance` y pasa solo el reviewer, salvo que toque zonas sensibles (6.4). **Decisión** (despacho + test). | grande en features pequeñas |
| H36 | E | M | AGENTS.md (B.2) | `AGENTS.md` es un estándar entre herramientas: Claude Code lo carga como **instrucciones** si no hay CLAUDE.md, y otras herramientas (Codex, Cursor) también. Aquí es un mapa sin reglas: nombre engañoso. | Renombrar a `docs/README.md` (mapa) o fusionarlo en CLAUDE.md (~0,4 k). **Decisión.** | ~0,4 k por sesión si se fusiona y se recorta |
| H37 | E | M | docs/<stack>/conventions.md | Las convenciones de stack las lee el agente "solo la de su scope", por instrucción. La doc. ofrece `.claude/rules/*.md` con `paths:`, que carga solo al tocar ficheros que casan. | Opción: `.claude/rules/<stack>.md` con `paths: ["<stack>/**"]`. [sin verificar] si las reglas con `paths` cargan dentro de subagentes; probar antes. **Decisión.** | — |
| H38 | E | B | leader.md (2,2 k, cargado en cada sesión) | Auditorías, métricas y reanudación son procedimientos ocasionales, y la doc. dice "procedure → skill". | Mover "Auditoría completa" y "Retrospectiva" a skills con `disable-model-invocation: true` (`/auditoria`, `/retro`); leader.md se queda con el despacho. | ~0,6 k por sesión |
| H39 | E | B | .claude/agents/*.md | No usan `maxTurns` ni `effort` (campos documentados). Un agente atascado puede consumir sin tope. | `maxTurns` generoso en revisores y explorer como red de seguridad; `effort` opcional. Documentar. | — |
| H40 | E | B | CLAUDE.md B.1 | Sin instrucción de compactación; tras un `compact` se puede perder la IT activa. | Una línea: "Al compactar, conserva feature, IT, acción de state.py y pendientes del humano". | — |
| H41 | E | B | `ajuste-AAAA-MM-DD` (HARNESS.md:130-132) | En CLAUDE.md los comentarios HTML se eliminan antes de inyectarse (doc. memoria). En `docs/` y agentes sí cuestan, aunque poco. | Indicar que en CLAUDE.md las marcas van como `<!-- -->`, que no cuestan tokens. | — |
| H42 | F | B | HARNESS.md:1131 + 1.8 | La regla de `docs/` obliga a propagar a HARNESS.md "si la lección es trasladable". En un proyecto, HARNESS.md es una copia de la plantilla: mezcla proyecto y plantilla. | En el proyecto, propagar a un `progress/para_la_plantilla.md`; la plantilla se actualiza en su propio repo. | — |
| H43 | G | B | — | No hay mantenimiento periódico de las instrucciones. La doc. ofrece `/doctor prompt-audit` sobre CLAUDE.md, rules, skills y subagentes. | Añadirlo a la retrospectiva y tras cada 4-5 cambios en `docs/CHANGELOG.md`. | — |
| H44 | G | B | tests/test_state.py | No hay test del caso H01 (veredicto que cita otro veredicto) ni de H02/H03. | Tres tests nuevos junto a los arreglos. | — |
| H45 | C | B | init.sh:36-38 | Con `TODO_HECHO` sale con 0 sin verificar nada: el CI de `main` queda verde sin ejecutar ningún stack. | Si no hay scope activo, ejecutar `--all` en el CI (o que el CI llame siempre a `--all`). **Decisión.** | — |
| H46 | F | B | HARNESS.md:94-151 (sección 1) | La regla 1.8 ocupa 30 líneas en la lista de reglas duras, con el formato del CHANGELOG duplicado (también en B.8). | Regla en 4 líneas; el formato, solo en `docs/CHANGELOG.md` (fichero real, H10). | ~0,3 k |

Comprobado sin hallazgo: alias de modelo `sonnet`/`opus`/`haiku` válidos
(doc. sub-agents); `Read(**/.env)` es sintaxis válida y equivale a
`Read(.env)`; `Agent` ausente de `tools` impide anidar (coherente con
test_settings.py:30-36); `SendMessage` es el mecanismo documentado para
reanudar un subagente; el anidamiento máximo por defecto es 3, compatible.

## 3. Estructura propuesta

```
.
├── CLAUDE.md                 ≤ 120 líneas: contexto, reglas duras, parámetros, comandos   (fichero real)
├── CHECKPOINTS.md            (fichero real con <RELLENAR>)
├── HARNESS.md                guía humana ~6-7 k: por qué, checklist, despacho, mapa de ficheros, lecciones→regla
├── harness.json              + parámetros opcionales (max_en_curso…) si se aprueban H23/H34
├── .claude/
│   ├── settings.json         agent: leader (H09), ask git/instaladores (H31), deny .env.* (H06),
│   │                         hooks con lanzador que falla cerrado (H05/H07), SessionStart ampliado (H08)
│   ├── agents/*.md           canónicos; leader sin procedimientos ocasionales
│   ├── skills/auditoria/, skills/retro/   (H38, invocación manual)
│   └── rules/<stack>.md      opcional, con paths: (H37)
├── docs/
│   ├── README.md             mapa (antes AGENTS.md, H36)
│   ├── CHANGELOG.md          con su formato y la primera entrada
│   ├── specs.md · verification.md · security.md (con apartados condicionales H19/H20)
│   ├── principios.md         ~0,6 k, solo posturas propias (H12)
│   ├── architecture.md · retrospective.md
│   └── ejemplos/frontend-conventions.md   (H21)
├── progress/  current.md · history.md · metrics.csv (cabecera) · audits/README.md
└── scripts/   state.py (H01-H04, H35) · run_py.sh (H05/H07) · guard_secrets.py (H30)
```

Contexto fijo por rol (estimado con docs de tamaño real; sin contar el
código que lea):

| Rol | Antes | Después | Qué cambia |
|---|---|---|---|
| leader (por sesión) | ~6,4 k (CLAUDE 1,7 + leader.md 2,2 + hook ≤2,5) | ~4 k | CLAUDE.md recortado, procedimientos a skills, hook ligero |
| spec_author | ~13,5 k | ~10 k | principios −1,9 k, CLAUDE −0,8 k |
| implementer | ~16,5 k | ~12,5 k | principios, CLAUDE, tope de spec en tokens |
| reviewer | ~18,4 k | ~14,5 k | ídem |
| security_reviewer | ~17,5 k | ~16 k | CLAUDE; security.md no se recorta (es específico) |
| montaje inicial | ~20,5 k lectura + ~12 k escritura | ~7 k lectura + rellenar huecos | H10 |

## 4. Fuentes consultadas (2026-10-03)

| URL | Qué se sacó |
|---|---|
| https://code.claude.com/docs/en/memory | CLAUDE.md: "target under 200 lines… longer files reduce adherence"; los imports no ahorran contexto; `.claude/rules/` con `paths:` cargan bajo demanda; comentarios HTML eliminados del contexto; semántica de AGENTS.md (H36); `/doctor prompt-audit` (H43). |
| https://code.claude.com/docs/en/sub-agents | Campos `model` (alias válidos), `tools`, `maxTurns`, `effort`, `omitClaudeMd`, `skills`; `agent` en settings / `--agent` para que la sesión principal sea un agente (H09, H11); `SendMessage` para reanudar; anidamiento de 3 niveles. |
| https://code.claude.com/docs/en/hooks | Matchers de SessionStart (`startup`, `resume`, `clear`, `compact`, `fork`); solo el código de salida 2 bloquea; un intérprete que no existe = error no bloqueante (H05); en Windows, Git Bash o PowerShell; salida al contexto capada a 10.000 caracteres (H08). |
| https://code.claude.com/docs/en/permissions | Sintaxis `Bash(git commit *)` / `:*`; `ask` frente a `deny`; patrones gitignore en Read/Edit; Read deny se aplica a `cat`/`head`… en Bash pero no a scripts arbitrarios (por eso guard_secrets sigue siendo necesario). |
| https://code.claude.com/docs/en/skills | Divulgación progresiva (solo nombre y descripción hasta invocarse); SKILL.md < 500 líneas; `disable-model-invocation` para procedimientos manuales (H38). |
| https://code.claude.com/docs/en/best-practices | CLAUDE.md corto ("Would removing this cause Claude to make mistakes?"); excluir lo que Claude ya sabe (H12); hooks deterministas frente a instrucciones advisory (H31); instrucciones de compactación en CLAUDE.md (H40). |
| https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | "smallest possible set of high-signal tokens"; recuperación just-in-time frente a precarga (H08, H10); subagentes que devuelven resúmenes de 1-2 k tokens (encaja con el tope de 200 líneas). |

## 5. Plan de aplicación

**Seguros** (sin decisión; no cambian el comportamiento del despacho):
1. README.md: H26.
2. guard_secrets.py: H27 (mensaje). H30 (regex) con tests nuevos de permitidos y bloqueados.
3. .claude/agents/spec_author.md: H28. explorer.md: H29.
4. scripts/state.py: H04 (`errors="replace"`).
5. HARNESS.md: H16, H17, H18, H19, H20, H21, H22, H46 (genericidad y
   condicionales), H13, H14 (deduplicación), H33, H40, H41, H43.
6. scripts/session_start.sh + settings.json: H07/H05 (lanzador que falla
   cerrado, con test) y H08 (matchers y contenido ligero).
7. settings.json: H06 en su forma sin decisión, con las variantes
   habituales añadidas una a una (`.env.staging`, `.env.test`, `.env.*.local`).

**Necesitan tu decisión:**
- D1 (H01, H02, H03, H44): arreglar el parseo de `state.py` (veredicto por
  línea exacta, tasks sin negrita, encabezado de sabotajes) con tests.
  Cambia el algoritmo de despacho. **Recomendado: sí.**
- D2 (H06): `Read(**/.env.*)` a costa de no leer `.env.example` con Read,
  o renombrar a `env.example`. **Recomendado: deny amplio y mantener
  `.env.example` legible solo por shell.**
- D3 (H09, H11): `"agent": "leader"` en settings (con Edit/Write en sus
  tools) frente a una frase condicional en CLAUDE.md. **Recomendado:
  `agent`** (tools y prompt garantizados, sin la orden que hoy llega a los
  subagentes).
- D4 (H10, H12, H15, H36): entregar `docs/` y la raíz como ficheros reales,
  recortar `principios.md` y renombrar o fusionar AGENTS.md. Es el cambio
  más grande. **Recomendado: sí.**
- D5 (H31): `ask` para git commit/push e instaladores. **Recomendado: sí.**
- D6 (H32): comprobación del CHANGELOG también en el CI. **Recomendado:
  sí** (unas 10 líneas en ci.yml + un script compartido con el hook).
- D7 (H35): modo ligero con `"sdd": false`. **Recomendado: sí**, con test.
- D8 (H23, H24, H34): parámetros en `harness.json` (máximo de features en
  curso, marcadores, umbrales) o solo documentarlos en una tabla.
  **Recomendado: solo tabla**; `harness.json` únicamente para lo que lee un
  script (`max_en_curso`).
- D9 (H37, H38, H39): rules con `paths`, skills para auditoría y
  retrospectiva, `maxTurns`. **Recomendado: skills y `maxTurns` sí; rules
  con `paths` solo tras probar que cargan en subagentes.**
- D10 (H45): que el CI ejecute siempre `init.sh --all`. **Recomendado: sí.**
- D11 (H42): propagación de lecciones a `progress/para_la_plantilla.md` en
  lugar de editar HARNESS.md dentro del proyecto. **Recomendado: sí.**

## 6. Estado tras la fase 2 (2026-10-03)

Aplicado con la aprobación del humano ("arréglalo tú"). 82 tests en verde.

| Hallazgos | Estado |
|---|---|
| H01, H02, H03, H04, H44 | **Aplicado** en `state.py`: línea `Veredicto:` exacta, tasks con o sin negrita, encabezado `## Sabotajes` solo en `impl.md`/`evidence.md`, `errors="replace"`. 5 tests nuevos que reproducen los fallos comprobados. |
| H05, H07 | **Aplicado**: `scripts/py.sh` (sale con 2 sin intérprete) en ambos hooks. Test con `PATH` vacío; el sabotaje `exit 2 → exit 0` hace caer el test. |
| H06 | **Aplicado con cambio**: la doc. de permisos dice que el deny de lectura también cubre `cat`/`head` en Bash, así que un comodín sobre todas las variantes haría ilegible `.env.example`. Lista explícita ampliada (`prod`, `dev`, `staging`, `test`, `ci`) + nota para añadir variantes. |
| H08 | **Aplicado**: matcher `startup\|resume\|clear\|compact`; `session_start.sh` da `state.py` + 80 líneas de `current.md` + rutas (no contenidos). |
| H09, H11 | **Aplicado con la opción 2**: frase condicional en CLAUDE.md. Se descartó `"agent": "leader"` porque la doc. dice que un subagente usa "its own system prompt, not the Claude Code system prompt": la sesión principal perdería el prompt de Claude Code. `leader.md`: `model: inherit` y tools con Edit/Write. |
| H10, H15 | **Aplicado y revisado por indicación del humano**: los ficheros existen como ficheros reales **y** HARNESS.md sigue siendo autosuficiente: Parte I (guía, ~7,4 k tokens) + Parte II (contenido literal de los 51 ficheros, ~26 k), generada por `scripts/harness_bundle.py` y comprobada por `tests/test_harness_bundle.py`. Probado: con solo HARNESS.md en un directorio vacío se extraen 51 ficheros y pasan los 82 tests. |
| H12 | **Aplicado**: `docs/principios.md` con solo posturas propias (~0,5 k tokens); el catálogo SOLID/GoF/antipatrones, eliminado. |
| H13, H14, H46 | **Aplicado**: roles en tabla + porqué; lecciones como tabla "lección → dónde quedó"; regla de docs en tabla de mecanismos. |
| H16-H22 | **Aplicado**: sin cifras, fechas ni anécdotas del origen; apartados condicionales en `docs/security.md`; frontend en `plantillas/stack/conventions-web.md`; tramos "en orden de dependencia". |
| H23 | **No aplicado**: un `max_en_curso` > 1 prometería un paralelismo que `state.py` no da. Documentado como límite (HARNESS.md §7 y §10). |
| H24 | **Aplicado como documentación**: tabla de marcadores fijos (§7) + test que comprueba que los agentes los escriben. |
| H25-H29 | **Aplicado**. |
| H30 | **Aplicado**: el patrón de un buscador suelto se ignora; tests nuevos de permitidos y bloqueados. |
| H31 | **Aplicado**: `permissions.ask` para commit/push e instaladores, con test. |
| H32 | **Aplicado**: `scripts/check_docs_changelog.sh` compartido por el pre-commit y el CI, con tests. |
| H33, H34 | **Aplicado**: tope en tokens; tabla "Parámetros del harness" en CLAUDE.md. |
| H35 | **Aplicado**: modo ligero (`"sdd": false`) sin spec ni puerta, con los dos vetos, y 2 tests. |
| H36 | **Aplicado**: el mapa es `docs/README.md`; no hay `AGENTS.md`. |
| H37 | **No aplicado**: queda pendiente probar que las reglas de `.claude/rules` con `paths` se cargan en subagentes. |
| H38, H39 | **Aplicado**: skills `/auditoria-seguridad` y `/retrospectiva` de invocación manual (test); `maxTurns` en los cinco subagentes. |
| H40-H43, H45 | **Aplicado**. |

Hallazgos nuevos durante la fase 2, ya corregidos:
- `guard_secrets` dejaba pasar el comando si el JSON de entrada era ilegible.
  Ahora falla cerrado y tolera un BOM (tests).
- `guard_secrets` leía stdin con la página ANSI de Windows. Ahora lee bytes
  en UTF-8.
- `session_start.sh` se situaba en el repositorio del directorio actual, no
  en el suyo. Ahora usa la ruta del script.
- `harness_bundle.py` contiene sus propios marcadores. Ahora toma el último
  marcador de fin (test de ida y vuelta).

Pendiente del humano:
- revisar y hacer el commit;
- `git update-index --chmod=+x` sobre los `.sh` nuevos tras el `git add`;
- borrar este fichero si no se quiere conservar.
