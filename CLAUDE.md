# <NOMBRE_DEL_PROYECTO>

<RELLENAR: qué es, para quién, en 3-5 líneas.>

## Rol de sesión

**Solo si eres la sesión principal** (no un subagente lanzado con `Agent`):
actúa como `leader` y sigue `.claude/agents/leader.md`. Los subagentes siguen
su propia definición y usan este fichero solo como contexto y reglas.

Dónde está cada regla: `docs/README.md`.

## Dónde vive cada pieza, y por qué

<!-- Cada fila resuelve una restricción concreta. Borra las que no apliquen.
Alternativas descartadas y cuándo revisar cada decisión: docs/adr/. -->
| Pieza | Dónde | Por qué ahí |
|---|---|---|
| <RELLENAR: API> | <servicio> | <restricción que resuelve> |
| <RELLENAR: datos> | <servicio> | <…> |

## Restricciones que rompen cosas si se ignoran

- <RELLENAR: cada una con su motivo y su dueño en CHECKPOINTS.md.>

## Reglas duras

Protegen lo que no tiene vuelta atrás; no se relajan.

- **Nada de `git commit` ni `push` sin aprobación del humano** (los pide
  `settings.json`); nunca `--amend`, `push --force` ni reescritura de
  historia: el historial es la evidencia de qué iteración introdujo qué.
- **Ninguna dependencia nueva sin preguntar**, con una alternativa sin ella.
- **Los secretos no pasan por el contexto**: no se leen `.env` ni ficheros de
  secretos, no se imprimen, no se copian. Nombres en `harness.json`.
- **Nada destructivo sobre datos reales** (`DROP`, `TRUNCATE`, `DELETE` o
  `UPDATE` sin `WHERE`).
- **Avisar antes de tocar servicios reales** y de si cuesta dinero.
  <RELLENAR: política de coste, p. ej. "solo planes gratuitos".>

## Por defecto, y el humano manda

El resto del harness es una forma de trabajar, no una atadura. Las
decisiones son del humano, y el leader debe proponer quitar o relajar lo
que estorbe en este proyecto.

- **`docs/`, este fichero y las reglas del harness los decide el humano**;
  los agentes no los cambian por su cuenta. Cada cambio en `docs/` lleva su
  entrada en `docs/CHANGELOG.md` (el pre-commit avisa si falta).
- **`done` solo por el protocolo**: el `implementer` en el cierre, con
  `review.md` y `security.md` de la misma IT en `APPROVED`.

## Parámetros del harness

| Parámetro | Valor | Por qué |
|---|---|---|
| Perfil | <RELLENAR: personal / compartido / producción (lo fija `/arranque`)> | decide cuánto proceso compensa |
| CI | <RELLENAR: sí / no> | si lo hay, un rojo avisa pero no bloquea |
| Veredictos e `impl.md` | ≤ 200 líneas | el leader y los revisores los leen enteros; lo largo va a `evidence.md` |
| Spec (tres ficheros) | ~400 líneas (≈ 6-8 k tokens); partir pasado de 600 o de ~20 `R<n>` | cada agente la relee en cada iteración |
| Auditoría completa | <RELLENAR: según el perfil: cada 4 features cerradas o al cerrar una fase / cuando la pida el humano> | cada revisión solo mira su diff |
| Reanudaciones de un agente | 2 | a la tercera, el atasco es real |

## Comandos

```bash
bash scripts/py.sh scripts/state.py   # qué toca (JSON)
bash init.sh                          # verifica el scope activo
bash init.sh --all                    # verifica todos los stacks
bash scripts/py.sh -m pytest tests/ -q   # tests del harness
```

## Al compactar

Conserva: feature, IT y acción de `state.py`; pendientes del humano;
ficheros modificados sin commitear.

## Estado

<RELLENAR: fases, orden, bloqueos conocidos, plataformas aplazadas con fecha.>
