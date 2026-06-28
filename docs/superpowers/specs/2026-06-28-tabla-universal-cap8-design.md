# Diseño — "De la geometría a la tabla que ya conoces" (sección nueva, cap. 8)

- **Fecha:** 2026-06-28
- **Estado:** aprobado (diseño); pendiente de escribir el plan de implementación
- **Entregable:** una sección nueva en `libro/manuscrito2/08-espacio-multidimensional.html` (edición HTML canónica)

## Contexto

El cap. 8 ("El espacio multidimensional") establece que las coordenadas son una
geometría real, y ya contiene:
- **Fig 8.2** — una "tabla universal" de 7 columnas (la hoja dispersa: 5 hechos de
  dominios distintos sobre los ejes Q/O/L/T/N/K, con códigos).
- La sección **"Frente a ℝⁿ, las tablas y los cubos"** — contrasta el modelo con
  tablas relacionales y cubos OLAP.

Lo que falta —y es el objetivo de esta sección— es el eslabón que responde al
reparo nº 1 del practicante (*"¿pero dónde está mi tabla?"*): mostrar que el grafo
**se proyecta de vuelta** a (a) una vista tabular legible para humanos y (b) una
tabla pivote, *bajo demanda*. La tabla no es el modelo; es una de sus vistas.

## Alcance

Sub-proyecto **1 de 2**. Este spec cubre **solo el capítulo** (contenido prosa +
tablas). La implementación real del aplanado en el prototipo Python
(`prototipo/wq/`) es un sub-proyecto aparte, con su propio spec, después.

## Ubicación exacta

Insertar la sección **después** de la sección de densidad (tras la caja "Una
densidad que se puede auditar", ~línea 451) y **antes** de la `<h2>`
"Frente a ℝⁿ, las tablas y los cubos" (~línea 453).

Razón: (1) las figuras nuevas quedan como **8.4** y **8.5** sin renumerar la
Fig 8.3 (dispersión); (2) el flujo entra natural a la comparación que sigue
("ya viste que recuperas tu tabla; ahora mira en qué se diferencia de las
tablas/cubos de verdad").

## Estructura de la sección (beats)

`<h2>`: **De la geometría a la tabla que ya conoces**

1. **Puente (prosa):** una consulta recorta un subconjunto de puntos; ¿cómo se le
   entrega ese recorte a quien pidió "una tabla"? Proyectando ejes a columnas.
   *La geometría no reemplaza la tabla: la genera bajo demanda.*
2. **La lectura plana (prosa, 1–2 frases):** callback a la **Fig 8.2 existente**
   ("esa hoja dispersa *es* la tabla universal de hechos, con códigos"). Sin
   figura nueva — no se duplica.
3. **Fig 8.4 — La proyección legible** (`<table>` nueva dentro de
   `figura figura--ancha`): filtra `K` ∈ familia de licencias (construcción,
   funcionamiento, micromovilidad), y el lexicon resuelve los códigos a etiquetas
   humanas. Prosa breve: el motor resuelve las URIs y proyecta el enlace relevante
   como columna.
4. **Fig 8.5 — La pivote** (`<table>` nueva): cruza **K × L** con conteos. Guiño
   de una frase: "en SQL, `GROUP BY` + `PIVOT`; aquí, pintar dos ejes en una
   matriz — la misma operación geométrica, ahora bidimensional".
5. **`caja--practica` "Para el desarrollador":** el frontend solo lanza la consulta
   de coordenadas y formatea los objetos devueltos como un DataFrame (pandas) o
   una tabla HTML, usando los nombres de las preguntas como cabeceras. Corto; la
   implementación real es el sub-proyecto del prototipo.
6. **`cita-destacada` de cierre:** *"La tabla nunca fue el modelo; era una de sus
   vistas."*

## Decisión 1 (resuelta): la columna "M" en la vista humana

El libro es explícito (Fig 8.1): **M es la urdimbre de enlaces, no un 7.º eje de
posición**. Por tanto:
- La **vista universal** se mantiene en los **6 ejes de valor** (Q/O/L/T/N/K), tal
  como ya está la Fig 8.2. No se añade una 7.ª columna "verbo" a la tabla cruda.
- La **proyección humana** (Fig 8.4) sí muestra una columna **Estado (M)**, pero
  enmarcada como **proyectar un enlace `M` concreto y relevante del reporte**
  (aquí, el cable `estado`), no como un eje de posición. Esto honra la intuición
  "7 preguntas → columnas" sin contradecir el modelo.

## Decisión 2 (resuelta): ejemplo municipal alineado al canon

Dominio municipal (Perú: soles `S/`, direcciones tipo "Jr./Av."), con
identificadores consistentes con el cap. 22 y el canon del libro:
- Ciudadanos: `juan`, `carla` (etiquetas "Juan", "Carla") — **no** inventar
  "Juan Pérez / María Silva".
- Trámites: estilo `tramite_juan_lic_04`; clases en K: `licencia_funcionamiento`,
  `licencia_micromov` (construcción/funcionamiento/multas para la pivote).
- Expedientes: estilo `expediente_2026`.
- Estados (cable `estado`): `solicitado`, `en_revision`, `aprobada`.
- Zonas (eje L): `zona_centro`, `zona_norte`, `zona_sur`.

### Datos concretos — Fig 8.4 (proyección legible)
Encabezado: "Reporte de trámites de licencias" (filtro `K = licencia_*`).
Columnas: Ciudadano (Q) · Expediente (O) · Ubicación (L) · Fecha (T) · Costo (N) · **Estado (M)**.

| Ciudadano (Q) | Expediente (O) | Ubicación (L) | Fecha (T) | Costo (N) | Estado (M) |
|---|---|---|---|---|---|
| Juan | Licencia de funcionamiento | Jr. Trujillo 450, Centro | 22-06-2026 | S/ 450,00 | Solicitado |
| Carla | Licencia de micromovilidad | Av. Perú 1200, Norte | 23-06-2026 | S/ 300,00 | En revisión |
| Marta | Remodelación de local | Jr. Lima 88, Centro | 24-06-2026 | S/ 520,00 | Aprobada |

(Nota en prosa: bajo esas etiquetas viven `juan`, `tramite_juan_lic_04`,
`expediente_2026`, `zona_centro`… resueltos por el lexicon.)

### Datos concretos — Fig 8.5 (pivote K × L)
Encabezado: "Trámites por tipo y zona". Filas = clases (K); columnas = zonas (L);
celdas = conteos.

| Tipo de trámite (K) \ Zona (L) | Centro | Norte | Sur |
|---|---|---|---|
| Licencias de construcción | 45 | 12 | 8 |
| Licencias de funcionamiento | 120 | 54 | 30 |
| Multas de fiscalización | 15 | 42 | 10 |

## Componentes y voz

- Tablas dentro de `<figure class="figura figura--ancha revelar"><div class="lienzo"><table>…`,
  con chips de eje (`<span class="eje eje--q">Q</span>`) en las cabeceras, igual
  que la Fig 8.2 existente.
- `figcaption` con `<span class="fnum">Figura 8.4.</span>` / `8.5.`
- `caja--practica` para "Para el desarrollador"; `cita-destacada` para el cierre.
- Voz: español neutro, registro del capítulo. Sin auto-elogio de honestidad
  (ver [[feedback_libro_tono_honestidad]] — no reintroducir "sin maquillaje", etc.).
- Numeración de figuras: nuevas = 8.4 y 8.5. **No** se renumera ninguna figura
  existente (verificar tras insertar).

## Lo que esta sección NO hace (anti-scope)

- **No** incluye un bloque SQL `antes/después` (eso vive en la Parte V / cap. 19).
- **No** re-argumenta "mejor que SQL" (ya lo hace la sección ℝⁿ/tablas/cubos que
  va justo después).
- **No** incluye código Pandas/implementación (es el sub-proyecto del prototipo).
- **No** añade una 7.ª columna "verbo" a la tabla universal (ver Decisión 1).

## Criterios de aceptación

1. La sección entra entre la densidad y "Frente a ℝⁿ…", con `<h2>` propio.
2. Dos `<table>` nuevas (8.4 proyección, 8.5 pivote) con los datos de arriba,
   estilo coherente con la Fig 8.2.
3. La Fig 8.3 (dispersión) conserva su número; no hay figuras fuera de orden.
4. Identificadores y etiquetas consistentes con el cap. 22 / canon municipal.
5. HTML válido; sin auto-elogio de honestidad; voz del capítulo.
6. El sitio sigue desplegando (push → GitHub Pages, ~25 s).

## Riesgos / notas

- Cap. 8 ya es largo: mantener la sección compacta (2 tablas + ~4 párrafos + 1
  caja + 1 cita).
- Verificar, tras insertar, que ninguna referencia en prosa a "Figura 8.x" quede
  descolocada.
- El prototipo (sub-proyecto 2) deberá producir exactamente estas tres vistas
  (plana / proyección / pivote) para que el capítulo y el código no se contradigan.
