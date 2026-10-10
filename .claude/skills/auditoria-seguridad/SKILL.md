---
name: auditoria-seguridad
description: Lanza una auditoria de seguridad completa del repositorio, o da destino a los hallazgos de una auditoria pendiente (audits_pending). Solo la sesion principal (leader), nunca un subagente, y solo tras confirmarlo con el humano - es cara.
---

# Auditoría de seguridad completa

Cada revisión de feature mira su diff; esta mira el conjunto (una tabla que
pierde su protección con la migración de otra feature, una variable pública
que entró por otro lado, una ruta vieja que no conoce un rol nuevo).

## Si `state.py` trae `audits_pending`: dar destino a los hallazgos

1. Lee `progress/audits/<fecha>/informe.md` (no `evidencia.md`). Si falta o
   está cortado, la auditoría no terminó: reanuda al `security_reviewer`
   (leader, "Agente que vuelve sin terminar"), no sigas.
2. Con el humano, cada hallazgo sale con un destino:
   - **arreglo pequeño del leader** (solo si cumple "Arreglos pequeños" de
     `.claude/agents/leader.md`);
   - **feature nueva** en `feature_list.json`, colocada delante de la que más
     depende de ella pero **nunca delante de la que está en curso**
     (`state.py` despacha la primera no `done`: la en curso quedaría parada
     a mitad de una IT y habría dos en curso), con el
     `archivo:línea` y el cambio propuesto copiados en su `acceptance` (así
     nadie reabre el informe);
   - **línea más** en el `acceptance` de una feature pendiente;
   - **descartado**, con motivo.
3. Escribe `progress/audits/<fecha>/cambios.md`: tabla hallazgo → destino.
   Sin hallazgos en un informe completo, también: `cambios.md` con "Sin
   hallazgos"; si falta, la auditoría sigue en `audits_pending` para
   siempre. Desde ahí se lee
   `cambios.md`, nunca el informe.

## Si no: lanzar una auditoría nueva

1. Confirma con el humano (es una ejecución cara sobre todo el repo) y elige
   con él el motor; los dos primeros orquestan muchos agentes y solo
   funcionan desde la sesión principal, nunca desde un subagente:
   - **`security-audit`** (Cloudflare), si está instalada: modo auditoría
     completa, perfil `quick` o `standard` y presupuesto de agentes
     acordados con el humano. Su salida va fuera del repo
     (`~/security-audit-skill/<repo>/run-<N>`, déjala ahí).
   - **`/insecure-defaults:audit`** (Trail of Bits), si está instalado: más
     barato y acotado a configuraciones inseguras por defecto (secretos de
     respaldo, credenciales por defecto, modos que fallan abiertos, CORS
     `*`, debug). Puede acompañar a cualquiera de los otros dos.
   - **`security_reviewer` en modo auditoría**: el de siempre, si no hay
     ninguna de las anteriores o el humano prefiere un solo agente.
2. Crea `progress/audits/<AAAA-MM-DD>/` (`-2` si ya existe una ese día).
3. Con `security_reviewer`, lánzalo con: "Modo auditoría. Carpeta
   `progress/audits/<fecha>/`. Revisa el repositorio entero contra su estado
   actual (ver tu sección 'Modo auditoría'). Escribe `informe.md` (≤ 200
   líneas) y, si hace falta, `evidencia.md`." Con las otras, escribe tú
   `informe.md` (≤ 200 líneas) a partir de su informe: hallazgos
   confirmados con gravedad y `archivo:línea`, los pendientes de validar
   aparte, y la ruta del informe original en `evidencia.md`.
4. La línea de `progress/metrics.csv` la escribe el hook de métricas con
   `feature = audit`; con los motores de la sesión principal no hay
   subagente que la dispare: apúntala tú (`it = <fecha>`).
5. Vuelve al primer apartado para dar destino a los hallazgos.
