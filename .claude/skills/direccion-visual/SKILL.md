---
name: direccion-visual
description: Decide la direccion visual del proyecto (paleta, tipografia, componentes, iconos, graficos, movimiento) con el humano y deja docs/<scope>/direccion-visual.md y una maqueta aprobada. Antes de la primera feature con pantallas, o para redisenar. Solo la sesion principal (leader).
---

# Dirección visual

Lección del piloto: la paleta salió de páginas de marketing y de la paleta
por defecto de Tailwind (índigo, Inter, todo en tarjetas iguales), quedó
congelada como `R<n>` de la spec y las pantallas "se notaban hechas con IA".
Nadie con criterio de diseño decidió nada, y nadie miró la app renderizada
hasta que lo hizo el humano.

Se hace una vez, en la sesión principal (tiene las skills de diseño y puede
enseñar la maqueta), y se repite solo para rediseñar.

## 1. Contexto

- Lee `CLAUDE.md` y `docs/<scope>/conventions.md`: qué es, quién lo usa,
  con qué frecuencia (herramienta diaria u ocasional), en qué dispositivo y
  con qué stack de interfaz.
- **Si ya hay interfaz**, captúrala (MCP de Playwright) e invoca
  `redesign-existing-projects` para listar los patrones genéricos que tiene.

## 2. Preguntas (5-8, cada una con recomendación)

Tono (denso y tranquilo, editorial, expresivo…), referentes que le gustan y
que no, claro/oscuro, densidad, **presupuesto de movimiento** (ninguno, solo
respuesta a acciones, una transición por vista…), librería de componentes
(invoca `pick-ui-library`), iconos, gráficos si hay datos, fuentes (con
licencia y servidas en local si hay CSP).

## 3. Propuesta

Invoca `frontend-design:frontend-design` y `frontend-design-direction`;
usa `ui-ux-pro-max` (`--design-system`, y `--domain color` o `typography`)
para paletas y parejas de fuentes. Redacta:

- 4-6 colores con nombre y hex, en claro y oscuro, con su contraste;
- tipografías y sus papeles, escala;
- concepto de layout con un boceto ASCII y la densidad;
- principios: qué hace única a esta interfaz y qué se evita.

**Revísala contra los valores por defecto** antes de enseñarla (lista de
`frontend-design`: acento índigo o violeta, tarjetas iguales con la misma
sombra, crema con serif y terracota, negro con verde ácido, etiquetas en
mayúsculas…). Lo que salga igual que para cualquier otro proyecto, se
cambia y se dice por qué. Una alternativa contrastada, como mucho.

## 4. Maqueta

Un HTML estático con la pantalla principal y datos verosímiles (incluido un
caso de peor caso: nombre largo, lista vacía) en
`docs/<scope>/direccion-visual/maqueta.html`. Captúrala en claro y oscuro y
enséñasela al humano. Como mucho tres vueltas; luego se decide.

## 5. Qué deja escrito

`docs/<scope>/direccion-visual.md` (≤ 150 líneas), que leen
`implementer_ui`, `reviewer` y `spec_author`:

- propósito y tono; tokens (tabla claro/oscuro); tipografía; layout y
  densidad;
- componentes: librería y reglas (p. ej. nada de tarjetas dentro de
  tarjetas);
- iconos y gráficos;
- **movimiento**: qué se anima, qué no, duraciones;
- **prohibido**: los valores por defecto descartados en el paso 3;
- las capturas aprobadas, en `docs/<scope>/direccion-visual/`.

Además:
- `docs/<scope>/conventions.md` tiene el comando del **modo de datos falsos**
  y el juego de **peor caso** (`plantillas/stack/conventions-web.md`); si
  aún no existen, va como `acceptance` de la primera feature con interfaz.
- Si se eligió la API View Transitions con React, propón precargar
  `vercel-react-view-transitions` en el `implementer_ui`.
- Entrada en `docs/CHANGELOG.md` (es un cambio en `docs/`), con el
  "Aprobado por" del humano.
