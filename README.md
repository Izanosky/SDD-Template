# Plantilla de harness SDD para Claude Code

Plantilla para desarrollar un proyecto con **Claude Code como equipo de
agentes con puertas de calidad**, siguiendo *Spec-Driven Development* (SDD):
ninguna feature se implementa sin una spec aprobada por un humano (salvo las
marcadas como ligeras), nada se da por hecho sin verificación ejecutable y
quien escribe el código no lo aprueba.

Agnóstica de lenguaje y stack. Lo que depende del proyecto está marcado
`<RELLENAR>`.

> **[HARNESS.md](HARNESS.md) basta por sí solo**: explica el porqué de cada
> pieza (Parte I) y contiene el contenido literal de todos los ficheros
> (Parte II), extraíbles con una orden. Este README es el resumen.

## Cómo funciona

```
feature_list.json          specs/<F>/                 progress/<F>/IT<n>/
   (qué hacer)       (requirements, design, tasks)   (impl, review, security)

 pending ──spec_author──> spec_ready ──HUMANO──> in_progress ──vetos──> done
                                        aprueba     │
                                                    ├─ implementer  → impl.md + evidence.md (## Sabotajes)
                                                    ├─ reviewer     → review.md   (Veredicto: …)
                                                    └─ security_rev → security.md (Veredicto: …)
```

- La sesión principal de Claude Code actúa como **`leader`**. Ejecuta
  `scripts/state.py`, que dice qué feature toca y qué acción, y lanza el
  subagente que corresponde. Los arreglos pequeños (sin comportamiento nuevo
  ni zonas sensibles) los hace él mismo.
- El **estado se deriva del disco**. Un rechazo abre una iteración nueva, y
  solo hay `done` con ambos veredictos `APPROVED` en la misma iteración.
- **Modo ligero** (`"sdd": false`): sin spec ni aprobación previa; se
  mantienen los dos vetos.
- `init.sh` es la puerta: tests, lint, formato, tipos, build, secretos y
  dependencias.

| Rol | Modelo | Qué hace |
|---|---|---|
| `leader` | el de la sesión | despacha, crea las IT, arreglos pequeños, métricas |
| `spec_author` | opus | escribe `specs/<F>/` |
| `explorer` | sonnet | investiga y deja hallazgos citados |
| `implementer` | sonnet | código, tests (TDD + sabotajes), cierre |
| `reviewer` | opus | veto funcional, con mutantes |
| `security_reviewer` | opus | veto de seguridad; auditoría completa |

## Requisitos

- Claude Code y git.
- bash (en Windows, Git Bash).
- Python 3.10+ con pytest, solo para el harness, sea cual sea el lenguaje del
  proyecto.
- [gitleaks](https://github.com/gitleaks/gitleaks).
- Las toolchains de tus stacks.

## Puesta en marcha

```bash
cp -r harness-sdd-template mi-proyecto && cd mi-proyecto   # o: extrae HARNESS.md (sección 3)
git init
git config core.hooksPath .githooks
git add -A
git update-index --chmod=+x init.sh scripts/*.sh .githooks/pre-commit plantillas/stack/init.sh
grep -rn "<RELLENAR" .      # lo que hay que rellenar
```

La lista completa de qué rellenar y en qué orden está en la sección 3 de
HARNESS.md; las decisiones previas, en su Anexo C. Atajo: abre Claude Code y
pide "rellena los `<RELLENAR>` de esta plantilla para <tu proyecto>;
pregúntame lo que no sepas".

## Uso diario

1. Abre Claude Code en la raíz. El hook de sesión inyecta el estado y la
   sesión actúa como `leader`.
2. Dile que continúe. Tus puntos de intervención:
   - aprobar cada spec;
   - aprobar dependencias nuevas y cambios en `docs/` (cada cambio, con su
     entrada en `docs/CHANGELOG.md`);
   - ejecutar las tasks con servicios reales;
   - hacer los commits (Claude Code te los pide confirmar).
3. Skills del harness: `/auditoria-seguridad` (con tu confirmación: es cara) y `/retrospectiva`.

## Comandos

```bash
bash scripts/py.sh scripts/state.py   # qué feature toca y qué acción (JSON)
bash init.sh                          # verifica el scope de la feature activa
bash init.sh --all                    # verifica todos los stacks (lo usa el CI)
bash scripts/py.sh -m pytest tests/ -q   # tests del harness
bash scripts/py.sh scripts/harness_bundle.py  # regenera la Parte II de HARNESS.md
```

## Mantener la plantilla

Tras cambiar cualquier fichero, ejecuta `bash scripts/py.sh scripts/harness_bundle.py`.
`tests/test_harness_bundle.py` falla si HARNESS.md no coincide con los
ficheros, así que la guía nunca se queda atrás.
