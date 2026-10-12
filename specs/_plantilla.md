# FNN — <Título>

Estado: borrador
<!-- Con el sí del humano: "Estado: aprobada (AAAA-MM-DD)". Copia este
fichero a specs/FNN-<nombre-corto>.md. Máximo ~400 líneas: cada agente la
relee en cada vuelta. Cada cosa se dice una vez y se cita archivo:línea en
vez de copiar código. -->

## Qué hace

<Dos o tres líneas: el comportamiento que gana el usuario.>

## Requisitos

Comportamiento observable y comprobable ("responde en < 500 ms con 1.000
elementos", no "rápido"). Cada uno con sus casos límite.

- **R1** — <CUANDO … el sistema DEBE …>
  - Límites: <vacío, máximo, caracteres raros, duplicado, servicio caído…>
- **R2** — <…>

<Si toca entrada externa, autenticación, datos de otros o acceso a datos:
requisitos de seguridad comprobables (ver docs/seguridad.md), aunque nadie
los haya pedido. El security_reviewer mide el código contra ellos.>

## Cómo se hace

<Ficheros y firmas, datos, flujo. Pantallas: solo lo propio de esta
feature; el aspecto sale de docs/diseno.md.>

### Descartado

- <Alternativa> — <por qué no>.

### Escalabilidad

Las cuatro preguntas, respondidas aunque sea con "no aplica: <motivo>":

1. **¿Funciona sin estado en memoria?** Si guarda estado, ¿por qué es
   correcto si el proceso se reinicia o hay varias instancias?
2. **¿Cada consulta nueva tiene índice?** Nombra las columnas.
3. **¿Hay algún límite sin acotar?** Listas, ficheros, colas, cuerpos. Los
   topes se cuentan en el origen (se cuenta en la base de datos, no se
   traen las filas).
4. **¿Hay N+1?**

## Lo que no se puede verificar con tests

<Lo que solo se comprueba a mano (un dispositivo físico, un servicio
real…), con el protocolo para comprobarlo. Si no hay nada: "nada".>

## Prueba con servicios reales

<Solo si la feature conecta con servicios reales (despliegue, pagos,
correo, APIs externas); si no, bórrala. Mirar la interfaz no cuenta: eso lo
cubren las capturas. La revisa el reviewer en la primera vuelta y la
ejecuta el humano al final.>

- Aviso: qué servicios toca y si puede costar dinero.
- Pasos copiables, **en orden ejecutable** (recursos antes de
  referenciarlos, variables antes del primer despliegue, migraciones antes
  que el código que las usa), cada uno con su resultado esperado y, si
  falla, qué pegar (el final del error, sin valores sensibles).
- **Nunca se pide pegar un secreto.**
- Antes de probar, se comprueba qué commit está desplegado y se reinician
  los procesos de larga duración.
- Comprobaciones de base de datos, solo de lectura.
- Opciones de panel que el código no controla (registro público, accesos
  anónimos…), comprobadas y apuntadas.

## Tareas

Si hay varios tramos, como mucho dos (normalmente lógica y datos, después
interfaz), cada uno se revisa antes del siguiente.

- [ ] T1 — <…> (R1)
- [ ] T2 — <…> (R2)

## Decisiones del humano

<Preguntas con recomendación; tras la respuesta, la respuesta tal cual y la
fecha.>

## Enmiendas

<Si algo cambia después de aprobar la spec (por ejemplo, el humano rechaza
el aspecto de una pantalla), no se reescribe lo aprobado: se añade aquí
"Enmienda AAAA-MM-DD", con requisitos nuevos que siguen la numeración. La
enmienda vuelve a pasar por la aprobación del humano.>

## Desviaciones

<Las anota el implementer: qué cambió respecto a la spec y por qué. Cada
una lleva "Visto bueno: <reviewer | humano>, AAAA-MM-DD" o queda
pendiente.>
