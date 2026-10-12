# Cambios en docs/

Una entrada por cambio, la más reciente arriba. El pre-commit (y el CI, si
lo hay) avisa de un cambio en `docs/` que no toque este fichero.
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

## 2026-10-12 — Perfil del proyecto, CI opcional y el harness al servicio del humano
- Ficheros: docs/CHANGELOG.md, docs/security.md, docs/README.md
- Antes → ahora: HARNESS.md y su test viajaban al proyecto y ponían el CI
  en rojo cada vez que se adaptaba un fichero → `/arranque` los borra en el
  paso 0. El CI era obligatorio → lo decide el perfil (personal, compartido,
  producción) y un rojo avisa sin bloquear. El CHANGELOG de `docs/` lo
  exigían el pre-commit y el CI → avisan. `CLAUDE.md` separa las reglas
  duras (no se relajan) de lo que es "por defecto" (lo cambia el humano, y
  el leader propone cambiarlo cuando estorba). `/arranque` pasa a ser una
  entrevista con recomendación en cada pregunta y trae `catalogo.md`
  (caché, pooling, escalado, observabilidad…) para los perfiles compartido
  y producción
- Por qué: en el piloto el CI fallaba por HARNESS.md desfasado, y el
  harness se vivía como una atadura en lugar de como una ayuda
- Aprobado por: humano (2026-10-12)
- Propagado a: CLAUDE.md, .claude/agents/leader.md,
  .claude/skills/arranque/ (SKILL.md, catalogo.md), plantillas/arranque.md,
  .githooks/pre-commit, .github/workflows/ci.yml, feature_list.json,
  tests/test_docs_changelog.py, HARNESS.md
- Cómo se medirá: en el próximo proyecto, número de fallos de CI o del
  pre-commit que no fueran del producto, y preguntas del arranque que el
  humano respondió con "no lo sé" (tienen que salir con recomendación)

## 2026-10-11 — Seguridad en serie, tras el reviewer
- Ficheros: docs/specs.md
- Antes → ahora: en el último tramo, reviewer y security_reviewer en
  paralelo sobre cada IT → primero el reviewer; el security_reviewer solo
  sobre una IT que el reviewer aprobó (sigue siendo solo en el último
  tramo). Cualquier rechazo abre una IT que vuelve a pasar por el reviewer
- Por qué: en el piloto el reviewer rechazó 49 de 96 revisiones; en
  paralelo, la mitad de las pasadas de seguridad (~61 k tokens cada una)
  caían en IT que iban a rehacerse, para ganar unos 3 minutos
- Aprobado por: autor de la plantilla
- Propagado a: scripts/state.py (y sus tests), .claude/agents/leader.md,
  reviewer.md, security_reviewer.md, plantillas/stack/conventions.md,
  HARNESS.md
- Cómo se medirá: `comparar.py`, "Pasadas del security_reviewer" por
  feature frente a la línea base

## 2026-10-11 — Foto del árbol por IT y quién ejecuta `init.sh` completo
- Ficheros: docs/specs.md, docs/verification.md
- Antes → ahora: el security_reviewer revisaba "desde su commit base"
  (`git rev-parse HEAD`) → desde la foto de `IT1` (`scripts/foto.sh`, un
  árbol de git con lo no seguido, sin commits); `init.sh` completo "en el
  security_reviewer, el cierre y el CI" → en el implementer antes de
  entregar (ya lo pedía su definición), el security_reviewer y el CI (el
  cierre solo edita texto)
- Por qué: las IT no se commitean, así que "el diff de la IT" no existía
  (piloto F08 IT4: el reviewer no pudo comparar con IT3); la base fallaba
  sin commits y arrastraba la feature anterior si no se había commiteado
- Aprobado por: autor de la plantilla
- Propagado a: .claude/agents/leader.md, reviewer.md, security_reviewer.md,
  CHECKPOINTS.md, init.sh, HARNESS.md
- Cómo se medirá: rechazos con causa `otro` por diffs mal leídos

## 2026-10-11 — Copias, procesos y cambios de rumbo sin pisar a nadie
- Ficheros: docs/verification.md
- Antes → ahora: sin regla sobre el scratchpad, las copias ni los procesos
  → cada agente en `<scratchpad>/<F>-IT<n>-<rol>/`, copias sin enlaces a
  `node_modules`/`.venv` (o el enlace se quita antes de borrar), procesos
  por PID (el hook bloquea matar por nombre y reescribir la historia).
  Fuera de docs/: IT descartable con `descartada.md` y reabrir una `done`
  como feature nueva (leader.md, state.py)
- Por qué: piloto (Gestor): `mut.py` pisado entre agentes (F13a IT2),
  junction a `node_modules` a un `rm -rf` de vaciarlo (F12 IT5),
  `taskkill` de todos los `node` (F03 IT6), IT de un framework abandonado
  sin forma de descartarla (F01 IT4), F13a reabierta a mano
- Aprobado por: autor de la plantilla
- Propagado a: .claude/agents/leader.md, scripts/guard_secrets.py,
  scripts/state.py, plantillas/stack/conventions.md (carpeta de trabajo de
  los mutantes fuera de tests y lint), .gitignore, HARNESS.md
- Cómo se medirá: en `para_la_plantilla.md`, ningún caso nuevo de esos

## 2026-10-10 — Menos iteraciones: mutantes por stack, vetos al final y en paralelo
- Ficheros: docs/verification.md, docs/specs.md
- Antes → ahora: mutantes a criterio de cada rol en todo el código → la
  herramienta de mutantes del stack, en zonas críticas, con el mismo comando
  para implementer y reviewer (fuera de ellas, un test flojo es una
  observación); TDD obligatorio → rojo demostrado por el mutante o el
  sabotaje; security_reviewer en cada tramo y después del reviewer → solo en
  el último tramo, en paralelo, sobre la feature entera; re-revisión
  completa siempre → acotada si el arreglo solo toca tests; `init.sh`
  completo en cada vuelta → `--rapido` para implementer y reviewer; tramos
  sin límite → dos como mucho; tests intermitentes anotados → se arreglan
  en la siguiente IT; task humana para mirar la interfaz → solo con
  servicios reales
- Por qué: piloto (Gestor): 42 de 44 primeras entregas rechazadas (31 por
  `tests`); IT de corrección = 37 % del tiempo y 41 % de los tokens;
  security 46 pasadas y 2 rechazos (131 min, 2,8 M tokens); 8 tests
  intermitentes sin arreglar; 9 features seguidas sin task humana
- Aprobado por: autor de la plantilla
- Propagado a: scripts/state.py (vetos por tramo), scripts/metricas.py
  (hook SubagentStop: el leader ya no escribe métricas), init.sh y
  plantillas/stack/ (--rapido, comando de mutantes), .claude/agents/
  (implementer, reviewer, security_reviewer, spec_author, leader),
  .claude/skills/arranque, plantillas/arranque.md, HARNESS.md
- Cómo se medirá: primeras entregas aprobadas, IT por feature y tokens por
  feature en metrics.csv frente al piloto

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
- Aprobado por: autor de la plantilla
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
- Aprobado por: autor de la plantilla
- Propagado a: .claude/skills/auditoria-seguridad/SKILL.md,
  .claude/skills/retrospectiva/SKILL.md, HARNESS.md

## <RELLENAR: AAAA-MM-DD> — Creación de docs/ desde la plantilla
- Ficheros: todos los de docs/
- Antes → ahora: — → reglas iniciales del harness
- Por qué: arranque del proyecto
- Aprobado por: <RELLENAR: humano>
- Propagado a: nada: es el punto de partida
