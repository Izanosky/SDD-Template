---
name: arranque
description: Ronda inicial de un proyecto - entrevista al humano en orden (requisitos, alcance, aspectos clave segun el alcance, stack, librerias, diseno visual y forma de trabajo del proyecto) con una recomendacion en cada pregunta, y deja todo en docs/proyecto.md. Usar al empezar, cuando docs/proyecto.md no existe o no esta aprobado, o para revisar una fase. Solo la sesion principal.
---

# Arranque

Lo que hace un equipo de verdad antes de escribir código: entender qué se
construye, para quién y con qué ambición, y solo después elegir cómo. Cada
fase depende de las anteriores; **no se pregunta por tecnología antes de
saber qué hace la aplicación**.

| Fase | Pregunta | Queda en |
|---|---|---|
| 1. Requisitos | ¿qué hace y para quién? | `docs/proyecto.md` |
| 2. Alcance | ¿para uno mismo o para muchos? | `docs/proyecto.md` |
| 3. Aspectos clave | ¿qué exige ese alcance? | `docs/proyecto.md` |
| 4. Stack | ¿con qué se construye? | `docs/proyecto.md` |
| 5. Librerías | ¿qué piezas van encima? | `docs/proyecto.md` |
| 6. Diseño visual | ¿cómo se ve? (si hay interfaz) | `docs/diseno.md` |
| 7. Forma de trabajo | ¿con cuánto rigor se construye? | `docs/proyecto.md` |

## Cómo se pregunta

Con el método de la skill **`entrevista`**: rondas sobre la frontera del
árbol de decisiones, de como mucho 4 preguntas, cada una con tu
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
- **Se escribe sobre la marcha**: al empezar, copia `proyecto.md` (de esta
  carpeta) a `docs/proyecto.md` y actualízalo al cerrar cada fase. Así se
  puede retomar en otra sesión. Al cerrar cada fase, propón `/clear`: el
  fichero basta para seguir.
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
entrevista, y en `docs/proyecto.md` queda la decisión con un enlace a la
investigación. Con alcance **compartido** o **producción**, ofrécela tú en
las fases 4 y 7 si hay decisiones que el humano no sabe valorar; no la
lances sin su sí.

## 1. Requisitos

Qué es, para quién y qué problema resuelve. Qué puede hacer el usuario
(acciones concretas, no adjetivos). Qué entra en la primera versión y **qué
no**. Qué datos maneja y de dónde salen. En qué dispositivos se usa, ahora
y más adelante.

Cierra la fase con la **lista de features** en orden. La primera es
siempre el **andamiaje**: el proyecto creado con el generador oficial del
framework, un "hola mundo" de punta a punta y la comprobación de los
supuestos de riesgo (fase 4). Después, la feature de producto más pequeña
que aporte valor.

## 2. Alcance

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

## 3. Aspectos clave

Con alcance **personal**, solo lo imprescindible: dónde viven los datos y
si se acepta perderlos. Con **compartido** o **producción**, recorre
`catalogo.md` (en esta carpeta) y trae cada tema que aplique: qué es en una
línea, por qué importa en este producto y tu propuesta. **Lo que es caro
cambiar después se decide ahora**; lo barato se aplaza con el disparador
que lo traerá.

## 4. Stack

Forma de la arquitectura (monolito, cliente-servidor, serverless,
local-first…), lenguaje, framework, base de datos y dónde se despliega.
Primero pregunta si el humano tiene preferencias o vetos (lo que conoce, lo
que quiere aprender, servicios que ya usa). Si no los tiene, propón 2-3
opciones con pros, contras y tu recomendación para **este** alcance. Pesa
también cuánto exigirá la interfaz: *en un piloto, el stack se eligió sin
pensar en la ambición visual y hubo que cambiar de framework a mitad de la
primera feature.*

Apunta los **supuestos de riesgo**: lo que, si resulta falso, obliga a
cambiar el stack (que una librería corra en la plataforma, que un plan
gratuito aguante). Los comprueba la feature de andamiaje antes de escribir
producto. Apunta también las **restricciones del entorno** (memoria del
hosting, arranque en frío, cuotas, límites de los planes), cada una con su
fecha y su fuente.

Si el humano quiere dejar constancia de las decisiones de arquitectura
como ADR, usa `architecture-decision-records`.

## 5. Librerías

Lo que va encima del stack: acceso a datos, validación, autenticación,
estado y caché en el cliente, formularios… Solo lo que pidan los requisitos
y el alcance. Cada librería, con su versión, para qué sirve y la
alternativa descartada. Antes de cualquier dependencia, mira si basta con
lo nativo. Si un hecho no es seguro (versión, licencia, mantenimiento,
límites), propón comprobarlo. **Lo que no esté en esta lista pide permiso
al instalarse.**

Las de interfaz (componentes, iconos, animación, fuentes) se eligen en la
fase 6, con las referencias delante. Las de pruebas, en la 7.

## 6. Diseño visual

Solo si hay interfaz: **`/direccion-visual`**. Queda en `docs/diseno.md`.

## 7. Forma de trabajo de este proyecto

Cuánto proceso compensa, según el alcance. Recomienda según esta tabla y
deja que el humano cambie cualquier casilla:

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

- **el comando que verifica todo** (tests, lint, tipos, build, auditoría de
  dependencias, según lo que se haya elegido) y el comando de mutantes, si
  los hay, en `docs/convenciones.md`. La feature de andamiaje los deja
  funcionando y demuestra que cada paso sabe fallar;
- **si se pasa un escáner de secretos** (por ejemplo, gitleaks) antes del
  primer push: un secreto commiteado y borrado sigue en el historial;
- **las zonas críticas**, si las hay (dinero, escritura de datos, permisos,
  parsers, fechas…);
- **los riesgos propios de seguridad** (3-6, del más grave al menos), en
  `docs/seguridad.md`, borrando los apartados condicionales que no
  apliquen;
- **las convenciones** (`docs/convenciones.md`). Propón en bloque lo
  estándar del stack elegido (estructura de carpetas y fronteras, manejo de
  errores, tipos, tests por capa y, si hay interfaz, el bloque web), para
  que el humano lo acepte de una vez o abra lo que quiera. Pregunta solo lo
  que es preferencia suya: en qué idioma van el código y los textos de la
  interfaz, si hay patrones que quiere prohibir o exigir, y el formato de
  ramas y mensajes de commit. Si quiere fundamentarlas mejor, ofrécele la
  investigación a fondo. Los comandos los completa F00;
- **las skills para los agentes según el stack**, si están instaladas: con
  React, `vercel-react-best-practices` y `vercel-composition-patterns` en el
  `implementer`; con Python, `modern-python`; con usuarios o servidor,
  `prd-securability-enhancement` para escribir las specs. Con el sí del
  humano, se añaden en `skills:` del agente y se ponen en `name-only` en
  `skillOverrides` de `.claude/settings.json`.

## Cierre

Comprueba que:

- no queda ninguna decisión abierta sin aplazar con su disparador;
- nada se contradice entre fases;
- la primera feature se puede construir sin preguntas de arquitectura
  pendientes.

Enseña un resumen de una pantalla: qué se decidió en cada fase, qué es
revisable y cuándo, y la primera feature. **Con el sí explícito del
humano**, escribe `Estado: aprobado (AAAA-MM-DD)` en `docs/proyecto.md` y
rellena `CLAUDE.md` (qué es el proyecto y el resumen del stack). Si la
carpeta no es todavía un repositorio git, propón `git init`. Después,
**propón el primer commit** (la plantilla y los documentos del arranque),
tras mirar `git status`: los revisores comparan contra `HEAD`, y sin un
commit previo no hay con qué comparar. Desde ahí se construye siguiendo
`docs/forma-de-trabajo.md`.

Si más adelante cambia una decisión de base, se vuelve a su fase, se
actualiza `docs/proyecto.md` y solo entonces se sigue.
