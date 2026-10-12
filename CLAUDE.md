# <NOMBRE_DEL_PROYECTO>

<Qué es y para quién, en 3-5 líneas. Lo rellena /arranque.>

## Forma de trabajo

1. **Arranque** (`/arranque`): si `docs/proyecto.md` no existe o no dice
   `Estado: aprobado`, se empieza por ahí. Es una entrevista en este orden:
   requisitos → alcance → aspectos clave → stack → librerías → diseño
   visual → forma de trabajo del proyecto.
2. **Construir**, feature a feature, según `docs/forma-de-trabajo.md`. Léelo
   antes de la primera feature y cuando dudes de cómo seguir.

**Si eres la sesión principal**: al empezar, lee "Features", "Estado
actual" y "Pendiente" de `docs/proyecto.md` y dile al humano por dónde va el
proyecto. Hablas con él, escribes las specs (skill `entrevista`), creas las
carpetas `progress/FNN/IT<n>/`, lanzas a los agentes (`explorer`,
`implementer`, `reviewer`, `security_reviewer`) y mantienes al día
`docs/proyecto.md`. **Si eres uno de esos agentes**, sigue tu definición:
este fichero es solo contexto.

Las decisiones son del humano. Tú propones, con recomendación y su porqué.
Si algo de esta forma de trabajo estorba en este proyecto, díselo y propón
cambiarlo en la sección 7 de `docs/proyecto.md`.

## Reglas duras

- Nada de `git commit` ni `push` sin el humano; nunca `--amend`,
  `push --force` ni reescribir la historia. El historial es la evidencia de
  qué feature introdujo qué.
- Ninguna dependencia nueva sin preguntar, con una alternativa sin ella.
- Los secretos no pasan por el contexto: no se leen `.env` ni claves, no se
  imprimen y no se copian.
- Nada destructivo sobre datos reales (`DROP`, `TRUNCATE`, o `DELETE` y
  `UPDATE` sin `WHERE`).
- Avisar antes de tocar servicios reales y de lo que cuestan.
  <Política de coste del proyecto, p. ej. "solo planes gratuitos". La
  rellena /arranque.>

## Proyecto

<Resumen del stack y del comando que verifica todo. Lo rellena /arranque.
El detalle está en `docs/proyecto.md`; los comandos y las convenciones, en
`docs/convenciones.md`; la seguridad, en `docs/seguridad.md`; y, si hay
interfaz, el diseño en `docs/diseno.md`.>

## Al compactar

Conserva la feature en curso, su iteración y su paso del ciclo; lo que
espera al humano; y los ficheros modificados sin commitear.
