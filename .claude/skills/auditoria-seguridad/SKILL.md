---
name: auditoria-seguridad
description: Lanza una auditoria de seguridad completa del repositorio, o da destino a los hallazgos de una auditoria pendiente (audits_pending).
disable-model-invocation: true
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

1. Confirma con el humano (es una ejecución cara sobre todo el repo).
2. Crea `progress/audits/<AAAA-MM-DD>/` (`-2` si ya existe una ese día).
3. Lanza `security_reviewer` con: "Modo auditoría. Carpeta
   `progress/audits/<fecha>/`. Revisa el repositorio entero contra su estado
   actual (ver tu sección 'Modo auditoría'). Escribe `informe.md` (≤ 200
   líneas) y, si hace falta, `evidencia.md`."
4. Línea en `progress/metrics.csv` con `feature = audit` e `it = <fecha>`.
5. Vuelve al primer apartado para dar destino a los hallazgos.
