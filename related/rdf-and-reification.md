# RDF, RDF-star y relaciones n-arias

Documento de referencia sobre la familia de estándares **RDF (Resource Description Framework)** y sus extensiones (reificación clásica, named graphs, RDF-star, n-ary relations). Es el **stack técnico más cercano** al patrón hecho/triple/situación de WQuestions y el candidato natural para una eventual implementación.

## Datos bibliográficos

- **RDF 1.1**: W3C Recommendation (2014) — *RDF 1.1 Concepts and Abstract Syntax*. https://www.w3.org/TR/rdf11-concepts/
- **RDFS**: W3C Recommendation — *RDF Schema 1.1*.
- **OWL 2**: W3C Recommendation (2012) — *OWL 2 Web Ontology Language*.
- **N-ary Relations Pattern**: W3C Working Group Note (2006) — *Defining N-ary Relations on the Semantic Web*. https://www.w3.org/TR/swbp-n-aryRelations/
- **Named Graphs**: incorporado a SPARQL 1.1 y RDF 1.1 Datasets.
- **RDF-star**: W3C Recommendation (2024) — *RDF-star and SPARQL-star*. Sintaxis para anidar triples.

## Motivación declarada

RDF nace como **modelo universal de datos para la Web Semántica**: cualquier afirmación sobre cualquier recurso (identificado por URI) puede expresarse como un triple `(sujeto, predicado, objeto)`. La extensiones (reificación, named graphs, RDF-star, n-ary patterns) surgen al chocar contra las limitaciones del modelo de triple plano:

- **Reificación clásica**: ¿cómo hacer afirmaciones *sobre* un triple? (procedencia, certidumbre, temporalidad).
- **Named graphs**: ¿cómo agrupar triples bajo un contexto sin perder la simplicidad?
- **N-ary relations**: ¿cómo modelar relaciones con más de dos argumentos sin perder navegabilidad?
- **RDF-star**: misma motivación que reificación pero con sintaxis compacta.

## Núcleo del framework

### Triple

La unidad atómica:

```
(sujeto, predicado, objeto)

donde
  sujeto   ∈ URI ∪ blank-node
  predicado ∈ URI
  objeto   ∈ URI ∪ blank-node ∪ literal
```

Ejemplo:
```
<ex:juan> <ex:edad> "35"^^xsd:integer .
<ex:juan> <ex:nacio_en> <ex:chile> .
```

### Reificación clásica

Para hablar *del triple* (no de lo que afirma), RDF lo convierte en un recurso con tres propiedades obligatorias:

```
_:stmt1 rdf:type rdf:Statement .
_:stmt1 rdf:subject   <ex:juan> .
_:stmt1 rdf:predicate <ex:nacio_en> .
_:stmt1 rdf:object    <ex:chile> .
_:stmt1 <ex:fuente>   <ex:registro_civil> .
_:stmt1 <ex:certeza>  "0.99"^^xsd:decimal .
```

Verboso: 4 triples para reificar 1.

### Named graphs (quad-stores)

Cada triple recibe un cuarto componente, el contexto / grafo nombrado:

```
(sujeto, predicado, objeto, grafo)
```

Permite agrupar triples bajo una situación, fuente, versión, fecha. Es la base del modelo de datasets de SPARQL.

### N-ary relation pattern (W3C 2006)

Para relaciones de aridad > 2, se introduce un nodo intermedio:

```
"Juan compró un libro a María por 20 soles el 13 de mayo"

No: (juan, compro, libro, maria, 20_soles, 2026-05-13)   ← no es un triple

Sí (n-ary pattern):
  _:compra1 rdf:type :Purchase .
  _:compra1 :buyer    <ex:juan> .
  _:compra1 :item     <ex:libro> .
  _:compra1 :seller   <ex:maria> .
  _:compra1 :amount   "20"^^:Soles .
  _:compra1 :date     "2026-05-13" .
```

El nodo intermedio (`_:compra1`) **reifica la relación**. Es exactamente el patrón "situación en T" de WQuestions.

### RDF-star (2024)

Sintaxis compacta que permite **embeber un triple como sujeto u objeto** de otro:

```
<< <ex:juan> <ex:edad> 35 >> <ex:certeza> 0.99 .
<< <ex:juan> <ex:edad> 35 >> <ex:fuente> <ex:dni> .
```

Mismo significado que la reificación clásica, fracción del verbo.

## Características clave

- **Triple como ladrillo universal**: cualquier afirmación encaja.
- **URI como identificador global**: descentralizado, sin namespace central obligatorio.
- **Heterogeneidad acomodada**: triples de distintos vocabularios coexisten.
- **Inferencia con RDFS/OWL**: capa de razonamiento opcional encima.
- **Query language**: SPARQL 1.1 (y SPARQL-star).
- **Persistencia**: triple stores (GraphDB, Stardog, Blazegraph, Apache Jena, Virtuoso).
- **Validación**: SHACL (Shapes Constraint Language).

## Aplicaciones

- DBpedia, Wikidata: knowledge graphs públicos masivos.
- Datasets gubernamentales (data.gov, data.europa.eu).
- Bioinformática (UniProt, GO).
- Patrimonio cultural (CIDOC CRM en RDF).

## Posicionamiento frente a WQuestions

| Aspecto | RDF / RDF-star | WQuestions |
|---|---|---|
| Unidad atómica | Triple (s, p, o) | Hecho atómico (caso binario) |
| Identidad | URI globales | Individuos en ejes (sin URI obligatorio) |
| Reificación | Clásica / RDF-star / n-ary pattern | Situaciones en O (D2) |
| Tipos | Ciudadanos OWL (`rdf:type`, `owl:Class`) | Reificados en K (D4) |
| Apertura semántica | Total (cualquier URI, cualquier vocabulario) | Cerrada (8 ejes) |
| Metanivel | Sí (TBox vs ABox) | No (todo plano) |
| Formalismo | Lógica de descripción + RDF abstracto | Conjuntos + tuplas |
| Consulta | SPARQL | Pendiente; proyección parcial |
| Madurez | Alta (W3C 1999+, producción global) | Inicial |

## Convergencias importantes

- **El triple = el hecho atómico binario**: estructura idéntica.

- **N-ary pattern = situación en T**: misma solución a la misma necesidad (reificar relaciones de aridad alta).

- **RDF-star ≈ hablar de hechos**: permite afirmar cosas sobre hechos sin reificación pesada. Cuando WQuestions necesite hablar de hechos (certeza, fuente, vigencia), RDF-star es el modelo a seguir.

- **SPARQL como inspiración de consulta**: el patrón "asignación parcial → conjunto de soluciones" de WQuestions es semánticamente el mismo que el "graph pattern matching" de SPARQL.

## Divergencias importantes

- **Apertura ilimitada vs ejes cerrados**: RDF permite que cualquier recurso esté en cualquier posición. WQuestions tipa los individuos en ejes disjuntos y eso restringe deliberadamente.

- **TBox/ABox vs todo plano**: en RDF/OWL, las clases (TBox) son metanivel respecto a las instancias (ABox). WQuestions rechaza esa separación: las clases son individuos en K.

- **Identidad por URI vs identidad por individuo**: RDF impone URIs globales. WQuestions deja la identidad abierta — un individuo es un símbolo en su eje, con identidad gestionada como el sistema decida (URI, UUID, integer, slug).

- **Inferencia OWL vs sin inferencia formalizada**: RDF/OWL trae 20 años de razonadores formales. WQuestions todavía no diseñó su capa de inferencia.

- **Validación SHACL vs constraint pendiente**: RDF ya tiene un lenguaje formal de constraints. WQuestions tendría que diseñarlo.

## Qué tomar prestado

- **El patrón n-ary relation como aval técnico de D2**: ya está estandarizado por el W3C, ya tiene implementaciones, ya tiene literatura. Confirma que la reificación de situaciones es la solución correcta.

- **RDF-star como sintaxis serializable de WQuestions**: si en algún momento WQuestions necesita un formato textual estándar, RDF-star ya cubre el caso de "hechos sobre hechos" con sintaxis limpia.

- **SPARQL como modelo de consulta**: el lenguaje de WQuestions puede inspirarse fuertemente en SPARQL — patrones, variables, FILTER, OPTIONAL, MINUS, UNION. El motor de SPARQL ya hace lo que WQuestions necesita.

- **SHACL como modelo de validación**: signaturas de propiedades en WQuestions son esencialmente shapes. SHACL es el vocabulario para expresarlas.

- **Triple stores como backend**: WQuestions podría implementarse encima de Apache Jena, GraphDB o Blazegraph sin reinventar persistencia.

- **Las URIs como mecanismo de identidad federada**: si WQuestions algún día quiere interoperar con datos externos, las URIs son el camino.

## Qué NO tomar prestado

- **La apertura total del modelo**: RDF permite cualquier triple; WQuestions deliberadamente restringe. No regresar a esa apertura.

- **OWL como capa de tipos**: si adoptáramos OWL, regresamos al metanivel TBox/ABox que K vino a evitar. El razonamiento OWL puede vivir aparte si surge la necesidad.

- **El sistema completo de namespaces / vocabularios mixtos**: WQuestions apuesta a un vocabulario unificado en P y M, no a federación de ontologías.

- **El monto de complejidad sintáctica**: RDF tiene 4-5 serializaciones (Turtle, N-Triples, JSON-LD, RDF/XML, TriG, RDF-star). WQuestions debería tener UNA representación canónica.

## Conclusión

RDF es el **stack técnico natural** para implementar WQuestions, pero NO su modelo conceptual. La diferencia es importante:

- **Como modelo conceptual**: RDF es demasiado abierto y demasiado comprometido con OWL/metanivel. WQuestions tiene una posición distinta.
- **Como stack técnico**: RDF resuelve persistencia, consulta (SPARQL), validación (SHACL), serialización, interoperabilidad. WQuestions podría montarse encima sin sacrificar su modelo.

La estrategia recomendada es:

1. **Definir WQuestions como modelo conceptual independiente** (en este documento).
2. **Especificar un mapping a RDF/RDF-star** como serialización canónica.
3. **Reusar SPARQL/SHACL/triple stores** como infraestructura runtime.

Esto da lo mejor de ambos mundos: la opinión limpia de WQuestions más la infraestructura industrial de RDF. Para WQuestions, RDF es:

1. **Validación técnica**: el patrón hecho/situación está estandarizado, escalado y probado.
2. **Camino de implementación**: si decidimos implementar, RDF está disponible.
3. **Puente a datos existentes**: 100B+ triples de datos abiertos en RDF; WQuestions puede consumirlos si define el mapping.
