---
name: retrospectiva
description: Retrospectiva del proyecto al terminar (TODO_HECHO) o al cerrar una fase. Mide el harness con datos y propone mantener, cambiar o quitar.
disable-model-invocation: true
---

# Retrospectiva

Sale un único documento, `progress/retrospective.md`, con tres columnas:
**mantener, cambiar, quitar**. Cada fila cita el dato que la justifica.
Tres frentes, en este orden.

## 1. El proceso (lo que se lleva a otro proyecto)

Datos, del más barato al más caro: `progress/metrics.csv` (ya trae el
veredicto y la causa de cada rechazo), `progress/history.md` y
`docs/CHANGELOG.md`. Los `review.md` y `security.md` **no se leen enteros**:
busca sus líneas `Veredicto:` y abre uno concreto solo para explicar un caso
raro (una feature con muchas IT, una causa `otro`) o para comprobar una
regla candidata a quitar (abajo): ahí busca el fallo que esa regla evita.

- Iteraciones por feature y **causa de cada rechazo** (`codigo`, `tests`,
  `spec`, `otro`). Qué tipo de rechazo cuesta más tokens.
- **Cada ajuste del CHANGELOG, si sirvió**: compara `metrics.csv` antes y
  después de su fecha. Con pocas features es un indicio, no una prueba:
  dilo.
- **Reglas candidatas a quitar**: que nadie cite una regla no prueba que
  sobre; puede ser justo la que evita el fallo. Es candidata solo si no sale
  de ninguna lección (su comentario "Leccion:" o una entrada del CHANGELOG)
  y el fallo que previene no aparece en ningún veredicto. Quitarla lo decide
  el humano, con su entrada en el CHANGELOG.
- **Coste por rol y por feature** (tokens y minutos).
- **Instrucciones**: `/doctor prompt-audit` (skill de serie de Claude Code,
  v2.1.283+, según code.claude.com/docs/en/commands, consultado el
  2026-10-03; si no puedes lanzarla tú, pídesela al humano) sobre
  `CLAUDE.md`, `.claude/agents/` y `.claude/skills/`: instrucciones
  obsoletas o contradictorias. Cada recorte propuesto, con fichero, línea y
  motivo.
- Lo trasladable a otros proyectos, a `progress/para_la_plantilla.md`.

## 2. El código

- **Auditoría de seguridad**: con el mismo criterio que el leader (4 o más
  features cerradas desde la última carpeta de `progress/audits/`, o una
  fase cerrada), propónsela al humano.
  `/auditoria-seguridad` solo se invoca a mano: tú no puedes lanzarla.
- **Atajos**: busca la etiqueta `ATAJO:` (`docs/principios.md`) en el
  código. Para cada uno: mantener, pagarlo ya o convertirlo en feature.
- **Sobreingeniería**, solo si el humano lo pide (recorre el repo entero):
  lanza `explorer` con el encargo "código que sobra: abstracciones con una
  sola implementación, código muerto, lo que ya hace la librería estándar o
  una dependencia instalada". Escribe `progress/explore_sobreingenieria.md`;
  aquí va solo su resumen.

## 3. El producto (solo lo sabe el humano)

Qué se usa y qué no; qué falló con servicios reales (las tasks humanas);
qué pidió la gente y nunca llegó a `feature_list.json`.
