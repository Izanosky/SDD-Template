# Plantilla: forma de trabajo con Claude Code

Una forma de trabajar para empezar y construir un proyecto con Claude Code
como lo haría un equipo de verdad: primero se entiende **qué** se construye
y para quién, después con qué ambición, y solo entonces **cómo**. Claude
pregunta, propone con una recomendación y aporta lo que tú no sabes que
necesitas. Las decisiones las tomas tú.

La plantilla es casi toda documentos que Claude sigue: unas reglas que se
cargan siempre (`.claude/rules/harness.md`), unos agentes y unas skills.
El `CLAUDE.md` es del proyecto: lo genera `/arranque` al cerrar. Lo único que se ejecuta son **dos hooks pequeños** que
protegen lo que no tiene vuelta atrás (secretos, historia de git, trabajo
sin commitear). No trae tests, CI ni métricas: si los quieres, se deciden
en el arranque o se piden después.

## Requisitos

- [Claude Code](https://code.claude.com/) y git.
- **bash** y **Python 3.10+** para los hooks. En Windows, bash es el de
  [Git for Windows](https://git-scm.com/download/win) (Git Bash), y tiene
  que estar en el PATH: compruébalo con `bash --version` en la terminal
  donde abres Claude Code.
  - **Sin bash, los hooks no llegan a ejecutarse** y Claude Code deja pasar
    los comandos sin vigilar, sin avisar.
  - Sin Python (con bash), el lanzador bloquea los comandos de terminal en
    vez de dejarlos pasar.
- Opcional: las skills de la tabla "Skills opcionales". Si una no está
  instalada, el harness funciona igual, sin ella.
- Opcional, para las capturas de interfaz: el plugin oficial `playwright`
  (MCP).

## Uso

1. Copia esta carpeta como raíz del proyecto nuevo y ejecuta `git init`
   si no es un repositorio. En un proyecto que ya existe, **no pises** su
   `CLAUDE.md`, su `.gitignore` ni su `.claude/settings.json`: fusiónalos a
   mano (el arranque añade a su `CLAUDE.md` lo que falte, sin
   sustituirlo). El resto (`.claude/rules/`, `.claude/agents/`,
   `.claude/skills/`, `.claude/hooks/`, `docs/`, `specs/`) se copia tal
   cual.
2. Antes del primer `git add -A`, mira `git status` y lleva a `.gitignore`
   lo personal que hubiera en la carpeta.
3. Abre Claude Code en ella y escribe `/arranque`, o di qué quieres
   construir.
4. Responde a la entrevista. Cada pregunta trae una recomendación, y "no lo
   sé" también vale.
5. Cuando apruebes el arranque, Claude construye feature a feature y te
   para en cada decisión: la spec, el visto bueno visual y el commit.

## 1. El arranque

`/arranque` es una entrevista con el método de la skill `entrevista`:

- se pregunta por rondas de como mucho 4 preguntas **cada una**. No es un
  límite total: hay tantas rondas como haga falta hasta que no queda
  ninguna decisión abierta, y si prefieres rondas más largas o más cortas,
  lo dices;
- en cada ronda solo entra lo que ya se puede preguntar sin adivinar
  respuestas que aún no has dado;
- cada pregunta trae la recomendación de Claude y su porqué;
- los hechos los busca Claude, y las decisiones las tomas tú.

Cada decisión queda en su documento de `docs/` (tabla de abajo), así que
se puede retomar en otra sesión y se consulta siempre aparte del código.

| Fase | Qué se decide |
|---|---|
| 1. Requisitos | qué hace la aplicación, para quién, qué entra en la primera versión y qué no, y la lista de features |
| 2. Alcance | personal, compartido o producción: cuánto rigor merece |
| 3. Aspectos clave | lo que exige ese alcance, traído por Claude aunque no lo menciones (caché, pool de conexiones, escalado, multi-tenant, idempotencia, observabilidad, copias, RGPD…; ver `catalogo.md`). Lo caro de cambiar después se decide ahora; lo barato se aplaza con su disparador |
| 4. Stack | arquitectura, lenguaje, framework, datos y despliegue: los eliges tú o Claude propone 2-3 opciones. Se apuntan los supuestos de riesgo |
| 5. Librerías | lo que va encima del stack, con versión y alternativa descartada. Lo que no esté en la lista pide permiso |
| 6. Diseño visual | `/direccion-visual`: qué pantallas se diseñan, tus referencias reales, tres direcciones para comparar (Google Stitch o miniaturas HTML), librerías de interfaz y tokens |
| 7. Forma de trabajo | cuánto proceso según el alcance: spec, pruebas, comando de verificación, zonas críticas y mutantes, revisiones, auditorías, ramas, skills de los agentes y convenciones de código (Claude propone las estándar del stack y te pregunta solo tus preferencias) |

En cualquier fase, y también después, puedes pedir una **investigación a
fondo** sobre convenciones, arquitecturas de referencia o cómo resuelven
algo productos parecidos. Claude propone antes la pregunta, las fuentes y
el coste, y el resultado queda en `docs/investigaciones/<tema>.md`, con
fuentes y fechas. La decisión la sigues tomando tú.

## 2. Construir

Una feature cada vez, en el orden de `docs/proyecto.md`. La primera, F00,
es el **andamiaje**: el proyecto creado con el generador oficial, un "hola
mundo" de punta a punta, el comando de verificación funcionando y los
supuestos de riesgo comprobados.

```
spec (con el humano) ─► aprobación ─► implementer ─► reviewer ─► security_reviewer ─► visto bueno visual ─► commit
                                         ▲              │               │
                                         └── IT<n+1> ◄──┴── cambios ◄───┘
```

Lo que `docs/proceso.md` no pida, se salta: por ejemplo, un proyecto personal
puede ir sin spec ni revisores en los cambios pequeños.

**Una carpeta por vuelta.** Cada intento de implementar es una iteración
con su carpeta, `progress/FNN/IT<n>/`. La crea la sesión principal antes de
lanzar al `implementer`, y nunca se reescribe una anterior:

| Fichero | Quién | Qué |
|---|---|---|
| `impl.md` | `implementer` | ficheros tocados, requisito → test, comandos, desviaciones, capturas (≤ 200 líneas) |
| `evidence.md` | `implementer` | lo largo; mutantes bajo `## Sabotajes` |
| `capturas/` | `implementer` | pantallas en claro y oscuro, 1280 y 390 px, caso normal y peor caso |
| `review.md` | `reviewer` | `Veredicto: APPROVED` o `CHANGES_REQUESTED`, con cada cambio citado `archivo:línea` |
| `security.md` | `security_reviewer` | igual, con la tabla de ataque; solo en la última vuelta |

Un rechazo abre `IT<n+1>` con los cambios pedidos citados tal cual. Así lo
que dijo cada agente sobrevive a un `/clear`, y el número de carpetas es el
número de intentos.

**Dónde está cada cosa:**

| Qué | Dónde |
|---|---|
| Qué es, alcance, features, estado, pendiente, lecciones | `docs/proyecto.md` |
| Aspectos clave, arquitectura, supuestos de riesgo, restricciones | `docs/arquitectura.md` |
| Stack y librerías aprobadas | `docs/stack.md` |
| Diseño visual y tokens | `docs/diseno.md` (los tokens, en el código) |
| Proceso del proyecto: specs, pruebas, zonas críticas, revisiones, ramas | `docs/proceso.md` |
| Convenciones del lenguaje y del código | `docs/convenciones.md` |
| Riesgos propios y lista de seguridad | `docs/seguridad.md` |
| Comandos y lo que rompe cosas | `CLAUDE.md` (lo genera `/arranque`; se carga siempre) |
| Spec de una feature | `specs/FNN-<nombre>.md`, desde `specs/_plantilla.md` |
| Iteraciones | `progress/FNN/IT<n>/` |
| Investigaciones a fondo | `docs/investigaciones/<tema>.md` |
| Auditorías y retrospectivas | `docs/auditorias/`, `docs/retrospectiva-<fecha>.md` |

El detalle del ciclo, con el incidente que motivó cada paso, está en
`.claude/forma-de-trabajo.md`.

## Agentes

| Agente | Qué hace | Modelo · `effort` · `maxTurns` | Skills precargadas (si están instaladas) |
|---|---|---|---|
| sesión principal | el arranque, las specs, lanzar los agentes, los arreglos pequeños, mantener `docs/proyecto.md` | el de la sesión | — |
| `explorer` | busca un hecho (una librería, un límite, cómo está hecho algo) con su fuente y su fecha | sonnet · low · 60 | — |
| `implementer` | construye la feature o el tramo, con pruebas y capturas | opus · medium · 200 | `ponytail`, `property-based-testing`, `migration`, `surgical-patch`, `make-interfaces-feel-better`, `web-design-guidelines` |
| `reviewer` | revisión funcional con contexto limpio; nunca edita código | opus · medium · 100 | `property-based-testing`, `web-design-guidelines`, `ponytail-review` |
| `security_reviewer` | seguridad de la feature entera, al final y tras el `APPROVED` del reviewer; también audita el repositorio | opus · medium · 100 | `differential-review` (e invoca `supply-chain-risk-auditor`, `variant-analysis` y `sharp-edges` cuando toca) |

Opus en quien construye y revisa porque lo caro son las vueltas de más,
no el precio por token. Opus cuesta el doble que Sonnet en entrada y
salida, pero lo mismo en lectura de caché, que es la mayor parte del
volumen de un implementer. Por eso cada ejecución sale entre 1,3 y 1,5
veces más cara, y una vuelta evitada por feature lo compensa. En la prueba
mínima (Opus), el reviewer aprobó 5 de 7 revisiones; en el piloto
(Sonnet), 47 de 96. Es un indicio, no una prueba, porque también cambiaron
las reglas. Con suscripción, la diferencia se nota en la cuota, no en
dólares. El `effort` va fijo para que los agentes no hereden el de la
sesión; la sesión principal lo sube a `high` en las revisiones de zonas
críticas y en la auditoría (el implementer se queda en `medium`). El implementer no carga las herramientas que no usa
(`disallowedTools`): con todas arrancaba con el doble de contexto que un
revisor. `maxTurns` pone tope al
gasto: si un agente llega a él, se reanuda; el número no se sube a
ciegas.

**Por qué ya no hay `spec_author` ni `leader`.** Un subagente no puede
esperar a que respondas: el `spec_author` acababa devolviendo preguntas y
había que reanudarlo. Por eso las specs las escribe la sesión principal
contigo. El `leader` era la sesión principal con un script (`state.py`) que
calculaba el siguiente paso. Ahora el estado vive en `docs/proyecto.md` y
en las carpetas `IT<n>`.

## Hooks

Vienen en `.claude/hooks/` y se activan desde `.claude/settings.json`. Son
ideas de [ECC](https://github.com/affaan-m/ECC) (config-protection,
block-no-verify y safety-guard), adoptadas tras el piloto.

| Hook | Cuándo | Qué hace |
|---|---|---|
| `guard_shell.py` | antes de cada comando de terminal | **bloquea** leer un `.env` (salvo `.env.example`), volcar el entorno o expandir un secreto (los nombres los toma de `.env.example`); saltarse los hooks de git; reescribir la historia; descartar cambios sin commitear; matar procesos por nombre |
| `guard_config.py` | antes de editar | **pregunta** antes de tocar la configuración de lint, formato, tipos o tests, o la del propio harness |

Cada regla viene de un incidente. *Un `taskkill /IM node.exe` mató todos
los `node` de la máquina; "restaurar de HEAD" para deshacer un sabotaje
borró el trabajo de varias iteraciones; un agente atascado en un check
relajaba la regla en vez de arreglar el código.* Si un bloqueo sobra, el
comando lo ejecutas tú.

## Skills del harness

Vienen en `.claude/skills/`. Las usa la sesión principal.

| Skill | Cuándo |
|---|---|
| `/arranque` | al empezar, o para revisar una fase |
| `entrevista` | el método de preguntas del arranque y de las specs. También sirve sola: "entrevístame sobre X" |
| `/direccion-visual` | fase 6 del arranque, o para rediseñar |
| `/auditoria-seguridad` | cada 4 features o al cerrar una fase, con tu sí (es cara) |
| `/retrospectiva` | al terminar o al cerrar una fase |

`entrevista` es una adaptación de
[`grill-me`](https://github.com/mattpocock/skills) de Matt Pocock (MIT).
Toma su árbol de decisiones por rondas y le añade lo que salió de las
pruebas: un tope de 4 preguntas por ronda, cómo tratar "no lo sé" y que
nada se investigue con coste sin tu sí.

## Skills opcionales

Ninguna es obligatoria. Instálalas en `~/.claude/skills/<nombre>/` (o como
plugin) **después de leerlas**: una skill son instrucciones que el agente
sigue con tus permisos. `skillOverrides` de `.claude/settings.json` las deja
en `name-only`, que recorta el listado de skills en cada turno sin romper
la precarga.

| Skill | Origen y licencia | Dónde se usa | Qué se vio en las pruebas |
|---|---|---|---|
| `web-design-guidelines` | [vercel-labs/web-interface-guidelines](https://github.com/vercel-labs/web-interface-guidelines), MIT | `implementer`, `reviewer` | el reviewer la usó como lista objetiva y encontró fallos reales (un hover sin limitar a puntero fino) |
| `ponytail:ponytail-review` | plugin [ponytail](https://github.com/DietrichGebert/ponytail), MIT | `reviewer` | dejó su `## Sobra` en todas las revisiones; casi siempre "nada que quitar", sin bloquear |
| `property-based-testing` | [trailofbits/skills](https://github.com/trailofbits/skills), CC BY-SA 4.0 | `implementer`, `reviewer` | el reviewer la usó para juzgar propiedades (formato de ids en los bordes) |
| `differential-review`, `supply-chain-risk-auditor`, `variant-analysis`, `sharp-edges` | trailofbits/skills, CC BY-SA 4.0 | `security_reviewer` | el security_reviewer las consideró por regla, pero en la prueba no hizo falta invocarlas (sin cambios de lockfile ni hallazgos que rastrear); de `differential-review`, precargada, no hay rastro medible |
| `ponytail:ponytail` | plugin ponytail, MIT | `implementer` | sin rastro medible: las precargadas no dejan huella en los ficheros |
| `migration`, `surgical-patch`, `investigate-first` | skills de usuario (origen sin registrar) | `implementer`; `investigate-first`, la sesión principal | sin rastro medible |
| `make-interfaces-feel-better` | affaan-m/ECC, MIT | `implementer` | sin rastro medible |
| `frontend-design` | plugin oficial de Anthropic | `/direccion-visual` sin Stitch | las tres miniaturas HTML |
| `ui-ux-pro-max`, `pick-ui-library`, `redesign-existing-projects` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), [emilkowalski/skills](https://github.com/emilkowalski/skills), [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill); MIT | `/direccion-visual` | paletas, fuentes y elección de librerías de interfaz |
| `architecture-decision-records`, `council` | affaan-m/ECC, MIT | `/arranque` | ADR si los quieres; contraste cuando hay varias opciones buenas |
| `/deep-research` | workflow de serie de Claude Code | `/arranque` | investigación amplia con fuentes; es la más cara |
| `security-audit` | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill), MIT | `/auditoria-seguridad` | motor opcional, con muchos agentes |
| `insecure-defaults` | trailofbits/skills, CC BY-SA 4.0 | `/auditoria-seguridad` | configuraciones inseguras por defecto |
| `spec-to-code-compliance`, `ponytail:ponytail-audit` | trailofbits/skills; ponytail | `/retrospectiva` | código frente a specs; sobreingeniería |
| `prd-securability-enhancement` | [OWASP/secure-agent-playbook](https://github.com/OWASP/secure-agent-playbook), CC BY 4.0 | specs, si hay usuarios o servidor | la propone el arranque |
| `vercel-react-best-practices`, `vercel-composition-patterns`, `vercel-react-view-transitions` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills), MIT | `implementer`, si el stack es React | las propone el arranque |
| `modern-python` | trailofbits/skills, CC BY-SA 4.0 | `implementer`, si el stack es Python | la propone el arranque |
| `grill-me` | [mattpocock/skills](https://github.com/mattpocock/skills), MIT | — | base de `entrevista`; no hace falta instalarla |
| `engineering:tech-debt`, `engineering:deploy-checklist` | plugin Engineering de Anthropic ([anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins), Apache-2.0) | `/retrospectiva`; antes de desplegar en producción | sin probar. `tech-debt` clasifica y prioriza la deuda mejor que la fórmula sola; `deploy-checklist` completa nuestros puntos de despliegue |
| `engineering:architecture`, `engineering:system-design`, `engineering:debug` | el mismo plugin | fase 4 del arranque; fallos sin causa clara | sin probar; equivalen a `architecture-decision-records`, `catalogo.md` e `investigate-first` |

**Sobre la evidencia**: las skills del `reviewer` y del
`security_reviewer` dejaron rastro en sus veredictos, así que se sabe que
se usaron. De las precargadas del `implementer` no hay forma de saberlo con
lo medido: no se invocan, se inyectan. Siguen porque no costaron
problemas. La `/retrospectiva` las revisa.

**ponytail**: su hook se inyecta en todos los subagentes. La variable
`PONYTAIL_SUBAGENT_MATCHER` de `.claude/settings.json` lo excluye de los
agentes del harness, que lo llevan precargado donde toca. *Antes se colaba
en los revisores.* Si no usas ponytail, la variable no hace nada.

**Revisión de la configuración de `.claude/`**, de vez en cuando:
`npx ecc-agentshield@<versión fijada> scan`
([AgentShield](https://github.com/affaan-m/agentshield), MIT). Ejecuta código
descargado: fija una versión con más de 7 días.

El plugin Engineering se instala con `claude plugin marketplace add
anthropics/knowledge-work-plugins` y `claude plugin install
engineering@knowledge-work-plugins`. Sus otras skills (`code-review`,
`testing-strategy`, `documentation`, `incident-response`, `standup`) no las
usa el harness: solapan con los revisores y la fase 7, o quedan fuera del
flujo.

**Herramientas externas** para `/direccion-visual`: tus referencias pueden
salir de [Refero](https://refero.design/), [Mobbin](https://mobbin.com/) o
apps que uses. Las tres direcciones se generan a mano en
[Google Stitch](https://stitch.withgoogle.com/) (gratis con cuenta de
Google). Sin Stitch, Claude hace miniaturas HTML.

## Recomendaciones

Recopiladas en las pruebas. El incidente que motivó cada una está en
`.claude/forma-de-trabajo.md`.

**Proceso**

- Requisitos antes que tecnología, y el alcance antes que el stack.
- La primera feature es el andamiaje y comprueba los supuestos de riesgo
  antes de escribir producto.
- Spec corta (~400 líneas como mucho); lo ambiguo se pregunta antes de
  redactar.
- La aprobación es un sí explícito, pero se dice qué frase vale y se
  repregunta solo lo que falta.
- Como mucho dos tramos por feature (lógica y datos, después interfaz).
- Quien implementa no se aprueba. La revisión de seguridad va al final y
  solo tras el `APPROVED` funcional.
- Visto bueno visual del humano antes de cerrar una feature con pantallas.
- Ampliar el alcance o arreglar algo cerrado es una feature nueva. Una spec
  aprobada no se reescribe: se enmienda con fecha.
- Una vuelta que deja de tener sentido se descarta con un `descartada.md`;
  no se borra.
- Un cambio de decisión de base para la feature y vuelve al arranque.
- La prueba con servicios reales la revisa el reviewer en la primera vuelta
  y la ejecuta el humano al final.
- Lo que falla o estorba lo apunta Claude, sin que se lo pidas, en
  "Lecciones"; los cambios en la forma de trabajo, con su fecha y su
  motivo.
- "Para" significa parar. Se avisa del coste cuando es alto.
- En equipo, una rama o worktree por feature.
- Tras el commit, se actualizan "Estado actual" y "Pendiente", y se propone
  `/clear`.
- Auditoría completa cada 4 features o al cerrar una fase; retrospectiva al
  final, con la deuda ordenada por (impacto + riesgo) × (6 − esfuerzo).
- En producción: diagrama de componentes y estimación de carga en el
  arranque, y antes de cada despliegue, la vuelta atrás decidida de
  antemano.
- Cada vuelta, con el modelo que necesita: `opus` para construir y revisar
  a fondo, `sonnet` para las revisiones acotadas y las correcciones
  pequeñas, `haiku` para lo mecánico.

**Agentes**

- Encargo con el contexto mínimo suficiente; las hipótesis, marcadas como
  tales; las reglas que cambiaron en la sesión, repetidas.
- Un agente que corta se reanuda con `SendMessage`, como mucho dos veces;
  no se lanza otro.
- Cada agente en su propia carpeta temporal. Los procesos se matan por su
  PID, nunca por nombre.
- Copias de trabajo sin enlaces a `node_modules` o `.venv`. Nunca
  "restaurar de HEAD" para deshacer un sabotaje.

**Pruebas**

- Un test vale si cae con el código roto (se rompe la línea, se ve caer, se
  restaura).
- Mutantes solo en zonas críticas, con el mismo comando para quien
  implementa y quien revisa.
- Los límites se comparan con la spec, no con la constante del código. Los
  dobles de prueba respetan los límites reales, y el adaptador real tiene
  sus propios tests.
- Lo que no se puede verificar con tests se dice y se comprueba a mano con
  un protocolo; nunca se da por verificado.
- Los tests intermitentes se arreglan, no se anotan.
- Un solo comando verifica todo, y se demuestra que cada paso sabe fallar.
- En Windows, `cosmic-ray` en lugar de `mutmut`, y Stryker con
  `--concurrency 2`.

**Interfaz**

- Profesional antes que original: referencias reales tuyas y tres
  direcciones para elegir.
- Se decide qué pantallas y qué plataforma van primero antes de generar
  las direcciones.
- Tokens en un único sitio, sin valores sueltos; movimiento, solo el que
  fija el diseño.
- Capturas de lo construido (claro y oscuro, escritorio y móvil, normal y
  peor caso) con un navegador aislado.
- Nunca un spinner sin explicar; un solo envío a la vez; respuestas de la
  API parseadas de forma estricta (más en `docs/convenciones.md`).

**Código y seguridad**

- Nativo antes que dependencia. Regla de tres. Se parsea en el borde. Nunca
  tragarse un error.
- Atajos marcados con `ATAJO: <límite> · <camino de mejora>`.
- Los secretos no pasan por el contexto. Uno que llega al chat, a un log o
  a un commit se rota, y conviene un escáner antes del primer push.
- El atacante no usa tu interfaz: autorización por objeto y por función,
  entrada validada en el borde, topes de consumo (lista completa en
  `docs/seguridad.md`).
- Cada diseño responde a las cuatro preguntas de escalabilidad: sin estado,
  índices, límites acotados, sin N+1.
- Nada destructivo sobre datos reales. Se avisa antes de tocar servicios
  reales y de su coste.
- Lo que se sabe de fuera, con su fuente y su fecha.

## Ficheros

```
CLAUDE.md                          el del proyecto; lo genera /arranque (en la plantilla, solo un aviso)
.claude/rules/harness.md           la forma de trabajo y las reglas duras; Claude lo carga siempre
README.md                          esto
.claude/settings.json              permisos (secretos, commits, dependencias), hooks y skillOverrides
.claude/hooks/                     guard_shell.py, guard_config.py y su lanzador py.sh
.claude/agents/                    explorer, implementer, reviewer, security_reviewer
.claude/skills/arranque/           la entrevista inicial y catalogo.md
.claude/skills/entrevista/         el método de preguntas
.claude/skills/direccion-visual/   el diseño visual
.claude/skills/auditoria-seguridad/
.claude/skills/retrospectiva/
.claude/forma-de-trabajo.md        cómo se construye, con el porqué de cada paso (de la plantilla)
docs/proyecto.md                   plantilla: qué es, alcance, features, estado, lecciones
docs/arquitectura.md               plantilla: aspectos clave, forma, supuestos, restricciones
docs/stack.md                      plantilla: stack y librerías aprobadas
docs/proceso.md                    plantilla: specs, pruebas, revisiones y ramas del proyecto
docs/convenciones.md               plantilla: convenciones del lenguaje y del código, interfaz web
docs/seguridad.md                  plantilla: lista de seguridad y riesgos propios
specs/_plantilla.md                esqueleto de una spec
```

## De dónde sale

- **Piloto** (proyecto real de tamaño medio: backend, worker y web, 18
  features). Se usaba un harness con siete agentes, un script que decidía
  el siguiente paso, hooks, tests del propio harness y CI. De ahí salen
  casi todas las lecciones: 42 de 44 primeras entregas rechazadas por
  criterios de test distintos, 47 pasadas de seguridad para 2 rechazos, y
  specs de miles de líneas.
- **Prueba mínima** (un contador de hábitos para una persona, tres
  features). Con el mismo harness se escribieron 742 líneas de producto,
  frente a unas 2.900 de specs y seguimiento y unas 4.200 de maquinaria del
  harness. Casi todas las incidencias venían del propio harness (un
  documento que se desfasaba, rituales de aprobación). Lo que sí aportó
  valor fue el bucle de construir y revisar en contexto limpio, los
  mutantes en la zona crítica, la revisión de seguridad (pilló una
  validación de coste cuadrático) y la dirección visual con referencias.
- **Esta plantilla** se queda con eso y con las lecciones, y quita la
  maquinaria. El harness anterior está en el historial de git (commit
  `8cf22b5` y anteriores) por si hay que recuperar alguna pieza.
