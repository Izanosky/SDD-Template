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

## TDD, sabotajes y mutantes

- **TDD**: test primero, verlo fallar **sobre el código real** (no con un
  script que imita el código viejo), implementar, verlo pasar.
- **Sabotajes** (implementer): borrar la línea crítica, ver caer un test,
  restaurar; encabezado `## Sabotajes` en `evidence.md`. `state.py` lo exige.
- **Mutantes** (reviewer): romper el código en una copia temporal y exigir
  que un test caiga. Mutante que sobrevive = test que falta.
- **Revertir solo la línea de producción**: si hace falta revertir también
  el test o el arnés, el test no protegía nada.

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
  tocados), nunca el trabajo: `init.sh` completo y checkpoints uno a uno.

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
