# Seguridad

Lo que exige el `security_reviewer`, y lo que tiene en cuenta el
`implementer` al construir. Los escáneres son el suelo, no el techo: se
revisa a mano lo demás. Borra los apartados condicionales que no apliquen a
este proyecto.

## Riesgos propios, del más grave al menos

<Los rellena /arranque: 3-6 riesgos de este proyecto, cada uno con dónde
se controla (fichero, test o regla).>

**El atacante no usa tu interfaz**: llama a la API y a los servicios
gestionados directamente, con cualquier clave pública del cliente.

## Secretos

- No pasan por el contexto de un agente: no se leen `.env` ni claves, no se
  imprimen y no se copian (`.claude/settings.json` bloquea leerlos).
- Viven solo donde se usan (el panel del servicio, las variables de la
  máquina que los necesita). **Mínimo privilegio**: cada proceso, solo los
  suyos.
- `.env.example` documenta los nombres y el formato, nunca los valores.
- **Un secreto que acaba en el chat, en un log o en un commit se rota.**
  Borrarlo después no basta: sigue en el historial de git. Antes del
  primer push, conviene pasar un escáner (por ejemplo, gitleaks) sobre el
  historial.
- **Lo que llega al cliente (bundle, app) es público**: lista cerrada de
  variables públicas.
- Tokens generados con un generador criptográfico, con un formato
  reconocible (prefijo y hex).

## Lo que se revisa a mano

- **Autorización por objeto**: cada consulta filtra por propietario en la
  propia consulta. Un recurso ajeno responde igual que uno inexistente
  (código, cuerpo y tiempo).
- **Autorización por función**: las rutas de admin, con su comprobación; un
  401 o 403 va antes que los errores de validación.
- **Asignación masiva**: los modelos de entrada rechazan campos extra; el
  propietario, los roles y los estados los pone el servidor.
- **Autenticación**: firma, algoritmo fijado, audiencia, emisor y
  caducidad. Los roles salen solo de claims que el usuario no puede editar.
  Los tokens de máquina son distintos de los de usuario, con alcance mínimo
  y comparados en tiempo constante.
- **Entrada en el borde**: lista blanca (dominios, formatos), tipos
  estrictos, longitudes y sin caracteres de control. **Unicode se
  normaliza (NFKC) antes de escapar**: los caracteres de ancho completo
  pueden volverse comodines tras una normalización posterior.
- **Comparar un host por prefijo es engañable** (`localhost.evil.com`): se
  parsea y se compara el host exacto.
- **Los datos de terceros son entrada del atacante** (títulos, nombres,
  descripciones): longitud acotada, y nunca en rutas de fichero,
  argumentos de línea de comandos ni sumideros HTML.
- **SSRF**: nunca se pasa una URL del usuario a algo que la resuelva. Se
  extrae el identificador y se reconstruye la URL, con lista blanca de
  hosts y sin redirecciones.
- **Consumo de recursos**: tope global de tamaño del cuerpo, contando bytes
  y sin fiarse de la cabecera; topes de páginas, ficheros, duración,
  elementos por usuario y tasa. Un coste cuadrático con datos del usuario
  también es un hallazgo.
- **Credenciales temporales** (URLs firmadas, tokens): siempre caducan.
- **Logs y errores**: nunca tokens, URLs firmadas ni datos sensibles. Los
  mensajes externos se sanean y se truncan, y el usuario no ve rutas,
  consultas ni trazas.
- **La configuración es código**: CORS con orígenes exactos (un comodín o
  una entrada mal formada impide arrancar); la documentación automática de
  la API, apagada en producción; las cabeceras de seguridad; las reglas de
  lint que prohíben imports peligrosos, cubriendo la importación dinámica,
  las subrutas y el acceso por corchetes. *En la práctica, la mayoría de
  los rechazos de seguridad salieron de la configuración y de los pasos que
  se le piden al humano, no del código.*
- **Base de datos**: consultas parametrizadas; unicidad y carreras con
  constraints, no con un `if`.
- **Dependencias**: sin vulnerabilidades altas, y cada paquete nuevo
  aprobado por el humano.

## Si delegas la autenticación en un proveedor

- Registro público desactivado si el grupo es cerrado, con una prueba de
  que se rechaza.
- Sesiones anónimas del proveedor rechazadas explícitamente si no se usan.

## Si la base de datos se expone por API (PostgREST, Supabase u otro BaaS)

- Toda tabla nueva, con control de acceso por fila y permisos mínimos.
- Toda función nueva revoca la ejecución a los roles públicos, porque se
  puede llamar por RPC con la clave pública. Sin SQL dinámico y con
  `search_path` fijado.
- Una verificación de solo lectura que lista lo accesible para los roles
  públicos y debe salir vacía.

## Si hay interfaz web

CSP restrictiva (orígenes de API y almacenamiento explícitos),
`frame-ancestors 'none'`, `Referrer-Policy: no-referrer` (para que una URL
firmada no salga en el `Referer`) y nada de `innerHTML` ni `eval` con datos
de la API. El riesgo de XSS de la sesión del cliente, documentado.
