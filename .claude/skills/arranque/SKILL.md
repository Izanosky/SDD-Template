---
name: arranque
description: Primer uso del harness en un proyecto - entrevista guiada que fija el perfil del proyecto (personal, compartido, produccion) y con el producto, arquitectura, stack y librerias; trae los temas profesionales que el humano no conoce (cache, escalado, observabilidad...) con propuesta y porque, decide el humano, y lo deja escrito. Solo la sesion principal (leader), nunca un subagente.
---

# Arranque

**De aquí salen los documentos que guían todo el proyecto**: cada spec,
cada encargo y cada revisión se miden contra ellos. Por eso nada empieza
hasta que esté todo claro: `state.py` devuelve `ARRANQUE` (y no despacha
ninguna feature) mientras `progress/arranque.md` no tenga la línea
`Estado: APROBADO`, que solo se escribe con el sí del humano al final.

Lecciones del piloto:

- una sola ronda con todo acababa en respuestas de "sigue";
- el stack se eligió sin pesar la ambición visual del producto, y hubo que
  cambiar de framework a mitad de la primera feature (una IT tirada, dos
  investigaciones, una enmienda de ~360 líneas);
- nadie preguntó en qué dispositivos se usaría: el deseo de usarla en el
  móvil llegó con la arquitectura de escritorio ya construida;
- las librerías de interfaz (componentes, animación, gráficos) se fueron
  eligiendo feature a feature, cada una con su investigación.

## Principios del flujo

- **Manda el humano.** Tú preparas, propones y recomiendas; él decide qué se
  decide, cómo y con cuánta investigación. **No investigues nada que no
  haya aprobado**, y antes di qué harías y su coste aproximado.
- **Entrevista, no formulario** <!-- ajuste-2026-10-12 -->: sigue una rama
  del árbol de decisiones hasta cerrarla antes de abrir otra, y cada
  pregunta lleva **tu respuesta recomendada y su porqué**. Las preguntas
  abiertas (las del producto), de una en una. Si una respuesta abre otra
  pregunta, haz esa primero.
- **Aportas lo que el humano no sabe.** "No lo sé" es una respuesta válida.
  Explica en dos líneas qué está en juego, recomienda y apunta la decisión
  como "por recomendación", que la deja revisable. Los temas que un equipo
  profesional se plantearía los traes tú (`catalogo.md`), aunque nadie los
  haya mencionado.
- **Proporcional al proyecto**: el perfil (paso 0) decide cuánto se
  pregunta y qué piezas del harness se instalan. Un proyecto personal no
  carga con CI ni con preguntas de escalado.
- **Nada se queda sin decidir por omisión**: el mapa de decisiones (paso 2)
  cubre todo el proyecto, y cada fila acaba decidida, aplazada con
  disparador o descartada por no aplicar.
- **En orden de dependencia**: lo que condiciona a lo demás, primero
  (plataforma → arquitectura → backend → frontend → calidad y operación).
  Una decisión no se pregunta antes que aquellas de las que depende.
- **Pocas interrupciones**: las preguntas cerradas, en tandas de hasta 4 con
  `AskUserQuestion` (si está), con la recomendada primero y su porqué. Lo
  obvio se propone en bloque para aceptarlo de una vez.
- **Lo que ya dice el repositorio** no se pregunta: se lee y se confirma.
  **Con código existente**, el mapa del paso 2 sale prerrellenado de las
  dependencias, la configuración y la estructura (lo que hay es la
  decisión tomada); el humano confirma o corrige, y solo las filas sin
  código detrás siguen el flujo normal.
- **Reanudable y barato**: el estado vive en `progress/arranque.md` (copia
  de `plantillas/arranque.md`), que se actualiza tras cada tanda. **Al
  cerrar cada bloque, propón `/clear`**: ese fichero basta para seguir, y
  las investigaciones no se arrastran en el contexto de la sesión.
- Sin commits: el primero lo hace el humano, al final (paso 6).

## 0. Soltar la plantilla y fijar el perfil

**Primero, con el sí del humano**, borra lo que solo sirve en el repo de la
plantilla: `HARNESS.md`, `scripts/harness_bundle.py`,
`tests/test_harness_bundle.py` y, si vinieron con la copia, `AUDITORIA.md`
y `PILOTO_PENDIENTE.md`. `HARNESS.md` guarda una copia de cada fichero y su
test falla en cuanto el proyecto adapta uno. Desde aquí, el harness del
proyecto son sus ficheros pequeños: se cambian cuando haga falta, y lo que
sirva para otros proyectos se apunta en `progress/para_la_plantilla.md`.

Después, **el perfil**. Pregunta, de una en una y con tu recomendación:
para quién es (solo para el humano, para personas conocidas o abierto al
público), qué pasa si falla o pierde datos, si mueve dinero o datos
sensibles de otros y qué quiere sacar el humano (aprender, tenerlo
funcionando, un producto). Propón el perfil con esta tabla y deja que el
humano cambie cualquier casilla:

| | personal | compartido | producción |
|---|---|---|---|
| Arranque | producto y las filas imprescindibles del mapa | mapa completo | mapa completo y `catalogo.md` entero |
| Spec formal | solo en features grandes o con zonas críticas; el resto, `"sdd": false` | todas salvo las triviales | todas salvo las triviales |
| Zonas críticas y mutantes | normalmente ninguna | las que haya | las que haya |
| CI | no | recomendado | sí |
| Auditoría de seguridad completa | cuando la pida el humano | cada 4 features | cada 4 features o al cerrar una fase |

Copia `plantillas/arranque.md` a `progress/arranque.md` y apunta ahí el
perfil y sus casillas, y también en "Parámetros del harness" de
`CLAUDE.md`, que es lo que lee el leader después. El perfil
se puede cambiar más adelante: se vuelve a esta tabla.

## 1. Producto

Primera tanda, abierta. Como mínimo debe quedar claro (y sigue tirando del
hilo cuando una respuesta abre otra):

- qué es, para quién, qué problema resuelve; qué entra en la primera
  versión y **qué no**;
- **dónde y en qué dispositivos se usa**, ahora y más adelante (escritorio,
  web, móvil, sin conexión);
- qué datos maneja, dónde deben vivir, si son sensibles, quién los ve (uno
  o varios usuarios) y cuánto costaría perderlos;
- **cuánto pesa la interfaz** (austera, pulida, con animaciones): condiciona
  el stack;
- volumen y crecimiento, presupuesto (gratis, de pago y cuánto), plazos;
- **preferencias y vetos del humano**: lenguajes que conoce o quiere
  aprender, servicios que ya usa, cosas que no quiere.

Escribe `CLAUDE.md` (qué es, para quién; "Estado") y `feature_list.json`:
`F00` (andamiaje, ya en la plantilla; se completa en el paso 4) y después
las features de producto en orden, la primera la más pequeña que aporte
valor.

## 2. Mapa de decisiones

Con el producto, rellena en `progress/arranque.md` la tabla de **todas** las
decisiones técnicas que aplican (borra las que no), en orden de
dependencia. Con perfil **personal**, solo las que el producto no puede
dejar sin decidir. Con **compartido** o **producción**, lee también
`catalogo.md` y añade una fila por cada tema que aplique (bloque
"Escala"), cada una con qué es en una línea y si se decide ahora o se
aplaza con disparador.

| Bloque | Decisiones |
|---|---|
| Plataforma | tipo de app (web, escritorio, móvil, CLI, servicio), empaquetado y distribución, sin conexión |
| Arquitectura | forma (monolito, cliente-servidor, local-first, serverless…), capas y fronteras, dónde vive cada pieza |
| Backend | lenguaje y versión, framework, estilo de API y contratos, validación, errores, tareas en segundo plano |
| Datos | almacenamiento o base de datos, ORM o acceso, migraciones y versionado de formatos, copias de seguridad |
| Seguridad | autenticación y autorización, secretos, riesgos propios y zonas sensibles |
| Frontend | framework, enrutado, estado y caché de datos, formularios, i18n, accesibilidad. Librería de componentes, estilos, iconos, animación, gráficos y fuentes: solo una propuesta; se deciden en `/direccion-visual`, con referencias delante |
| Calidad | tests por capa (unidad, integración, extremo a extremo), lint, formato, tipos, auditoría de dependencias, **zonas críticas** (dinero, datos, permisos, parsers…) y la **herramienta de mutantes** del stack para ellas |
| Operación | build, CI (según el perfil), despliegue y ramas, entornos, logs y errores, coste |
| Escala | las filas que salgan de `catalogo.md` (perfil compartido o producción) |

Cada fila con una **propuesta** y un **modo**:

- **obvia**: hay una opción claramente mejor para este producto (dilo y
  por qué); se acepta en bloque;
- **a elegir**: 2-3 opciones conocidas con sus pros y contras; decide el
  humano;
- **a investigar**: hay hechos que no sabes con seguridad (versión,
  mantenimiento, licencia, límites de un plan, soporte de una plataforma)
  o una apuesta arriesgada.

Cierra el mapa con los **2-3 supuestos de riesgo**: lo que, si resulta
falso, obliga a cambiar una decisión de base (que un puente entre procesos
funcione con la CSP, que una librería corra en la plataforma, que un plan
gratuito aguante el volumen). Los comprobará `F00` antes de escribir
producto.

Enseña el mapa y deja que el humano lo ajuste: cambiar el modo de una
fila, decidir alguna él directamente, marcar qué investigar y con cuánto
esfuerzo. **Solo entonces** se pasa al paso 3.

## 3. Decidir, bloque a bloque

Por bloque y en orden:

1. Las **obvias**, en una sola pregunta para aceptarlas o abrir alguna.
2. Las **a investigar** que el humano aprobó, todas las del bloque a la
   vez y en paralelo:
   - `explorer` para preguntas acotadas (una librería, un plan, un límite);
   - `/deep-research` (workflow de serie de Claude Code) para una pregunta
     amplia que necesita fuentes cruzadas; es el más caro;
   - una **prueba mínima** en el scratchpad si una opción depende de algo
     sin comprobar (que un puente entre procesos funcione, que una
     librería corra en la plataforma);
   - `council` si, tras investigar, sigue habiendo varias buenas sin
     ganadora y el humano quiere contraste.
   Cada hecho con fuente y fecha. Las librerías, con licencia, último
   release y si cumplen la política de dependencias.
3. Las **a elegir**, con las opciones y la recomendación (ya con lo
   investigado).
4. Antes de cerrar el bloque, **coherencia** con lo ya decidido (versiones
   compatibles, licencias, plataforma, CSP, coste) y **qué la haría
   revisable**: cada decisión se marca fija o revisable con su disparador
   ("app móvil: revisar al cerrar la fase 2").

Actualiza `progress/arranque.md` al cerrar cada bloque.

## 4. Lo que queda escrito

- **ADR** en `docs/adr/` para cada decisión de arquitectura, plataforma,
  datos o framework principal (skill `architecture-decision-records`:
  contexto, decisión, alternativas y por qué no, consecuencias, cuándo
  revisarla).
- `docs/architecture.md`, sección "Stack y librerías": cada pieza con
  versión, para qué, alternativa descartada y su ADR si lo tiene. Es la
  lista de dependencias aprobadas: lo que no esté ahí sigue pidiendo
  permiso.
- `F00` en `feature_list.json` con sus scopes reales y una línea de
  `acceptance` por supuesto de riesgo. Va en modo ligero: andamiaje con el
  generador oficial, `init.sh` que sabe fallar, CI en verde (si el perfil
  lo lleva) y un "hola mundo" de punta a punta. Quita las líneas de
  `acceptance` que el perfil no lleve (CI, mutantes).
- **CI**: si el perfil lo lleva, `.github/workflows/ci.yml` con la
  toolchain de cada stack, con versión fijada y actions fijadas por SHA. Si
  no, borra el fichero. Un CI en rojo avisa, pero no bloquea el trabajo. Lección: en el piloto la primera feature cargó
  con el toolchain y el cambio de stack, y necesitó 11 IT.
- `harness.json` (scopes, secretos), el resto de `CLAUDE.md` (la tabla
  "Dónde vive cada pieza" enlaza a los ADR), `docs/security.md`,
  `docs/verification.md` (con las zonas críticas), `docs/<scope>/conventions.md` y
  `<scope>/init.sh` desde `plantillas/stack/`, las zonas sensibles de
  `.claude/agents/leader.md` y la entrada de `docs/CHANGELOG.md`.
- **Skills según el stack**, propuestas al humano; con su sí, en `skills:`
  del agente y `"name-only"` en `skillOverrides` de `.claude/settings.json`:

| Si el proyecto… | Skill | Agente |
|---|---|---|
| usa React | `vercel-react-best-practices`, `vercel-composition-patterns` | `implementer_ui` |
| usa la API View Transitions | `vercel-react-view-transitions` | `implementer_ui` |
| usa Python | `modern-python` | `implementer` |
| tiene usuarios o servidor | `prd-securability-enhancement` | `spec_author` |
| usa una plataforma con skills propias (Supabase, Cloudflare…) | las suyas, si están instaladas | el que las use |

  Lo que no esté instalado se apunta en `README.md` ("Skills opcionales") y
  se le dice al humano cómo instalarlo.

## 5. Diseño

Si hay interfaz, `/direccion-visual` **después de F00** y antes de la
primera feature con pantallas: ahí se eligen, con referencias reales que
aporta el humano, las librerías de interfaz (componentes, iconos,
animación, fuentes) y el aspecto, y los tokens se escriben ya en el
stack. F00 instala solo el framework. Lección del banco de pruebas: con la librería
de componentes decidida en el arranque, quedó instalada antes de mirar
ninguna referencia.

## 6. Aprobación final

Antes de pedirla, comprueba:

- ninguna fila abierta en `progress/arranque.md` (decidida, aplazada con
  disparador, o "no aplica");
- ningún hueco por rellenar (`grep -rn "<RELLENAR" .`; `README.md` y
  `plantillas/` citan la marca sin ser huecos);
- los documentos no se contradicen entre sí (lo que dice `CLAUDE.md`,
  los ADR, "Stack y librerías", las convenciones y `init.sh`);
- `F00` tiene sus supuestos de riesgo y la primera feature de producto se
  puede especificar con lo decidido, sin preguntas de arquitectura
  pendientes.

Enseña al humano un resumen de una pantalla: decisiones por bloque (con las
revisables y su disparador), documentos escritos y lo que le queda al
humano: instalar gitleaks y `git config core.hooksPath .githooks`, el CI si
lo hay, demostrar que cada paso de `init.sh` sabe fallar y el primer
commit. **Con su sí explícito**, añade
`Estado: APROBADO` (fecha) a `progress/arranque.md`; desde ahí `state.py`
despacha la primera feature. Si luego cambia una decisión de base, se
vuelve a su fila del mapa y a su ADR (leader, "Skills").
