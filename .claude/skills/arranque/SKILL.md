---
name: arranque
description: Ronda inicial de un proyecto - entrevista al humano en orden (requisitos, alcance, aspectos clave segun el alcance, stack, librerias, diseno visual y forma de trabajo del proyecto) con una recomendacion en cada pregunta, y deja cada decision en su documento de docs/ y el CLAUDE.md del proyecto. Usar al empezar, cuando docs/proyecto.md no dice "Estado: aprobado", o para revisar una fase. Solo la sesion principal.
---

# Arranque

Lo que hace un equipo de verdad antes de escribir código: entender qué se
construye, para quién y con qué ambición, y solo después elegir cómo. Cada
fase depende de las anteriores; **no se pregunta por tecnología antes de
saber qué hace la aplicación**.

Cada decisión queda en su documento de `docs/`, que ya existen como
plantillas con huecos `<…>`:

| Fase | Pregunta | Queda en |
|---|---|---|
| 1. Requisitos | ¿qué hace y para quién? | `docs/proyecto.md` |
| 2. Alcance | ¿para uno mismo o para muchos? | `docs/proyecto.md` |
| 3. Aspectos clave | ¿qué exige ese alcance? | `docs/arquitectura.md` |
| 4. Arquitectura y stack | ¿cómo se organiza y con qué se construye? | `docs/arquitectura.md`, `docs/stack.md` |
| 5. Librerías | ¿qué piezas van encima? | `docs/stack.md` |
| 6. Diseño visual | ¿cómo se ve? (si hay interfaz) | `docs/diseno.md` |
| 7. Forma de trabajo | ¿con cuánto rigor se construye? | `docs/proceso.md`, `docs/convenciones.md`, `docs/seguridad.md` |

## Cómo se pregunta

Con el método de la skill **`entrevista`**: rondas sobre la frontera del
árbol de decisiones, de como mucho 4 preguntas **por ronda** (no en total:
las rondas siguen hasta que no quede nada abierto), cada una con tu
recomendación y su porqué. Los hechos los buscas tú y las decisiones las
toma el humano. Además:

- **Manda el humano.** No investigues nada sin su sí, y antes di qué
  mirarías y cuánto costaría.
- **Tú traes lo que el humano no sabe que necesita** (fase 3), aunque nadie
  lo haya mencionado.
- **Proporcional al alcance**: un proyecto personal no carga con preguntas
  de escalado.
- **Con código ya existente**, lo que hay es la decisión tomada: se lee y
  se confirma, no se pregunta.
- **Se escribe sobre la marcha**: rellena el documento de cada fase al
  cerrarla. Así se puede retomar en otra sesión, y al cerrar cada fase
  puedes proponer `/clear`: los documentos bastan para seguir.
- **Sin commits**: el primero lo hace el humano al final.

**Para investigar** (solo lo que apruebe el humano):

- `explorer`, para una pregunta acotada: una librería, un plan, un límite;
- `/deep-research`, para una pregunta amplia con fuentes cruzadas (es la
  más cara);
- una **prueba mínima** en una carpeta temporal, si una opción depende de
  algo que nadie ha comprobado;
- `council`, si tras investigar quedan varias opciones buenas sin ganadora.

Cada hecho, con su fuente y su fecha.

**Investigación a fondo, a petición del humano**, en cualquier fase y sobre
cualquier tema: convenciones, arquitecturas de referencia, cómo resuelven
algo productos parecidos o qué prácticas usa un equipo profesional para
este tipo de proyecto. Antes de lanzarla, propón:

- la pregunta exacta y lo que queda fuera;
- las fuentes (documentación oficial, repositorios de referencia,
  artículos de ingeniería de empresas que lo hacen a escala);
- con qué se hace (`explorer` o `/deep-research`) y su coste aproximado.

Con el sí del humano, el resultado queda en
`docs/investigaciones/<tema>.md`, con las fuentes, las fechas y las
opciones con sus pros y contras. La decisión se sigue tomando con la
entrevista, y queda en su documento con un enlace a la investigación. Con
alcance **compartido** o **producción**, ofrécela tú en las fases 4 y 7 si
hay decisiones que el humano no sabe valorar; no la lances sin su sí.

## 1. Requisitos → `docs/proyecto.md`

Qué es, para quién y qué problema resuelve. Qué puede hacer el usuario
(acciones concretas, no adjetivos). Qué entra en la primera versión y **qué
no**. Qué datos maneja y de dónde salen. En qué dispositivos se usa, ahora
y más adelante.

Cierra la fase con la **lista de features** en orden. La primera es
siempre el **andamiaje** (F00): el proyecto creado con el generador oficial
del framework, un "hola mundo" de punta a punta y la comprobación de los
supuestos de riesgo (fase 4). Después, la feature de producto más pequeña
que aporte valor.

## 2. Alcance → `docs/proyecto.md`

Para quién es (solo el humano, personas conocidas o abierto al público),
cuántos usuarios se esperan y en cuánto tiempo, qué pasa si falla o pierde
datos, si mueve dinero o datos sensibles de otros, el presupuesto (gratis o
de pago, y cuánto) y los plazos. Propón uno de estos niveles y deja que el
humano lo ajuste:

- **Personal**: uno mismo. Simple, barato, se acepta que sea tosco.
- **Compartido**: unas pocas personas conocidas. Los datos de otros ya
  importan.
- **Producción**: público o muchos usuarios. Arquitectura, escala,
  seguridad y operación cuentan desde el principio.

## 3. Aspectos clave → `docs/arquitectura.md`

Con alcance **personal**, solo lo imprescindible: dónde viven los datos y
si se acepta perderlos. Con **compartido** o **producción**, recorre
`catalogo.md` (en esta carpeta) y trae cada tema que aplique: qué es en una
línea, por qué importa en este producto y tu propuesta. **Lo que es caro
cambiar después se decide ahora**; lo barato se aplaza con el disparador
que lo traerá.

## 4. Arquitectura y stack → `docs/arquitectura.md` y `docs/stack.md`

Forma de la arquitectura (monolito, cliente-servidor, serverless,
local-first…), lenguaje, framework, base de datos y dónde se despliega.
Primero pregunta si el humano tiene preferencias o vetos (lo que conoce, lo
que quiere aprender, servicios que ya usa). Si no los tiene, propón 2-3
opciones con pros, contras y tu recomendación para **este** alcance. Pesa
también cuánto exigirá la interfaz: *en un piloto, el stack se eligió sin
pensar en la ambición visual y hubo que cambiar de framework a mitad de la
primera feature.*

La forma va a `arquitectura.md`; el lenguaje, el framework, los datos y el
despliegue, con su versión y la alternativa descartada, a `stack.md`.

Apunta en `arquitectura.md` los **supuestos de riesgo**: lo que, si resulta
falso, obliga a cambiar el stack (que una librería corra en la plataforma,
que un plan gratuito aguante). Los comprueba F00 antes de escribir
producto. Apunta también las **restricciones del entorno** (memoria del
hosting, arranque en frío, cuotas, límites de los planes), cada una con su
fecha y su fuente.

Con alcance **compartido** o **producción**, cierra la fase con:

- un **diagrama de componentes y flujo de datos** en texto (qué piezas hay,
  qué se dicen y dónde viven los datos), para que el humano vea la
  arquitectura de un vistazo;
- una **estimación de carga** con números aunque sean gruesos (usuarios,
  peticiones al día o por segundo en el pico, volumen de datos al año),
  contrastada con las restricciones del entorno. Es lo que dice si un plan
  gratuito aguanta o si hace falta caché o escalar.

Si el humano quiere dejar constancia de las decisiones de arquitectura
como ADR, usa `engineering:architecture` o `architecture-decision-records`,
la que esté instalada, y enlázalos desde `arquitectura.md`. Para un diseño
de sistema con más detalle (contratos de API, colas, reintentos,
redundancia), `engineering:system-design`.

## 5. Librerías → `docs/stack.md`

Lo que va encima del stack: acceso a datos, validación, autenticación,
estado y caché en el cliente, formularios… Solo lo que pidan los requisitos
y el alcance. Cada librería, con su versión, para qué sirve y la
alternativa descartada. Antes de cualquier dependencia, mira si basta con
lo nativo. Si un hecho no es seguro (versión, licencia, mantenimiento,
límites), propón comprobarlo. **`stack.md` es la lista de dependencias
aprobadas: lo que no esté ahí pide permiso al instalarse.**

Las de interfaz (componentes, iconos, animación, fuentes) se eligen en la
fase 6, con las referencias delante. Las de pruebas, en la 7.

## 6. Diseño visual → `docs/diseno.md`

Solo si hay interfaz: **`/direccion-visual`**.

## 7. Forma de trabajo → `docs/proceso.md`, `docs/convenciones.md` y `docs/seguridad.md`

Cuánto proceso compensa, según el alcance. Recomienda según esta tabla y
deja que el humano cambie cualquier casilla. El resultado va a
`proceso.md`:

| | Personal | Compartido | Producción |
|---|---|---|---|
| Spec antes de construir | solo en las features con decisiones | en todas salvo cambios pequeños | en todas salvo cambios pequeños |
| Pruebas | de la lógica que importa | de comportamiento, una por requisito | de comportamiento, una por requisito |
| Zonas críticas y mutantes | normalmente ninguna | las que haya, con mutantes | las que haya, con mutantes |
| Revisión funcional (`reviewer`) | opcional | sí | sí |
| Revisión de seguridad (`security_reviewer`) | si hay datos de otros o red | sí, al final de cada feature | sí, al final de cada feature |
| Auditoría completa | a petición | cada 4 features | cada 4 features o al cerrar una fase |
| Ramas | `main` | una por feature | una por feature |

Además, decide con el humano y apunta:

- en `proceso.md`: **las zonas críticas**, si las hay (dinero, escritura de
  datos, permisos, parsers, fechas…); **si se pasa un escáner de
  secretos** (por ejemplo, gitleaks) antes del primer push, porque un
  secreto commiteado y borrado sigue en el historial; y **las skills para
  los agentes según el stack**, si están instaladas: con React,
  `vercel-react-best-practices` y `vercel-composition-patterns` en el
  `implementer`; con Python, `modern-python`; con usuarios o servidor,
  `prd-securability-enhancement` para escribir las specs. Con el sí del
  humano, se añaden en `skills:` del agente y se ponen en `name-only` en
  `skillOverrides` de `.claude/settings.json`;
- en `convenciones.md`: **las convenciones del lenguaje y del código**.
  Propón en bloque lo estándar del stack elegido (estructura de carpetas y
  fronteras, manejo de errores, tipos, tests por capa y, si hay interfaz,
  el bloque web), para que el humano lo acepte de una vez o abra lo que
  quiera. Pregunta solo lo que es preferencia suya: en qué idioma van el
  código y los textos de la interfaz, si hay patrones que quiere prohibir o
  exigir, y el formato de ramas y mensajes de commit. Si quiere
  fundamentarlas mejor, ofrécele la investigación a fondo;
- en `seguridad.md`: **los riesgos propios de seguridad** (3-6, del más
  grave al menos), borrando los apartados condicionales que no apliquen;
- **el comando que verifica todo** (tests, lint, tipos, build, auditoría de
  dependencias, según lo que se haya elegido) y el de mutantes, si los
  hay: van a la sección "Comandos" del `CLAUDE.md`. F00 los deja
  funcionando y demuestra que cada paso sabe fallar.

## Cierre

Comprueba que:

- no queda ningún hueco `<…>` en los documentos de `docs/` (o se borró la
  sección porque no aplica);
- no queda ninguna decisión abierta sin aplazar con su disparador (las
  revisables, en "Decisiones revisables" de `proyecto.md`);
- nada se contradice entre documentos;
- la primera feature se puede construir sin preguntas de arquitectura
  pendientes.

Enseña un resumen de una pantalla: qué se decidió en cada fase, qué es
revisable y cuándo, y la primera feature. **Con el sí explícito del
humano**, escribe `Estado: aprobado (AAAA-MM-DD)` en `docs/proyecto.md` y
**genera el `CLAUDE.md` del proyecto** (abajo). Si la carpeta no es
todavía un repositorio git, propón `git init`. Después, **propón el primer
commit** (la plantilla y los documentos del arranque), tras mirar `git
status`: los revisores comparan contra `HEAD`, y sin un commit previo no
hay con qué comparar. Desde ahí se construye siguiendo
`.claude/forma-de-trabajo.md`.

Si más adelante cambia una decisión de base, se vuelve a su fase, se
actualiza su documento (y `CLAUDE.md`, si cambia algo de lo que recoge) y
solo entonces se sigue.

## El `CLAUDE.md` del proyecto

Sustituye al de la plantilla ("Proyecto sin arrancar"). Claude lo lee en
cada sesión, y cada agente también, así que sigue la guía oficial de
Claude Code (code.claude.com/docs/en/best-practices y /memory): **corto
(unas 40 líneas, nunca más de 200), con encabezados y viñetas, y solo lo
que hace falta en cada sesión y no se deduce del código.** Para cada línea:
*¿quitarla haría que Claude se equivoque?* Si no, fuera.

**Las decisiones no van aquí: viven en `docs/`**, y el `CLAUDE.md` las
enlaza. Solo lleva lo que Claude necesita en cada sesión para no
equivocarse:

```
# <Nombre>
<Una o dos líneas: qué es y para quién.>

## Comandos
<verificar todo, verificar rápido, arrancar, datos falsos (normal y peor
caso), mutantes. Los completa F00.>

## Lo que rompe cosas
- <regla> — <motivo> → <documento donde se decidió> (p. ej. "las fechas,
  siempre en local: la racha depende del día del usuario →
  docs/arquitectura.md").

## Dónde está cada decisión
- Qué es, alcance, features y estado: docs/proyecto.md
- Arquitectura, supuestos y restricciones: docs/arquitectura.md
- Stack y librerías aprobadas: docs/stack.md
- Diseño visual: docs/diseno.md
- Proceso (specs, pruebas, revisiones, ramas): docs/proceso.md
- Convenciones del código: docs/convenciones.md
- Seguridad: docs/seguridad.md
```

"Lo que rompe cosas" es lo único que se repite de los documentos: unas
pocas reglas que, si Claude no las tiene presentes en cada sesión, rompen
algo, cada una en una línea y con el enlace a dónde se decidió. No repite
la forma de trabajo ni las reglas duras (están en
`.claude/rules/harness.md`, que se carga siempre). **Si el proyecto ya
tenía un `CLAUDE.md` propio**, no lo sustituyas: añade lo que falte,
enséñale el cambio al humano y respeta lo que ya había.

**Se mantiene vivo**: cuando cambia un comando o aparece una regla que
rompe cosas, se actualiza en el momento. Se añade una línea cuando Claude
comete el mismo error por segunda vez o el humano repite una corrección, y
se poda lo que Claude ya hace bien sin ella (`/doctor prompt-audit` lo
revisa). Si Claude se salta una instrucción concreta, se marca esa sola con
"IMPORTANTE"; si se marcan muchas, ninguna destaca.
