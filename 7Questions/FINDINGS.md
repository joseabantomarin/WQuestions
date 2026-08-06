# 7Questions — Hallazgos del Benchmark

**Fecha:** 2026-07-11
**Objetivo:** Comparar almacenamiento 7D (coordenadas) vs triplets en términos de rendimiento.

## Resultados

### 1. Serialización

| Formato | Tamaño | Diferencia |
|---------|--------|-----------|
| Coordenadas | 314 bytes | +7.9% |
| Triplets | 291 bytes | baseline |

**Conclusión:** Las coordenadas son PEOR en tamaño. Razón: los `null` se serializan como `null`, mientras que triplets omiten campos innecesarios.

### 2. Rendimiento de Operaciones

| Operación | Latencia | Notas |
|-----------|----------|-------|
| Put | 0.65 µs/op | Muy rápido |
| Query | 44 µs/op | Lento — escaneo O(n) |
| Show model | 0.44 ms | Serialización JSON |

**Conclusión:** El problema no es Put (es rápido), sino Query que escanea todo.

### 3. Costo en Tokens (LLM)

| Formato | Tokens (100 puntos) | Ahorro |
|---------|-------------------|--------|
| Coordenadas | ~1292 | -5.7% |
| Triplets | ~1370 | baseline |

**Conclusión:** Ahorro marginal en tokens (~5.7%).

## Hipótesis

El bottleneck **NO es la estructura de datos**, sino:

1. **Serialización innecesaria** — los `null` son verbose
2. **Query ineficiente** — escaneo bruto es O(n)
3. **Token overhead en LLM** — la IA gasta ciclos interpretando

## Próximos Pasos

- [ ] Implementar índices (hash por eje) para speedup query
- [ ] Comprimir datos: omitir `null`, usar notación compacta
- [ ] Medir latencia red vs CPU
- [ ] Comparar contra tuplas numéricas (si performance es critica)
