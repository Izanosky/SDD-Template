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

Datos: `progress/metrics.csv`, `progress/*/IT*/review.md` y `security.md`,
`progress/history.md`, `docs/CHANGELOG.md`.

- Iteraciones por feature y **causa de cada rechazo** (`codigo`, `tests`,
  `spec`, `otro`). Qué tipo de rechazo cuesta más tokens.
- **Cada ajuste del CHANGELOG, si sirvió**: compara `metrics.csv` antes y
  después de su fecha.
- **Reglas muertas**: las que ningún veredicto ni `impl.md` citó nunca.
  Candidatas a borrarse (con su entrada en el CHANGELOG).
- **Coste por rol y por feature** (tokens y minutos).
- Ejecuta `/doctor prompt-audit` sobre `CLAUDE.md`, `.claude/agents/` y
  `.claude/skills/`: propone recortes y detecta contradicciones.
- Lo trasladable a otros proyectos, a `progress/para_la_plantilla.md`.

## 2. El código

- Auditoría de seguridad completa (`/auditoria-seguridad`).
- Sobreingeniería y deuda: revisión del repo entero buscando código que
  sobra, y los atajos marcados a propósito en el código.

## 3. El producto (solo lo sabe el humano)

Qué se usa y qué no; qué falló con servicios reales (las tasks humanas);
qué pidió la gente y nunca llegó a `feature_list.json`.
