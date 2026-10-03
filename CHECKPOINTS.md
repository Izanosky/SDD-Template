# Checkpoints de "done"

Cada ítem tiene un único dueño: dos agentes no se contradicen.

## Bloque funcional — dueño: `reviewer`

- Cada `R<n>` tiene un test que lo cubre de verdad (verificado con mutantes).
- Tabla `## Sabotajes` presente y reproducible.
- Tasks marcadas; task humana revisada y ejecutable paso a paso.
- `init.sh` en verde, ejecutado por el reviewer.
- Se respetan `docs/architecture.md`, `docs/principios.md` y las convenciones del stack.
- <RELLENAR: checkpoints funcionales propios del proyecto.>

## Bloque de escalabilidad — dueño: `reviewer`

- Stateless, o `design.md` justifica por qué no.
- Consultas nuevas con índice.
- Sin N+1.
- Sin límites sin acotar; los topes se cuentan en el origen.

## Bloque de seguridad — dueño: `security_reviewer`

- Sin secretos en código, specs ni artefactos públicos (bundles, apps).
- Todo input validado en el borde.
- Autorización explícita por objeto y por función en cada ruta tocada.
- Tabla de ataque completa para cada ruta o acción nueva.
- Credenciales temporales con caducidad.
- Configuración (escáner, lint, CSP, CORS) y runbooks revisados como código.
- Dependencias nuevas aprobadas y sin CVEs altos.
- <RELLENAR: riesgos propios del proyecto.>
