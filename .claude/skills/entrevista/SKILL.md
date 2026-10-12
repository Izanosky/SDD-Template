---
name: entrevista
description: Metodo para sacar del humano toda la informacion necesaria sin dar nada por supuesto - rondas de preguntas sobre el arbol de decisiones, cada una con recomendacion, hasta que no quede ninguna rama abierta. La usan /arranque y la sesion principal antes de una spec; tambien sirve sola ("entrevistame sobre X").
---

# Entrevista

Inspirada en `grill-me` de Matt Pocock (MIT). Si `grill-me` está
instalada, esta skill la sustituye dentro del harness, con lo aprendido en
las pruebas.

El objetivo es llegar a **un entendimiento compartido sin nada supuesto**.
Una decisión que nadie tomó, la acaba tomando el código por omisión, y
cambiarla después cuesta.

## El árbol de decisiones

Cada decisión cuelga de otras: no se elige la base de datos sin saber qué
datos hay ni quién los ve. Trabaja el árbol **por rondas**. La **frontera**
son las decisiones cuyos requisitos previos ya están resueltos, es decir,
las que se pueden preguntar ahora sin adivinar respuestas que aún no has
oído.

- Cada ronda pregunta la frontera, **como mucho 4 preguntas por ronda**.
  Es un tope por ronda, **no en total**: se hacen tantas rondas como haga
  falta, hasta que no quede ninguna decisión abierta. *En un piloto, una
  ronda con todas las decisiones a la vez acabó en respuestas de "sigue".*
  Si la frontera es más grande, empieza por lo que más condiciona al resto
  y deja lo demás para las rondas siguientes. Si el humano prefiere rondas
  más largas o más cortas, se ajusta.
- Una pregunta que depende de otra que sigue abierta en esta ronda va a la
  ronda siguiente, no a esta.
- Cada respuesta cambia el árbol: recalcula la frontera antes de la
  siguiente ronda.

## Formato de cada pregunta

```
❓ **P1 · <título>**: <la pregunta, con las opciones si las hay y qué
cambia con cada una>

➡️ Recomiendo: <respuesta> — <por qué, para este proyecto>
```

Con `AskUserQuestion` disponible, las preguntas cerradas se hacen con ella:
la recomendada va primera y lleva "(Recomendado)". Lo obvio se propone en
bloque, para aceptarlo de una vez.

## Hechos frente a decisiones

- **Los hechos los buscas tú**, nunca el humano: lo que ya dice el
  repositorio, una versión, un límite de un plan. Si hace falta, lanza un
  subagente (`explorer`) y no te bloquees esperándolo: solo esperan las
  preguntas que dependen de ese hecho. Lo que cueste dinero o mucho tiempo
  (una investigación amplia, `/deep-research`), primero se le propone al
  humano con su coste.
- **Las decisiones son del humano**: se le plantean y se espera su
  respuesta.
- **"No lo sé" es una respuesta válida**: explica en dos líneas qué está en
  juego, recomienda y apúntalo como "por recomendación", lo que lo deja
  revisable.

## Cuándo termina

La entrevista termina cuando la frontera está vacía: todas las ramas
recorridas y ninguna decisión tomada en silencio. Entonces resume lo
acordado y **pide confirmación** de que es así. No actúes sobre ello hasta
tenerla. Lo decidido se escribe donde diga quien te usa
(el documento de `docs/` que toque, la spec…) a medida que se decide, para poder retomarlo
en otra sesión.
