# Espacios Conceptuales — Gärdenfors

Documento de referencia sobre la teoría de **conceptual spaces** de Peter Gärdenfors, una de las propuestas más influyentes para representar conocimiento en términos *geométricos* multidimensionales. Su relación con WQuestions es de metáfora compartida ("coordenadas") con desarrollo divergente (geométrico vs simbólico).

## Datos bibliográficos

- **Libro fundacional**: Gärdenfors, P. (2000) — *Conceptual Spaces: The Geometry of Thought*. MIT Press / Bradford Books.
- **Extensión aplicada**: Zenker, F. & Gärdenfors, P. (eds.) (2015) — *Applications of Conceptual Spaces: The Case for Geometric Knowledge Representation*. Springer.
- **Continuación**: Gärdenfors, P. (2014) — *The Geometry of Meaning: Semantics Based on Conceptual Spaces*.

## Motivación declarada

Gärdenfors observa que las dos grandes tradiciones de representación del conocimiento (la **simbólica**: lógica/IA clásica, basada en proposiciones discretas; y la **subsimbólica**: redes neuronales, basada en patrones continuos) son ambas inadecuadas para capturar fenómenos cognitivos básicos como:

- Similitud entre conceptos.
- Prototipos y categorización gradual.
- Aprendizaje desde ejemplos.
- Razonamiento por analogía.

Propone un **nivel intermedio conceptual** entre lo simbólico y lo subsimbólico, basado en geometría.

## Núcleo del framework

### Dimensiones de calidad

Un **espacio conceptual** se construye a partir de un conjunto de **dimensiones de calidad** (*quality dimensions*). Cada dimensión es un eje continuo (o discreto pero ordenado) que representa una propiedad básica:

- Espacio: x, y, z (cartesianas).
- Color: matiz, saturación, brillo (HSL).
- Sonido: frecuencia, intensidad, timbre.
- Sabor: dulce, salado, ácido, amargo, umami.
- Tiempo: instante en un eje lineal.
- Temperatura, peso, tamaño, etc.

Las dimensiones forman **dominios** integrados (por ejemplo, las tres dimensiones de color forman juntas el dominio "color"; las tres espaciales forman "ubicación").

### Objetos como puntos

Un **objeto** se representa como un punto en el espacio conceptual: tiene un valor en cada dimensión relevante. La similitud entre objetos es **distancia geométrica** (típicamente euclidiana o variante).

### Conceptos como regiones convexas

Una **categoría natural** se representa como una región **convexa** en el espacio conceptual. Convexidad significa: si A y B pertenecen al concepto, cualquier punto "entre" A y B también pertenece. Esto explica naturalmente:

- **Prototipos**: el centroide de la región es el ejemplar más típico.
- **Gradualidad**: la distancia al centroide mide la tipicidad.
- **Aprendizaje**: una región se aprende a partir de ejemplares y se ajusta.

### Tres niveles

Gärdenfors propone tres niveles de representación, complementarios:

1. **Simbólico**: lógica, lenguaje, reglas.
2. **Conceptual**: espacios geométricos con dimensiones de calidad.
3. **Subsimbólico**: redes neuronales, percepción.

Los espacios conceptuales hacen de puente.

## Características clave

- **Continuidad**: las dimensiones suelen ser continuas (números reales).
- **Similitud emergente**: la distancia da semántica natural de "parecerse".
- **Prototipos**: emergen geométricamente del centroide.
- **Convexidad**: criterio formal para "categoría natural".
- **Compositionalidad**: combinar conceptos = operaciones geométricas (intersección, producto cartesiano de dimensiones).
- **Cercanía a la cognición**: hay evidencia psicológica de que humanos sí razonan en algo parecido a espacios geométricos.

## Aplicaciones

- Representación semántica en NLP (word embeddings comparten esta intuición).
- Categorización en visión por computadora.
- Modelado de conceptos en robótica.
- Razonamiento por analogía.

## Posicionamiento frente a WQuestions

| Aspecto | Gärdenfors | WQuestions |
|---|---|---|
| Naturaleza de dimensiones | Continuas, geométricas | Discretas, simbólicas |
| Unidad básica | Punto en espacio | Hecho atómico (tupla) |
| Concepto | Región convexa | Individuo en `K` |
| Similitud | Distancia (emergente) | No definida (a diseñar) |
| Prototipos | Centroides | No tratados |
| Aprendizaje | Natural (ajustar regiones) | Pendiente |
| Tipos de relación | Implícitas (geometría) | Explícitas (`P`, `M`) |
| Razonamiento | Por similitud y proximidad | Por igualdad y unificación |
| Cognición | Plausibilidad psicológica | No prioritaria |

## Convergencias importantes

- **Metáfora compartida**: ambos parten de la intuición de que el conocimiento se organiza en torno a **ejes/dimensiones/coordenadas**. La pregunta "¿quién/qué/dónde/cuándo/cuánto?" en WQuestions tiene la misma forma que la pregunta "¿qué dimensiones definen este dominio?" en Gärdenfors.

- **Dominios como agrupaciones de ejes**: Gärdenfors agrupa dimensiones en dominios (color = matiz+saturación+brillo). WQuestions tiene una agrupación similar al separar ejes de valor (Q/O/L/T/N/K) de ejes estructurales (P/M).

- **Reificación de propiedades**: en Gärdenfors, "rojo" es una región del dominio color; en WQuestions, "rojo" sería un individuo en `K` (un valor categórico). En ambos casos, propiedades concretas son ciudadanos.

## Divergencias importantes

- **Continuidad vs discreto**: Gärdenfors apuesta a la representación continua para capturar gradualidad y similitud; WQuestions usa identidad discreta. Una persona "es" o "no es" Juan; no hay "Juan-ridad" gradual.

- **Similitud nativa vs nula**: Gärdenfors obtiene similitud gratis de la geometría; WQuestions debería definirla aparte si la quiere.

- **Concepto = región vs concepto = individuo**: en Gärdenfors el concepto "perro" es una región del espacio (un conjunto de puntos posibles); en WQuestions sería un individuo en `K` al que se "instancian de".

- **Razonamiento**: Gärdenfors permite razonamiento por proximidad, interpolación, extrapolación; WQuestions razona por igualdad y unificación de variables.

- **Aplicabilidad**: Gärdenfors brilla en dominios perceptuales (color, forma, sonido, espacio); WQuestions brilla en dominios institucionales / informacionales (ventas, viajes, registros). Son complementarios.

## Qué tomar prestado

- **La idea de "dominios integrados"**: agrupar varios ejes de calidad bajo un dominio (como color = matiz+sat+brillo) sugiere que WQuestions podría tener **subestructuras dentro de `K`** o **propiedades agrupadas** para conceptos compuestos.

- **La noción de prototipo / región convexa**: cuando WQuestions necesite búsqueda aproximada o ranking ("encuentra las ventas más parecidas a X"), una capa geométrica encima de los ejes simbólicos sería el camino. Idea: cada eje de WQuestions podría tener una **función de distancia** asociada (Euclidean para N, string-edit para nombres, etc.).

- **El puente al subsimbólico**: si WQuestions se conecta con LLMs o embeddings, Gärdenfors da el marco teórico para hacer ese puente — los embeddings de un LLM son esencialmente espacios conceptuales aprendidos.

## Qué NO tomar prestado

- **El compromiso ontológico fuerte con la continuidad**: muchas cosas en WQuestions son inherentemente discretas (identidad, transacción, factura). Forzarlas en un espacio continuo sería artificial.

- **La centralidad de la convexidad**: las "categorías" en WQuestions son extensionalmente definidas (`instancia_de` enumera miembros), no por geometría. La convexidad no aplica.

- **La cercanía a la cognición humana**: WQuestions optimiza para procesabilidad por máquinas, no para plausibilidad psicológica.

## Conclusión

Gärdenfors es la **inspiración metafórica más clara** de WQuestions ("conocimiento como coordenadas") pero el **desarrollo más divergente**. La diferencia clave: Gärdenfors apuesta a lo continuo y geométrico para capturar similitud y prototipos; WQuestions apuesta a lo discreto y simbólico para capturar identidad y consulta exacta.

Para WQuestions, espacios conceptuales son:

1. **Validación de la metáfora**: las "coordenadas" como organización del conocimiento tienen pedigree teórico.
2. **Fuente de extensiones futuras**: si en algún momento queremos búsqueda aproximada, ranking, o conexión con embeddings, el camino es enriquecer cada eje con una semántica geométrica.
3. **Complemento natural**: WQuestions y espacios conceptuales pueden coexistir — los símbolos viven en WQuestions, las similitudes viven en espacios derivados de ellos.

En un sistema maduro de IA con WQuestions como backbone, espacios conceptuales serían la capa de "razonamiento por similitud" colocada *encima* del modelo simbólico.
