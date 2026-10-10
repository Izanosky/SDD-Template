# Arranque

<!-- Copiar a progress/arranque.md al empezar /arranque. state.py no
despacha ninguna feature hasta que la linea de estado diga APROBADO: no la
traduzcas ni la cambies de formato. -->

Estado: en curso

## Producto

<5-10 líneas: qué es, para quién, primera versión y lo que no entra,
dispositivos ahora y más adelante, datos y su sensibilidad, peso de la
interfaz, presupuesto, preferencias y vetos del humano.>

## Mapa de decisiones

Modo: **obvia** (se acepta en bloque) · **elegir** (2-3 opciones, decide el
humano) · **investigar** (solo con su sí y su coste dicho) · **no aplica**.
Borra las filas que no apliquen; añade las que falten.

| Bloque | Decisión | Propuesta | Modo | Decidido | Fija / revisable (cuándo) | ADR |
|---|---|---|---|---|---|---|
| Plataforma | tipo de app, empaquetado, sin conexión | | | | | |
| Arquitectura | forma, capas y fronteras, dónde vive cada pieza | | | | | |
| Backend | lenguaje y versión, framework, API y contratos, validación, errores, segundo plano | | | | | |
| Datos | almacenamiento, acceso u ORM, migraciones y formatos, copias | | | | | |
| Seguridad | autenticación y autorización, secretos, zonas sensibles | | | | | |
| Frontend | framework, enrutado, estado y caché, formularios, estilos, componentes, iconos, animación, gráficos, i18n, accesibilidad | | | | | |
| Calidad | tests por capa, lint, formato, tipos, auditoría de dependencias | | | | | |
| Operación | build, CI, despliegue y ramas, entornos, logs, coste | | | | | |

## Supuestos de riesgo

Los 2-3 que, si fallan, obligan a cambiar una decisión de base. Los
comprueba F00 antes de escribir producto.

1. <supuesto> — cómo se comprueba — fila del mapa afectada

## Bloques cerrados

<Una línea por bloque al cerrarlo: fecha y qué se decidió. Tras cada uno se
puede hacer /clear: este fichero basta para seguir.>
