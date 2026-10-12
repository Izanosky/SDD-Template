# Plantilla: forma de trabajo con Claude Code

Una forma de trabajar para empezar y construir un proyecto con Claude Code,
como lo haría un equipo de verdad: primero se entiende **qué** se construye
y para quién, y solo después se decide **cómo**. La plantilla no ejecuta
nada (no trae tests, CI ni scripts). Solo describe la forma de trabajo,
para que Claude la siga y tú decidas en cada paso.

## Uso

1. Copia esta carpeta como raíz del proyecto nuevo (o copia sus ficheros en
   uno que ya exista).
2. Abre Claude Code en ella y di qué quieres construir, o escribe
   `/arranque`.
3. Responde a la entrevista. Cada pregunta trae una recomendación; "no lo
   sé" también vale.

## El flujo

| Fase | Qué se decide |
|---|---|
| 1. Requisitos | qué hace la aplicación, para quién, qué entra en la primera versión y qué no |
| 2. Alcance | personal, compartido o producción: cuánto rigor merece |
| 3. Aspectos clave | lo que exige ese alcance (caché, escalado, pool de conexiones, observabilidad, copias…), traído por Claude aunque no lo menciones |
| 4. Stack | arquitectura, lenguaje, framework, datos y despliegue: los eliges tú o Claude propone opciones |
| 5. Librerías | lo que va encima del stack, con versión y alternativa descartada |
| 6. Diseño visual | referencias reales, tres direcciones para comparar, librerías de interfaz y tokens |

Después se construye feature a feature, siguiendo `docs/forma-de-trabajo.md`:
lo que funcionó en proyectos anteriores, como recomendaciones. Si quieres
specs, tests, revisiones o CI, pídelos cuando los necesites.

## Ficheros

| Fichero | Para qué |
|---|---|
| `CLAUDE.md` | lo que Claude lee siempre: la forma de trabajo y las reglas duras |
| `.claude/skills/arranque/` | la entrevista inicial (`SKILL.md`), el catálogo de aspectos clave, la fase de diseño y la plantilla de `docs/proyecto.md` |
| `docs/forma-de-trabajo.md` | cómo se construye una vez hecho el arranque, y quién hace cada paso |
| `.claude/agents/` | `implementer` (construye), `reviewer` (revisión funcional) y `security_reviewer` (seguridad, al final). Heredan el modelo de la sesión; para cambiarlo, añade `model:` en su cabecera |
| `.claude/settings.json` | impide leer secretos y pide permiso para commits, push e instalar dependencias |
