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
