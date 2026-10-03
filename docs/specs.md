# El proceso SDD

Ninguna feature con `"sdd": true` se implementa sin spec escrita y aprobada.

```
pending ──spec_author──> spec_ready ──HUMANO──> in_progress ──vetos──> done
```

## Los tres ficheros (`specs/<F>/`, plantillas en `specs/_plantilla/`)

**`requirements.md` — el qué.** Notación EARS, `R1`, `R2`…, comportamiento
observable, nunca implementación:

| Forma | Plantilla |
|---|---|
| Ubicua | *El sistema DEBE `<respuesta>`* |
| Evento | *CUANDO `<disparador>`, el sistema DEBE `<respuesta>`* |
| Estado | *MIENTRAS `<estado>`, el sistema DEBE `<respuesta>`* |
| No deseada | *SI `<condición>`, ENTONCES el sistema DEBE `<respuesta>`* |
| Opcional | *DONDE `<característica>`, el sistema DEBE `<respuesta>`* |

Un requisito que no se puede convertir en test es un deseo ("debe ser
rápido" no; "DEBE responder en < 500 ms con 1.000 elementos" sí). Cada `R<n>`
con input enumera sus casos límite: vacío o solo espacios, longitud máxima,
caracteres de control, duplicado, servicio externo caído o lento.

**`design.md` — el cómo.** Ficheros y firmas; **alternativas descartadas y
por qué**; las cuatro preguntas de escalabilidad (`docs/architecture.md`);
preguntas al humano **con recomendación** (tras la respuesta, "Decisiones del
humano (fecha)"); sección vacía **"Desviaciones aprobadas"**, donde el
implementer *anexa* y nunca sobrescribe.

**`tasks.md` — los pasos.** `T1`, `T2`… con sus `R<n>`; no repite el diseño.
Con varios stacks o capas, agrupadas en **tramos** en orden de dependencia:
cada tramo es una IT aprobada antes del siguiente. Si hay servicios reales,
la última es la **prueba humana**, con `ÚNICA TASK CON SERVICIOS REALES` en
su cabecera. Mapa inverso `R<n> → T<n>` al final.

**Tamaño**: ~400 líneas entre los tres (≈ 6-8 k tokens). Cada cosa se dice
una vez, se cita `archivo:línea` en vez de copiar código y no hay
pseudocódigo de funciones enteras.

## Seguridad obligatoria

Si la feature toca input, auth, datos sensibles o acceso a datos, lleva
`R<n>` de seguridad verificables por test **aunque el `acceptance` no los
pida**: el security_reviewer mide el código contra ellos.

## La puerta humana

El leader resume la spec: qué hace, decisiones abiertas con recomendación,
dependencias nuevas, servicios reales y coste. Solo el humano mueve
`spec_ready → in_progress`.

**Enmiendas**: si el humano rechaza algo ya aprobado (p. ej. el aspecto de
una pantalla), se añaden secciones fechadas ("Enmienda AAAA-MM-DD", `R<n>`
nuevos a continuación), vuelve a pasar por la puerta y se sigue en nuevas IT
de la misma feature. Lo aprobado no se reescribe.

## Modo ligero (`"sdd": false`)

Para cambios pequeños y bien entendidos, el humano marca la feature con
`"sdd": false` al escribirla. No hay spec ni puerta de aprobación: el
`acceptance` hace de requisitos (cada línea, un `R<n>`) y la feature empieza
directamente por el implementer. **Los dos vetos se mantienen.** Si durante
la IT aparece una decisión de diseño de verdad, se pasa a `"sdd": true`.

## Iteraciones y cierre

- Cada vuelta vive en `progress/<F>/IT<n>/` (la crea el leader). El número de
  carpetas es el contador de intentos.
- `CHANGES_REQUESTED` → nueva IT. Un rechazo de seguridad re-verifica
  **ambos** vetos.
- **Correcciones de texto al cerrar**: si el único problema es texto en
  `specs/` o `progress/`, el reviewer aprueba y lista cada corrección
  literal; se aplican en el cierre. Nunca para código, tests, dependencias
  ni seguridad.
- **Cierre**: ambos `APPROVED` en la misma IT y sin tramos pendientes →
  correcciones de texto, `done`, entrada en `progress/history.md` (resumen
  redactado por el leader), `progress/current.md` al día. La task humana
  puede quedar pendiente en `current.md`.
- **Hotfix de una feature `done`**: no se reabre (`state.py` salta las
  `done` y solo admite una en curso). Se añade una feature nueva a
  `feature_list.json` (p. ej. `F01-fix1`), normalmente con `"sdd": false`,
  el bug y su test esperado en `acceptance`, colocada justo tras la que está
  en curso (delante, habría dos en curso). <!-- ajuste-2026-10-03 -->
- **Hallazgos de auditoría**: features nuevas con `archivo:línea` y el
  cambio propuesto copiados en su `acceptance`.
