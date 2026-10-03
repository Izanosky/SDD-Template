# Mapa de reglas

No contiene reglas: dice dónde está cada una. Cada rol lee solo lo suyo.

| Pregunta | Documento |
|---|---|
| ¿Qué es buen trabajo aquí? | `docs/architecture.md`, `docs/principios.md` |
| ¿Baseline de seguridad? | `docs/security.md` |
| ¿Proceso SDD y formato de las specs? | `docs/specs.md` |
| ¿Cómo se demuestra que algo funciona? ¿Pruebas con servicios reales? | `docs/verification.md` |
| ¿Convenciones de código? | `docs/<stack>/conventions.md` del scope activo, **solo ese** |
| ¿Cuándo está terminada una feature? | `CHECKPOINTS.md` |
| ¿Qué cambió en las reglas y por qué? | `docs/CHANGELOG.md` |
| ¿Qué hace cada rol? | `.claude/agents/<rol>.md` |
| ¿Auditorías completas? | `progress/audits/` y la skill `/auditoria-seguridad` |
| ¿Coste de cada agente y causa de cada rechazo? | `progress/metrics.csv` |
| ¿Retrospectiva? | skill `/retrospectiva` |
| ¿Por qué el harness es así? ¿Cómo se reconstruye? | `HARNESS.md` (ningún agente lo carga al trabajar) |
