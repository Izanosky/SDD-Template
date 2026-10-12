---
name: arranque
description: Ronda inicial de un proyecto nuevo - entrevista al humano en orden (requisitos, alcance, aspectos clave segun el alcance, stack, librerias y diseno visual) con una recomendacion en cada pregunta, y deja las decisiones en docs/proyecto.md y docs/diseno.md. Usar al empezar un proyecto, cuando docs/proyecto.md no existe o no esta aprobado, o para revisar una fase.
---

# Arranque

Lo que hace un equipo de verdad antes de escribir código: entender qué se
construye, para quién y con qué ambición, y solo entonces elegir cómo. Cada
fase depende de las anteriores; **no se pregunta por tecnología antes de
saber qué hace la aplicación**.

| Fase | Pregunta | Queda en |
|---|---|---|
| 1. Requisitos | ¿qué hace y para quién? | `docs/proyecto.md` |
| 2. Alcance | ¿para uno mismo o para muchos? | `docs/proyecto.md` |
| 3. Aspectos clave | ¿qué exige ese alcance? | `docs/proyecto.md` |
| 4. Stack | ¿con qué se construye? | `docs/proyecto.md` |
| 5. Librerías | ¿qué piezas usamos encima? | `docs/proyecto.md` |
| 6. Diseño visual | ¿cómo se ve? (si hay interfaz) | `docs/diseno.md` |

## Cómo preguntar

- **Manda el humano.** Tú propones y recomiendas; él decide. No investigues
  nada sin su sí, y antes di qué mirarías y cuánto costaría.
- **Entrevista, no formulario**: una rama hasta cerrarla antes de abrir
  otra. Cada pregunta lleva **tu recomendación y su porqué**. Las preguntas
  abiertas, de una en una. Las cerradas, en tandas de hasta 4
  (`AskUserQuestion`), con la recomendada primero. Lo obvio, en bloque para
  aceptarlo de una vez.
- **"No lo sé" vale**: explica en dos líneas qué está en juego, recomienda y
  apúntalo como "por recomendación", que lo deja revisable.
- **Tú traes lo que el humano no sabe que necesita** (fase 3), aunque nadie
  lo haya mencionado.
- **Proporcional al alcance**: un proyecto personal no carga con preguntas
  de escalado.
- **Lo que ya dice el repositorio no se pregunta**: se lee y se confirma.
- **Se escribe sobre la marcha**: copia `proyecto.md` (de esta carpeta) a
  `docs/proyecto.md` al empezar y actualízalo al cerrar cada fase. Así se
  puede retomar en otra sesión.

## 1. Requisitos

Qué es, para quién y qué problema resuelve. Qué puede hacer el usuario
(acciones concretas, no adjetivos). Qué entra en la primera versión y **qué
no**. Qué datos maneja y de dónde salen. En qué dispositivos se usa, ahora
y más adelante. Sigue tirando del hilo cuando una respuesta abre otra.

Cierra la fase con la **lista de features** en orden: la primera, la más
pequeña que aporte valor.

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
si se aceptan perderlos. Con **compartido** o **producción**, recorre
`catalogo.md` (en esta carpeta) y trae cada tema que aplique: qué es en una
línea, por qué importa en este producto y tu propuesta. **Lo que es caro
cambiar después se decide ahora**; lo barato se aplaza con el disparador
que lo traerá.

## 4. Stack

Forma de la arquitectura (monolito, cliente-servidor, serverless,
local-first…), lenguaje, framework, base de datos y dónde se despliega.
Primero pregunta si el humano ya tiene preferencias o vetos (lo que conoce,
lo que quiere aprender, servicios que ya usa). Si no los tiene, propón 2-3
opciones con pros, contras y tu recomendación para **este** alcance.

Antes de cerrar la fase, apunta los **supuestos de riesgo**: lo que, si
resulta falso, obliga a cambiar el stack (que una librería corra en la
plataforma, que un plan gratuito aguante). Se comprueban en la primera
feature, antes de escribir producto.

## 5. Librerías

Lo que va encima del stack: acceso a datos, validación, autenticación,
estado y caché en el cliente, formularios, tests… Solo lo que pidan los
requisitos y el alcance. Cada librería, con su versión, para qué sirve y la
alternativa descartada. Antes de cualquier dependencia, mira si basta con
lo nativo. Si un hecho no es seguro (versión, licencia, mantenimiento,
límites), propón comprobarlo.

Las de interfaz (componentes, iconos, animación, fuentes) se eligen en la
fase 6, con las referencias delante.

## 6. Diseño visual

Solo si hay interfaz. Sigue `diseno.md` (en esta carpeta): referencias
reales que aporta el humano, tres direcciones para comparar, librerías de
interfaz y tokens. Queda en `docs/diseno.md`.

## Cierre

Comprueba que no queda ninguna decisión abierta sin aplazar, que nada se
contradice y que la primera feature se puede construir sin preguntas de
arquitectura pendientes. Enseña un resumen de una pantalla: qué se decidió
en cada fase, qué es revisable y cuándo, y la primera feature. **Con el sí
explícito del humano**, escribe `Aprobado: AAAA-MM-DD` en
`docs/proyecto.md` y rellena `CLAUDE.md` (qué es el proyecto y el resumen
del stack). Desde ahí se construye siguiendo `docs/forma-de-trabajo.md`.

Si más adelante cambia una decisión de base, se vuelve a su fase y se
actualiza `docs/proyecto.md` antes de seguir.
