# Convenciones

Cómo se escribe el código de este proyecto, en detalle. Las leen el
`implementer` y el `reviewer`. Solo va lo que difiere de las convenciones
estándar del lenguaje: lo que el modelo ya sabe no se escribe. La
configuración de las herramientas manda; aquí se explica el porqué. Lo
rellena `/arranque` (fase 7). Si una regla rompe cosas cuando se olvida,
se repite también en una línea en "Lo que rompe cosas" del `CLAUDE.md`. Si hay varios stacks
(por ejemplo, API y web), repite las secciones por stack.

## Comandos

Están en el `CLAUDE.md` del proyecto, que Claude carga en cada sesión: verificar
todo, verificar rápido, arrancar, datos falsos (normal y peor caso) y
mutantes. Cada paso de verificación **se ha demostrado que sabe fallar**
(F00): se planta un fallo y se mira el código de salida. La carpeta de
trabajo de los mutantes (`mutants/`, `.stryker-tmp/`…) queda fuera de los
tests, del lint y de git. En Windows, `mutmut` no funciona (usa
`cosmic-ray`, siempre en una copia, porque muta el fichero en su sitio;
lo que necesita su comando está en `.claude/forma-de-trabajo.md`), y
Stryker necesitó `--concurrency 2`.

## Estructura y fronteras

<Módulos, quién puede importar a quién, dónde vive lo compartido (una única
definición para lo que cruza procesos).>

## Idioma y nombres

<Código en … / textos en … / los nombres de test describen
comportamiento.>

## Errores

<Cómo se lanzan, qué ve el usuario, qué va al log. Nunca se traga un
error.>

## Tipos y datos

<La entrada no es la fila; campos extra rechazados; tipos cerrados para los
estados.>

## Tests

<Framework y qué se prueba en cada capa. El doble de prueba sirve para
probar a quien llama, no al adaptador: cada método nuevo de un adaptador
real (repositorio, cliente HTTP, almacenamiento) tiene su propio test, con
un cliente grabador que comprueba los filtros exactos y los valores
escritos. El arnés restaura el valor inicial capturado, nunca un literal.
Lo que se compara con un servicio usa la forma que ese servicio devuelve.>

## Patrones prohibidos

<Cada uno con su motivo.>

## Restricciones de plataforma

<Lo que rompe cosas en este entorno, con su motivo (p. ej. APIs que un
sistema móvil suspende con la pantalla bloqueada).>

## Si hay interfaz web

Cada punto salió de una iteración rechazada en un proyecto real. Borra lo
que no aplique.

- **El aspecto sale de `docs/diseno.md`** y de sus tokens. Una pantalla sin
  estilos no está terminada: un reset de CSS puede dejar invisibles los
  campos de un formulario.
- **Nunca un spinner indefinido**: todo estado de espera dice **qué** se
  espera y **por qué** (servicio dormido, proceso desconectado, motivo real
  del fallo).
- **Fluidez**:
  - lecturas en caché (esqueleto en la primera carga; al volver, lo
    anterior con un indicador de refresco);
  - una sola petición por ruta en vuelo, y un refresco fallido conserva los
    datos;
  - mutaciones optimistas, en serie por recurso y con reversión y aviso;
  - al volver atrás se restauran el scroll y el estado de la vista;
  - todo se vacía al cerrar sesión o al cambiar de usuario.
- **El estado del servidor no se duplica en estado local.**
- **Un solo envío a la vez por acción**: el botón queda inactivo mientras
  dura.
- **La capa de interfaz no importa el cliente de datos** directamente; se
  hace cumplir con una regla de lint que cubra la importación dinámica,
  las subrutas y el acceso por corchetes.
- **Sin sumideros HTML** (`innerHTML`, `dangerouslySetInnerHTML`, `eval`)
  con datos de fuera.
- **El almacenamiento del navegador puede fallar** (ventana privada,
  cuotas): todo acceso, en `try/catch`. Solo identificadores y números,
  validados al leer.
- **Las respuestas de la API se parsean de forma estricta**: otra forma da
  "respuesta inesperada", nunca una pantalla rota. Los ids de la ruta se
  validan antes de llamar a la API.
- **Los tests miran lo que ve el usuario** (textos, roles), no la
  estructura.
- **Accesibilidad básica**: el foco vuelve a su sitio al cerrar un diálogo,
  y los atajos de teclado se ignoran dentro de los campos de texto.
