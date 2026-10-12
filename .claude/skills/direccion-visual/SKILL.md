---
name: direccion-visual
description: Decide con el humano la direccion visual (librerias de interfaz, tokens, tipografia, movimiento) a partir de referencias reales que aporta el y de tres direcciones comparadas, y deja docs/diseno.md. Fase 6 de /arranque, o para redisenar. Solo la sesion principal.
---

# Dirección visual

El objetivo es que parezca **profesional antes que original**. Lo distintivo
se concentra en uno o dos detalles; el resto, contención. Se pregunta con
el método de la skill `entrevista`.

Lo que se aprendió en las pruebas:

- Con los valores por defecto (índigo, Inter, tarjetas iguales), las
  pantallas "se notaban hechas con IA".
- Con "evita lo genérico" como único criterio salió algo distinto, pero
  amateur. Hacen falta un listón (las referencias) y opciones entre las que
  elegir.
- Cuando la librería de componentes se decidía en el arranque, quedaba
  instalada antes de haber mirado ninguna referencia. Por eso las librerías
  de interfaz se eligen aquí.

## 1. Contexto y alcance de las pantallas

Lee `docs/proyecto.md` y cuéntale al humano en 3-4 líneas qué es el
producto, qué pantallas vienen y qué queda fuera. Si ya hay interfaz,
captúrala. Después, que el humano decida:

- **qué pantallas se diseñan**: las de las primeras features, alguna más
  (una landing, por ejemplo) o una pantalla base que sirva de guía;
- **qué plataforma va primero**, móvil o escritorio.

*En una prueba, esto se decidió a mitad del paso 4 y hubo que rehacer los
prompts.*

## 2. Referencias: las aporta el humano

**Sin referencias no se propone nada.** Pide 3-6 capturas o URLs de
productos reales del mismo tipo (sector, plataforma, densidad) que al
humano le parezcan profesionales: de [Refero](https://refero.design/),
[Mobbin](https://mobbin.com/) o apps que use. Guárdalas en
`docs/diseno/referencias/`. De cada una, una línea: qué se toma (escala
tipográfica, espaciado, cuánto color y dónde, densidad) y qué no.

## 3. Preguntas, pocas y con recomendación

Tono, claro u oscuro, densidad, cuánto movimiento, y las **librerías de
interfaz**: componentes, iconos, animación y fuentes (con su licencia;
servidas en local si hay CSP). Para elegirlas, `pick-ui-library` si está
instalada. Cada dependencia necesita el sí del humano y se apunta en
`docs/stack.md`.

## 4. Tres direcciones, y elige el humano

- **Con [Google Stitch](https://stitch.withgoogle.com/)** (gratis, lo maneja
  el humano): redacta un prompt por dirección para las pantallas acordadas,
  con contenido real (caso normal y peor caso) y las referencias. Tienen
  que ser tres direcciones de verdad distintas (densidad, jerarquía, uso
  del color), no tres paletas. El humano elige y guarda en
  `docs/diseno/stitch/` las capturas y el `DESIGN.md` de la elegida. El
  HTML que exporta Stitch es referencia, no código.
- **Sin Stitch**: haz tú tres miniaturas HTML (`frontend-design` si está
  instalada, y `ui-ux-pro-max` para paletas y fuentes) y enséñalas juntas.

Antes de enseñarlas, descarta las **señales de amateur**: una fuente "con
personalidad" en todo el texto, fondo de página tintado, muchos colores
saturados, cifras en monoespaciada en lugar de números tabulares, dos
fuentes expresivas compitiendo o insignias repetidas en cada fila.

**Lo que se aprueba aquí es la referencia** (la captura de Stitch o la
miniatura). Las capturas de la pantalla real llegan con la primera feature
que la construye, y ahí el humano da su visto bueno visual. *En una prueba
se pedían capturas de una pantalla que todavía no existía.*

## 5. Qué queda escrito

`docs/diseno.md` (≤ 120 líneas), que leen el `implementer` y el `reviewer`:

- propósito y tono;
- las referencias y qué se toma de cada una;
- la dirección elegida;
- las librerías de interfaz;
- los **tokens**: colores en claro y oscuro con su contraste, tipografía y
  escala, espaciado, radios, sombras y duraciones;
- reglas de componentes, de movimiento (qué se anima, cuándo y cuánto dura)
  y lo prohibido.

Al construir, los tokens viven **en un único sitio y en la forma nativa del
stack**: el tema de la librería, variables CSS o la configuración de
Tailwind. Las pantallas no usan valores sueltos. Si el framework ya está
instalado, escribe ya los tokens. Si no, lo hace la primera feature.

Para las capturas al construir, la primera feature con pantallas deja en
la sección "Comandos" del `CLAUDE.md` el comando que arranca la app con datos falsos
(caso normal y peor caso). Si
el navegador de Playwright busca Chrome y solo hay Edge, se configura con
`--browser msedge`. Que vaya con `--isolated`, para no compartir ventana
con el humano.
