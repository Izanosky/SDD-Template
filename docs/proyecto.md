# <Nombre del proyecto>

Estado: en curso
<!-- Lo rellena /arranque. Al final del arranque, con el sí del humano:
"Estado: aprobado (AAAA-MM-DD)". -->

Las decisiones están cada una en su documento: `arquitectura.md`,
`stack.md`, `diseno.md`, `proceso.md`, `convenciones.md` y `seguridad.md`.
Este fichero es el producto y el día a día.

## Qué es

<Qué es, para quién y qué problema resuelve. Qué puede hacer el usuario.
Qué entra en la primera versión y qué no. Datos que maneja. Dispositivos,
ahora y más adelante.>

## Alcance

<Personal / compartido / producción, y por qué: usuarios, consecuencias de
un fallo, dinero o datos sensibles, presupuesto, plazos.>

## Decisiones revisables

- <Decisión> — revisar cuando <disparador> (en `<documento>`).

## Features

Una por línea, en orden. Al cerrarla, `[x]` con la fecha y el commit.

- [ ] F00 — Andamiaje: generador oficial, "hola mundo" de punta a punta,
  comandos de verificación y supuestos de riesgo comprobados.
- [ ] F01 — <La feature de producto más pequeña que aporte valor.>

## Estado actual

<Feature en curso, su iteración (`progress/FNN/IT<n>/`) y en qué paso del
ciclo está (spec, aprobada, implementando, revisión, seguridad, visto
bueno, commit). Se reescribe en cada paso.>

## Pendiente

- <Lo que espera al humano, observaciones abiertas que no bloquean, tests
  intermitentes y arreglos que quedan para la siguiente feature. Se quita
  lo hecho.>

## Lecciones

Lo que falla o estorba de la forma de trabajo, apuntado en el momento por
la sesión principal (cuándo, en `.claude/rules/harness.md`): qué pasó,
cuánto costó y de qué feature e iteración salió. Sin proponer todavía el
arreglo. Lo lee la `/retrospectiva`.

- <AAAA-MM-DD — qué pasó · coste · (FNN ITn)>
