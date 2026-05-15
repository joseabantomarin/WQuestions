# FrameNet, VerbNet y PropBank — semántica de frames léxicos

Documento de referencia sobre tres recursos lingüísticos masivos —**FrameNet**, **VerbNet** y **PropBank**— que comparten con WQuestions la intuición de que el verbo es la unidad organizadora de la semántica oracional y los roles son los conectores. Son los **precedentes industriales** del frame "verbo como signatura de tipo" introducido en la sección 9 de WQuestions.md y del `lexicon.md` del proyecto.

## Datos bibliográficos

- **FrameNet**: Charles Fillmore, ICSI Berkeley. https://framenet.icsi.berkeley.edu
  - Fundacional: Fillmore, C. (1976) — *Frame Semantics and the Nature of Language*; Fillmore, C., Johnson, C. & Petruck, M. (2003) — *Background to FrameNet*.
- **VerbNet**: Karin Kipper Schuler, UPenn. https://verbs.colorado.edu/verbnet/
  - Fundacional: Kipper, K. et al. (2008) — *A Large-scale Classification of English Verbs*.
- **PropBank**: Martha Palmer, UPenn / UColorado. https://propbank.github.io
  - Fundacional: Palmer, M., Gildea, D. & Kingsbury, P. (2005) — *The Proposition Bank*.
- **FrameNets multilingües**: Spanish FrameNet (UNAM), German FrameNet (Saarland), Japanese FrameNet, etc.

## Motivación declarada

Los tres recursos comparten una motivación común: el significado de una oración no se reduce a la suma de los significados de sus palabras; **el verbo organiza un escenario** (frame) con participantes (roles) que las palabras del entorno saturan. Capturar ese escenario es indispensable para procesamiento de lenguaje natural y para representación semántica.

Los tres comparten esta visión pero difieren en el énfasis:

- **FrameNet** prioriza **frames semánticos** (escenarios conceptuales) y los anota con ejemplos reales del corpus.
- **VerbNet** prioriza **clases de verbos** con sintaxis similar y semántica similar; genera predicados lógicos.
- **PropBank** prioriza **anotación a gran escala** sobre corpus reales con roles minimalistas (Arg0–Arg5).

## Núcleo: FrameNet

### Frames

Un **frame** es un escenario conceptual con participantes (frame elements) y relaciones internas. Ejemplo:

```
Frame: Commerce_buy
  Core frame elements:
    Buyer   — quien adquiere
    Goods   — qué se adquiere
    Seller  — quien vende
    Money   — el monto pagado
  Non-core elements:
    Time, Place, Manner, Means, Purpose, ...
```

### Lexical Units (LUs)

Cada frame se realiza en el lenguaje a través de **unidades léxicas**: palabras (verbos, sustantivos, adjetivos) que activan el frame. Para `Commerce_buy`:

```
Lexical units: buy.v, purchase.v, purchaser.n, buyer.n
```

Una LU es **palabra + sentido**. La polisemia se maneja distribuyendo sentidos a frames distintos.

### Anotaciones

FrameNet anota corpus reales con frames y elementos. Ejemplo:

```
[Buyer Chuck] bought [Goods a car] [Seller from Jerry] [Money for $1000]
                 ^buy.v evoca el frame Commerce_buy
```

### Relaciones entre frames

Frames se conectan por relaciones jerárquicas:

- **Inheritance**: `Commerce_buy` hereda de `Transfer`.
- **Subframe**: `Commerce_buy` es subframe de `Commerce_scenario`.
- **Causative_of**, **Perspective_on**, etc.

### Métricas

FrameNet 1.7 (en inglés): ~1.200 frames, ~13.000 lexical units, ~200.000 oraciones anotadas.

## Núcleo: VerbNet

### Clases de verbos

VerbNet agrupa verbos en clases por compartir:

- **Sintaxis**: patrones de subcategorización (NP V NP, NP V NP PP, ...).
- **Semántica**: implicaciones lógicas similares.

Ejemplo: la clase `give-13.1` agrupa `give, hand, lend, loan, pass, sell, sneak, ...`. Todos comparten:

```
Frame: NP V NP NP    "John gave Mary a book"
Frame: NP V NP to NP "John gave a book to Mary"

Thematic roles: Agent, Recipient, Theme
Semantic predicates:
  transfer(during(E), Theme, Agent→Recipient)
  has_possession(start(E), Agent, Theme)
  has_possession(end(E),   Recipient, Theme)
```

### Roles temáticos canónicos

VerbNet usa un inventario cerrado de ~30 roles: Agent, Theme, Patient, Recipient, Beneficiary, Instrument, Location, Source, Goal, Path, Experiencer, Stimulus, etc.

### Métricas

VerbNet (inglés): ~270 clases, ~5.800 verbos.

## Núcleo: PropBank

### Filosofía

PropBank deliberadamente usa roles **mínimos y por-verbo** (Arg0–Arg5), no un inventario semánticamente etiquetado.

```
sell.01 (commerce: seller-X gives goods-Y to buyer-Z for price-W)
  Arg0: seller
  Arg1: thing sold
  Arg2: buyer
  Arg3: price paid
  Arg4: benefactive
```

Más anotaciones generales (ArgM-LOC, ArgM-TMP, ArgM-MNR, ArgM-CAU...) para circunstancias.

### Métricas

PropBank anota el Penn Treebank entero (~1M tokens) + extensiones.

## Características compartidas

- **Léxico-céntricas**: la unidad organizadora es el verbo (o lexical unit).
- **Roles como conectores**: los participantes entran vía roles, no como argumentos del verbo.
- **Cobertura amplia**: miles de verbos anotados con datos reales.
- **Recursos descargables**: usables en pipelines de Semantic Role Labeling, ingestores de información, etc.

## Posicionamiento frente a WQuestions

| Aspecto | FrameNet | VerbNet | PropBank | WQuestions |
|---|---|---|---|---|
| Unidad organizadora | Frame | Clase de verbos | Verbo (por sentido) | Tipo de situación en K |
| Roles | Frame Elements (por frame) | ~30 roles temáticos universales | Arg0-Arg5 (por verbo) | Catálogo canónico D7 |
| Tipos de situación reificados | Implícito (frame ≈ tipo) | Implícito (clase) | No | Sí (K explícito) |
| Polisemia | Múltiples frames por palabra | Múltiples clases | Múltiples sentidos (`sell.01`, `sell.02`) | Múltiples entradas por unidad léxica en lexicon |
| Cláusulas embebidas | Anotación contextual | Argumento sentencial | ArgM-PRD u otros | Situación como valor (composable) |
| Granularidad | Alta semántica | Media | Mínima | Alta semántica + tipada |
| Apertura | Abierta (crece con corpus) | Cerrada (clases definidas) | Por-verbo (no universal) | Catálogo canónico + extensiones de dominio |
| Propósito | Análisis lingüístico, NLP | Análisis sintáctico-semántico, NLP | Anotación de corpus, SRL | Modelado y consulta de información para IA |

## Convergencias importantes

- **El verbo como organizador**: idéntico a la frame "verbo como signatura de tipo" en WQuestions.
- **Roles como ciudadanos primarios**: idéntico al catálogo canónico D7. Los nombres incluso coinciden con el catálogo de WQuestions (Agent ≈ agente, Goal ≈ destino, Source ≈ origen, Instrument ≈ instrumento).
- **Polisemia tratada por unidad léxica**: idéntica a la convención de WQuestions de tener una entrada por verbo+complemento.
- **Anotaciones composicionales**: cláusulas embebidas, modificadores, aspectos — todos los recursos los acomodan, igual que WQuestions.

## Divergencias importantes

- **Foco en lenguaje vs foco en datos**: estos recursos describen *cómo significan las palabras*; WQuestions describe *cómo se almacenan los hechos del mundo*. El verbo es el puente pero los propósitos divergen.
- **Reificación explícita de tipo**: en WQuestions la `instancia_de` apunta a un individuo en `K`; en FrameNet/VerbNet el frame es metanivel (no se manipula como dato).
- **Cierre vs apertura**: WQuestions cierra los ejes (8) pero deja el lexicon abierto; FrameNet abre los frames; VerbNet cierra clases pero abre roles dentro.
- **PropBank usa roles posicionales (Arg0–Arg5)**, no semánticos; WQuestions usa roles semánticos nombrados como FrameNet/VerbNet.

## Qué tomar prestado

### De FrameNet

- **El catálogo de frames** como inspiración para poblar `K` con tipos de situación bien delimitados (Commerce_buy → `accion_vender`, Communication → familia de `accion_decir/preguntar/prometer`, Motion → familia de `accion_ir/venir/llegar`).
- **El concepto de Lexical Unit**: una palabra+sentido evoca un frame. WQuestions lo adopta directamente en el lexicon (entradas por unidad léxica, no por verbo).
- **Las relaciones entre frames** (Inheritance, Subframe, Causative_of): cuando WQuestions necesite jerarquías en K, este es el modelo.
- **Las anotaciones de corpus reales**: si en algún momento WQuestions construye un parser texto→hechos, FrameNet provee ejemplos masivos para entrenamiento.

### De VerbNet

- **Las clases de verbos**: organizar el lexicon de WQuestions por clases (verbos de transferencia, verbos de movimiento, verbos psicológicos) facilita extensión.
- **Los predicados semánticos**: VerbNet adjunta lógica a cada clase. WQuestions podría incorporar esa lógica como reglas de inferencia en futuras versiones.
- **El inventario de roles temáticos**: ya integrado en D7. VerbNet valida que ~30 roles son suficientes para cubrir el léxico.

### De PropBank

- **La estrategia de anotación a gran escala**: el modelo de PropBank (corpus anotado disponible) es replicable. Si WQuestions quiere un dataset de entrenamiento, PropBank es el modelo a copiar.
- **La conexión a tareas de NLP**: SRL (Semantic Role Labeling) entrenado sobre PropBank es la tecnología más directa para hacer ingesta automática texto → hechos WQuestions.

## Qué NO tomar prestado

- **El compromiso con corpus en inglés**: WQuestions debe poder operar sobre cualquier idioma. La estructura del lexicon (entradas por unidad léxica) lo permite; solo hay que poblar para cada idioma.
- **La complejidad anotacional**: FrameNet tiene capas profundas de anotación que sobrecargan el modelo. WQuestions debe mantener la información estrictamente necesaria: tipo de situación + valores de roles + propiedades modales.
- **El número de roles abierto** (FrameNet tiene cientos): WQuestions apuesta por un catálogo canónico cerrado (~30-50) más extensiones de dominio. Más sostenible y mejor para razonamiento automático.

## Conclusión

FrameNet, VerbNet y PropBank son la **infraestructura léxica industrial** más desarrollada para la intuición que WQuestions hereda en la sección 9: el verbo organiza la semántica oracional vía roles. WQuestions toma de ellos:

1. **Validación de la intuición**: 30+ años de lexicografía computacional confirman que el modelo verbo→escenario→roles funciona en escala real.
2. **Vocabulario y catálogos**: los inventarios de roles temáticos (VerbNet) y los frames (FrameNet) son donantes directos para `K` y para el lexicon.
3. **Tecnología de ingesta**: el pipeline SRL (entrenado sobre PropBank/FrameNet) es el camino más corto para texto → hechos WQuestions.
4. **Modelo de gobierno**: cómo crece un recurso léxico (FrameNet ha crecido 25+ años con liberaciones públicas) es un blueprint para cómo gestionar el lexicon de WQuestions.

La diferencia fundamental es de propósito: estos recursos describen *el lenguaje*; WQuestions describe *el mundo accedido a través del lenguaje*. Una vez ingestado el texto, FrameNet y VerbNet quedan atrás; WQuestions empieza a operar sobre los hechos.

Para WQuestions, estos recursos son:

1. **Donantes de vocabulario y estructura** para poblar `K` y el `lexicon.md`.
2. **Validación empírica** de que el frame "verbo como signatura de tipo" funciona.
3. **Camino de implementación** para la ingesta automática desde texto.
4. **Precedentes a citar** para argumentar la rigurosidad teórica del proyecto.
