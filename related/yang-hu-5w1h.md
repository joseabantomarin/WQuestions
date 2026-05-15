# Yang & Hu — 5W1H-based Conceptual Modeling Framework for Domain Ontology

Documento de referencia sobre el trabajo de Yang, Hu y colaboradores. Es el precedente más cercano en intención a WQuestions y por eso merece su propia ficha.

## Datos bibliográficos

- **Paper original (2011)**: Liu Yang, Zhi-gang Hu, Jun Long, Tao Guo — *5W1H-based Conceptual Modeling Framework for Domain Ontology and Its Application on STPO*. Seventh International Conference on Semantics, Knowledge and Grids (SKG), IEEE.
  - DOI / IEEE Xplore: https://ieeexplore.ieee.org/document/6088118/
  - Semantic Scholar: https://www.semanticscholar.org/paper/5W1H-based-Conceptual-Modeling-Framework-for-Domain-Yang-Hu/9082d809b2b16c8c900c0b4c59b6faf616cc1674
- **Extensión (2012)**: *Conceptual Modelling for Domain Ontology Using a 5W1H Six-Layer Framework*. Advanced Materials Research, Vols. 282–283.
  - https://www.scientific.net/AMR.282-283.68

Ambos papers están detrás de paywall; esta ficha resume lo público (abstracts, descripciones en buscadores académicos, citas en literatura derivada).

## Motivación declarada

> "It is laborious and time consuming to build domain ontology, which models a specific domain and specifies the concepts in a particular subject."

El framework busca **acelerar y sistematizar** la construcción de ontologías de dominio dándole al ontólogo un esqueleto pre-definido (las 6 preguntas) sobre el cual elicitar conceptos y relaciones.

## Núcleo del framework

Los autores proponen que cualquier ontología de dominio puede analizarse y construirse desde 6 aspectos, las clásicas preguntas 5W1H:

1. **Who** — agentes / actores del dominio.
2. **What** — entidades / cosas que importan.
3. **When** — aspectos temporales.
4. **Where** — aspectos espaciales / ubicaciones.
5. **Why** — propósitos, motivaciones, causas.
6. **How** — métodos, procesos, formas.

El paper de 2012 lo extiende a una estructura de **seis capas** (presumiblemente una capa por pregunta, organizada jerárquicamente), aunque los detalles internos de cada capa no son públicos sin acceso al texto completo.

## Características clave

- **Mapeable al modelo de clases OO**: "The 5W1H conceptual modeling framework can be mapped to the class model in Object-Oriented method, which is used to model things in real world."
- **Tecnología de implementación**: aunque el paper no se publicita como OWL puro, el lenguaje y el contexto de la conferencia (Semantics, Knowledge and Grids) sugiere que las ontologías resultantes se expresan en OWL/RDF, alineadas con el ecosistema Semantic Web.
- **Escalabilidad declarada**: "scalable to business changes and user requirements".
- **Apoyo a la inferencia**: "helpful to define reasoning rules for inferring knowledge and to share domain knowledge".

## Aplicaciones documentadas

- **STPO (Science & Technology Project Ontology)**: el caso principal del paper de 2011. Ontología para el dominio de proyectos de ciencia y tecnología, con conceptos y relaciones derivados de las 6 preguntas.
- **Expert Ontology**: mencionada en el paper de 2012, en el dominio de información sobre expertos.

En ambos casos, el output es **una ontología OWL específica por dominio**, no un esquema universal.

## Lo que no se puede confirmar sin acceso al texto completo

- Definiciones formales precisas de cada una de las 6 categorías (¿qué cuenta como Who vs What cuando un agente es también un sistema?).
- Cómo se representan formalmente las relaciones entre las 6 aristas (¿son slots OWL? ¿predicados? ¿asociaciones UML?).
- Tratamiento de instancias vs clases (probable: heredan el modelo OWL estándar — clases y propiedades en TBox, instancias en ABox).
- Tratamiento de conceptos abstractos / vocabularios controlados (probable: `owl:Class` o `skos:Concept`).
- Detalle interno de las 6 capas del paper de 2012.

## Posicionamiento frente a WQuestions

| Aspecto | Yang & Hu | WQuestions |
|---|---|---|
| Número de coordenadas | 6 (5W1H) | 8 (Q, O, L, T, N, K + P, M) |
| Naturaleza | Metodología de elicitación | Estructura de datos persistente |
| Output | Una ontología OWL por dominio | Una población de hechos sobre un esquema universal |
| Tipos vs instancias | Hereda OWL (clases en TBox, instancias en ABox) | `K` reifica tipos como individuos plano |
| "Why" | Eje propio | No tiene eje; se modela como relación causal en M |
| "Cuanto" | Atributo OWL | Eje propio (N) |
| "Cual" | Propiedad OWL | Eje propio (P) |
| Universalidad | Por dominio | Por diseño |
| Apoyo a inferencia | Reglas OWL/SWRL | Pendiente de diseñar |

## Qué tomar prestado de Yang & Hu

- **Su metodología de elicitación 5W1H**: útil para poblar WQuestions con hechos de un dominio nuevo. Preguntar sistemáticamente "¿quién hace esto? ¿qué cosas hay? ¿cuándo ocurre? ¿dónde? ¿por qué? ¿cómo?" sirve para descubrir individuos que poblar en los ejes.
- **La estructura de seis capas (2012)**: sugiere niveles de abstracción dentro de cada pregunta. WQuestions todavía no tiene jerarquías internas por eje; podría adoptarlo si surgieran dominios con clara estratificación (por ejemplo: en `L`, la capa "país" sobre la capa "ciudad" sobre la capa "dirección puntual").
- **Su evidencia empírica**: dos dominios distintos (STPO, Expert) cubiertos razonablemente bien con el esqueleto 5W1H — buen punto de partida para argumentar que extender a 8 ejes universales es factible.

## Qué NO tomar prestado

- **El acoplamiento a OWL/UML/OO**: WQuestions decidió mantenerse first-order y plano (D4: tipos como individuos en K). Adoptar la jerarquía de clases OWL revertiría esa decisión.
- **El enfoque "una ontología por dominio"**: contradice directamente la apuesta de WQuestions de tener un solo esquema universal.

## Conclusión

Yang & Hu valida que el esqueleto 5W1H **cubre dominios reales** y es **suficientemente expresivo para guiar construcción de ontologías**. WQuestions toma esa validación como punto de partida y se mueve un paso más allá: si 5W1H sirve como guía universal de elicitación, ¿podría también servir como esquema universal de almacenamiento y consulta? Yang & Hu deja esa pregunta sin responder; WQuestions la responde apostando que sí (con K añadido para cerrar el agujero de los conceptos abstractos).
