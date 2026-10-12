# Forma de trabajo

Cómo se construye un proyecto una vez hecho el arranque
(`docs/proyecto.md` aprobado). No son reglas que se cumplan solas: son lo
que funcionó en proyectos anteriores, cada punto con el problema que
resolvió. El humano decide qué se usa en cada proyecto y lo puede cambiar
cuando estorbe. Tests, CI, revisiones o métricas se añaden cuando él lo
pide; esta plantilla no los impone.

## Quién hace qué

| Quién | Qué hace |
|---|---|
| **Sesión principal** (con el humano) | el arranque, las specs (un subagente no puede esperar a que el humano responda), lanzar los agentes, pasar sus resultados y los arreglos pequeños |
| `implementer` | construye la feature o el tramo y devuelve qué hizo, con qué tests y qué capturas |
| `reviewer` | revisión funcional con contexto limpio: `Veredicto: APPROVED` o `CHANGES_REQUESTED` |
| `security_reviewer` | seguridad de la feature entera, al final y tras el `APPROVED` del reviewer |

Los cambios pequeños y claros los hace la sesión principal sin lanzar
agentes. Si un revisor pide cambios, se relanza el `implementer` con esos
cambios citados tal cual, y después vuelve a pasar el `reviewer`.

## El ciclo de una feature

1. **Una feature cada vez, en el orden de `docs/proyecto.md`.** La primera
   monta el esqueleto con el generador oficial del framework, cruza la
   arquitectura de punta a punta con un "hola mundo" y comprueba los
   supuestos de riesgo **antes** de escribir producto. *En un piloto, un
   cambio de framework a mitad de la primera feature tiró una iteración
   entera.*
2. **Spec corta cuando hay decisiones**, y nada de spec en los cambios
   pequeños y claros. Lleva:
   - qué hace, en requisitos comprobables ("responde en < 500 ms con 1.000
     elementos", no "rápido");
   - los casos límite de cada entrada: vacía, máxima, caracteres raros,
     duplicada, servicio caído;
   - cómo se hace y qué se descartó;
   - las preguntas al humano, con recomendación.

   Unas 400 líneas como mucho: cada agente la relee en cada vuelta. *Specs
   de 1.000-2.000 líneas costaban más de lo que aportaban.*
3. **Si el alcance es ambiguo, se pregunta antes de redactar.** *Una spec
   se reescribió entera por no hacerlo.*
4. **Aprobación del humano**, con un sí explícito a la spec y a sus
   decisiones. Al pedirla, se dice qué frase vale ("apruebo con las
   recomendadas"). Si falta algo, se repregunta solo eso, en una línea.
   *"Sigue" no es aprobar; pero tres idas y vueltas por la frase exacta
   cansan.*
5. **Implementar** (`implementer`), con las pruebas que el humano haya
   pedido. *Más de dos tramos por feature multiplica las vueltas:
   normalmente basta con lógica y datos primero, y después la interfaz.*
6. **Revisión independiente** (`reviewer`), si el humano la quiere: con el
   contexto limpio, nunca quien implementó. **La de seguridad va al
   final de la feature y solo cuando la funcional ya aprobó.** *En un
   piloto, revisar seguridad en cada tramo supuso 47 pasadas para 2
   rechazos; en paralelo con la funcional, la mitad de las pasadas caían
   en código que se iba a rehacer.*
7. **Visto bueno visual del humano** en las features con pantallas, antes
   de cerrar. Sus cambios son un arreglo pequeño o una vuelta más.
8. **Cierre y commit**, con el humano. Tras el commit se actualiza lo que
   diga "pendiente". *Una sesión arrancó con un pendiente que ya estaba
   hecho.*

**Cambios de rumbo.** Ampliar el alcance al cerrar es una feature nueva,
no una enmienda (*una spec llegó a 699 líneas*). Un arreglo sobre algo ya
cerrado también es una feature nueva, pequeña. Si cambia una decisión de
base (stack, plataforma, datos), se para, se decide y se actualiza
`docs/proyecto.md` antes de seguir.

## Pruebas (cuando se pidan)

- **Un test vale si cae con el código roto.** Para comprobarlo, se rompe la
  línea de producción, se ve caer el test y se restaura. Si para
  restaurar hay que tocar también el test, el test no protegía nada.
- **Mutantes solo en las zonas críticas** (dinero, escritura de datos,
  permisos, parsers, fechas), con la herramienta del stack. Quien
  implementa y quien revisa usan **el mismo comando y el mismo criterio**.
  Fuera de esas zonas basta un test de comportamiento por requisito. *En
  un piloto se rechazaron 42 de 44 primeras entregas por mutantes que el
  implementador no había probado: cada uno usaba un criterio distinto.*
- **Un test de límite se compara con el valor de la spec**, no con la
  constante del código.
- **Un doble de prueba respeta los límites reales** (paginación, filtros).
  *Uno que los ignoraba validó un bug.*
- **Un test intermitente se arregla en la siguiente vuelta**, no se anota.
- **Un solo comando verifica todo**: tests, lint, tipos, build y auditoría
  de dependencias. Antes de fiarse de él, se demuestra que cada paso sabe
  fallar. *Hubo un comprobador de tipos que no comprobaba nada.*

## Interfaz

- **El aspecto sale de `docs/diseno.md`**, no de cada spec: las specs lo
  citan y solo fijan lo propio de sus pantallas.
- **Capturas de lo construido**: claro y oscuro, escritorio y móvil, caso
  normal y peor caso, con un modo de datos falsos que lo permita. *Los
  fallos visuales solo los veía el humano.*
- **El navegador de capturas, aislado** (Playwright con `--isolated`). *Un
  navegador compartido con el humano estropeó una tanda de capturas.*

## Código

- **Nativo antes que dependencia**, y ninguna dependencia nueva sin
  preguntar.
- **Regla de tres**: no se abstrae hasta el tercer uso real.
- **Se parsea en el borde y se confía dentro.** Todo lo que viene de fuera
  (usuario, red, almacenamiento) se valida al entrar.
- **Nunca tragarse un error**: hacia fuera, un mensaje cerrado; hacia el
  log, el detalle saneado.
- **Las carreras se resuelven con constraints o escrituras condicionales**,
  no con leer-comprobar-escribir.
- **Atajos marcados**: `ATAJO: <límite> · <camino de mejora>` en un
  comentario, para encontrarlos todos después.

## Trabajar con agentes

- **Encargos con el contexto mínimo suficiente**: qué hacer, qué leer, qué
  no tocar y las reglas que cambiaron en la sesión. El agente arranca en
  frío.
- **Las hipótesis se etiquetan como hipótesis.** *Una causa supuesta y falsa
  costó una vuelta entera.*
- **Cada agente trabaja en su propia carpeta temporal.** *Uno ejecutó la
  lista de mutantes de otro.*
- **Los procesos se matan por su PID, nunca por nombre.** *`taskkill /IM
  node.exe` mató todos los `node` de la máquina.*
- **Las copias de trabajo, sin enlaces a `node_modules` o `.venv`.** *Un
  `rm -rf` atravesó el enlace y casi vacía el original.*
- **Lo que se sabe de fuera** (versiones, planes, límites), con su fuente y
  su fecha. *Un proveedor pasó a "legacy" entre dos consultas.*

## Seguridad

- **Los secretos no pasan por el contexto**: no se leen `.env` ni claves, no
  se imprimen y no se copian (`.claude/settings.json` lo bloquea).
- **El atacante no usa tu interfaz**: llama a la API directamente. Toda
  comprobación importante vive en el servidor o en los datos.
- **Nada destructivo sobre datos reales** (`DROP`, `TRUNCATE`, o `DELETE`
  y `UPDATE` sin `WHERE`).
- **Se avisa antes de tocar servicios reales** y de lo que cuestan.
