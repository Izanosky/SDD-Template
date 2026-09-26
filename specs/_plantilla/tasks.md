# FNN — <Título> · Tasks

Concisa: cada task remite a design.md, no lo repite.

- [ ] **T1 — <título>** (TDD). <Qué se prueba primero y qué se implementa.> → R1, R2
- [ ] **T2 — Test del adaptador real** con cliente grabador: filtros exactos, valores escritos, ramas de lectura. → R3
- [ ] **T3 — Cierre sin servicios reales.** `init.sh` y `pytest tests/` en verde; comprobaciones estáticas: <lista>.
- [ ] **T4 — PRUEBA REAL · la ejecuta el humano.** Aviso: conecta con <servicios>. Pasos en orden ejecutable, resultado esperado de cada uno, ningún secreto pegado. → humo de R1, R3

## Mapa inverso

| Requisito | Task |
|---|---|
| R1, R2 | T1, T4 |
| R3 | T2, T4 |
