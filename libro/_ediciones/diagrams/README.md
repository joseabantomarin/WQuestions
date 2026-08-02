# Diagramas del libro

Esta carpeta contiene los diagramas que aparecen en los `.docx` generados.

## Estructura

```
diagrams/
  src/    ← fuente (Python con matplotlib/networkx)
  png/    ← salida (generada automáticamente, no editar a mano)
```

## Cómo agregar un diagrama nuevo

1. **Escribir el script fuente** en `src/NN_nombre.py` (NN = número de orden de aparición en el libro).
   Cada script es independiente: importa lo que necesita, dibuja con matplotlib, guarda PNG en `../png/`.
   Ver `src/01_ocho_ejes.py` como ejemplo.

2. **Renderizar**:
   ```bash
   ./render_diagrams.sh
   ```
   Esto ejecuta cada `src/*.py` y deja los PNG en `png/`.

3. **Referenciar desde un capítulo** con sintaxis markdown estándar:
   ```markdown
   ![Los ocho ejes de WQuestions](../diagrams/png/01_ocho_ejes.png)
   ```
   El alt-text se usa como leyenda en el `.docx` (cursiva, debajo de la imagen).
   También se admite leyenda explícita:
   ```markdown
   ![alt corto](../diagrams/png/foo.png "Leyenda larga al pie")
   ```

4. **Regenerar los `.docx`**:
   ```bash
   python3 md_to_docx.py
   ```

## Convenciones estéticas

Para que todos los diagramas se sientan parte del mismo libro, usar:

- **Tipografía**: por defecto (sans-serif de matplotlib).
- **Colores principales**:
  - Tinta general: `#1f2937` (gris oscuro)
  - Azul "ejes de valor": fondo `#e0e7ff`, borde `#4f46e5`
  - Ámbar "ejes estructurales / predicados": fondo `#fef3c7`, borde `#b45309`
  - Verde para reificación/situaciones: fondo `#dcfce7`, borde `#15803d`
  - Gris suave para fondo/anillo: `#9ca3af` / `#f3f4f6`
- **DPI**: 200 (suficiente para impresión a 6 pulgadas de ancho).
- **Tamaño**: imágenes cuadradas o ligeramente apaisadas; el convertidor las pondrá a 6" de ancho.
- **Texto en el diagrama**: mínimo. Las explicaciones van en la prosa del capítulo, no en el diagrama. Si una etiqueta no cabe, se simplifica.

## Cuándo usar diagrama vs prosa vs tabla

- **Tabla** (markdown nativa): cuando los datos están bien estructurados en filas y columnas.
- **Bloque de código**: cuando se muestran tripletas, signaturas o hechos en notación del modelo.
- **Diagrama**: cuando hay relaciones espaciales, topológicas, jerárquicas o causales que se pierden en texto. Especialmente útil para:
  - Arquitecturas de capas (D8, MCP + LLM)
  - Espacios multidimensionales (cap 9)
  - Cadenas causales (cap 11, ejemplo del fútbol)
  - Plantilla vs instancia (cap 5, D4)
  - Grafos de hechos con varios sujetos compartidos

## Diagramas previstos

| # | Nombre | Capítulo | Estado |
|---|---|---|---|
| 01 | Los ocho ejes de WQuestions | 7 (cierre Parte II) | ✓ hecho |
| 02 | El hecho atómico | 8 | pendiente |
| 03 | Grafo de hechos sobre una situación | 8 | pendiente |
| 04 | Espacio multidimensional (hoja dispersa) | 9 | pendiente |
| 05 | Situación reificada y sus participantes | 10 | pendiente |
| 06 | Cadena causal (minuto 89 del fútbol) | 11 | pendiente |
| 07 | Arquitectura D8 de cuatro capas | 13–14 | pendiente |
| 08 | WQuestions + LLM + MCP | 19 | pendiente |
| 09 | Plantilla en K + instancia en O | 5 o 17 | pendiente |
| 10 | Bitemporalidad / vigencia D9 | 10 o 17 | pendiente |
