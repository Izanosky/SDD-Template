---
name: retrospectiva
description: Retrospectiva al terminar el proyecto o al cerrar una fase - que mantener, cambiar o quitar de la forma de trabajo, del codigo y del producto, con el dato que lo justifica. Solo la sesion principal.
---

# Retrospectiva

Sale un único documento, `docs/retrospectiva-AAAA-MM-DD.md`, con tres
columnas: **mantener, cambiar, quitar**. Cada fila cita el dato o el
incidente que la justifica. Si con pocas features un dato es solo un
indicio, dilo.

## 1. La forma de trabajo

Fuentes, de la más barata a la más cara:

- el estado de las features, la sección "Lecciones" (el diario de lo que
  falló o estorbó) y los cambios fechados de la sección 7 en
  `docs/proyecto.md`;
- `git log`, que da un commit por feature, con su fecha;
- las carpetas `progress/FNN/IT<n>/`: el número de carpetas es el número de
  intentos, y la primera línea de cada `review.md` y `security.md` dice el
  veredicto. Lee esas líneas y abre un fichero entero solo para explicar un
  caso raro;
- las specs (`specs/`);
- las auditorías (`docs/auditorias/`);
- lo que recuerde el humano.

Qué buscar:

- **Qué costó vueltas**: features que necesitaron varias rondas de
  revisión, y por qué (código, tests, una spec ambigua…).
- **Si cada cambio de la forma de trabajo sirvió**: compara las vueltas
  por feature antes y después de su fecha.
- **Qué no aportó**: un paso que nunca cambió nada. Ojo: que nadie cite una
  regla no prueba que sobre, porque puede ser justo la que evita el fallo.
  Antes de proponer quitarla, busca el incidente que la motivó en
  `docs/forma-de-trabajo.md`.
- **Las skills**: cuáles dejaron rastro en las revisiones o en el código y
  cuáles no.
- **Lo que fue un estorbo**: pregúntaselo al humano.

Cada lección nueva se propone al humano **como recomendación con su
incidente**, para `docs/forma-de-trabajo.md`. Si sirve para otros
proyectos, también para el README de la plantilla.

## 2. El código

- **Atajos**: busca la etiqueta `ATAJO:` y decide con el humano, para cada
  uno, si se mantiene, se paga ya o pasa a ser una feature.
- **Decisiones revisables** de `docs/proyecto.md` cuyo disparador ya se
  cumplió.
- **Seguridad**: si hay 4 o más features cerradas desde la última
  auditoría, propón `/auditoria-seguridad`.
- **Sobreingeniería**, solo si el humano lo pide: `/ponytail:ponytail-audit`
  si está instalada.
- **Código frente a specs**, al cerrar una fase y solo con el sí del
  humano, porque lanza un agente por requisito:
  `/spec-to-code-compliance:spec-to-code-compliance`.

## 3. El producto (solo lo sabe el humano)

Qué se usa y qué no, qué falló con servicios reales y qué se pidió y nunca
llegó a la lista de features.
