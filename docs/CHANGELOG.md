# Cambios en docs/

Una entrada por cambio, la más reciente arriba. **Obligatoria**: el
pre-commit y el CI rechazan un cambio en `docs/` que no toque este fichero.
Junto a la regla cambiada, la marca `<!-- ajuste-AAAA-MM-DD -->`, para que la
retrospectiva pueda medir si sirvió.

Formato:

```
## AAAA-MM-DD — <título corto>
- Ficheros: docs/<…>.md
- Antes → ahora: <regla anterior> → <regla nueva>
- Por qué: <dato o incidente: FNN ITn, auditoría, métrica>
- Aprobado por: <humano>
- Propagado a: <CLAUDE.md, .claude/agents/x.md, CHECKPOINTS.md…> o "nada: <motivo>"
- Cómo se medirá: <qué mirar en metrics.csv o en los veredictos, si aplica>
```

## 2026-10-03 — Hotfix sin excepción "urgente" y etiqueta ATAJO:
- Ficheros: docs/specs.md, docs/principios.md
- Antes → ahora: hotfix "delante si es urgente" → siempre justo tras la
  feature en curso; atajo "comentario con su límite" → etiqueta literal
  `ATAJO: <límite> · <camino de mejora>`
- Por qué: delante de la feature en curso quedaban dos en curso (rompe
  test_como_mucho_una_feature_en_curso); sin etiqueta fija la retrospectiva
  no puede encontrar los atajos
- Aprobado por: <humano>
- Propagado a: .claude/skills/auditoria-seguridad/SKILL.md,
  .claude/skills/retrospectiva/SKILL.md, HARNESS.md

## <AAAA-MM-DD> — Creación de docs/ desde la plantilla
- Ficheros: todos los de docs/
- Antes → ahora: — → reglas iniciales del harness
- Por qué: arranque del proyecto
- Aprobado por: <humano>
- Propagado a: nada: es el punto de partida
