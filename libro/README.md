# Libro WQuestions

**Arquitectura universal de la información — Las preguntas como coordenadas**

## La fuente única

[`manuscrito2/`](manuscrito2/) es la edición canónica, en HTML. Todo cambio al
libro se hace ahí. No hay una versión paralela en Markdown que mantener
sincronizada: las ediciones anteriores están retiradas en
[`_ediciones/`](_ediciones/) y no se editan.

La HTML es la fuente y no un formato de salida porque el libro depende de
componentes que el Markdown no puede representar: figuras SVG en línea, cajas de
decisión de diseño, el componente de tripletas y los charts de datos.

```
libro/
├── manuscrito2/            ← EL LIBRO
│   ├── index.html          — portada y navegación
│   ├── indice.html         — índice completo
│   ├── 00-introduccion.html
│   ├── 01…34-*.html        — los capítulos
│   ├── anexo-reglas.html   — las nueve decisiones D1–D9 reunidas
│   ├── referencias.html    — fuentes, numeradas por orden de aparición
│   ├── assets/             — CSS, JS, tipografías, imágenes
│   ├── GUIA-DE-ESTILO.md   — canon de voz, componentes y ejemplos (interno)
│   └── WQuestions.pdf      — salida generada
├── generar_pdf_html.py     — genera el PDF desde manuscrito2/
├── esquema_capitulos.md    — outline de trabajo
├── propuesta_editorial.md  — para editoras y agentes literarios
├── honestidad.md           — notas sobre qué está construido y qué no
└── _ediciones/             — ediciones retiradas; no editar
```

## Estructura del libro

34 capítulos más introducción, en seis partes y tres anexos:

| Parte | Capítulos |
|---|---|
| Apertura | 00 · Introducción |
| I — El problema | 01 |
| II — Las siete coordenadas | 02–06 |
| III — Cómo funcionan juntas | 07–12 |
| IV — Del lenguaje a los hechos | 13–15 |
| V — En la práctica | 16–25 |
| VI — IA, futuro y cierre | 26–31 |
| Anexos | 32–34, más referencias y decisiones de diseño |

## Generar el PDF

```bash
python3 generar_pdf_html.py
```

Concatena el `<main>` de cada página de `manuscrito2/` en un solo documento y lo
imprime con Chrome headless. Solo usa la biblioteca estándar; la única
dependencia externa es Chrome. Sale en `manuscrito2/WQuestions.pdf`.

## Antes de escribir

Lee [`manuscrito2/GUIA-DE-ESTILO.md`](manuscrito2/GUIA-DE-ESTILO.md). Fija la voz
(español neutro, tuteo, sin voseo), el esqueleto HTML de un capítulo, las clases
de los componentes, el repertorio canónico de ejemplos y el mapa autoritativo de
las decisiones de diseño D1–D9. Ese mapa importa especialmente: cada `Dn` se
enuncia formalmente en un solo capítulo y en los demás solo se referencia.
