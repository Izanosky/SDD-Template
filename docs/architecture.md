# Arquitectura

## Estilo

<RELLENAR. Por defecto, **monolito modular**: un proceso por despliegue,
dividido en módulos que se llaman por funciones. Un servicio nuevo carga con
la prueba: qué problema paga la latencia y el despliegue extra.>

## Módulos y fronteras que no se cruzan

<RELLENAR: módulos, quién puede importar a quién, dónde viven los contratos
compartidos (una única definición para lo que cruza procesos).>

## Escalabilidad: las cuatro preguntas

Cada `design.md` las responde explícitamente:
1. **¿Es stateless?** Si guarda estado en memoria, ¿por qué es correcto si el
   proceso se reinicia o hay varias instancias?
2. **¿La consulta nueva tiene índice?** Nombrar las columnas.
3. **¿Hay algún límite sin acotar?** Listas, ficheros, colas, cuerpos. Los
   topes se cuentan en el origen (contar en la base de datos, no traer filas).
4. **¿Hay N+1?**

## Restricciones del entorno

Datos que caducan: cada fila con fecha y fuente.

| Restricción | Valor (fecha, fuente) | Consecuencia de diseño |
|---|---|---|
| <RELLENAR: memoria/CPU del hosting, arranque en frío, cuotas, límites de planes> | | |
