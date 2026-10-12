# Forma de trabajo

Cómo se construye un proyecto una vez hecho el arranque, cuando
`docs/proyecto.md` dice `Estado: aprobado`. Cada recomendación lleva el
incidente que la motivó en las pruebas. Cuánto proceso se aplica (specs,
pruebas, revisiones) lo fija la sección 7 de `docs/proyecto.md`, que decide
el humano y que se puede cambiar cuando estorbe.

## Quién hace qué

| Quién | Qué hace |
|---|---|
| **Sesión principal** (con el humano) | el arranque, las specs (un subagente no puede esperar a que el humano responda), lanzar los agentes, pasarle al humano sus resultados, los arreglos pequeños y mantener al día `docs/proyecto.md` |
| `explorer` | busca un hecho concreto (una librería, un límite, cómo está hecho algo) con su fuente y su fecha |
| `implementer` | construye la feature o el tramo y devuelve qué hizo, con qué tests y qué capturas |
| `reviewer` | revisión funcional con contexto limpio: `Veredicto: APPROVED` o `CHANGES_REQUESTED` |
| `security_reviewer` | seguridad de la feature entera, al final y tras el `APPROVED` del reviewer |

**Skills del harness**:

- `/arranque`: la ronda inicial;
- `entrevista`: el método de preguntas, que usan el arranque y las specs;
- `/direccion-visual`: el diseño, o un rediseño;
- `/auditoria-seguridad`: el repositorio entero;
- `/retrospectiva`: al terminar o al cerrar una fase.

## Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Requisitos, alcance, decisiones, librerías, forma de trabajo | `docs/proyecto.md` |
| Lista de features, la que está en curso y lo pendiente | `docs/proyecto.md`, al final |
| Diseño visual y tokens | `docs/diseno.md` (los tokens, en el stack) |
| Comandos, estructura, errores, patrones prohibidos, interfaz web | `docs/convenciones.md` |
| Riesgos propios y lista de seguridad | `docs/seguridad.md` |
| Lecciones del proyecto, según ocurren | `docs/proyecto.md`, sección "Lecciones" |
| Spec de una feature | `specs/FNN-<nombre>.md`, desde `specs/_plantilla.md` |
| Cada vuelta de una feature | `progress/FNN/IT<n>/` (abajo) |
| Investigaciones a fondo (convenciones, arquitecturas…) | `docs/investigaciones/<tema>.md` |
| Auditorías y retrospectivas | `docs/auditorias/`, `docs/retrospectiva-<fecha>.md` |
| Qué cambió en la feature en curso | `git diff HEAD` (un commit por feature) |

### Una carpeta por vuelta

Cada intento de implementar una feature (o un tramo) es una **iteración**
con su carpeta, `progress/FNN/IT<n>/`. La crea la sesión principal **antes**
de lanzar al `implementer`, y la siguiente vuelta, tras un rechazo, es
`IT<n+1>`. Nunca se reescribe una anterior.

| Fichero | Lo escribe | Contenido |
|---|---|---|
| `impl.md` | `implementer` | ficheros tocados, requisito → test (fichero y aserción), comandos y su resultado, desviaciones, capturas (≤ 200 líneas) |
| `evidence.md` | `implementer` | lo largo: salidas de comandos y mutantes bajo `## Sabotajes` (o `N/A: <motivo>` fuera de las zonas críticas). Una prueba no se borra por espacio: se mueve aquí |
| `capturas/` | `implementer` | `<pantalla>-<tema>-<ancho>-<datos>.png` |
| `review.md` | `reviewer` | primera línea `Veredicto: APPROVED` o `Veredicto: CHANGES_REQUESTED`, causa y cambios pedidos con su cita (≤ 200 líneas) |
| `security.md` | `security_reviewer` | igual, con la tabla de ataque; solo en la última vuelta de la feature |

**Para qué sirve**: lo que dice cada agente sobrevive a un `/clear` y a un
cambio de sesión. La siguiente vuelta lee los cambios pedidos del fichero,
no de la memoria de nadie. Y el número de carpetas es el número de
intentos, el dato que la retrospectiva necesita. *En el piloto, de las
carpetas salieron todas las cifras que motivaron los cambios (rechazos por
causa, pasadas de seguridad inútiles).* La carpeta se commitea con la
feature.

**Al empezar cada sesión**, la sesión principal lee las secciones
"Features", "Estado actual" y "Pendiente" de `docs/proyecto.md` y dice al
humano por dónde va el proyecto. **Al cerrar cada paso del ciclo**, las
actualiza. *Al quitarse un estado que se pudiera derivar, lo único que
recuerda en qué punto está el proyecto es ese fichero. Una sesión arrancó
con un pendiente que ya estaba hecho, porque nadie lo había actualizado
tras el commit.*

## El ciclo de una feature

1. **Una feature cada vez, en el orden de `docs/proyecto.md`.** La primera,
   F00, monta el esqueleto con el generador oficial del framework, cruza la
   arquitectura de punta a punta con un "hola mundo", deja funcionando el
   comando de verificación (demostrando que cada paso sabe fallar) y
   comprueba los supuestos de riesgo **antes** de escribir producto. *En un
   piloto, un cambio de framework a mitad de la primera feature tiró una
   iteración entera, y la primera feature cargó con el toolchain y
   necesitó 11 vueltas.*
2. **Spec**, si la sección 7 la pide para esta feature. Sin spec, el
   encargo lleva los requisitos (cada línea, un requisito) y, si aparece
   una decisión de diseño de verdad, se para y se escribe la spec. La escribe la
   sesión principal con el humano, usando la skill `entrevista`. Antes de
   redactar, se pregunta lo ambiguo: *una spec se reescribió entera por no
   hacerlo.* Va en `specs/FNN-<nombre>.md`, desde la plantilla, y ocupa
   unas 400 líneas como mucho: *specs de 1.000-2.000 líneas costaban más de
   lo que aportaban, porque cada agente las relee en cada vuelta.* El
   aspecto no se especifica: sale de `docs/diseno.md`.
3. **Aprobación del humano**, con un sí explícito a la spec y a cada una de
   sus decisiones. Al pedirla, se dice qué frase vale ("apruebo con las
   recomendadas"). Si falta algo, se repregunta solo eso, en una línea.
   *"Sigue" no es aprobar (en un piloto se aprobaron cuatro specs así),
   pero tres idas y vueltas por la frase exacta cansan.* Con el sí se
   escribe `Estado: aprobada (fecha)` y las respuestas en "Decisiones del
   humano".
4. **Implementar** (`implementer`), en una carpeta `progress/FNN/IT<n>/`
   recién creada y con el encargo tipo de más abajo. Como
   mucho dos tramos (normalmente lógica y datos, después interfaz), y cada
   tramo se revisa antes del siguiente. *Cada tramo es otro ciclo de
   implementación y revisión.*
5. **Revisión funcional** (`reviewer`), si la sección 7 la pide, con
   contexto limpio y nunca a cargo de quien implementó, sobre la misma
   `IT<n>`. Si pide cambios, se crea `IT<n+1>` y se relanza el
   `implementer` con los cambios de `review.md` citados tal cual. Después
   vuelve el `reviewer`. Las desviaciones a las que el reviewer da el
   visto bueno, la sesión principal las marca en la spec ("Visto bueno:
   reviewer, fecha").
6. **Revisión de seguridad** (`security_reviewer`), si la sección 7 la pide:
   **al final de la feature y solo tras el `APPROVED` del reviewer** (si
   el proyecto va sin reviewer, tras la última vuelta del implementer). *En
   un piloto, en cada tramo supuso 47 pasadas para 2 rechazos; en paralelo
   con el reviewer, la mitad de las pasadas caían en código que se iba a
   rehacer.* Si pide cambios, se hace otra vuelta, que pasa por el
   `reviewer` y después por seguridad.
7. **Prueba con servicios reales**, si la spec la tiene: la ejecuta el
   humano siguiendo sus pasos, y el resultado se resume en el `evidence.md`
   de la última vuelta (códigos y estados, nunca tokens). Si no se puede
   hacer ya, queda en "Pendiente". *En el piloto, nueve features seguidas
   se cerraron sin ejecutarla.* **Visto bueno visual del humano** en las
   features con pantallas, con las capturas delante. Sus cambios son un arreglo pequeño o una vuelta
   más. *Antes no había un momento para él, y un cambio pedido al ver las
   capturas entró por la puerta de atrás.*
8. **Cierre**: la feature se marca `[x]` en `docs/proyecto.md` y se
   actualizan "Estado actual" y "Pendiente". Después, **se propone el
   commit** con un mensaje ya redactado; lo hace el humano o lo aprueba.
   Tras el commit, se apunta el hash y se propone `/clear`: el estado está
   en disco. *En un piloto, la sesión principal llegó a acumular 16-24
   millones de tokens leídos de caché.*

Cada 4 features cerradas, o al cerrar una fase, se propone
`/auditoria-seguridad` si la sección 7 la incluye. Al terminar, se propone
`/retrospectiva`.

### Encargo tipo

El agente arranca en frío. El encargo lleva el contexto mínimo suficiente:

```
Implementa FNN (<título>), IT<n>[, tramo <X>: T<a>-T<b>]. Spec: specs/FNN-<nombre>.md.
La carpeta progress/FNN/IT<n>/ ya existe: deja ahí impl.md y evidence.md.
[Cambios pedidos: <de IT<n-1>/review.md o security.md, tal cual>.]
Dependencias aprobadas: <lista o "ninguna nueva">.
[Reglas que han cambiado en esta sesión: <…>.] [Arreglos míos que verás en el diff: <…>.]
[No toques: <…>.] [Hipótesis sin verificar: <…>.]
```

Al `reviewer` y al `security_reviewer`:

```
Revisa FNN (<título>), IT<n>. Spec: specs/FNN-<nombre>.md (o requisitos: <…>).
Escribe progress/FNN/IT<n>/review.md (o security.md).
[Revisión acotada: el rechazo anterior fue solo por tests.] [Arreglos míos que verás en el diff: <…>.]
```

- **Las hipótesis, etiquetadas como hipótesis.** *Una causa supuesta y
  falsa costó una vuelta entera.*
- **El detalle sutil de una corrección, explícito** ("el siguiente bloque
  empieza en lo recibido, no en lo pedido").
- **Las reglas que cambiaron en la sesión, repetidas**: la definición del
  agente no las tiene.
- **Los arreglos que hizo la sesión principal, declarados**: *uno sin
  declarar volvió como "cambio no explicado".*
- **Agentes en paralelo, solo sobre ficheros distintos**, y se les dice.

### Agente que vuelve sin terminar

Si un agente corta antes de escribir su fichero (`impl.md`, `review.md` o
`security.md`), no se lanza otro, que empezaría de cero: se le escribe con `SendMessage` para que continúe. Como
mucho dos veces; a la tercera, el atasco es real y se para para contárselo
al humano.

### Arreglos pequeños

Los hace la sesión principal, sin agentes, si **no añaden comportamiento**
ni tocan zonas sensibles (entrada externa, autenticación, secretos,
migraciones, dependencias). Se apuntan en "Pendiente" o se declaran en el
siguiente encargo. *Un error de pocas líneas con el protocolo completo
costaba más que el propio arreglo.*

### Cambios de rumbo

Todos, con el sí del humano.

- **Una spec aprobada no se reescribe.** Si algo cambia (por ejemplo, el
  humano rechaza el aspecto de una pantalla ya aprobada), se añade una
  "Enmienda AAAA-MM-DD" con requisitos nuevos, que vuelve a pasar por su
  aprobación, y se sigue en nuevas vueltas de la misma feature.
- **Descartar una vuelta** (por ejemplo, cambia el stack con una iteración
  sin revisar): se escribe `progress/FNN/IT<n>/descartada.md` con el motivo
  y quién lo decidió, se desmarcan en la spec las tareas que marcó, y el
  encargo de la siguiente dice qué código de la descartada se quita y qué
  se conserva. La carpeta no se borra.
- **Ampliar el alcance al cerrar** es una feature nueva, no una enmienda.
  *Una spec llegó a 699 líneas.*
- **Un arreglo sobre algo ya cerrado** también es una feature nueva,
  pequeña, que se pone justo detrás de la que está en curso.
- **Si cambia una decisión de base** (stack, plataforma, datos), se para la
  feature, se vuelve a su fase del arranque, se actualiza
  `docs/proyecto.md` y solo entonces se sigue.
- **Investigación a fondo**, cuando el humano la pida (convenciones,
  arquitecturas, cómo lo resuelven otros): igual que en el arranque, se
  propone primero la pregunta, las fuentes y el coste, y el resultado queda
  en `docs/investigaciones/<tema>.md`.
- **Un fallo sin causa clara** o un test intermitente se investiga antes de
  tocar código (`investigate-first`, si está instalada).
- **Cambiar la forma de trabajo** (sección 7 de `docs/proyecto.md`): se
  apunta con su fecha y su motivo, para que la retrospectiva pueda ver si
  sirvió.

### Control y coste

- **Si el humano dice "para", no se lanza nada más.**
- **Se avisa del coste cuando es alto**: una investigación amplia, una
  auditoría con muchos agentes, una vuelta más sobre una feature grande.
- **Modelos**: `implementer`, `reviewer` y `security_reviewer` en `opus`,
  y `explorer` en `sonnet`. Lo caro son las vueltas de más, no el precio
  por token. Opus cuesta el doble que Sonnet en entrada y salida, pero lo
  mismo en lectura de caché (precios de la API, octubre de 2026), y en un
  implementer la caché es la mayor parte del volumen. Por eso una ejecución
  sale entre 1,3 y 1,5 veces más cara, y una vuelta evitada por feature ya
  lo compensa. *En la prueba mínima, con Opus, el reviewer aprobó 5 de 7
  revisiones. En el piloto, con Sonnet, 47 de 96. Entre una prueba y otra
  cambiaron también las reglas, así que es un indicio, no una prueba.*
- **`maxTurns`** en cada agente pone tope al gasto: 200 el implementer, 100
  los revisores y 60 el explorer. Si un agente llega al tope, se reanuda
  (arriba), no se sube el número a ciegas.
- **`/clear` tras cada feature** y tras cada fase del arranque: todo el
  estado está en disco.

### Lecciones del proyecto

Cuando algo de la forma de trabajo falla o estorba, la sesión principal lo
apunta **en el momento** en la sección "Lecciones" de `docs/proyecto.md`:
qué pasó, cuánto costó y de qué feature e iteración salió, sin proponer
todavía el arreglo. *En la prueba mínima, ese diario fue lo que más sirvió
para mejorar la plantilla.* La `/retrospectiva` lo convierte en cambios.

### En equipo

Una sola feature en curso por árbol de trabajo. Con varias personas o
varias features a la vez, una rama o un worktree por feature, cada uno con
su sesión, y `docs/proyecto.md` se reconcilia al fusionar.

## Pruebas

Según la sección 7 de `docs/proyecto.md`:

- **Un test vale si cae con el código roto.** Se rompe la línea de
  producción, se ve caer el test y se restaura. Si para restaurar hay que
  tocar también el test, el test no protegía nada.
- **Mutantes solo en las zonas críticas**, con la herramienta del stack.
  Quien implementa y quien revisa usan **el mismo comando y el mismo
  criterio**. Fuera de esas zonas basta un test de comportamiento por
  requisito. *En un piloto se rechazaron 42 de 44 primeras entregas por
  mutantes que el implementador no había probado: cada uno usaba un
  criterio distinto. En la prueba siguiente, un mutante encontró un fallo
  real en la zona crítica (recortar antes de ordenar).*
- **Un test de límite se compara con el valor de la spec**, no con la
  constante del código.
- **Un doble de prueba respeta los límites reales** (paginación, filtros).
  *Uno que los ignoraba validó un bug.* El adaptador real también tiene
  tests en sus bordes (cero filas, conflicto).
- **Un test intermitente se arregla en la siguiente vuelta** (o se pone en
  cuarentena con su motivo): se apunta en "Pendiente" y va en el siguiente
  encargo. *Se anotaron ocho y nadie los arregló.*
- **Lo que no se puede verificar con tests** (un dispositivo físico, un
  servicio real) se dice en la spec y en el veredicto, y se comprueba a mano
  con un protocolo escrito. Nunca se da por verificado sin más.
- **Un solo comando verifica todo**: tests, lint, tipos, build y auditoría
  de dependencias. Antes de fiarse de él, se demuestra que cada paso sabe
  fallar. *Hubo un comprobador de tipos que no comprobaba nada.*
- **Herramientas de mutantes en Windows**: `mutmut` no funciona en Windows
  nativo (usa `cosmic-ray`), y Stryker necesitó `--concurrency 2` para no
  dar ETIMEDOUT.

## Interfaz

- **El aspecto sale de `docs/diseno.md`**, no de cada spec, y los tokens
  viven en un único sitio. *Una paleta por defecto fijada en una spec se
  quedó congelada en todas las pantallas.*
- **Capturas de lo construido**: claro y oscuro, escritorio y móvil, caso
  normal y peor caso, con un modo de datos falsos que lo permita. *Los
  fallos visuales solo los veía el humano, y las tareas "mira la interfaz"
  nunca se hacían.*
- **El navegador de capturas, aislado** (Playwright con `--isolated`). *Un
  navegador compartido con el humano estropeó una tanda de capturas.*
- **Movimiento, solo el que fija el diseño.** *Las animaciones añadidas por
  pulir fueron la mayor fuente de vueltas.*

## Código

- **Nativo antes que dependencia**, y ninguna dependencia nueva sin
  preguntar.
- **Regla de tres**: no se abstrae hasta el tercer uso real.
- **Se parsea en el borde y se confía dentro.** Todo lo que viene de fuera
  (usuario, red, almacenamiento) se valida al entrar y tiene tope.
- **Nunca tragarse un error**: hacia fuera, un mensaje cerrado; hacia el
  log, el detalle saneado.
- **Las carreras se resuelven con constraints o escrituras condicionales**,
  no con leer-comprobar-escribir.
- **Una librería frágil, detrás de un adaptador** en un único fichero.
- **Atajos marcados**: `ATAJO: <límite> · <camino de mejora>` en un
  comentario, para encontrarlos todos después.

## Entorno y agentes

- **Cada agente trabaja en su propia carpeta temporal.** *Uno ejecutó la
  lista de mutantes de otro.*
- **Los procesos se matan por su PID, nunca por nombre.** *`taskkill /IM
  node.exe` mató todos los `node` de la máquina, y un servidor de Vite
  sobrevivió a TaskStop.*
- **Las copias de trabajo, sin enlaces a `node_modules` o `.venv`.** *Un
  `rm -rf` atravesó el enlace y casi vacía el original.*
- **Nunca "restaurar de HEAD" para deshacer un sabotaje**: se pierde el
  trabajo sin commitear.
- **Lo que se sabe de fuera** (versiones, planes, límites), con su fuente y
  su fecha. *Un proveedor pasó a "legacy" entre dos consultas.*
- **Windows y Linux**: los `.sh` con finales LF y bit de ejecución
  (`git update-index --chmod=+x`); `python` no existe en todos los
  sistemas. *Pasaba en verde en Windows y fallaba en Linux.*
- **Antes del primer `git add -A`, `git status`**: lo personal va a
  `.gitignore`. *Un Excel con una nómina entró en el índice.*

## Seguridad

La lista completa está en `docs/seguridad.md`.

**Dos hooks lo hacen cumplir** (`.claude/hooks/`, ideas de ECC adoptadas
tras el piloto; necesitan Python 3.10+):

- `guard_shell.py`, antes de cada comando de terminal, **bloquea**:
  - leer un `.env` (salvo `.env.example`), volcar el entorno o expandir un
    secreto; los nombres de los secretos los toma de `.env.example`;
  - saltarse los hooks de git (`--no-verify`, `commit -n`, cambiar
    `core.hooksPath`);
  - reescribir la historia (`--amend`, `push --force`, `rebase`,
    `filter-branch`);
  - descartar cambios sin commitear (`reset --hard`, `checkout --`,
    `restore`, `clean -f`, `stash drop`);
  - matar procesos por nombre.

  Si un bloqueo sobra, lo ejecuta el humano.
- `guard_config.py`, antes de editar la configuración de lint, formato,
  tipos o tests, o la del propio harness (`.claude/settings.json` y
  `.claude/hooks/`), **pregunta** al humano. *Un agente atascado en un check
  tiende a relajar la regla en vez de arreglar el código.*

Sin Python, el lanzador bloquea los comandos de terminal en vez de
dejarlos pasar sin vigilar.

- **Los secretos no pasan por el contexto**: no se leen `.env` ni claves,
  no se imprimen y no se copian (`.claude/settings.json` lo bloquea). Un
  secreto que llega al chat, a un log o a un commit se rota: borrarlo no
  basta, porque sigue en el historial. Antes del primer push conviene
  pasar un escáner de secretos.
- **El atacante no usa tu interfaz**: llama a la API directamente.
- **Nada destructivo sobre datos reales** (`DROP`, `TRUNCATE`, o `DELETE`
  y `UPDATE` sin `WHERE`).
- **Se avisa antes de tocar servicios reales** y de lo que cuestan. Los
  pasos que se le piden al humano van en orden ejecutable, con el
  resultado esperado y **sin pedirle nunca un secreto**.
