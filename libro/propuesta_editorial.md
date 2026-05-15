# Propuesta editorial

## Título tentativo

**Las preguntas como coordenadas: arquitectura universal para la información en la era de la inteligencia artificial**

(Título de trabajo. Alternativas: *El espacio de las preguntas*, *Quién, qué, dónde, cuándo: el atlas universal de la información*, *Las ocho coordenadas de lo que sabemos*.)

## Autor

**Jose Roberto Abanto Marín** (Celendín, Perú, 1973).

Desarrollador de software con treinta y cinco años de experiencia construyendo sistemas a la medida. Es el creador de **Ghenesis**, un framework *meta-driven* que persiste la lógica de negocio en base de datos — formularios, reportes, módulos — para permitir su administración sin tocar el código de la aplicación. Esa obsesión por separar el qué del cómo, por buscar la capa donde la información deja de depender de la aplicación que la consulta, atraviesa toda su trayectoria profesional y desemboca naturalmente en este libro.

Apasionado de las bases de datos, los modelos de inteligencia artificial y la ciencia en general, encuentra en la física cuántica y en los enigmas del universo una forma de mantener viva la sospecha de que todo lo aparentemente complejo esconde, en algún nivel, una estructura más simple. La filosofía es para él una herramienta de trabajo: una manera de detectar los patrones, las abstracciones y los paradigmas que se asoman en cada problema técnico.

*Las preguntas como coordenadas* es el primer libro en el que reúne esas tres líneas — la práctica de tres décadas modelando datos, la curiosidad científica y la mirada filosófica — alrededor de una sola tesis arquitectónica.

## Audiencia objetivo

Tres niveles, en estilo Hofstadter / Pinker:

1. **Lectores con interés general en IA y filosofía**: el libro como invitación a repensar cómo organizamos la información del mundo.
2. **Profesionales técnicos** (arquitectos de información, ingenieros de datos, desarrolladores de IA): el libro como propuesta arquitectónica concreta.
3. **Investigadores y académicos** (lingüística computacional, representación del conocimiento, semántica formal): el libro como aporte teórico verificable contra precedentes.

El texto está estratificado: cada capítulo abre con narrativa accesible y profundiza con rigor formal en sus segundas mitades. El lector puede leer "en superficie" o "a profundidad" según interés.

## Tesis central

> **Ocho preguntas fundamentales bastan para organizar cualquier información del mundo, y reconocerlas como coordenadas cambia cómo construimos sistemas de IA.**

La historia humana de organizar información se ha apoyado en dos grandes tradiciones: las ontologías de dominio (taxonomías biológicas, catálogos bibliográficos, registros administrativos) y las preguntas fundamentales (5W1H del periodismo, las preguntas-W indoeuropeas, los modos de pregunta aristotélicos). Las primeras explotan, las segundas conservan.

Este libro argumenta que un esquema universal basado en ocho coordenadas-pregunta — *quién, qué, dónde, cuándo, cuánto, cuál, cómo, y la pregunta meta-clasificatoria* — es:

1. **Suficiente** para modelar cualquier dominio (validado en transporte, comercio, salud, música, derecho, química, deporte).
2. **Necesario** para que sistemas de IA accedan a información de forma uniforme, sin reentrenamiento por dominio.
3. **Familiar** para humanos porque es cómo el lenguaje natural ya organiza el mundo (las preguntas-W son anteriores a cualquier ontología).
4. **Verificable** porque coincide con tradiciones formales independientes (neo-davidsoniano, Barwise-Perry, CIDOC CRM, FrameNet).

## Por qué este libro existe

Hay tres vacíos que ningún libro actual llena bien:

1. **Para el lector general**: no hay una explicación accesible de por qué la representación del conocimiento importa, ni de cómo IA y lenguaje se conectan estructuralmente. *Conceptual Spaces* de Gärdenfors es académico; los libros de divulgación sobre IA son operativos.

2. **Para el profesional técnico**: existen muchas ontologías (CIDOC CRM, Schema.org, Biolink) pero ningún libro que las contraste con un esquema universal alternativo y muestre cuándo conviene cada uno.

3. **Para el académico**: las líneas (neo-davidsoniano, Barwise-Perry, FrameNet, OKB Canonicalization, bitemporal data) están desconectadas. Este libro las une bajo una arquitectura coherente — y demuestra que la unión funciona.

## Libros comparables

| Libro | Año | Comparación |
|---|---|---|
| *Conceptual Spaces* — Peter Gärdenfors | 2000 | Metáfora geométrica del conocimiento. WQuestions es la versión discreta-simbólica. |
| *Situations and Attitudes* — Barwise & Perry | 1983 | Teoría matemática de la información. WQuestions la convierte en arquitectura de datos. |
| *The Geometry of Meaning* — Gärdenfors | 2014 | Semántica continua. WQuestions complementa con semántica discreta-tipada. |
| *Knowledge Representation and Reasoning* — Brachman & Levesque | 2004 | Manual técnico de KR. WQuestions ofrece un sistema unificado. |
| *Building Ontologies with Basic Formal Ontology* — Arp, Smith, Spear | 2015 | Manual de BFO. WQuestions presenta una arquitectura alternativa más simple. |

## Estructura tentativa (síntesis)

Seis partes, ≈21 capítulos, ≈250-300 páginas en formato académico-divulgativo:

```
PARTE I    — POR QUÉ LAS PREGUNTAS           (3 caps)
PARTE II   — LAS OCHO COORDENADAS             (4 caps)
PARTE III  — CÓMO FUNCIONAN JUNTAS            (4 caps)
PARTE IV   — DEL LENGUAJE A LOS HECHOS        (3 caps)
PARTE V    — EN LA PRÁCTICA                   (4 caps)
PARTE VI   — IMPLICACIONES Y FUTURO           (3 caps + conclusión)
```

Detalle completo en `esquema_capitulos.md`.

## Estado del manuscrito

A fecha de hoy:

- **Material conceptual completo**: 9 decisiones de diseño formalizadas, 12 convenciones documentadas, 7 dominios modelados como casos de validación, 12 fichas de precedentes académicos e industriales.
- **Prototipo conceptual**: documentación técnica de ~30.000 palabras en `WQuestions.md` y archivos asociados.
- **Capítulos escritos**: introducción (borrador).
- **Estimación de redacción restante**: 6-9 meses dedicando tiempo razonable.

## Idioma de publicación

**Primera edición: español neutro**, con ejemplos en contextos genéricos (sin referencias regionales específicas) para que el texto sea igualmente legible en cualquier país hispanohablante. Los lectores hispanohablantes están subatendidos en este tipo de literatura técnica.

**Segunda edición: traducción al inglés** dirigida al mercado académico-técnico internacional. La estructura permite traducción casi directa.

## Editoriales objetivo

A explorar:

- **Académicas técnicas**: MIT Press, Springer (Synthese Library), Cambridge University Press.
- **Académicas en español**: Fondo de Cultura Económica, Editorial UPC, Universidad Externado.
- **Técnicas profesionales**: O'Reilly, Manning (canal técnico, traducción al inglés directa).
- **Divulgación informada en español**: Crítica, Anagrama, Debate.

## Razones para publicar este libro ahora

- **Momento**: 2026 es el momento en que function calling, agentic AI y conexión LLM-knowledge-graphs se han vuelto producción. Hay demanda de arquitecturas claras.
- **Vacío detectado**: ninguna publicación combina rigor filosófico-lingüístico con propuesta arquitectónica práctica.
- **Validación previa**: la propuesta se ha contrastado contra 8 precedentes serios sin que ninguno la subsuma.
- **Hispanohablante**: el mercado en español tiene poco material original sobre representación de conocimiento; la mayoría son traducciones.

---

## Anexos

- `esquema_capitulos.md` — outline detallado capítulo por capítulo.
- `WQuestions.md` (en el directorio raíz del proyecto) — documentación técnica fuente.
- `related/` — 12 fichas de precedentes con análisis comparativo.
