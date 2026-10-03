# Seguridad

Lo que el `security_reviewer` exige. Los escáneres (gitleaks, auditoría de
dependencias) son el suelo, no el techo: él verifica su salida y revisa a
mano lo demás.

## Riesgos propios, ordenados por gravedad

<RELLENAR: los 3-6 riesgos de este proyecto, el más grave primero, con dónde
se controla cada uno (archivo, test, checkpoint).>

| Categoría OWASP API Top 10 | Dónde aparece aquí |
|---|---|
| <RELLENAR> | |

**El atacante no usa tu interfaz**: llama a la API y a los servicios
gestionados directamente, con cualquier clave pública del cliente.

## Secretos: cuatro capas

1. Permisos de `.claude/settings.json` (Read/Edit de `.env*`, `*.pem`,
   `*.key`). Si usas otras variantes de `.env`, añádelas.
2. Hook `scripts/guard_secrets.py`: bloquea comandos que leen `.env`,
   expanden un secreto de `harness.json` o vuelcan el entorno. Falla cerrado.
3. Pre-commit con gitleaks sobre el índice, `--redact`, falla cerrado.
4. CI: gitleaks sobre la historia completa.

- Los secretos **no pasan por el contexto de un agente** y viven solo donde
  se usan (panel del servicio, variables del sistema de la máquina que los
  necesita). **Mínimo privilegio**: cada proceso, solo los suyos.
- `.env.example` documenta nombres y formato, sin valores.
- Tokens generados con un CSPRNG, con un formato que la regla de gitleaks
  reconozca siempre (prefijo + hex).
- Un secreto que acaba en el chat o en un log se rota.
- **Lo que llega al cliente (bundle, app) es público**: lista cerrada de
  variables públicas, y el build falla ante cualquier otra.

## Lo que se revisa a mano

- **Autorización por objeto**: cada consulta filtra por propietario en la
  propia consulta. Un recurso ajeno responde igual que uno inexistente
  (código, cuerpo, tiempo).
- **Autorización por función**: rutas de admin con su comprobación; 401/403
  antes que errores de validación.
- **Asignación masiva**: los modelos de entrada rechazan campos extra; el
  propietario, los roles y los estados los pone el servidor.
- **Autenticación**: firma, algoritmo fijado, audiencia, emisor y caducidad;
  roles solo de claims que el usuario no puede editar; tokens de máquina
  distintos de los de usuario, con alcance mínimo y comparados en tiempo
  constante.
- **Input en el borde**: lista blanca (dominios, formatos), tipos estrictos,
  longitudes, sin caracteres de control. Normaliza Unicode (NFKC) **antes**
  de escapar: caracteres de ancho completo pueden volverse comodines tras
  una normalización posterior.
- **Datos de terceros son input del atacante** (títulos, nombres,
  descripciones): longitud acotada; nunca en rutas de fichero, argumentos de
  línea de comandos ni sumideros HTML.
- **SSRF**: nunca pasar una URL del usuario a algo que la resuelve; extraer
  el identificador y reconstruir la URL; lista blanca de hosts, sin
  redirecciones.
- **Consumo de recursos**: tope global de tamaño de cuerpo (contando bytes,
  no fiándose de la cabecera), y topes de páginas, ficheros, duración,
  elementos por usuario y tasa.
- **Credenciales temporales** (URLs firmadas, tokens) siempre caducan.
- **Logs y errores**: nunca tokens, URLs firmadas ni datos sensibles; los
  mensajes externos se sanean y se truncan; el usuario no ve rutas, consultas
  ni trazas.
- **Configuración como código**: CORS con orígenes exactos (un comodín o una
  entrada mal formada impide arrancar), documentación automática de la API
  apagada en producción, cabeceras de seguridad, reglas de lint que prohíben
  imports peligrosos (cubriendo importación dinámica, subrutas y acceso por
  corchetes).
- **Base de datos**: consultas parametrizadas; unicidad y carreras con
  constraints, no con un `if`.
- **Dependencias**: sin CVEs altos; cada paquete nuevo, aprobado.
- **Cadena de suministro**: actions del CI fijadas por SHA; binarios
  descargados con checksum.

## Si delegas la autenticación en un proveedor

- Registro público desactivado si el grupo es cerrado, con prueba de humo de
  que se rechaza.
- Sesiones anónimas del proveedor rechazadas explícitamente si no se usan.

## Si la base de datos se expone por API (p. ej. PostgREST o un BaaS)

- Toda tabla nueva con control de acceso por fila y permisos mínimos.
- Toda función nueva revoca la ejecución a los roles públicos: se puede
  llamar por RPC con la clave pública. Sin SQL dinámico y con `search_path`
  fijado.
- Una verificación global de solo lectura que lista lo accesible para los
  roles públicos y debe salir vacía.

## Si hay interfaz web

CSP restrictiva (orígenes de API y almacenamiento explícitos),
`frame-ancestors 'none'`, `Referrer-Policy: no-referrer` (una URL firmada no
sale en el `Referer`), sin `innerHTML`/`eval` con datos de la API, y la
sesión del cliente con su riesgo de XSS documentado.
