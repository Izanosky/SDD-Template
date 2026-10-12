# Forma de trabajo (de la plantilla)

Este fichero viene de la plantilla y es igual en todos los proyectos. Lo
propio de cada proyecto está en `docs/` (cada decisión en su documento) y
en `CLAUDE.md` (comandos y lo que rompe cosas), que genera `/arranque`.

## Cómo se trabaja

1. **Arranque** (`/arranque`): si `docs/proyecto.md` no dice
   `Estado: aprobado`, se empieza por ahí. Es una entrevista en este orden:
   requisitos → alcance → aspectos clave → stack → librerías → diseño
   visual → forma de trabajo del proyecto. Cada decisión queda en su
   documento de `docs/`, y al cerrar genera el `CLAUDE.md` del proyecto.
2. **Construir**, feature a feature, según `.claude/forma-de-trabajo.md`. Léelo
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
cambiarlo en `docs/proceso.md`.

## Lecciones: las apuntas tú

Sin esperar a que te lo pidan, la sesión principal apunta en la sección
"Lecciones" de `docs/proyecto.md`, en el momento en que pasa, cada vez que:

- el humano corrige algo, se queja o repite una instrucción;
- una vuelta se rechaza por algo que la forma de trabajo debía evitar, o
  dos vueltas seguidas fallan por la misma causa;
- un agente vuelve sin terminar, se sale de su encargo o malinterpreta un
  documento;
- un hook bloquea algo legítimo, o deja pasar algo que debía parar;
- una instrucción de la plantilla es ambigua, se contradice o no sirve
  para este proyecto;
- algo cuesta mucho más de lo esperado (tiempo, vueltas, tokens).

Una línea por lección: fecha, qué pasó, cuánto costó y de qué feature e
iteración salió, sin proponer todavía el arreglo. Los agentes no editan
`docs/`: lo que vean lo dejan en su fichero de la iteración, bajo
`## Para la forma de trabajo`, y tú lo pasas a "Lecciones".

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

## Al compactar

Conserva la feature en curso, su iteración y su paso del ciclo; lo que
espera al humano; y los ficheros modificados sin commitear.
