# Reestructura "a la vena" + enriquecimiento técnico — Diseño

**Fecha:** 2026-06-06
**Tipo:** Reestructura de capítulos del libro WQuestions (Frente 1) + contenido técnico
(JSON / prompts / Python / SQL con resaltado) (Frente 2).

## Objetivo

1. **Arrancar "a la vena":** que el libro entre rápido al modelo en vez de abrir con dos
   capítulos teóricos. La teoría y las anécdotas se dosifican "justo a tiempo".
2. **Verse técnico y profesional:** incorporar JSON, prompts de LLM, Python y SQL reales
   y verificables, con resaltado de sintaxis.

## Decisiones tomadas (con el autor)

- **Reestructura B:** mantener un **Cap 1 mínimo (~1 pág)** con solo el gancho
  (sala de emergencias + Babel + "el mismo hecho, cuatro idiomas" + "la causa del problema").
- **Teoría de convergencia → intermezzo corto** (capítulo nuevo) ubicado *después* de que el
  modelo ya está establecido (cierre de la Parte II), no al inicio.
- **Contenido técnico: rico + resaltado de color** (codehilite + Pygments).

## Frente 1 — Reestructura

### Nueva numeración (cambio quirúrgico)

Quitar *Intentos previos* (−1) y añadir el intermezzo (+1) se cancelan: **del Cap 7 en
adelante todo conserva su número.** Solo se mueven cuatro capítulos.

```
Cap 1  Torre de Babel   → reescrito a ~1 pág (solo el gancho). Sigue siendo Cap 1.
Cap 2  Intentos previos → SE DISUELVE.
Cap 3  Cuatro pilares   → Cap 2
Cap 4  Clase            → Cap 3  (+ absorbe la crítica a intentos previos)
Cap 5  Cuánto           → Cap 4
Cap 6  Cómo/relaciones  → Cap 5
       (NUEVO) Las raíces (intermezzo) → Cap 6
Cap 7..32              → SIN CAMBIO
```

### Operaciones de archivo (git mv)

- `01_torre_de_babel.md` → reescribir (slim). Se queda como `01_torre_de_babel.md`.
- `02_intentos_previos.md` → **eliminar** (contenido migrado a clase, ver abajo).
- `03_cuatro_pilares.md` → `02_cuatro_pilares.md`
- `04_clase.md` → `03_clase.md`
- `05_cuanto.md` → `04_cuanto.md`
- `06_como_relaciones.md` → `05_como_relaciones.md`
- **Nuevo** `06_raices.md` (intermezzo).
- `07_*`…`32_*` → sin cambio.

### Migración de contenido

- **Cap 1 (slim):** conservar las secciones "Una sala de emergencias", "El mismo hecho,
  cuatro idiomas", "La causa de todo el problema" + un puente de 2–3 líneas hacia el modelo.
  **Quitar** las secciones teóricas (la pista, aula de 1917, Cicerón, Aristóteles, gramática,
  el niño, invariantes, el cimiento) → van al intermezzo.
- **Intermezzo `06_raices.md`:** las secciones teóricas removidas, pulidas como capítulo
  autónomo: "Por qué estas preguntas y no otras — Aristóteles, Cicerón, el periodismo, el niño".
  Cierra la Parte II respondiendo *por qué* las coordenadas son universales (después de verlas).
- **Disolver Cap 2 en clase (nuevo Cap 3):** añadir a `clase` una sección que **sea** el
  diagnóstico que hoy se referencia ("el problema que diseccionamos en el Cap 2"): las
  ontologías y la web semántica construyeron catálogos de **nodos**, no el piso de **cables**;
  por eso se quedaron a medias. (El matiz 5W1H-como-extracción puede ir, comprimido, al inicio
  de clase o al cap. lexicon.)

### Referencias a corregir

- **−1 (Cap 4→3, Cap 6→5):**
  - `11_verbo_signatura.md:104` "Capítulo 6" (universo V) → **Capítulo 5**
  - `27_seguridad_privacidad.md:69` "Capítulo 4" (enchufe URIs) → **Capítulo 3**
  - `26_prueba_reflexiva.md:45` "Capítulo 4" → **Capítulo 3**
  - (sweep de cualquier "Capítulo 3/4/5/6" entre los propios archivos movidos)
- **Reescribir (no renumerar):**
  - `04_clase.md:190` "el problema que diseccionamos en el Capítulo 2" → "como vimos en este
    mismo capítulo" (la crítica ya vive ahí).
  - `29_conclusion.md:32` "ontologías que enumeramos en el capítulo 2" → al cap. de ontologías
    (Cap 3) o "más atrás".
  - `11_verbo_signatura.md:437` "las reglas de Cicerón… del Capítulo 1" → **Capítulo 6** (raíces).
  - `26_prueba_reflexiva.md:39` "el Capítulo 1 abrió con la torre de Babel" → se mantiene (Cap 1
    sigue abriendo con Babel).
  - `29_conclusion.md:5` "la conocimos en el primer capítulo" → se mantiene (Cap 1 conserva la ER).
- **Títulos de capítulo** en los 4 archivos movidos (`# Capítulo N — …`).
- **Introducción:** reescribir "El recorrido" y las etiquetas de Parte:
  - Parte I — El problema (Cap 1).
  - Parte II — Las siete coordenadas (Cap 2–5) + intermezzo "Las raíces" (Cap 6).
  - Partes III–VI: rangos sin cambio (7–10, 11–13, 14–23, 24–29).

### Verificación Frente 1

`grep` final de refs numéricas + `python3 libro/generar_pdf.py` (cuenta de capítulos correcta,
sin enlaces de diagrama rotos). Commit.

## Frente 2 — Contenido técnico (rico + color)

### Infraestructura (una vez)

- `pip install pygments` (requerido por codehilite).
- En `libro/generar_pdf.py`: añadir `"codehilite"` a las extensiones de `markdown.Markdown(...)`
  y embeber el CSS de Pygments (`HtmlFormatter().get_style_defs('.codehilite')`) en el `<style>`.
- Convención: ` ```json `, ` ```python `, ` ```sql `, ` ```text ` (prompts).

### Mapa de artefactos (uno o dos por capítulo, reales)

| Artefacto | Capítulo (nueva num.) |
|---|---|
| JSON — situación reificada serializada | Hecho atómico (7) / Situaciones (9) |
| JSON — entrada de lexicon | Lexicon (12) |
| JSON — function-schema (tool) | LLMs (24) |
| JSON — permiso/consentimiento (volver el pseudo-texto a JSON) | Seguridad (27) |
| Prompt — NL→hechos (extracción) | Lexicon (12) / LLMs (24) |
| Prompt — compilador de reglas (IA como motor de inferencia) | Qué falta (28) |
| Python — afirmar hecho / validar signatura / consultar (5–15 líneas) | Verbo (11) + un dominio Parte V |
| SQL — CREATE/JOIN que se rompe vs. patrón único | "Antes y después" de Parte V (14–21) |
| SQL — "consulta eterna" vs. patrón de grafo | Hecho atómico (7) |

### Principio innegociable

Todo artefacto **real y verificable**: Python corre contra el prototipo; JSON pasa `json.loads`;
SQL válido en sqlite; prompt usable. Nada decorativo inventado.

### Ejecución Frente 2

Subagentes en paralelo (uno por capítulo/artefacto), cada uno: (1) escribe el artefacto,
(2) lo verifica, (3) lo inserta con 1–2 frases de encuadre. Revisión de cabeceras/markdown al
final, regenerar PDF, commit.

## Secuencia

1. Frente 1 completo (cambia numeración) → verificar → commit.
2. Frente 2 sobre numeración estable → verificar → commit.

## No incluido (YAGNI)

- No se reescriben capítulos que no lo necesiten.
- No se añade contenido técnico "de relleno"; solo donde aporta.
- El prototipo Python no cambia (salvo que un snippet revele un bug real).
