# <Nombre del proyecto>

Estado: en curso
<!-- Al final del arranque, con el sí del humano: "Estado: aprobado (AAAA-MM-DD)". -->

## 1. Requisitos

<Qué es, para quién, qué problema resuelve. Qué puede hacer el usuario.
Qué entra en la primera versión y qué no. Datos que maneja. Dispositivos.>

## 2. Alcance

<Personal / compartido / producción, y por qué: usuarios, consecuencias de
un fallo, dinero o datos sensibles, presupuesto, plazos.>

## 3. Aspectos clave

| Tema | Decisión | Ahora / aplazado (disparador) | Por qué |
|---|---|---|---|
| | | | |

## 4. Stack

| Pieza | Elección | Alternativa descartada | Por qué |
|---|---|---|---|
| Arquitectura | | | |
| Lenguaje y framework | | | |
| Datos | | | |
| Despliegue | | | |

### Componentes, flujo de datos y carga

<Con alcance compartido o producción: diagrama en texto de las piezas y
lo que se dicen, y la estimación de carga (usuarios, peticiones en el pico,
volumen de datos al año).>

### Supuestos de riesgo

1. <Supuesto> — cómo lo comprueba la feature de andamiaje.

### Restricciones del entorno

Datos que caducan: cada fila con su fecha y su fuente.

| Restricción | Valor (fecha, fuente) | Consecuencia de diseño |
|---|---|---|
| <memoria o CPU del hosting, arranque en frío, cuotas, límites de un plan> | | |

## 5. Librerías

Lo que no esté aquí pide permiso al instalarse.

| Librería | Versión | Para qué | Alternativa descartada |
|---|---|---|---|
| | | | |

## 6. Diseño visual

Ver `docs/diseno.md`.

## 7. Forma de trabajo

| | Decidido |
|---|---|
| Spec antes de construir | |
| Pruebas | |
| Zonas críticas (con mutantes) | |
| Revisión funcional | |
| Revisión de seguridad | |
| Auditoría completa | |
| Ramas y commits | un commit por feature, lo aprueba el humano |
| Skills de los agentes según el stack | |

Los comandos (verificar, mutantes, datos falsos) están en
`docs/convenciones.md`. Riesgos propios de
seguridad: `docs/seguridad.md`.

Cambios a esta sección a mitad de proyecto, con su fecha y su motivo, para
que la retrospectiva pueda ver si sirvieron:

- <AAAA-MM-DD — qué cambió · por qué · quién lo decidió>

## Decisiones revisables

- <Decisión> — revisar cuando <disparador>.

## Features

Una por línea, en orden. Al cerrarla, `[x]` con la fecha y el commit.

- [ ] F00 — Andamiaje: generador oficial, "hola mundo" de punta a punta,
  comando de verificación y supuestos de riesgo comprobados.
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

Lo que falla o estorba de la forma de trabajo, apuntado en el momento:
qué pasó, cuánto costó y de qué feature e iteración salió. Sin proponer
todavía el arreglo. Lo lee la `/retrospectiva`. *En la prueba anterior,
este diario fue lo que más sirvió para mejorar la plantilla.*

- <AAAA-MM-DD — qué pasó · coste · (FNN ITn)>
