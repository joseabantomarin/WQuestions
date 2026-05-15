# Resumen del Proyecto: WQuestions

## Visión General
**WQuestions** es un proyecto enfocado en definir un estándar (modelo de información) universal para representar hechos del mundo real basándose en "coordenadas-pregunta". La premisa principal es que la información puede estructurarse respondiendo a preguntas fundamentales (quién, qué, dónde, cuándo, cuál, cuánto, cómo, y qué tipo), facilitando así que sistemas de Inteligencia Artificial y bases de datos heterogéneas puedan interoperar y razonar de manera unificada.

## Estructura Conceptual del Modelo
Según la documentación principal (`WQuestions.md`), el modelo se basa en un espacio multidimensional definido por conjuntos o ejes:

### Ejes de Valor (Individuos)
1.  **Q (quién)**: Agentes capaces de acción.
2.  **O (qué)**: Objetos, eventos, situaciones concretas.
3.  **L (dónde)**: Ubicaciones físicas.
4.  **T (cuándo)**: Momentos o intervalos.
5.  **N (cuánto)**: Magnitudes y cantidades.
6.  **K (clase)**: Tipos, conceptos abstractos y categorías.

### Ejes Estructurales (Etiquetas/Conectores)
7.  **P (cuál)**: Nombres de propiedades (atributos).
8.  **M (cómo)**: Relaciones (enlaces entre entidades).

Una de las piezas centrales para conectar el lenguaje natural con este modelo es el **Lexicon** (`lexicon.md`), el cual actúa como un diccionario que mapea verbos (unidades léxicas) a tipos de situaciones (en el eje K) y define sus roles obligatorios y opcionales.

## Organización de los Archivos

El proyecto está claramente estructurado en tres bloques principales:

1.  **El Núcleo del Modelo (Raíz del proyecto):**
    *   `WQuestions.md`: El documento maestro que detalla las decisiones de diseño (D1 a D7), los ejes, la formalización matemática y los roles canónicos.
    *   `lexicon.md`: El catálogo de verbos canónicos mapeados a situaciones.
    *   `conversacion1.md` y `diagram.md`: Probablemente registros de diseño, refinamiento del modelo y representaciones visuales.

2.  **El Libro (`/libro`):**
    *   Parece que estás escribiendo un libro estructurado en varias partes (desde el problema de la fragmentación de datos hasta implementaciones futuras).
    *   `esquema_capitulos.md`: Contiene un esquema muy detallado de 21 capítulos divididos en 6 partes ("Por qué las preguntas", "Las ocho coordenadas", "Cómo funcionan juntas", etc.).
    *   `propuesta_editorial.md`: Documento orientado a presentar el proyecto a una editorial.
    *   Scripts y carpetas (`convertir.sh`, `manuscrito/`): Herramientas para la compilación del libro.

3.  **Investigación y Antecedentes (`/related`):**
    *   Contiene notas y análisis de modelos existentes y teorías previas que fundamentan WQuestions.
    *   Ejemplos de archivos: `neo-davidsonian.md`, `cidoc-crm.md`, `rdf-and-reification.md`, `yang-hu-5w1h.md`, `framenet-verbnet.md`, entre otros. Esto demuestra un trabajo de fundamentación teórica muy sólido.

## Estado Actual
El proyecto tiene una base teórica sumamente estructurada. Has logrado definir no solo la arquitectura matemática del modelo, sino también un plan de divulgación extenso (el libro) y el inicio de su aplicabilidad práctica (el Lexicon y ejemplos en dominios como ventas y taxis).
