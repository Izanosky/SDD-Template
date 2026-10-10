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

## 2026-10-10 — Interfaz con dirección visual y capturas; skills precargadas
- Ficheros: docs/specs.md, docs/verification.md, docs/README.md,
  docs/architecture.md, docs/adr/README.md (nuevo)
- Antes → ahora: decisiones de arquitectura repartidas en `CLAUDE.md` sin
  alternativas ni disparador de revisión, y la primera spec podía empezar
  con el stack a medio decidir → `/arranque` guiado por el humano (mapa de
  todas las decisiones técnicas, investigación solo la que él apruebe),
  ADR en `docs/adr/`, "Stack y librerías" en `docs/architecture.md` como
  lista de dependencias aprobadas, y `state.py` devuelve `ARRANQUE` hasta
  que el humano lo aprueba;
  el aspecto se fijaba como `R<n>` de cada spec y nadie veía
  la interfaz renderizada → dirección visual única en
  `docs/<scope>/direccion-visual.md` (skill `/direccion-visual`), tramos
  `(interfaz)` hechos por el `implementer_ui` con capturas que el `reviewer`
  revisa; skills precargadas por rol (`skills:`) en vez de "opcionales"
- Por qué: piloto (Gestor, 17 features): 0 invocaciones de skills de diseño
  en 110 ejecuciones del implementer, interfaces "hechas con IA" (paleta
  índigo y tarjetas por defecto) y fallos visuales encontrados por el humano
  (F03 T8, F09, InvestmentsPanel)
- Aprobado por: <humano>
- Propagado a: .claude/agents/ (implementer_ui nuevo, implementer,
  reviewer, security_reviewer, spec_author, explorer, leader),
  .claude/skills/ (arranque y direccion-visual nuevas, auditoria-seguridad,
  retrospectiva), .claude/settings.json (skillOverrides, guard_config),
  scripts/ (state.py, skills.py, agent_tokens.py, guard_config.py,
  guard_secrets.py),
  specs/_plantilla/tasks.md, plantillas/stack/conventions-web.md,
  harness.json, README.md, HARNESS.md
- Cómo se medirá: columna `skills` de metrics.csv; rechazos del reviewer
  por capturas frente a fallos visuales que encuentre el humano después

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
