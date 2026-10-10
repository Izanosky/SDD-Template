# Verificación

Que un agente diga que algo funciona no es demostrarlo.

## `init.sh` es la puerta

```
bash init.sh            scope de la feature activa
bash init.sh --all      todos los scopes de harness.json (el CI usa este)
bash init.sh --dry-run  solo anuncia el scope
```

El raíz delega en `<scope>/init.sh`; **un scope sin `init.sh` bloquea**, no
se salta. Cada stack cubre, fallando a la primera:

| | <RELLENAR: stack A> | <RELLENAR: stack B> |
|---|---|---|
| tests | | |
| lint | | |
| formato | | |
| tipos | | |
| build | | |
| secretos | gitleaks `--redact` (config de la raíz) | ídem |
| dependencias | | |

## Un verificador tiene que saber fallar

Tras escribir cada paso, **planta un fallo a propósito** y comprueba que el
código de salida no es 0. Falsos verdes habituales: un comprobador de tipos
que con cierta configuración no comprueba nada; un test que compara un
literal que el código ya no usa; un arnés que pisa con un literal el valor
que dice proteger.

## Zonas críticas y mutantes <!-- ajuste-2026-10-10 -->

Lección del piloto: el reviewer rechazó 42 de 44 primeras entregas, casi
siempre por un mutante que sobrevivía en una línea que el implementer no
había saboteado; las IT de corrección fueron el 37 % del tiempo. Los dos
usaban criterios distintos, y el mismo rigor en dinero que en una animación.

**Zonas críticas** (las fija `/arranque`): <RELLENAR: p. ej. dinero y
cálculos, escritura de datos y migraciones, autenticación y permisos,
parsers y validación de entrada externa>.

- **En zonas críticas, la herramienta de mutantes del stack** (decidida en
  `/arranque`, comando en `docs/<scope>/conventions.md`) sobre los ficheros
  críticos tocados en la IT. La pasa el implementer antes de entregar y la
  repite el reviewer: **el mismo comando, el mismo criterio**. Cada
  superviviente acaba en un test nuevo o en "equivalente: <por qué>". Donde
  la herramienta no llega (una consulta, un filtro, configuración), un
  sabotaje a mano: borrar la línea, ver caer un test, restaurar.
- **Fuera de las zonas críticas**, un test de comportamiento por viñeta de
  cada task. Un test flojo ahí es una observación del reviewer, no un
  rechazo, salvo que un `R<n>` se quede sin ningún test.
- Resultado en `evidence.md`, encabezado `## Sabotajes` (`state.py` lo
  exige): comando, muertos/supervivientes y qué se hizo con cada
  superviviente; `N/A: <motivo>` si la IT no toca zonas críticas.
- **Rojo sobre el código real**: lo exigible es que el test caiga con el
  código roto, y eso lo demuestran el mutante o el sabotaje. Escribir el
  test antes es recomendable, no obligatorio (en el piloto no se cumplió y
  no era lo que protegía).
- **Revertir solo la línea de producción**: si hace falta revertir también
  el test o el arnés, el test no protegía nada.

## Tests intermitentes

Un test que falla a veces es un fallo, no ruido: el leader lo apunta y se
arregla (o se pone en cuarentena con su motivo) en la siguiente IT de la
feature en curso. Lección: en el piloto se anotaron ocho y nadie los
arregló; cada uno costó repeticiones y desconfianza en los resultados.

## Interfaz: capturas <!-- ajuste-2026-10-10 -->

Los tests de interfaz (jsdom y similares) no ven el resultado: un texto
cortado, una columna desalineada o un diálogo vacío pasan en verde. En cada
tramo `(interfaz)`:

- el `implementer_ui` arranca el **modo de datos falsos** (normal y peor
  caso), captura cada pantalla tocada (claro/oscuro, 1280 y 390 px, ~8 como
  mucho) en `progress/<F>/IT<n>/capturas/` y las lista en `impl.md`
  (`## Capturas`);
- el `reviewer` las abre y bloquea **solo por fallos que se ven** (cortado,
  solapado, desalineado, contraste, peor caso roto, contradicción con
  `docs/<scope>/direccion-visual.md`). El gusto va a observaciones.

## Dobles de test

- **El doble prueba al llamador, no al adaptador.** Cada método nuevo de un
  adaptador real (repositorio, cliente HTTP, almacenamiento) lleva test
  propio con un **cliente grabador**: filtros exactos, valores escritos,
  cada rama de lectura (sin datos, nulo, válido).
- Un falso que ignora la petición puede validar un bug: si el código pagina
  o lee por bloques, el falso respeta el rango y los límites reales.
- El arnés restaura el **valor inicial capturado tras el import**.
- Comparar contra un servicio usa **la forma que el servicio devuelve**.

## Trazabilidad y presupuestos

- `impl.md`: tabla `R<n> → test` (fichero, test, aserción).
- `impl.md`, `review.md`, `security.md` ≤ 200 líneas, con citas; lo largo a
  `evidence.md`. **Una prueba no se borra por presupuesto, se mueve.** El
  leader no abre `evidence.md`; los revisores, solo para cuestionar una
  prueba.
- En `n > 1` se reduce el **contexto** (cambios pedidos, diff, ficheros
  tocados). **Re-revisión acotada**: si el rechazo anterior fue solo por
  `tests` y el diff de esta IT solo añade o cambia tests, se verifica lo
  pedido (cada superviviente citado ahora muere) y `init.sh --rapido`; si
  el diff toca producción, revisión completa.
  <!-- ajuste-2026-10-10 -->
- `init.sh --rapido` (tests, lint, formato, tipos) en las vueltas del
  implementer y del reviewer; `init.sh` completo (build, secretos,
  auditoría de dependencias) en el security_reviewer, el cierre y el CI.

## Portabilidad local ↔ CI

- `.sh` con bit de ejecución (`git update-index --chmod=+x`), `eol=lf` en
  `.gitattributes`, y llamados además con `bash script.sh`.
- Python: `sys.executable` en tests; en shell, `scripts/py.sh` (prueba
  `python3`, `python`, `py` **ejecutándolos**).
- `bash` desde Python en Windows: `shutil.which("bash")`, no `"bash"` (que
  resuelve antes a la de WSL).
- Relojes monotónicos: estado inicial `-inf`, no `0`.
- Si algo solo falla en el CI, sospecha primero de estas.

## Lo que no se puede verificar con tests

Se dice en el veredicto y se verifica a mano con un protocolo escrito y su
resultado registrado. <RELLENAR: casos propios, p. ej. comportamiento en un
dispositivo físico.> Nunca se declara verificado sin más.

## Pruebas con servicios reales (task humana)

Solo si la feature conecta con servicios reales (despliegue, pagos, correo,
APIs externas). Mirar la interfaz no es una task humana: lo cubren las
capturas. Lección: en el piloto, nueve features seguidas se cerraron sin
ejecutar su task humana, que el reviewer había revisado en cada IT1.
<!-- ajuste-2026-10-10 -->

La revisa el reviewer **ya en IT1** y la ejecuta el humano al final.

- Avisa de que conecta con servicios reales y de si puede costar dinero.
- **Orden ejecutable**: recursos antes de referenciarlos; variables antes
  del primer despliegue; migraciones antes que el código que las usa; el
  proceso que valida antes que los que confían en él.
- Pasos copiables, con el resultado esperado de cada uno; si falla, qué pegar
  (solo el final del error, sin valores sensibles).
- **Nunca pedir que se pegue un secreto.**
- Ten en cuenta la terminal real: variables reservadas y alias del shell;
  ventanas de credenciales que no reciben el foco en consolas integradas.
- Verificaciones de base de datos de solo lectura; nada destructivo a mano.
- Reinicia los procesos de larga duración tras cambiar su código o sus
  dependencias. Comprueba el commit desplegado antes de probar.
- Opciones de panel que el código no controla (registro público, accesos
  anónimos…): comprobarlas y anotarlas.
- Datos de proveedores (planes, cuotas, menús): documentación actual, con
  fecha.
- Resultado a `evidence.md` como resumen (códigos, estados, nunca tokens).
