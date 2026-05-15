# Trabajos relacionados — fichas comparativas

Cada archivo en este directorio analiza un precedente teórico o técnico de WQuestions y lo compara contra el modelo actual. La estructura es uniforme: datos bibliográficos, motivación, núcleo del framework, tabla comparativa, qué tomar prestado, qué no, conclusión.

## Índice

| Ficha | Precedente | Cercanía a WQuestions |
|---|---|---|
| [yang-hu-5w1h.md](yang-hu-5w1h.md) | Yang & Hu (2011) — 5W1H Conceptual Modeling Framework for Domain Ontology | Más cercana en intención (5W1H como esqueleto) |
| [mahmood-5w1h-events.md](mahmood-5w1h-events.md) | Mahmood et al. (ADBIS 2021) — 5W1H Aware Framework para eventos multimedia | Aplicación práctica reciente de 5W1H |
| [neo-davidsonian.md](neo-davidsonian.md) | Davidson / Parsons / Kratzer — Event semantics | El formalismo lingüístico más parecido al hecho atómico |
| [barwise-perry-situations.md](barwise-perry-situations.md) | Barwise & Perry (1983) — Teoría de situaciones | El ancestro filosófico-matemático más profundo |
| [gardenfors-conceptual-spaces.md](gardenfors-conceptual-spaces.md) | Gärdenfors (2000) — Conceptual Spaces | Misma metáfora "coordenadas", desarrollo divergente (geométrico) |
| [cidoc-crm.md](cidoc-crm.md) | CIDOC CRM (ISO 21127) | Precedente industrial más fuerte (event-centric + E55 Type ≈ K) |
| [rdf-and-reification.md](rdf-and-reification.md) | RDF, RDF-star, N-ary patterns (W3C) | Stack técnico natural para implementación |
| [framenet-verbnet.md](framenet-verbnet.md) | FrameNet, VerbNet, PropBank | Recursos léxicos donantes para `lexicon.md` y para ingesta texto→hechos |
| [bitemporal-snodgrass.md](bitemporal-snodgrass.md) | Snodgrass / SQL:2011 / BiTRDF | Refinamiento de D9: agregar transaction time al valid time |
| [qudt-measurements.md](qudt-measurements.md) | QUDT (Quantities, Units, Dimensions, Types) | Vocabulario canónico para mediciones reificadas; donante para K |
| [universal-schema-biolink.md](universal-schema-biolink.md) | Universal Schema / Biolink / KBpedia | Precedentes de esquemas universales cross-dominio; valida D8 |
| [llm-function-calling.md](llm-function-calling.md) | LLMs + Function Calling + MCP (2024-2026) | Puente operativo entre WQuestions y agentes LLM; D8 como function schema |

## Cómo leerlas

- Si vienes a **entender el contexto académico de WQuestions**: empieza por `barwise-perry-situations.md` y luego `neo-davidsonian.md`.
- Si vienes a **decidir cómo implementar WQuestions**: empieza por `cidoc-crm.md` y `rdf-and-reification.md`.
- Si vienes a **justificar las decisiones de diseño**: `yang-hu-5w1h.md` cubre por qué 5W1H, los demás complementan.
- Si vienes a **construir el lexicon o ingestar texto**: empieza por `framenet-verbnet.md` y `neo-davidsonian.md`.
- Si vienes a **enriquecer WQuestions**: cada ficha tiene una sección "Qué tomar prestado" con extensiones concretas.
- Si vienes a **planificar extensiones temporales**: empieza por `bitemporal-snodgrass.md`.
- Si vienes a **modelar mediciones científicas**: empieza por `qudt-measurements.md`.
- Si vienes a **integrar con LLMs / function calling**: empieza por `llm-function-calling.md`.
- Si vienes a **justificar la apuesta universal del proyecto**: empieza por `universal-schema-biolink.md`.
