# Convenciones de interfaz web — material para copiar

<!-- Solo si el proyecto tiene interfaz web. Copia a
docs/<stack>/conventions.md lo que aplique; cada punto salió de una
iteración rechazada en un proyecto real. -->

- **Cada spec que crea pantallas define su aspecto.** Una pantalla sin
  estilos no está terminada (un reset CSS puede dejar los campos de un
  formulario invisibles). No dejar el diseño para una feature final: una
  feature aprobada funcionalmente puede reabrirse si el humano rechaza el
  aspecto. Base visual común (paleta, tipografía, componentes) en una carpeta
  que cada spec reutiliza.
- **Nunca un spinner indefinido**: todo estado de espera dice **qué** se
  espera y **por qué** (servicio dormido, proceso desconectado, motivo real
  del fallo). Los estados raros legítimos, sin explicar, parecen fallos.
- **Fluidez**: caché de lecturas en memoria (esqueleto en la primera carga;
  al volver, lo anterior con indicador de refresco; una sola petición por
  ruta en vuelo; un refresco fallido conserva los datos). Mutaciones
  optimistas, en serie por recurso, sin duplicados, con reversión y aviso.
  Al volver atrás se restaura el scroll y el estado de la vista. Todo se
  vacía al cerrar sesión, al expirar y al cambiar de usuario.
- **El estado de servidor no se duplica en estado local.**
- **Un solo envío a la vez por acción** (botón inactivo mientras dura).
- **Variables públicas del bundle**: lista cerrada; el build falla ante
  otra.
- **La capa de UI no importa el cliente de datos** directamente: regla de
  lint que cubra importación dinámica, subrutas y acceso por corchetes.
- **Sin sumideros HTML** (`innerHTML`, `dangerouslySetInnerHTML`, `eval`)
  con datos de la API.
- **Almacenamiento del navegador puede fallar** (ventana privada, cuotas):
  todo acceso en `try/catch`; solo identificadores y números, validados al
  leer y borrados al cerrar sesión.
- **Respuestas de la API parseadas estrictamente**; otra forma da
  "respuesta inesperada", nunca un render roto. Ids de ruta validados antes
  de llamar a la API.
- **Tests de lo que ve el usuario** (textos, roles), no de la estructura.
- **Restricciones de plataforma que rompen cosas**, escritas con su motivo
  (p. ej. APIs que un sistema operativo móvil suspende con la pantalla
  bloqueada).
- **Accesibilidad básica**: foco devuelto al cerrar diálogos; atajos de
  teclado ignorados dentro de campos de texto.
