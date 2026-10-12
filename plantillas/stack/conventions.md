# Convenciones — <stack>

<!-- Copiar a docs/<stack>/conventions.md. Solo lo que difiere de las
convenciones estándar del lenguaje: lo que el modelo ya sabe no se escribe.
Si el stack tiene interfaz web, copiar también lo que aplique de
plantillas/stack/conventions-web.md. -->

<Lenguaje y versión.> Se lee solo cuando el scope activo incluye <stack>.
La configuración de las herramientas manda; esto explica el porqué.

## Herramientas
<Tests · lint · formato · tipos · build · auditoría, con el comando.
Casos donde el comprobador se queda corto y cómo se acota.>
<Mutantes (zonas críticas, docs/verification.md): herramienta del stack y
el comando para unos ficheros concretos, p. ej. `npx stryker run --mutate
<ficheros>`, `cargo mutants --file <fichero>`; en Python, `mutmut run`
(3.x: ficheros en `[tool.mutmut] paths_to_mutate` de `pyproject.toml`) **no
funciona en Windows nativo** (comprobado 2026-10-11): ahí, `cosmic-ray`
(8.x: `cosmic-ray init cr.toml s.sqlite && cosmic-ray exec cr.toml s.sqlite
&& cr-report s.sqlite`), que muta el fichero en sitio mientras corre:
siempre en una copia del scope. Lo usan implementer y reviewer igual.
Su carpeta de trabajo (`mutants/`, `.stryker-tmp/`…) fuera de la recogida
de tests y del lint.>

## Idioma
<Código en … / prosa en … / nombres de test que describen comportamiento.>

## Errores
<Cómo se lanzan, qué ve el usuario, qué va al log.>

## Modelos / tipos
<Entrada ≠ fila; campos extra rechazados; tipos cerrados para estados.>

## Concurrencia
<Qué es bloqueante, dónde se ejecuta.>

## Tests
<Framework; qué se prueba; dobles; adaptador real con cliente grabador;
límites contra el literal de la spec.>

## Estructura
<Módulos, fronteras, dónde vive lo compartido.>

## Patrones prohibidos
<Lista, cada uno con su motivo.>
