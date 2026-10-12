# Fase 6: diseño visual

El objetivo es que parezca **profesional antes que original**. Lo distintivo
se concentra en uno o dos detalles; el resto, contención. Lo que se aprendió
en proyectos anteriores:

- Con los valores por defecto (índigo, Inter, tarjetas iguales), las
  pantallas "se notaban hechas con IA".
- Con "evita lo genérico" como único criterio salió algo distinto, pero
  amateur. Hacen falta un listón (las referencias) y opciones entre las que
  elegir.

## 1. Alcance de las pantallas

Antes de nada, decide con el humano **qué pantallas se diseñan**: las de
las primeras features, alguna más (una landing, por ejemplo) o una sola
pantalla base como guía. Decide también **qué plataforma va primero**, móvil
o escritorio. En una prueba anterior esto se decidió tarde y hubo que
rehacer los prompts.

## 2. Referencias: las aporta el humano

**Sin referencias no se propone nada.** Pide 3-6 capturas o URLs de
productos reales del mismo tipo que al humano le parezcan profesionales (de
Refero, Mobbin, o apps que use). Guárdalas en `docs/diseno/referencias/`.
De cada una, una línea: qué se toma (escala tipográfica, espaciado, cuánto
color y dónde, densidad) y qué no.

## 3. Preguntas, pocas y con recomendación

Tono, claro u oscuro, densidad, cuánto movimiento, y las **librerías de
interfaz**: componentes, iconos, animación y fuentes (con su licencia). Cada
dependencia necesita el sí del humano.

## 4. Tres direcciones, y elige el humano

- **Con Google Stitch** (lo maneja el humano): redacta un prompt por
  dirección, con contenido real (caso normal y peor caso) y las
  referencias. Tienen que ser tres direcciones de verdad distintas
  (densidad, jerarquía, uso del color), no tres paletas. El HTML que
  exporta Stitch es referencia, no código.
- **Sin Stitch**: haz tú tres miniaturas HTML y enséñalas juntas.

Antes de enseñarlas, descarta las **señales de amateur**: una fuente "con
personalidad" en todo el texto, fondo de página tintado, muchos colores
saturados, cifras en monoespaciada en lugar de números tabulares, dos
fuentes expresivas compitiendo o insignias repetidas en cada fila.

## 5. Qué queda escrito

`docs/diseno.md` (≤ 120 líneas):

- propósito y tono;
- las referencias y qué se toma de cada una;
- la dirección elegida;
- las librerías de interfaz;
- los **tokens**: colores en claro y oscuro con su contraste, tipografía y
  escala, espaciado, radios, sombras y duraciones;
- reglas de componentes, de movimiento y lo prohibido.

Al construir, los tokens viven **en un único sitio y en la forma nativa del
stack**: el tema de la librería, variables CSS o la configuración de
Tailwind. Las pantallas no usan valores sueltos.
