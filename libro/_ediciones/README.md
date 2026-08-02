# Ediciones retiradas

Nada de lo que hay en esta carpeta es el libro. La edición viva y única es
[`libro/manuscrito2/`](../manuscrito2/), en HTML.

Esto se guarda por si alguna vez hace falta consultar de dónde vino el texto
actual. No se edita, no se regenera y no alimenta ningún artefacto.

## Qué hay aquí

| Carpeta | Qué es | Último cambio |
|---|---|---|
| `2026-06-markdown/` | 33 capítulos en Markdown. La edición anterior a la HTML | 26 jun 2026 |
| `2026-05-docx/` | 43 `.docx` generados desde una edición **aún más antigua** que la de Markdown | 21 may 2026 |
| `diagrams/` | Diagramas matplotlib/networkx que se incrustaban en los `.docx` | — |

Y los generadores que leían el Markdown: `generar_pdf.py`, `md_to_docx.py`,
`convertir.sh`, `render_diagrams.sh`, más el `requirements.txt` que solo servía
al primero.

## Por qué se retiraron

La edición HTML no es una conversión del Markdown: es una reescritura. La guía
de estilo lo fija en su línea 10 — «Redacción desde cero: no copiar frases del
manuscrito original» — y su §4 reemplaza además el repertorio de ejemplos.
Comparadas, las diferencias no son de redacción sino de contenido:

- Al Markdown le faltan **dos capítulos enteros**: el 11 (*La identidad a través
  de los sistemas*) y el 12 (*Puentes: objetos, bits, grafos y cadenas*). Por eso
  numera hasta 32 y la HTML hasta 34.
- Le faltan **dos anexos**: `anexo-reglas.html` (las nueve decisiones D1–D9
  reunidas) y `referencias.html`.
- El `2026-05-docx/` va una generación más atrás todavía: conserva
  `02_invariantes` y `03_intentos_previos`, capítulos que ya no existen ni en el
  Markdown.

Mantener las tres en paralelo era la causa de que el `.docx` que iba a editoriales
se generara desde un manuscrito incompleto.

## Si algún día hace falta un DOCX

No se regenera desde aquí. Se construye desde `manuscrito2/`, extrayendo el
`<main>` de cada página como ya hace
[`generar_pdf_html.py`](../generar_pdf_html.py).
