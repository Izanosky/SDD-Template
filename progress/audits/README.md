# Auditorías de seguridad completas

Una carpeta por auditoría, `<AAAA-MM-DD>/` (`-2` si hay dos el mismo día),
nunca dentro de una feature ni de una IT. Procedimiento: skill
`/auditoria-seguridad`.

```
informe.md     hallazgos con gravedad y archivo:línea (security_reviewer)
evidencia.md   anexo: tabla de ataque, pruebas, lo que está limpio
cambios.md     destino de cada hallazgo (leader, con el humano)
```

Sin `cambios.md` la auditoría está pendiente y `state.py` lo avisa
(`audits_pending`). Con él, se lee `cambios.md` y nunca el informe.
