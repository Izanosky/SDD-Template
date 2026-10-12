# Catálogo: lo que se plantearía un equipo profesional

Se lee en el paso 2 de `/arranque` con perfil **compartido** o
**producción**. No es una lista que cumplir: sirve para que nada importante
se quede sin pensar por no saber que existía. El humano no tiene por qué
conocer estos temas; tú los traes.

Por cada tema que aplique: qué es en una línea, por qué importa **en este
producto** y tu propuesta (**ahora**, **más adelante** con su disparador o
**no aplica**). El criterio para elegir:

- **Si es caro cambiarlo después, se decide ahora.** Son cosas que quedan
  repartidas por todo el código o por los datos.
- **Si es barato añadirlo después, se aplaza** hasta que aparezca la señal
  (YAGNI). Hasta entonces, con la opción simple.

Faltan temas seguro: añade los que pida el producto (pagos, tiempo real,
IA, mapas, ficheros grandes…). Si no sabes cómo lo resuelven productos
parecidos, propón investigarlo (modo **investigar**, con su coste).

## Caro de cambiar después: se decide en el arranque

| Tema | Qué es | Señal de que aplica | Por defecto sensato |
|---|---|---|---|
| Forma de la arquitectura | monolito, monolito modular o servicios separados | casi siempre | monolito modular; se parte solo con un motivo medido |
| Servidor sin estado | nada de sesiones ni ficheros en la memoria o el disco de una instancia | más de una instancia, autoescalado, serverless | sesión en token o en un almacén compartido; ficheros en almacenamiento de objetos |
| Varios clientes u organizaciones (multi-tenant) | cómo se separan los datos de cada cliente | "empresas", "equipos", "cuentas" | columna de tenant y autorización en la capa de datos (RLS o equivalente) |
| Autenticación y autorización | quién eres y qué puedes hacer: proveedor o propia, roles | más de un usuario | un proveedor probado; contraseñas propias solo con motivo |
| Identificadores | autoincremental o UUID/ULID | IDs en URLs, sincronización, fusión de datos | no adivinables en lo que se expone |
| Dinero | importes, redondeo, moneda, cobros | cualquier cobro | enteros en céntimos o decimal; tarjetas solo a través del proveedor de pagos |
| Idempotencia | repetir una operación no la duplica | pagos, webhooks, colas, reintentos del cliente | clave de idempotencia en las escrituras que cobran o notifican |
| Fechas, idioma y región | UTC en los datos, textos traducibles, formatos locales | usuarios en varios países o idiomas | UTC siempre; textos fuera del código si hay más de un idioma previsto |
| Datos personales (RGPD) | qué se guarda, cuánto tiempo, cómo se exporta y se borra | datos de personas, usuarios de la UE | lo mínimo; borrado real; dónde viven los datos |
| Contratos de API y versiones | que un cliente antiguo siga funcionando | app móvil (no se actualiza a la vez), terceros que consumen la API | versionar desde el principio si hay clientes que no controlas |
| Migraciones del esquema | cambiar la base de datos sin parar ni perder datos | cualquier BD que vaya a evolucionar | herramienta de migraciones desde el día 1; expandir antes de contraer |
| Accesibilidad | teclado, contraste, lector de pantalla | interfaz para el público | desde el principio: añadirla al final es rehacer pantallas |
| Coste que crece con el uso | qué se paga por usuario, petición o GB | proveedores de pago o con límites gratuitos | alerta de presupuesto en cada proveedor desde el día 1 |

## Barato después: se aplaza con su disparador

| Tema | Qué es | Disparador para hacerlo | Mientras tanto |
|---|---|---|---|
| Caché | guardar resultados caros para no recalcularlos (memoria, Redis, CDN, cabeceras HTTP). Lo difícil es invalidarla | lecturas repetidas con latencia medida alta, o coste de una API externa | sin caché; cabeceras HTTP en los estáticos |
| Pool de conexiones a la BD | reutilizar conexiones en vez de abrir una por petición | errores "too many connections", mucha concurrencia. **En serverless, ahora**: cada instancia abre las suyas | el pool del driver o del ORM; en serverless, el pooler del proveedor |
| Escalado horizontal | más instancias detrás de un balanceador (requiere servidor sin estado) | CPU o latencia al límite con una instancia | una instancia y el autoescalado del proveedor |
| Colas y segundo plano | sacar lo lento de la petición (correos, procesar ficheros, llamadas externas) | peticiones de más de 1-2 s, trabajo que hay que reintentar | cola del proveedor o tabla en la BD; nunca hilos sueltos |
| Límites de uso (rate limiting) | que nadie tumbe el servicio ni pruebe contraseñas a fuerza bruta | API pública, mucho tráfico | **en login y registro, ahora**; en el resto, con tráfico |
| Paginación y topes | ninguna lista ni subida sin tamaño máximo | listas que crecen con los usuarios | tope en todo desde el principio (es una convención, no infraestructura) |
| Observabilidad | logs estructurados, errores con contexto (tipo Sentry), métricas, alertas | usuarios que no eres tú: no te contarán qué falla | logs estructurados y captura de errores en la primera versión pública; métricas y trazas con varios servicios |
| Copias y restauración | copias automáticas y **una restauración probada** | datos que no se pueden regenerar | copias del proveedor; probar una restauración antes de abrir al público |
| Entornos | local, pruebas (staging) y producción, con datos y secretos separados | usuarios a los que no puedes romper nada | local y producción |
| Despliegue y vuelta atrás | desplegar sin cortar y volver a la versión anterior en minutos | despliegues frecuentes, usuarios que pagan | el del proveedor con rollback; feature flags si se despliega más de lo que se publica |
| Disponibilidad (SLO) | cuánto tiempo caído es aceptable; decide la redundancia | clientes que pagan, contratos | sin objetivo formal |
| CDN | servir estáticos e imágenes desde cerca del usuario | usuarios lejos del servidor, imágenes pesadas | la del hosting |
| Búsqueda | texto completo, filtros, relevancia | la de la BD se queda corta o lenta | la búsqueda de texto de la BD |
| Ficheros subidos | almacenamiento de objetos, tipo y tamaño máximos, URLs firmadas | subidas de usuarios | almacenamiento del proveedor con límites |
| Correo y notificaciones | proveedor transaccional, plantillas, bajas | correos a usuarios | proveedor transaccional; nunca SMTP propio |
| Tiempo real | websockets o SSE, reconexión, presencia | chat, colaboración, paneles en vivo | sondeo periódico |
| Registro de acciones | quién hizo qué y cuándo | varios administradores, dinero, B2B | logs de aplicación |
| Pruebas de carga | medir antes de optimizar | lanzamiento con fecha, pico previsto | nada |
