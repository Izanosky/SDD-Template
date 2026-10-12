---
name: auditoria-seguridad
description: Auditoria de seguridad del repositorio entero (no de un diff) y destino de sus hallazgos con el humano. Proponerla cada 4 features cerradas o al cerrar una fase, y lanzarla solo con su si - es cara. Solo la sesion principal.
---

# Auditoría de seguridad

Cada revisión de una feature mira su diff. Esta mira el conjunto: una regla
de acceso que pierde su protección por el cambio de otra feature, una
variable pública que entró por otro lado, una ruta vieja que no conoce un
rol nuevo.

## 1. Lanzarla

Confirma con el humano, porque recorre todo el repositorio, y elige con él
el motor:

- **`security_reviewer` en modo auditoría**: el de siempre, con un solo
  agente. Encargo: "Modo auditoría. Revisa el repositorio entero en su
  estado actual. Hallazgos con gravedad y `archivo:línea`."
- **`security-audit`** (Cloudflare), si está instalada: muchos agentes, más
  a fondo y más cara. Perfil y presupuesto, acordados con el humano.
- **`/insecure-defaults:audit`** (Trail of Bits), si está instalado: barato
  y acotado a configuraciones inseguras por defecto (secretos de respaldo,
  credenciales por defecto, modos que fallan abiertos, CORS `*`, debug).
  Puede acompañar a cualquiera de los otros dos.

Las dos últimas orquestan agentes y solo funcionan desde la sesión
principal.

## 2. Informe

El `security_reviewer` escribe `docs/auditorias/AAAA-MM-DD.md`; con los otros
motores, lo escribes tú a partir de su informe (≤ 200 líneas): los hallazgos
confirmados, con su gravedad y `archivo:línea`; aparte, los que están
pendientes de validar; y la ruta del informe original del motor, si lo
hay.

## 3. Destino de cada hallazgo, con el humano

- **arreglo pequeño** ahora mismo, si no añade comportamiento;
- **feature nueva** en `docs/proyecto.md`, con el `archivo:línea` y el
  cambio propuesto copiados en ella, para que nadie tenga que reabrir el
  informe. Nunca se pone delante de la feature que está en curso;
- **descartado**, con su motivo.

Apunta el destino de cada uno al final del informe. Sin ese apartado, la
auditoría no está cerrada.
