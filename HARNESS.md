# Harness SDD para desarrollo con agentes — guía completa

Documento autocontenido para montar, en un proyecto nuevo, la forma de
trabajar que se probó en un proyecto real (≈10 features, ≈30 iteraciones,
frontend + backend + worker + servicios en la nube). Es **agnóstico de
lenguaje y tecnología**: lo que depende del proyecto está marcado como
**`<RELLENAR>`** y reunido en la sección 1 y en el Anexo C.

Cómo usarlo:
- **Humano:** lee la sección 0 y sigue la checklist de la sección 1.
- **Claude en el proyecto nuevo:** "Monta el harness siguiendo HARNESS.md".
  Los ficheros listos para copiar están en esta misma carpeta
  (`harness-sdd-template/`); lo que aquí aparece en el Anexo B son las
  plantillas de texto.

---

## Índice

0. Qué es y por qué funciona
1. Checklist de arranque (lo que falta rellenar)
2. Estructura del repositorio
3. Roles
4. El proceso SDD
5. Tabla de despacho y ciclo de iteraciones
6. Verificación
7. Seguridad (baseline)
8. Principios de programación
9. Patrones de diseño
10. Patrones de arquitectura, integración y datos
11. Antipatrones
12. Escalabilidad y límites
13. Git, ramas y despliegue
14. Pruebas con servicios reales (runbooks para el humano)
15. Coste y tokens
16. Lecciones aprendidas (catálogo)
- Anexo A: ficheros de la carpeta plantilla
- Anexo B: plantillas de texto (CLAUDE.md, AGENTS.md, CHECKPOINTS.md, specs, conventions, progress)
- Anexo C: decisiones pendientes en un proyecto nuevo

---

## 0. Qué es y por qué funciona

Un **harness** es el andamiaje que convierte "un agente que escribe código"
en "un equipo con puertas de calidad". Seis roles, un proceso con aprobación
humana, verificación ejecutable y un estado derivado del disco.

Ideas que lo sostienen:

1. **Nada se declara hecho: se demuestra.** `init.sh` (tests, lint, formato,
   tipos, build, secretos, dependencias) es la puerta. Que un agente diga
   "funciona" no cuenta.
2. **Quien escribe no aprueba.** El `implementer` escribe; el `reviewer` y
   el `security_reviewer` vetan por separado. Ambos `APPROVED` en la misma
   iteración, o no hay `done`.
3. **Humano en la puerta de diseño.** Ninguna feature pasa de spec a
   implementación sin aprobación humana. Es el único punto obligatorio.
4. **Estado derivado, no mantenido.** `scripts/state.py` calcula qué toca a
   partir de `feature_list.json` y de las carpetas `progress/<F>/IT<n>/`.
   No hay contadores ni campos que sincronizar.
5. **Historial inmutable.** Cada iteración es una carpeta nueva. No se
   reescriben veredictos ni evidencias pasadas; las correcciones se anexan.
6. **Divulgación progresiva.** `AGENTS.md` es un mapa; cada rol lee solo lo
   que necesita (el `conventions.md` de *su* stack, no todos).
7. **Presupuestos con honestidad.** Informes ≤ 200 líneas; lo largo va a
   `evidence.md`. **Una prueba no se borra por presupuesto, se mueve.**
8. **Defensa en profundidad para secretos**: permisos, hook, pre-commit, CI.
9. **Las lecciones se convierten en reglas o en tests**, no en recuerdos.

---

## 1. Checklist de arranque

Orden recomendado. Cada `<RELLENAR>` se decide aquí o se registra en el
Anexo C si aún no se sabe.

1. **Copiar** la carpeta `harness-sdd-template/` como raíz del repo nuevo y
   `git init`.
2. **`harness.json`**: `proyecto`, `scopes` (nombres de carpeta de cada
   stack, p. ej. `backend`, `frontend`, `worker`) y `secretos` (nombres de
   las variables secretas; ver sección 7).
3. **`CLAUDE.md`** desde el Anexo B.1: qué es el proyecto, **tabla "dónde
   vive cada pieza y por qué"**, restricciones que rompen cosas,
   prohibiciones, estructura, estado.
4. **`AGENTS.md`** y **`CHECKPOINTS.md`** desde el Anexo B.2 y B.3, con los
   checkpoints propios del proyecto.
5. **`docs/`**: crear estos ficheros copiando las secciones de este
   documento:
   | Fichero | Sección de este documento |
   |---|---|
   | `docs/specs.md` | 4 |
   | `docs/verification.md` | 6 y 14 |
   | `docs/security.md` | 7 + riesgos propios del proyecto `<RELLENAR>` |
   | `docs/principios.md` | 8, 9, 10, 11 |
   | `docs/architecture.md` | 12 + arquitectura propia `<RELLENAR>` |
   | `docs/<stack>/conventions.md` | Anexo B.5, uno por stack `<RELLENAR>` |
6. **Stacks**: por cada scope, crear `<scope>/` con su andamiaje y su
   `init.sh` a partir de `plantillas/stack/init.sh`. **Demostrar que cada
   paso sabe fallar** (sección 6.2). Versionar con `+x`.
7. **`.gitleaks.toml`**: una regla por cada secreto con formato reconocible.
8. **CI** (`.github/workflows/ci.yml`): añadir las toolchains de cada stack
   con versión fijada.
9. **Hooks**: `git config core.hooksPath .githooks` (una vez por clon;
   documentarlo en el README).
10. **`feature_list.json`**: features en orden de prioridad (el orden **es**
    la prioridad). La primera, la más pequeña que atraviese la arquitectura
    de punta a punta. Agrupar por fases si hay dependencias (p. ej. "backend
    antes que frontend").
11. **`progress/current.md`** y **`progress/history.md`** vacíos (Anexo B.7).
12. `python -m pytest tests/` y `./init.sh --all` en verde. Primer commit.
13. Arrancar Claude Code en el repo: actuará como `leader`.

---

## 2. Estructura del repositorio

```
.
├── CLAUDE.md                 rol de sesión, contexto, restricciones, prohibiciones
├── AGENTS.md                 mapa: dónde está cada regla (no contiene reglas)
├── CHECKPOINTS.md            criterios de "done", cada bloque con un único dueño
├── harness.json              proyecto, scopes, nombres de secretos
├── feature_list.json         features: id, title, status, sdd, scope, acceptance
├── init.sh                   dispatcher: verifica el scope activo (o --all)
├── .gitleaks.toml            escáner de secretos (config única, raíz)
├── .githooks/pre-commit      gitleaks sobre el índice, falla cerrado
├── .github/workflows/ci.yml  historia de secretos + tests del harness + init.sh
├── .claude/
│   ├── settings.json         deny de .env, hook de sesión, hook guard_secrets
│   └── agents/               leader, spec_author, explorer, implementer,
│                             reviewer, security_reviewer
├── scripts/
│   ├── state.py              tabla de despacho (qué toca ahora)
│   ├── session_start.sh      muestra estado + current.md + última IT
│   └── guard_secrets.py      bloquea comandos de shell que sacan secretos
├── tests/                    tests DEL HARNESS (no del producto)
├── docs/                     reglas que leen los agentes
├── specs/<F>/                requirements.md, design.md, tasks.md
├── progress/
│   ├── current.md            estado vivo de la sesión, pendientes del humano
│   ├── history.md            bitácora append-only de features cerradas
│   ├── explore_<tema>.md     salidas del explorer
│   └── <F>/IT<n>/            impl.md, review.md, security.md, evidence.md
└── <scope>/                  cada stack con su init.sh y su código
```

`feature_list.json` — estados: `pending → spec_ready → in_progress → done`.
**Sin contador de intentos**: el número de carpetas `IT<n>` ya lo es.
Editarlo **como texto** (un serializador lo reformatea entero).

---

## 3. Roles

| Rol | Modelo | Escribe | Nunca |
|---|---|---|---|
| `leader` | sonnet | carpetas `IT<n>`, encargos | código, specs, `done` |
| `spec_author` | opus | `specs/<F>/` | código, tests |
| `explorer` | sonnet (opus en fronteras de arquitectura) | `progress/explore_*.md` | código, specs, decisiones |
| `implementer` | sonnet | código, tests, `impl.md`, `evidence.md` | autoaprobarse |
| `reviewer` | opus | `review.md` | editar código |
| `security_reviewer` | opus | `security.md` | editar código |

Por qué esos modelos: el que más produce (implementer) es el más barato; las
puertas (spec, vetos) usan el más capaz, porque sus fallos se propagan.

Reglas transversales:
- **Los revisores no pueden abrir subagentes** (test en `test_settings.py`):
  cierra la única vía por la que el gasto se multiplica sin control.
- **Cada checkpoint tiene un único dueño**: dos agentes no se contradicen.
- **`docs/` y las reglas del harness las decide el humano**; los agentes
  sugieren.

Las definiciones completas están en `.claude/agents/*.md` de la plantilla.

---

## 4. El proceso SDD (→ `docs/specs.md`)

Ninguna feature se implementa sin spec escrita y aprobada.

### 4.1 Los tres ficheros

**`requirements.md` — el qué.** Notación EARS, `R1`, `R2`…, comportamiento
observable, nunca implementación:

| Forma | Plantilla |
|---|---|
| Ubicua | *El sistema DEBE `<respuesta>`* |
| Evento | *CUANDO `<disparador>`, el sistema DEBE `<respuesta>`* |
| Estado | *MIENTRAS `<estado>`, el sistema DEBE `<respuesta>`* |
| No deseada | *SI `<condición>`, ENTONCES el sistema DEBE `<respuesta>`* |
| Opcional | *DONDE `<característica>`, el sistema DEBE `<respuesta>`* |

"Debe ser rápido" no es un requisito; "DEBE responder en < 500 ms con 1.000
elementos" sí. Un requisito que no se puede convertir en test es un deseo.

**`design.md` — el cómo.** Ficheros y firmas; **alternativas descartadas y
por qué**; las cuatro preguntas de escalabilidad (sección 12); decisiones
para el humano **con recomendación**; sección vacía **"Desviaciones
aprobadas"** donde el implementer *anexa* (nunca sobrescribe).

**`tasks.md` — los pasos.** `T1`, `T2`… discretas, con sus `R<n>`.
**Concisa**: no repite design (se relee en cada iteración). La última task,
si hay servicios reales, es la **prueba humana** (sección 14).

### 4.2 Seguridad obligatoria en la spec

Si la feature toca input, auth, datos sensibles o acceso a datos, lleva
`R<n>` de seguridad verificables por test **aunque el acceptance no los
pida**. Lo que no está en la spec no lo audita nadie.

### 4.3 La puerta humana

```
pending ──spec_author──> spec_ready ──HUMANO──> in_progress ──vetos──> done
```

El leader resume la spec al humano: qué hace, **decisiones abiertas con
recomendación**, dependencias nuevas a aprobar, coste/servicios reales
implicados. Las respuestas del humano se registran en design.md como
"Decisiones del humano (fecha)".

### 4.4 Iteraciones y cierre

- Cada vuelta vive en `progress/<F>/IT<n>/`. La crea el leader.
- `CHANGES_REQUESTED` → nueva `IT<n+1>` con los cambios pedidos.
- **Correcciones de texto al cerrar**: si el único problema es texto en
  `specs/`/`progress/`, el reviewer aprueba y lista cada corrección literal
  (fichero, línea, actual → nuevo). El implementer las aplica en el cierre.
  Ahorra una iteración completa por una frase. **Nunca** para código, tests,
  dependencias, seguridad.
- **Cierre (paso 8)**: con `review.md` y `security.md` `APPROVED` en la
  misma IT: aplicar correcciones de texto, marcar la task humana, `done` en
  `feature_list.json`, anexar a `history.md` (resumen **redactado por el
  leader**), actualizar `current.md`.
- **Hotfix de una feature ya `done`**: nueva `IT<n>` en su carpeta, mismo
  ciclo implementer → reviewer → security_reviewer. No se reabre el estado.

---

## 5. Tabla de despacho y ciclo

`python scripts/state.py` devuelve `{feature, status, scope, iteration, action}`:

| `action` | Acción del leader |
|---|---|
| `LANZAR_SPEC_AUTHOR` | spec_author sobre la feature |
| `PEDIR_APROBACION_HUMANA` | parar y presentar la spec |
| `CREAR_IT1_Y_LANZAR_IMPLEMENTER` | crear `IT1`, implementer |
| `LANZAR_IMPLEMENTER_EN_IT<n>` | IT sin `impl.md` (sesión cortada): implementer ahí |
| `LANZAR_REVIEWER` | reviewer sobre `IT<n>` |
| `LANZAR_SECURITY_REVIEWER` | security_reviewer sobre la misma `IT<n>` |
| `CREAR_IT<n>_LANZAR_IMPLEMENTER_LUEGO_REVIEWER` | nueva IT tras rechazo funcional |
| `CREAR_IT<n>_…_LUEGO_REVIEWER_Y_SECURITY` | tras rechazo de seguridad: re-verifican **ambos** |
| `LANZAR_IMPLEMENTER_PASO_8_MARCAR_DONE` | cierre |
| `TODO_HECHO` | nada pendiente |

---

## 6. Verificación (→ `docs/verification.md`)

### 6.1 `init.sh` es la puerta

```
./init.sh            scope de la feature activa
./init.sh --all      todos los scopes de harness.json
./init.sh --dry-run  solo anuncia el scope
```

El raíz delega en `<scope>/init.sh`. **Un scope sin `init.sh` bloquea**, no
se salta (saltarlo sería un "OK" falso). Cada stack cubre, fallando a la
primera: **tests · lint · formato · tipos · build · secretos · auditoría de
dependencias**. `<RELLENAR>` herramientas por stack.

### 6.2 Un verificador tiene que saber fallar

Tras escribir cada paso, **plantar un fallo a propósito** y comprobar que el
código de salida no es 0. Casos reales de "falso verde":
- un comprobador de tipos que, con cierta configuración, no comprobaba nada;
- un test que comparaba un literal que el código ya no usaba;
- un arnés de test que pisaba con un literal el valor que decía proteger.

### 6.3 TDD y mutantes

- Test primero; **verlo fallar sobre el código real** (no con un script que
  imita el código viejo); implementar; verlo pasar. Salida roja **literal**
  en `evidence.md`.
- **Mutantes**: el reviewer rompe el código en una copia temporal (quitar un
  filtro, invertir una condición, volver a un cálculo anterior, relajar una
  validación) y exige que algún test caiga. Mutante que sobrevive = test que
  falta.
- **Revertir solo la línea de producción** para demostrar que el test la
  protege. Si hace falta revertir también el test o el arnés, el test no
  protegía nada.

### 6.4 Dobles de test

- **El doble prueba al llamador, no al adaptador.** Todo método nuevo de un
  adaptador real (repositorio, cliente HTTP, almacenamiento) lleva test
  propio con un **cliente grabador** que comprueba filtros exactos, valores
  escritos y cada rama de lectura (sin datos, nulo, válido).
- **Un falso que devuelve respuestas fijas sin mirar la petición puede
  validar un bug.** Si el código pagina o lee por bloques, el falso respeta
  el rango pedido y los límites reales del servicio (máximo de filas por
  respuesta, etc.).
- El arnés restaura el estado del módulo al **valor inicial capturado tras
  el import**, nunca a un literal copiado.
- Lo que compara contra un servicio usa **la forma que el servicio
  devuelve**, no la que escribiste (p. ej. un motor SQL entrecomilla
  palabras clave al reescribir una definición: comparar por catálogo).

### 6.5 Trazabilidad y presupuestos

- `impl.md` trae la tabla completa `R<n> → test` (fichero y nombre).
- `impl.md`, `review.md`, `security.md` ≤ 200 líneas; citas
  (`archivo:línea`), no volcados; lo largo a `evidence.md`.
- **El leader no abre `evidence.md`.** Los revisores solo para cuestionar
  una prueba concreta.
- En iteraciones `n > 1` se reduce el **contexto**, nunca el trabajo:
  `init.sh` completo y checkpoints uno a uno en cada vuelta.

### 6.6 Portabilidad local ↔ CI

El autor puede trabajar en Windows/macOS y el CI corre en Linux:
- **Bit de ejecución**: `git update-index --chmod=+x <fichero>.sh` (test en
  `test_settings.py`). Llamar a los scripts con `bash script.sh` además.
- **Finales de línea**: `.gitattributes` con `*.sh text eol=lf`.
- **Intérprete**: `sys.executable` en tests; en shell, probar candidatos
  (`python`, `python3`, `py`) **ejecutándolos**, no solo mirando el PATH.
- **Relojes monotónicos** empiezan cerca de 0 en una máquina recién
  arrancada: el estado inicial de "última vez" es `-inf`, no `0`.
- Si solo falla en el CI, sospechar primero de estas cuatro.

### 6.7 Lo que no se puede verificar con tests

Se dice explícitamente en el veredicto y se verifica a mano con un
protocolo escrito y resultado registrado (p. ej. comportamiento en un
dispositivo físico). Nunca se declara verificado sin más.

---

## 7. Seguridad — baseline (→ `docs/security.md`)

### 7.1 Secretos: cuatro capas

1. **Permisos** (`.claude/settings.json`): `deny` de Read/Edit sobre `.env*`,
   `*.pem`, `*.key`.
2. **Hook `guard_secrets.py`**: bloquea comandos de shell que leen `.env`,
   expanden un secreto (`$X`, `$env:X`, `%X%`, `os.environ`, `process.env`)
   o vuelcan el entorno (`env`, `printenv`, `set`, `gci env:`).
3. **Pre-commit** con gitleaks sobre el índice, **falla cerrado**.
4. **CI** escanea la historia completa.

Reglas:
- Los secretos **no pasan por el contexto de un agente**: no se leen, no se
  imprimen, no se pegan en el chat. Un secreto en el contexto puede acabar en
  un log, un veredicto o un commit.
- Viven solo donde se usan: panel de variables del servicio, variables de
  usuario del SO del equipo que los necesita. **Nunca** en ficheros del repo.
  **Mínimo privilegio**: cada máquina solo con los que necesita.
- `.env.example` documenta nombres y formato, sin valores.
- Generar tokens con un CSPRNG, sin que el valor pase por pantalla.
- Si un secreto o token acaba en el chat/log: rotarlo (o, si caduca pronto,
  al menos no reutilizarlo e invalidar la sesión).
- Todo lo que llega al cliente (bundle web, app) es **público**: solo
  valores públicos por diseño, lista cerrada, y el build falla ante
  cualquier otro.

### 7.2 OWASP como mapa

Estándar mínimo: **OWASP API Security Top 10** (y el Top 10 web si hay
interfaz web). `<RELLENAR>` en `docs/security.md` una tabla "categoría →
dónde aparece en este proyecto" y los **riesgos propios ordenados por
gravedad**.

### 7.3 Lo que el security_reviewer revisa a mano

- **Autorización por objeto (BOLA/IDOR):** cada consulta filtra por
  propietario **en la propia consulta**, no solo en la ruta. Un recurso
  ajeno responde **igual que uno inexistente** (mismo código, mismo cuerpo,
  mismo tiempo): no revelar existencia. Sin excepción "de admin" salvo que
  la spec la pida.
- **Autorización por función:** rutas de admin con su dependencia; 401/403
  antes que 422 (no validar el cuerpo de quien no puede llamar).
- **Asignación masiva:** los modelos de entrada rechazan campos extra; el
  propietario, roles y estados los pone el servidor, nunca el cuerpo.
- **Autenticación:** verificación de firma, algoritmo fijado, `aud`/`iss`/
  `exp`; roles solo de claims que el usuario no puede editar; tokens de
  máquina distintos de los de usuario y con alcance mínimo; comparación en
  tiempo constante.
- **Validación de input en el borde**: lista blanca (dominios, formatos),
  tipos estrictos, longitudes, sin caracteres de control.
- **SSRF**: nunca pasar una URL del usuario a un proceso que la resuelve;
  extraer el identificador y reconstruir la URL.
- **Consumo de recursos**: todo tiene tope (cuerpos, páginas, ficheros,
  duración, tasa por usuario).
- **Credenciales temporales** (URLs firmadas, tokens) **siempre caducan**.
- **Logs**: nunca tokens, URLs firmadas ni cuerpos con datos sensibles; los
  mensajes externos se sanean (saltos de línea y caracteres de control
  fuera, longitud máxima) para que no falsifiquen líneas.
- **Mensajes de error** al usuario sin rutas, consultas ni trazas.
- **CORS**: orígenes exactos desde configuración; `*`, comodines o entradas
  mal formadas → el servicio no arranca. Previews/entornos de prueba fuera.
- **Cabeceras y CSP** en la web; sin sumideros HTML inseguros; sesión en el
  cliente con su riesgo XSS documentado.
- **Base de datos**: consultas parametrizadas; RLS/permisos mínimos; las
  unicidades y carreras se resuelven con **constraints**, no con `if`.
- **Dependencias**: sin CVEs altos; cada paquete nuevo aprobado.
- **Registro público de usuarios**: desactivado si el grupo es cerrado, con
  prueba de humo de que se rechaza.

---

## 8. Principios de programación (→ `docs/principios.md`)

Guía, no dogma: cada uno lleva **cuándo no aplicarlo**. Ante conflicto, gana
el que produce el código más simple que cumple la spec y se deja verificar.

### 8.1 Simplicidad

- **YAGNI** — no construir lo que no pide una spec aprobada. *Ejemplo:* no
  añadir un modo depuración, latidos o notificaciones "por si acaso".
  *Excepción:* validación en fronteras de confianza y manejo de errores que
  evitan pérdida de datos no son especulativos.
- **KISS** — la solución más simple que funciona. Un sondeo periódico gana a
  un canal en tiempo real si nadie puede abrir conexiones hacia el cliente.
- **Menos es más / borrar antes que añadir** — el mejor código es el que no
  existe; quitar dependencias es una mejora.
- **Nativo antes que dependencia** — biblioteca estándar, capacidad nativa
  de la plataforma (constraint en la BD, elemento HTML), dependencia ya
  instalada; solo entonces una nueva, y aprobada.
- **Regla de tres** — no abstraer hasta el tercer uso real.

### 8.2 Diseño de módulos

- **SOLID**
  - **S — Responsabilidad única**: un módulo, un motivo para cambiar
    (ruta / acceso a datos / modelos separados). Señal de alarma: un nombre
    que necesita "y".
  - **O — Abierto/cerrado**: extender sin tocar lo estable; aislar lo que
    cambia (una librería frágil detrás de una interfaz).
  - **L — Sustitución de Liskov**: un doble o implementación alternativa
    cumple el mismo contrato (mismos errores, mismos límites).
  - **I — Segregación de interfaces**: interfaces pequeñas (dos métodos
    mejor que diez).
  - **D — Inversión de dependencias**: depender de abstracciones inyectadas
    (puertos), no de implementaciones concretas.
  *Cuándo no:* una interfaz con una única implementación y sin doble de test
  es ceremonia; créala cuando haya un segundo consumidor o un test que la
  necesite.
- **DRY** — una sola fuente de verdad para **conocimiento** (contratos,
  constantes de negocio, listas de secretos). *No* para código que se
  parece por casualidad: duplicar dos líneas es mejor que acoplar dos
  módulos. Aplicar con la regla de tres.
- **Separación de responsabilidades (SoC)** y **alta cohesión, bajo
  acoplamiento**.
- **Ley de Deméter** — hablar con vecinos directos, no con los vecinos de
  los vecinos.
- **Composición sobre herencia**.
- **Tell, don't ask** — pedir a un objeto que haga algo en lugar de
  consultarlo y decidir fuera.
- **Command–Query Separation (CQS)** — una función o cambia estado o
  devuelve datos, no ambas (salvo operaciones atómicas justificadas).
- **Principio de menor sorpresa** — nombres y comportamientos obvios.
- **Explícito mejor que implícito** — configuración, dependencias y efectos
  visibles.

### 8.3 Robustez

- **Fail fast** — validar configuración al arrancar; faltar una variable
  obligatoria aborta con un mensaje que nombra la variable (no su valor).
- **Validar en el borde, confiar dentro** — parsear a tipos del dominio en
  la entrada (*parse, don't validate*).
- **Hacer irrepresentables los estados ilegales** — tipos cerrados
  (enumeraciones, literales) para estados y motivos de error.
- **Inmutabilidad por defecto**.
- **Idempotencia** — reintentar una operación no duplica efectos (claves
  únicas, escrituras condicionales).
- **Concurrencia optimista** — escritura condicional (`UPDATE … WHERE
  estado = esperado`) en vez de leer-comprobar-escribir; el perdedor recibe
  un conflicto.
- **No tragarse errores** — capturar para manejar o relanzar; nunca un
  `except` vacío.
- **Errores con motivos cerrados** hacia fuera, detalle saneado hacia el
  log.

### 8.4 Seguridad como principio

- **Mínimo privilegio**, **defensa en profundidad**, **seguro por
  defecto** (cerrado salvo que se abra explícitamente), **fallar cerrado**
  (si el control no puede ejecutarse, se bloquea).

### 8.5 Proceso

- **TDD**, **"deja el campamento mejor"** (sin salirse del alcance de la
  task), **commits pequeños y atómicos**, **Conventional Commits**.
- **Pragmatismo documentado** — un atajo deliberado se marca en el código
  con su límite y su camino de mejora (p. ej. `# atajo: bloqueo global;
  por cuenta si importa el rendimiento`).

---

## 9. Patrones de diseño (→ `docs/principios.md`)

Usar un patrón cuando resuelve un problema presente, no para parecer
ordenado. Formato: **para qué · cuándo · cuándo no**.

### 9.1 Creacionales
- **Factory Method / proveedor** — construir la dependencia en un punto
  (p. ej. `get_store()` inyectado). *Cuándo:* la construcción depende de
  configuración o se sustituye en tests. *No:* para un `new` trivial.
- **Abstract Factory** — familias de objetos compatibles. Raro en apps
  pequeñas.
- **Builder** — objetos con muchos parámetros opcionales o construcción por
  pasos (peticiones, consultas).
- **Singleton (por proceso)** — un cliente compartido y seguro entre hilos
  (caché de un solo elemento). *No:* estado mutable global.
- **Prototype** — clonar configuraciones base. Raro.

### 9.2 Estructurales
- **Adapter** — envolver una librería externa con la interfaz propia (la
  pieza frágil queda en un fichero).
- **Facade** — una puerta simple a un subsistema complejo.
- **Decorator** — añadir comportamiento sin herencia (reintentos, caché,
  logging alrededor de una llamada).
- **Proxy** — control de acceso, carga diferida, caché.
- **Composite** — árboles parte-todo (menús, carpetas).
- **Bridge** — separar abstracción e implementación cuando ambas varían
  (p. ej. reproductor × backend de salida). Raro en apps pequeñas.
- **Flyweight** — compartir estado inmutable entre muchas instancias.

### 9.3 De comportamiento
- **Strategy** — algoritmos intercambiables detrás de una interfaz (el
  descargador real y el falso de test).
- **Observer / publicar-suscribir** — notificar cambios a interesados
  (notificaciones push, eventos de UI). *No:* si nadie puede abrir la
  conexión hacia el suscriptor; ahí, **sondeo**.
- **Command** — encapsular una acción (colas, deshacer, reintentos).
- **Chain of Responsibility** — cadena de comprobaciones que puede cortar
  (autenticación → autorización → validación).
- **Template Method** — esqueleto fijo con pasos variables.
- **State** — comportamiento según estado explícito (máquina de estados de
  un trabajo: `pending → approved → running → done/failed`).
- **Iterator** — recorrer sin exponer la estructura (paginación por
  bloques).
- **Mediator** — coordinar componentes sin que se conozcan (el `leader` del
  propio harness).
- **Memento** — guardar y restaurar estado.
- **Visitor** — operaciones sobre estructuras estables. Raro.

---

## 10. Patrones de arquitectura, integración y datos

### 10.1 Estilos
- **Monolito modular (por defecto)** — un proceso dividido en módulos que se
  llaman por funciones. **Un servicio nuevo carga con la prueba**: hay que
  justificar qué problema paga la latencia y el despliegue extra.
- **Capas** (presentación / aplicación / dominio / infraestructura).
- **Hexagonal / puertos y adaptadores** y **Clean Architecture** — el
  dominio no depende de frameworks; la infraestructura se enchufa.
- **Microservicios** — solo con equipos, escalado o ciclos de despliegue
  realmente independientes.
- **Event-driven**, **CQRS**, **Event Sourcing** — cuando el dominio lo
  pide; no por defecto.
- **Pipes and filters** — procesamiento por etapas.
- **Serverless / estático + API** — webs estáticas en CDN, API aparte.

### 10.2 Aplicación y datos
- **Repository** — la persistencia detrás de métodos con nombre de dominio.
- **Service layer** — casos de uso orquestando repositorios.
- **Unit of Work** — agrupar cambios en una transacción.
- **DTO** — modelos de entrada/salida separados de las filas; el de entrada
  rechaza campos extra.
- **Contratos compartidos** — una única definición para lo que cruza
  procesos (cliente y servidor la importan).
- **Anti-Corruption Layer** — traducir un sistema externo al lenguaje
  propio.
- **Paginación** — `limit + 1` para saber si hay más; `offset` acotado.
- **Escritura condicional / optimistic locking**, **claves de
  idempotencia**, **constraints únicos** para carreras.
- **Migraciones versionadas, nunca editadas**; una corrección es una
  migración nueva; cada migración con su verificación de solo lectura.

### 10.3 Integración y resiliencia
- **Polling vs push** — sondeo cuando el cliente no puede recibir
  conexiones; push/Observer cuando sí.
- **Reintento con backoff exponencial y jitter**; **timeout** en toda
  llamada externa; **Circuit Breaker** cuando un tercero cae a menudo.
- **Rate limiting** (token bucket / GCRA) con estado persistente si hay
  varias instancias.
- **Colas con estados explícitos** y recuperación de huérfanos (trabajos
  `running` de un proceso que murió pasan a fallo).
- **Outbox** — publicar eventos de forma consistente con la transacción.
- **Saga** — transacciones largas entre servicios con compensaciones.
- **Strangler Fig** — sustituir un sistema por partes.
- **Feature flags** — solo si hay despliegue continuo con riesgo real.
- **URLs firmadas con caducidad** — el cliente accede directamente al
  almacenamiento sin que la API haga de proxy.

---

## 11. Antipatrones a vigilar

God object/módulo · Big Ball of Mud · Golden Hammer · Lava Flow (código
muerto que nadie se atreve a borrar) · Copy-paste programming · Magic
numbers · Shotgun surgery · Feature envy · Primitive obsession (strings
para todo) · Anemic domain (si hay lógica de dominio real) · Premature
optimization · **Speculative generality** (abstracciones "para luego") ·
**Tests que no pueden fallar** · **Dobles que validan el bug** · Estado
mutable global · Distributed monolith · N+1 · Listas sin límite · Errores
tragados · Secretos en código o en `VITE_*`/equivalentes públicos.

---

## 12. Escalabilidad y límites (→ `docs/architecture.md`)

Cada `design.md` responde explícitamente:
1. **¿Es stateless?** Si guarda estado en memoria del proceso, ¿por qué es
   correcto si el proceso se reinicia o hay varias instancias?
2. **¿La consulta nueva tiene índice?** Nombrar las columnas.
3. **¿Hay algún límite sin acotar?** Listas, ficheros, colas, cuerpos.
   Los topes se **cuentan en el origen** (contar en la BD, no traer filas).
4. **¿Hay N+1?**

`docs/architecture.md` incluye además una tabla `<RELLENAR>` de
**restricciones del entorno** (memoria/CPU del hosting, arranque en frío,
límites de planes gratuitos, cuotas) con su consecuencia de diseño. Son
datos que caducan: fecha y fuente.

---

## 13. Git, ramas y despliegue

- **Una rama por feature** desde `main` actualizado (`feat/fNN-nombre`); PR
  a `main`; CI en verde antes de fusionar.
- **Los commits los hace el humano** (el agente prepara el mensaje). Nunca
  `--amend` sobre commits existentes, `push --force` ni reescritura de
  historia: el historial es la evidencia de qué iteración introdujo qué.
- **Commits por rutas** cuando hay trabajo de varias tareas mezclado
  (`git add <rutas>`), no `git add -A` a ciegas.
- **Trampa de upstream:** crear una rama desde `origin/main` la deja
  siguiendo `origin/main`; un `git push` sin argumentos subiría a `main`.
  Quitar el upstream (`git branch --unset-upstream`) y hacer el primer push
  con `-u origin <rama>`.
- **Una rama fusionada que recibe commits nuevos necesita un PR nuevo.**
- **Despliegue continuo desde `main`**: la prueba real de una feature
  requiere que esté fusionada y desplegada; comprobar el commit desplegado
  antes de probar.
- **Lockfiles versionados**; regenerar sin actualizar versiones.
- Mensajes: Conventional Commits en el idioma del proyecto, con el motivo.

---

## 14. Pruebas con servicios reales (runbooks para el humano)

La última task de una feature con servicios externos la ejecuta el humano.
Reglas para escribir sus pasos:

- **Avisar** de que conecta con servicios reales (y si puede costar dinero).
- **Orden ejecutable**: crear recursos antes de referenciarlos; si el
  despliegue necesita variables, que existan antes del primer despliegue (en
  el formulario de creación).
- **Pasos copiables** y **resultado esperado** de cada uno; si falla, qué
  pegar (logs sin valores sensibles).
- **Nunca pedir que se pegue un secreto**; tokens de prueba en variables de
  la consola, no en pantalla.
- Tener en cuenta la terminal real: en consolas integradas del IDE las
  ventanas emergentes de credenciales pueden no recibir el foco (pedir con
  lectura en la propia consola); variables reservadas y alias del shell
  (p. ej. en PowerShell `$PID` es de solo lectura y `H` es un alias).
- Verificaciones de base de datos **de solo lectura** y comparando con la
  forma real del catálogo.
- Nada destructivo a mano en datos reales: lo de prueba se borra por la API.
- Procesos de larga duración (workers) se **reinician** tras cambiar su
  código o sus dependencias.
- **Datos caducos del proveedor** (planes gratuitos, menús del panel,
  servicios "legacy"): consultar la documentación oficial actual y citar
  fecha antes de recomendar. Configurar **alertas de gasto** si hay método
  de pago.
- El resultado va a `evidence.md` como resumen (códigos, estados, nunca
  tokens).

---

## 15. Coste y tokens

- Lo que más gasta es **leer y verificar**, y **las iteraciones**. Reducir
  iteraciones ahorra más que acortar respuestas.
- Specs concisas (se releen en cada iteración de cada agente).
- Correcciones de texto al cerrar en vez de iteraciones por una frase.
- Reglas repetidas en `docs/` para que el implementer acierte a la primera
  (cada hallazgo que se repite en dos features se convierte en regla).
- Partir features grandes o multi-stack.
- Cierre con modelo barato y resumen redactado por el leader.
- Auditorías puntuales (sobreingeniería, deuda) en vez de modos permanentes
  que chocan con las reglas del harness.
- El leader informa del coste real y respeta "para" sin lanzar más agentes.

---

## 16. Lecciones aprendidas (catálogo)

Cada una costó al menos una iteración. Las que ya son regla o test lo
indican.

**Harness**
1. Una carpeta `IT<n>` vacía se despachaba como "revisar" → guarda en
   `state.py` (test incluido).
2. Tests del harness con valores fijos ("el scope es backend") se rompen al
   cambiar de fase → derivar el esperado del estado real.
3. Reescribir `feature_list.json` con un serializador reformatea todo → editar
   como texto.
4. Reglas del harness editadas a mitad de sesión pueden no estar en la
   definición cargada del agente → repetirlas en el encargo.
5. El leader que pasa una hipótesis sin verificar como causa provoca una
   iteración inútil → verificar o etiquetar "hipótesis".
6. Instrucciones de corrección ambiguas generan bugs nuevos → especificar el
   detalle sutil (p. ej. "el siguiente bloque empieza en lo recibido").

**Tests**
7. El doble en memoria escondía que faltaba un filtro en el adaptador real
   (repetido en tres features) → test del adaptador real con cliente
   grabador (regla).
8. Un falso que ignoraba el rango pedido validó un bug de paginación → los
   falsos respetan los límites reales.
9. Un arnés que reseteaba a un literal hacía inútil el test de regresión →
   restaurar el valor inicial capturado.
10. Un test que comparaba un literal obsoleto no podía fallar → mutantes.
11. Demostrar el rojo con un script aparte no prueba nada → rojo sobre el
    código real.
12. Comprobaciones por prefijo (`startsWith("http://localhost")`) se
    engañan con `localhost.evil.com` → parsear y comparar el host exacto.
13. Reglas de lint para prohibir algo se esquivan con importación dinámica,
    subrutas o acceso por corchetes → cubrir esas variantes.

**Portabilidad / CI**
14. Script sin bit de ejecución: verde en Windows, `Permission denied` en
    Linux (test incluido).
15. Reloj monotónico inicializado a `0`: la primera recarga se bloqueaba en
    máquinas recién arrancadas → `-inf`.
16. `python` no existe en todos los sistemas → `sys.executable` / probar
    candidatos.
17. Un comprobador de tipos que no comprobaba nada con cierta configuración
    → demostrar que falla inyectando un error.
18. El CI necesita las toolchains de cada stack y dependencias desde el
    lockfile si faltan.

**Datos y SQL**
19. El motor reescribe definiciones (entrecomilla palabras clave) → los
    `verify` comparan por catálogo, no por texto.
20. Carreras resueltas con constraints y escrituras condicionales, no con
    comprobaciones previas.
21. Leer por bloques depende de un máximo de filas por respuesta configurable
    en el servicio → parar en bloque vacío y avanzar por lo recibido.

**Seguridad y operación**
22. Silenciar la salida de una librería hizo invisible el motivo de un fallo
    → registrar el detalle saneado en el log propio.
23. Mensajes externos en logs pueden inyectar líneas o secuencias de
    terminal → quitar saltos de línea y caracteres de control, truncar.
24. Literales de prueba con aspecto de secreto disparan el escáner → baja
    entropía en tests; allowlist solo por ruta y fichero concreto.
25. Tokens pegados accidentalmente en el chat al copiar un error → pedir
    solo el final del error; rotar o invalidar lo expuesto.
26. Un runbook con los pasos en orden imposible (usar variables antes de
    crearlas) bloqueó el despliegue → orden ejecutable, recursos primero.
27. Un worker de larga duración siguió con código viejo tras cambios → 
    reiniciar procesos tras cambios de código o dependencias.
28. La rama de la feature se subió pero no se fusionó: la prueba real dio 404
    → comprobar el commit desplegado antes de probar.
29. Un servicio de hosting pasó a "legacy" → consultar documentación actual
    y fechar.

---

## Anexo A — Ficheros de la carpeta plantilla

| Fichero | Estado |
|---|---|
| `harness.json` | `<RELLENAR>` proyecto, scopes, secretos |
| `feature_list.json` | ejemplo con F01 `<RELLENAR>` |
| `init.sh` | listo (dispatcher) |
| `plantillas/stack/init.sh` | plantilla por stack `<RELLENAR>` comandos |
| `scripts/state.py` | listo (con la guarda de IT vacía) |
| `scripts/session_start.sh` | listo |
| `scripts/guard_secrets.py` | listo (lee `harness.json`) |
| `tests/test_*.py` | listos (tests del harness) |
| `.claude/settings.json` | listo |
| `.claude/agents/*.md` | listos, genéricos, con las lecciones |
| `.githooks/pre-commit` | listo |
| `.github/workflows/ci.yml` | `<RELLENAR>` toolchains |
| `.gitleaks.toml` | `<RELLENAR>` reglas de secretos propios |
| `.gitignore`, `.gitattributes` | base; ampliar por stack |
| `specs/_plantilla/` | plantillas de requirements/design/tasks |

---

## Anexo B — Plantillas de texto

### B.1 `CLAUDE.md`

````markdown
# <NOMBRE_DEL_PROYECTO>

<Qué es, para quién, en 3-5 líneas.>

## Rol de sesión

Al arrancar una sesión en este repositorio, actúa como `leader` y sigue
`.claude/agents/leader.md`. Lo primero: `python scripts/state.py`.
Para saber dónde está cada regla, `AGENTS.md`.

## Dónde vive cada pieza, y por qué

| Pieza | Dónde | Por qué ahí |
|---|---|---|
| <API> | <servicio> | <restricción que resuelve> |
| <Datos> | <servicio> | <…> |
| <Web> | <servicio> | <…> |

## Restricciones que rompen cosas si se ignoran

- <Cada una con su motivo concreto y su dueño en CHECKPOINTS.md.>

## Prohibiciones

- **No hacer `git commit` sin aprobación del humano**; nunca `--amend`,
  `push --force` ni reescritura de historia.
- **No añadir dependencias sin preguntar.**
- **No tocar `.env` ni ningún fichero de secretos.** Los secretos del
  proyecto (`harness.json`) no se leen, no se imprimen, no se copian.
- **No ejecutar operaciones destructivas sobre datos reales.**
- **No marcar una feature `done` fuera del protocolo del harness.**
- **No cambiar `docs/` ni reglas del harness sin decisión del humano.**

## Estructura

<Árbol de carpetas de primer nivel con una línea por carpeta.>

## Comandos

```bash
python scripts/state.py   # qué toca
./init.sh                 # verifica el scope activo
./init.sh --all           # verifica todo
pytest tests/             # tests del harness
```

## Estado

<Fases, orden, bloqueos conocidos.>
````

### B.2 `AGENTS.md`

````markdown
# Mapa del repositorio

No contiene reglas: dice dónde está cada una. Al arrancar,
`python scripts/state.py`.

| Pregunta | Documento |
|---|---|
| ¿Qué es buen trabajo aquí? | `docs/architecture.md`, `docs/principios.md` |
| ¿Baseline de seguridad? | `docs/security.md` |
| ¿Proceso SDD? | `docs/specs.md` |
| ¿Cómo se demuestra que algo funciona? | `docs/verification.md` |
| ¿Convenciones? | `docs/<stack>/conventions.md` del scope activo, solo ese |
| ¿Cuándo está terminada una feature? | `CHECKPOINTS.md` |

Roles en `.claude/agents/`. `CLAUDE.md` fija el rol de arranque.
````

### B.3 `CHECKPOINTS.md`

````markdown
# Checkpoints de "done"

Cada ítem tiene un único dueño.

## Bloque funcional — dueño: `reviewer`
- Cada `R<n>` tiene un test que lo cubre de verdad (verificado con mutantes).
- Todas las tasks marcadas.
- `init.sh` en verde.
- Se respetan `docs/architecture.md`, `docs/principios.md` y las convenciones del stack.
- <Checkpoints funcionales propios del proyecto.>

## Bloque de escalabilidad — dueño: `reviewer`
- Stateless, o `design.md` justifica por qué no.
- Consultas nuevas con índice.
- Sin N+1.
- Sin límites sin acotar.

## Bloque de seguridad — dueño: `security_reviewer`
- Sin secretos en código, specs ni artefactos públicos (bundles).
- Todo input validado en el borde.
- Autorización explícita por objeto y por función en cada ruta tocada.
- Credenciales temporales con caducidad.
- Dependencias nuevas aprobadas y sin CVEs altos.
- <Riesgos propios del proyecto.>
````

### B.4 Specs (`specs/_plantilla/`)

Ver los tres ficheros de la carpeta. Estructura mínima:
- `requirements.md`: contexto (3 líneas), `R<n>` EARS agrupados, cuáles son
  de seguridad, tabla acceptance → `R<n>`, fuera de alcance.
- `design.md`: ficheros tocados, firmas, decisiones numeradas con motivo,
  alternativas descartadas, las 4 preguntas de escalabilidad, decisiones del
  humano (con fecha), desviaciones aprobadas (vacía).
- `tasks.md`: `T<n>` con `R<n>` cubiertos, la última humana si procede,
  mapa inverso `R<n> → T<n>`.

### B.5 `docs/<stack>/conventions.md`

````markdown
# Convenciones — <stack>

<Lenguaje y versión.> Se lee solo cuando el scope activo incluye <stack>.
La configuración de las herramientas manda; esto explica el porqué.

## Herramientas
<Tests · lint · formato · tipos · build · auditoría — con el comando.>
<Casos donde el comprobador estricto se queda corto y cómo se acota.>

## Idioma
<Código en … / prosa en … / nombres de test que describen comportamiento.>

## Errores
<Cómo se lanzan, qué ve el usuario, qué va al log.>

## Modelos / tipos
<Entrada ≠ fila; campos extra rechazados; tipos cerrados para estados.>

## Concurrencia
<Qué es bloqueante, dónde se ejecuta, reglas.>

## Tests
<Framework; qué se prueba; dobles; test del adaptador real; mutantes.>

## Estructura
<Módulos, fronteras que no se cruzan, dónde vive lo compartido.>

## Patrones prohibidos
<Lista con motivo.>
````

### B.6 Encargo tipo del leader a un implementer

```
Implementa <F> (<título>), iteración IT<n>. La carpeta progress/<F>/IT<n>/
ya existe; escribe ahí impl.md y evidence.md.
Sigue specs/<F>/{requirements,design,tasks}.md. [Cambios pedidos: <lista
de progress/<F>/IT<n-1>/review.md>.] La task humana final no la ejecutes.
Dependencias aprobadas: <lista o "ninguna">. TDD con rojo→verde literal
sobre el código real. Reglas: sin commit, sin .env, sin dependencias no
aprobadas, no marques done. [Ficheros que NO debes tocar: <…>.]
Al terminar: ./init.sh y pytest tests/ en verde.
```

### B.7 `progress/current.md` y `history.md`

`current.md`: sesión activa (qué feature, qué acción), pendientes del
humano, advertencias heredadas, decisiones recientes. Se sobrescribe.

`history.md`: append-only. Por feature: `## FNN — título (done, fecha,
IT<n>)`, entrega, iteraciones con qué falló en cada una, lecciones.

---

## Anexo C — Decisiones pendientes en un proyecto nuevo

Rellenar antes de la primera spec (o registrar como pendiente en
`current.md`):

- [ ] Qué es el producto, para quién, alcance de la primera versión.
- [ ] Stacks (`scopes`) y, por stack: lenguaje, framework, herramientas de
      test/lint/formato/tipos/build/auditoría.
- [ ] Dónde vive cada pieza (hosting, base de datos, almacenamiento, auth)
      y **por qué** (restricción que resuelve). Coste: ¿todo gratis? límites.
- [ ] Secretos del proyecto (nombres) y dónde vive cada uno.
- [ ] Riesgos de seguridad propios, ordenados por gravedad, y su mapeo OWASP.
- [ ] Restricciones del entorno (memoria, CPU, arranque en frío, cuotas).
- [ ] Arquitectura: módulos, fronteras, contratos compartidos.
- [ ] Features iniciales, orden y fases.
- [ ] Qué no se puede verificar con tests y cómo se verificará a mano.
- [ ] Política de ramas y despliegue (qué rama despliega dónde).
- [ ] Idioma del código y de la prosa.
