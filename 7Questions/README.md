# 7Questions — Experimento de Coordenadas

Prototipo experimental para comparar almacenamiento en **coordenadas 7D** vs **triplets**.

## Idea

En lugar de guardar datos como triplets etiquetadas:
```
{subject: "venta_123", role: "vendedor", value: "juan"}
```

Guardamos como puntos en un espacio 7D:
```
[q, o, l, t, n, k, m] = [juan, venta_123, ?, ?, 50, libro, comprador]
```

Las 7 dimensiones son implícitas — la IA interpreta cuál es cuál al insertar.

## Estructura

- `src/storage.py` — almacenamiento sparse 7D (dict)
- `src/api.py` — operaciones (put, get, query, show_state)
- `src/mcp.py` — wrapper MCP para exponer al cliente
- `tests/benchmark.py` — comparación coords vs triplets

## Objetivo

1. Medir latencia de operaciones
2. Contar tokens en serialización
3. Comparar contra MCP actual
4. Decidir si vale la pena el cambio

## Status

🔨 En construcción
