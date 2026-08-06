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
│   ├── WQuestions.pdf      — salida generada (edición completa)
│   └── WQuestions-resumen.pdf — salida generada (sin código)
├── generar_pdf_html.py     — genera ambos PDF desde manuscrito2/
├── generar_pdf_resumen.py  — la poda del resumen; lo encadena el anterior
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
dependencia externa es Chrome.

Un solo comando produce las dos ediciones, para que no se desincronicen:

| Salida | Qué contiene |
|---|---|
| `manuscrito2/WQuestions.pdf` | el libro completo |
| `manuscrito2/WQuestions-resumen.pdf` | sin bloques de código, sin figuras ni diagramas de tripleta, y sin los anexos 33 y 34; los casos de dominio (16–24) quedan enteros |

El resumen lo poda [`generar_pdf_resumen.py`](generar_pdf_resumen.py), que también
corre suelto si hace falta rehacer solo esa edición.

Una nota sobre el tamaño de letra: la edición completa lleva tablas más anchas que
la página, así que Chrome la encoge entera al imprimir (hoy, al 72%). El resumen ya
no desborda y saldría a tamaño natural, con un cuerpo de texto visiblemente mayor
que el del libro completo. Para que las dos ediciones se vean iguales, el builder
del resumen lee la escala del PDF completo recién generado y la reproduce con
`zoom`. Si algún día se corrige el desborde de las tablas, el resumen se ajusta
solo: no hay ningún factor escrito a mano.

## Antes de escribir

Lee [`manuscrito2/GUIA-DE-ESTILO.md`](manuscrito2/GUIA-DE-ESTILO.md). Fija la voz
(español neutro, tuteo, sin voseo), el esqueleto HTML de un capítulo, las clases
de los componentes, el repertorio canónico de ejemplos y el mapa autoritativo de
las decisiones de diseño D1–D9. Ese mapa importa especialmente: cada `Dn` se
enuncia formalmente en un solo capítulo y en los demás solo se referencia.
