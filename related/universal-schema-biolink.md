# Universal Schema y Biolink Model — esquemas canónicos cross-dominio

Documento de referencia sobre la línea de investigación e ingeniería de **esquemas universales**: representaciones canónicas que permiten consultar e integrar conocimiento heterogéneo bajo un vocabulario compartido. Es el campo donde WQuestions se posiciona, con la diferencia de que WQuestions define el canónico a priori en vez de inferirlo a posteriori.

## Datos bibliográficos

### Universal Schemas (línea académica)
- **Limin Yao (UMass)** — *Universal Schema for Knowledge Representation from Text and Structured Data* (Ph.D. dissertation, 2014).
- **Riedel, Yao, McCallum, Marlin** — *Relation Extraction with Matrix Factorization and Universal Schemas* (NAACL 2013).

### Open Knowledge Base Canonicalization
- **Vashishth, Jain, Talukdar** — *CESI: Canonicalizing Open Knowledge Bases using Embeddings and Side Information* (WWW 2018).
- *Open Knowledge Base Canonicalization: Techniques and Challenges* (CEUR 2024).
- *Jointly Canonicalizing and Linking Open Knowledge Base via Unified Embedding Learning* (ACM WWW 2024).
- *Open Knowledge Base Canonicalization with Multi-task Learning* (arXiv 2403.14733).

### Biolink Model
- **Biolink Model** — esquema universal para grafos biomédicos. https://biolink.github.io/biolink-model/
- *Biolink Model: A Universal Schema for Knowledge Graphs in Clinical, Biomedical, and Translational Science* (Database journal 2022). https://pmc.ncbi.nlm.nih.gov/articles/PMC9372416/

### KBpedia
- **KBpedia** — open-source integrated knowledge structure. https://kbpedia.org

## Motivación declarada

Cada base de conocimiento define su propio vocabulario:
- DBpedia, Wikidata, YAGO usan distintos predicates para "fue presidente de".
- En biomedicina, una proteína puede llamarse de cinco formas distintas en cinco bases.
- Los Open Information Extraction systems producen relaciones libres sin canonicalizar.

Resultado: los datos están dispersos, redundantes, sin matching. La integración requiere trabajo humano costoso.

**Universal Schemas** y **canonicalization** son dos respuestas a este problema:

1. **Universal Schema**: en vez de definir un esquema fijo, tratar el conjunto de todos los patrones observados como el "schema". Aprender embeddings que igualen patrones equivalentes.

2. **OKB Canonicalization**: dado un Open Knowledge Base con relaciones no canonicalizadas, agruparlas en clusters de sinónimos y asignar identificadores únicos.

3. **Schemas universales fijos** (como Biolink): definir un esquema único y exhaustivo para un dominio (biomedicina), pedir que todas las bases del dominio mapeen hacia él.

## Núcleo del framework

### Universal Schema (Riedel et al.)

Idea central: tratar el "schema" como **la matriz de co-ocurrencia entre entidades y patrones de relación**, donde los patrones pueden ser:
- Relaciones de KB (KB:president_of)
- Patrones textuales (X "was elected president of" Y)
- Patrones de OpenIE (X "is leader of" Y)

Los embeddings aprenden a equiparar patrones semánticamente equivalentes. No hay schema explícito; el schema *emerge* del aprendizaje.

### Biolink Model

Schema universal **explícito y curado** para biomedicina. Define:
- **Categories** (entidades): Gene, Protein, Disease, ChemicalEntity, Phenotype, etc. — un árbol jerárquico de tipos.
- **Slots** (relaciones): treats, causes, regulates, has_phenotype, etc. — con dominio y rango tipados.
- **Mapping rules**: cómo importar de OBO, ChEBI, MeSH, DrugBank, etc. al esquema unificado.

Es la prueba de concepto más cercana de que un schema universal **explícito** puede unificar un dominio entero (toda la biomedicina translacional).

### OKB Canonicalization

Proceso de tres pasos:
1. Identificar entidades y relaciones en texto/datos no estructurados.
2. Generar embeddings (con LLMs o GNNs).
3. Clusterizar; asignar identificadores únicos por cluster.

Resultado: cada concepto/relación tiene UN identificador canónico, incluso si aparecía como "vivió_en", "residió_en", "fue_residente_de".

## Características clave

- **Cross-domain**: integran datos heterogéneos bajo vocabulario común.
- **Escalables**: aplican a millones o billones de hechos.
- **Híbridos**: combinan ML (embeddings) con curaduría humana.
- **Estándares de facto**: Biolink es estándar comunitario en NIH-funded research.

## Aplicaciones

- **Biolink**: NCATS Translator program, conectando ~30 KGs biomédicos.
- **Wikidata canonicalization**: matching entre ediciones por idioma.
- **DBpedia, YAGO**: ingesta canonicalizada desde Wikipedia.
- **Industria biomédica**: BenevolentAI, Recursion, varios farmacéuticos usan grafos canonicalizados.

## Posicionamiento frente a WQuestions

| Aspecto | Universal Schema | Biolink | OKB Canonicalization | WQuestions |
|---|---|---|---|---|
| Definición del schema | Emergente (embeddings) | Curado explícito | Inferido post-hoc | **A priori** explícito |
| Granularidad | Por relación | Por slot tipado | Por cluster | Por rol canónico + axes |
| Dominio | Cualquiera | Biomedicina | Cualquiera | Cualquiera (apuesta) |
| Audiencia | Sistemas NLP/ML | Bioinformáticos | Sistemas de integración | Modeladores generales |
| Inmutabilidad | No central | No central | No central | Convención |
| Validez temporal | No central | Limitada | No central | D9 |
| Reglas/inferencia | Limitado | Limitado | Limitado | Convención + pendiente |

## Convergencias importantes

- **Mismo problema fundamental**: cómo unificar vocabularios heterogéneos. Universal Schema, Biolink, OKB Canonicalization y WQuestions son cuatro respuestas distintas.

- **Schema universal explícito viable**: Biolink demuestra que un schema único cross-dominio (biomedicina) es factible a escala. Es la validación más fuerte de la apuesta de WQuestions.

- **Reconocimiento del problema de polisemia**: todos los enfoques admiten que el mismo concepto se expresa de formas distintas y requiere reconciliación. WQuestions lo aborda con D8 (capas y aliases).

- **Tipado de entidades como ciudadanos**: Biolink categorías = K en WQuestions. Confirmación cross-design.

## Divergencias importantes

- **A priori vs a posteriori**: Universal Schema y OKB Canonicalization asumen heterogeneidad existente y la reconcilian; WQuestions define el canónico **antes** y deja los dialectos como vistas. Filosóficamente, WQuestions es más prescriptivo.

- **Schemas emergentes vs explícitos**: Universal Schema (Riedel) deriva el schema de los datos vía ML. WQuestions y Biolink lo definen explícitamente.

- **Dominio único vs múltiple**: Biolink cubre biomedicina solamente; WQuestions apuesta por universalidad cross-dominio.

- **Roles vs slots**: Biolink usa slots tipados por dominio. WQuestions tiene un catálogo D7 más pequeño y universal, con extensiones de dominio. Más opinionado.

## Qué tomar prestado

- **De Biolink**: la prueba de concepto de que un schema universal explícito funciona a escala. Su metodología:
  - Categorías jerárquicas para entidades (mapear a K con `instancia_de`).
  - Slots con dominio/rango (D7 lo hace, Biolink lo hace más detallado).
  - Mapping rules a otras ontologías (esto es lo que D8 propone con aliases por dominio).
  - Documentación curada por comunidad.

- **De Universal Schema (Riedel)**: la idea de que **patrones de superficie y patrones canónicos coexisten**. WQuestions ya tiene esto vía lexicon (capa 2 de D8). Los embeddings de Universal Schema pueden ser una técnica para aprender aliases automáticamente.

- **De OKB Canonicalization**: técnicas para detectar sinónimos cuando WQuestions necesite ingerir datos no estructurados. Si dos personas modelan la misma situación con verbos distintos, hay que canonicalizarlas — los métodos de embedding son aplicables.

- **De KBpedia**: el patrón de estructura integrada de conocimiento de propósito general — comparable en intención a WQuestions.

## Qué NO tomar prestado

- **El compromiso a schemas emergentes**: WQuestions apuesta por la claridad de un schema definido. Aprender el schema automáticamente es interesante pero secundario.

- **El sesgo OWL/RDF**: Biolink vive en OWL/RDF. WQuestions es agnóstico de stack.

- **El tamaño de Biolink**: Biolink tiene cientos de categorías y slots porque cubre biomedicina densamente. WQuestions apuesta por un catálogo canónico pequeño + extensiones de dominio. No replicar la explosión categorial.

## Recomendación para WQuestions

1. **Citar Biolink como precedente principal** del posicionamiento. Es el ejemplo más cercano de "schema universal explícito que funciona a escala".

2. **Estudiar el mapping de Biolink a otras ontologías** (ChEBI, MeSH, DrugBank): es exactamente el patrón D8 de aliases por dominio aplicado en producción. WQuestions puede copiar la metodología.

3. **Adoptar técnicas de canonicalization** para implementación futura del ingestor texto → hechos. Si el usuario habla naturalmente, WQuestions necesita canonicalizar; los métodos de embedding son maduros.

4. **Reconocer la diferencia filosófica**: WQuestions es **prescriptivo** (define el canónico antes); los enfoques de canonicalization son **descriptivos** (reconcilian heterogeneidad existente). Ambas son válidas, sirven a usos distintos.

## Conclusión

Universal Schemas, Biolink, OKB Canonicalization y KBpedia son la **familia de proyectos hermanos** de WQuestions. Comparten el problema fundamental (vocabularios heterogéneos → necesidad de canónico) pero divergen en respuesta.

**Lo más importante para WQuestions**: Biolink demuestra empíricamente que la apuesta de schema universal explícito es viable, al menos en un dominio amplio. WQuestions extiende la apuesta a todos los dominios, lo cual es más ambicioso pero no irracional.

Para el libro, este precedente debe ocupar un capítulo o sección que diga: "El sueño de un esquema universal no es nuevo. Biolink lo ha logrado para biomedicina; nosotros lo intentamos para todo dominio. Los principios son los mismos; el alcance es más amplio."

Para WQuestions operativamente:

1. **Validación pragmática**: Biolink prueba la viabilidad.
2. **Donante de metodología**: mapping a ontologías existentes, documentación curada, gobernanza comunitaria.
3. **Técnicas de canonicalization** para futuras versiones del ingestor.
4. **Posicionamiento claro**: WQuestions = Biolink generalizado + lexicon-céntrico (D8) + temporal-aware (D9).
