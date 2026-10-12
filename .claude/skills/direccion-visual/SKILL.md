---
name: direccion-visual
description: Decide con el humano la direccion visual del proyecto (librerias de interfaz, tokens, tipografia, movimiento) a partir de referencias reales que aporta el humano y de tres direcciones comparadas, y deja docs/<scope>/direccion-visual.md, los tokens en el stack y las capturas aprobadas. Tras F00 y antes de la primera feature con pantallas, o para redisenar. Solo la sesion principal (leader).
---

# Dirección visual

Lecciones:
- Piloto: la paleta salió de páginas de marketing y de los valores por
  defecto (índigo, Inter, tarjetas iguales) y las pantallas "se notaban
  hechas con IA".
- Banco de pruebas (2026-10-11): con "evita lo genérico" como único
  criterio salió una propuesta distinta pero amateur (fuente rara en todo,
  cifras en monoespaciada, fondo tintado, muchos colores saturados).
  Faltaban un listón y opciones entre las que elegir.

Va **después de F00** (el framework ya está instalado) y antes de la
primera feature con pantallas; se repite solo para rediseñar. Objetivo:
**profesional antes que original**. Lo distintivo, en uno o dos detalles;
el resto, contención.

## 1. Contexto, primero para el humano

Lee `CLAUDE.md`, `progress/arranque.md` y el `acceptance` de la primera
feature con interfaz. **Antes de preguntar**, cuéntale en 3-4 líneas qué es
el producto, qué pantallas vienen y qué queda fuera. Si ya hay interfaz,
captúrala.

## 2. Referencias: las aporta el humano

**Sin referencias no se propone nada.** Pídele 3-6 capturas de productos
reales que le parezcan profesionales y del mismo tipo (sector, plataforma,
densidad): de Refero, Mobbin o apps que use. Las guarda en
`docs/<scope>/direccion-visual/referencias/`. Si el MCP de Refero está
conectado, puedes proponerle candidatas, pero elige él.

De cada una, una línea: qué se toma (escala tipográfica, espaciado, cuánto
color y dónde, cómo muestra cifras y listas, densidad) y qué no.

## 3. Preguntas, pocas y con recomendación

Tono, claro/oscuro, densidad, cuánto movimiento y las **librerías de
interfaz**: componentes, iconos, animación y fuentes (licencia; servidas en
local si hay CSP). El arranque fijó el framework; estas se eligen aquí, con
las referencias delante (`pick-ui-library`). Cada dependencia, con el sí
del humano y a "Stack y librerías" de `docs/architecture.md`.

## 4. Tres direcciones, y elige el humano

- **Con Google Stitch** (stitch.withgoogle.com, a mano, lo maneja el
  humano): redacta un prompt por dirección para la pantalla principal, con
  contenido real (normal y peor caso), las referencias como imágenes y las
  restricciones. Tres direcciones de verdad distintas (densidad, jerarquía,
  uso del color), no tres paletas. El humano elige y guarda en
  `docs/<scope>/direccion-visual/stitch/` las capturas y el `DESIGN.md` de
  la elegida. El HTML que exporta es referencia, no código del producto.
- **Sin Stitch**: las haces tú como miniaturas HTML
  (`frontend-design:frontend-design`, `ui-ux-pro-max` para paletas y
  fuentes) y se las enseñas juntas.

Antes de enseñarlas, descarta lo que tenga **señales de amateur**: fuente
"con personalidad" en todo el texto, fondo de página tintado, muchos colores
saturados, cifras en monoespaciada en lugar de números tabulares, dos
fuentes expresivas compitiendo, insignias repetidas en cada fila.

## 5. Qué deja escrito

- **Los tokens, en un único sitio y en la forma nativa del stack** (tema de
  la librería de componentes, variables CSS, configuración de Tailwind…):
  colores claro/oscuro con su contraste, tipografía y escala, espaciado,
  radios, sombras y duraciones. Las pantallas no usan valores sueltos.
- `docs/<scope>/direccion-visual.md` (≤ 120 líneas), que leen
  `spec_author`, `implementer_ui` y `reviewer`: propósito y tono, las
  referencias y qué se toma de cada una, dónde viven los tokens y el papel
  de cada uno (los valores no se copian), tipografía, layout y densidad,
  reglas de componentes, movimiento (qué, cuándo, duraciones) y lo
  prohibido.
- Las capturas aprobadas de la pantalla principal (claro y oscuro, 1280 y
  390 px, normal y peor caso) en `docs/<scope>/direccion-visual/`.
- En `docs/<scope>/conventions.md`, el comando del modo de datos falsos con
  su peor caso.
- Si el MCP del navegador no arranca (p. ej. busca Chrome y solo hay Edge),
  configúralo para el navegador instalado (Playwright: `--browser msedge`)
  y anótalo en `conventions.md`.
- Entrada en `docs/CHANGELOG.md`, con el "Aprobado por" del humano.
