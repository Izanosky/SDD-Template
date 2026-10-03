# Principios

Solo las posturas de este proyecto. Lo que cualquier ingeniero ya sabe
(SOLID, patrones de diseño, nombres claros) no se repite aquí. Ante un
conflicto, gana el código más simple que cumple la spec y se deja verificar.

- **Nada que no pida una spec aprobada** (sin "por si acaso"). La validación
  en fronteras de confianza y el manejo de errores que evita perder datos no
  son especulativos.
- **Nativo antes que dependencia**: biblioteca estándar → capacidad de la
  plataforma (constraint en la base de datos, elemento HTML) → dependencia ya
  instalada → nueva, y solo con aprobación.
- **Regla de tres**: no se abstrae hasta el tercer uso real. Una interfaz con
  una sola implementación y sin doble de test es ceremonia.
- **Una librería frágil, detrás de un adaptador en un único fichero**:
  cuando el tercero cambie, el arreglo cabe ahí.
- **DRY para conocimiento** (contratos, constantes de negocio, listas de
  secretos), no para código que se parece por casualidad.
- **Fallar pronto al arrancar**: una variable obligatoria que falta aborta
  con un mensaje que la nombra, nunca con su valor.
- **Parsear en el borde y confiar dentro**; estados como tipos cerrados.
- **Carreras con escritura condicional y constraints**, no con
  leer-comprobar-escribir. Reintentos idempotentes.
- **Nunca tragarse un error**: motivos cerrados hacia fuera, detalle saneado
  hacia el log.
- **Fallar abierto solo hacia un control posterior**: si una comprobación
  previa (p. ej. consultar a un tercero) falla, la petición sigue y la frena
  el control que ya existía, nunca un error 500. Un control de seguridad
  falla cerrado.
- **Sondeo antes que push** si nadie puede abrir conexiones hacia el cliente.
- **Atajos marcados**: un atajo deliberado lleva un comentario
  `ATAJO: <límite> · <camino de mejora>`, con esa etiqueta literal para que
  la retrospectiva pueda encontrarlos todos. <!-- ajuste-2026-10-03 -->
- <RELLENAR: posturas propias del proyecto.>
