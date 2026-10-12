# <NOMBRE_DEL_PROYECTO>

<Qué es y para quién, en 3-5 líneas. Lo rellena /arranque.>

## Forma de trabajo

1. **Arranque** (skill `arranque`): si `docs/proyecto.md` no existe o no
   dice `Aprobado`, empieza por ahí. Es una entrevista en este orden:
   requisitos → alcance → aspectos clave → stack → librerías → diseño
   visual.
2. **Construir**, feature a feature, según `docs/forma-de-trabajo.md`. Léelo
   antes de la primera feature y cuando dudes de cómo seguir.

Las decisiones son del humano. Tú propones, con recomendación y su porqué.
Si algo de esta forma de trabajo estorba en este proyecto, díselo y propón
cambiarlo.

## Reglas duras

- Nada de `git commit` ni `push` sin el humano; nunca `--amend`,
  `push --force` ni reescribir la historia.
- Ninguna dependencia nueva sin preguntar.
- Los secretos no pasan por el contexto: no se leen `.env` ni claves, no se
  imprimen y no se copian.
- Nada destructivo sobre datos reales.
- Avisar antes de tocar servicios reales y de lo que cuestan.

## Proyecto

<Resumen del stack y dónde está cada documento. Lo rellena /arranque:
`docs/proyecto.md` (requisitos, alcance, decisiones), `docs/diseno.md`.>
