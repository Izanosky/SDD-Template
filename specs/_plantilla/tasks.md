# FNN — <Título> · Tasks

Concisa: cada task remite a design.md, no lo repite. Con varios stacks o
capas, un tramo por bloque, en orden de dependencia; cada tramo es una IT.

## Tramo A — <stack o capa que los demás consumen>
- [ ] **T1 — <título>** (TDD). <Qué se prueba primero y qué se implementa.> → R1, R2
- [ ] **T2 — Test del adaptador real** con cliente grabador: filtros exactos, valores escritos, ramas de lectura. → R3

## Tramo B — <siguiente>
- [ ] **T3 — <título>**. <…> → R4

## Cierre
- [ ] **T4 — ÚNICA TASK CON SERVICIOS REALES · la ejecuta el humano.** Aviso: conecta con <servicios>. Pasos en orden ejecutable, resultado esperado de cada uno, ningún secreto pegado. → humo de R1, R3

<!-- Si no hay servicios reales, borra T4. La cabecera "SERVICIOS REALES" es
un marcador que lee scripts/state.py: no la traduzcas. -->

## Mapa inverso

| Requisito | Task |
|---|---|
| R1, R2 | T1, T4 |
| R3 | T2, T4 |
| R4 | T3 |
