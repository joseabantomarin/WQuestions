# CIDOC CRM — Conceptual Reference Model

Documento de referencia sobre **CIDOC CRM** (Conceptual Reference Model), estándar ISO 21127 originalmente diseñado para patrimonio cultural pero ampliamente adoptado como ontología de eventos. Es probablemente la **implementación industrial más cercana en intención a WQuestions**.

## Datos bibliográficos

- **Nombre completo**: ISO 21127:2014 — *Information and documentation — A reference ontology for the interchange of cultural heritage information*.
- **Mantenedor**: ICOM CIDOC (International Council of Museums, Committee for Documentation).
- **Sitio oficial**: https://cidoc-crm.org
- **Versiones**: actualmente CIDOC CRM v7.x, con extensiones (CRMsci para ciencia, CRMdig para digital, FRBRoo para bibliotecas, etc.).
- **Aplicación moderna**: *CIDOC CRM-Based Knowledge Graph Construction for Cultural Heritage Using LLMs* (MDPI 2025).

## Motivación declarada

Permitir el **intercambio semántico** entre instituciones culturales (museos, archivos, bibliotecas) que documentan información heterogénea sobre objetos, eventos, personas, lugares y tiempos. La intuición central: las relaciones entre objetos del patrimonio rara vez son directas; casi siempre pasan por **eventos** (la creación de una pintura, la donación, la restauración, el préstamo, el descubrimiento, la datación). Modelar el patrimonio como red de eventos da expresividad, robustez histórica y trazabilidad.

## Núcleo del framework

### Jerarquía de clases (selección)

CIDOC CRM define ~80 clases (`E1` a `E99` aproximadamente). Las más relevantes para WQuestions:

```
E1   CRM Entity                      (raíz)
├── E77  Persistent Item
│   ├── E70  Thing
│   │   ├── E18  Physical Thing
│   │   │   ├── E19  Physical Object
│   │   │   └── E24  Physical Human-Made Thing
│   │   └── E89  Propositional Object (ideas, conceptos)
│   ├── E39  Actor
│   │   ├── E21  Person
│   │   └── E74  Group / E40 Legal Body
│   ├── E53  Place
│   └── E55  Type                    ← KEY!
├── E2   Temporal Entity
│   ├── E3   Condition State
│   └── E5   Event
│       └── E7   Activity            (event with explicit agent)
├── E52  Time-Span
└── E59  Primitive Value             (números, strings, etc.)
```

### Propiedades (selección)

Cada propiedad tiene código P-numerado y signatura:

- `P14 carried out by`: E7 Activity → E39 Actor
- `P7 took place at`: E4 Period → E53 Place
- `P4 has time-span`: E2 Temporal Entity → E52 Time-Span
- `P11 had participant`: E5 Event → E39 Actor
- `P12 occurred in the presence of`: E5 Event → E77 Persistent Item
- `P2 has type`: E1 CRM Entity → E55 Type    ← análogo a `instancia_de`
- `P67 refers to`, `P70 documents`, `P108 has produced`...

Total: ~190 propiedades en la versión actual.

### E55 Type — la clave para nosotros

`E55 Type` reifica las **clasificaciones** (vocabularios controlados, tesauros, sistemas de tipos) como entidades de primer orden dentro del modelo. Cualquier `E1 CRM Entity` puede tener `P2 has type` apuntando a un `E55 Type`. Esto permite que los tipos sean datos consultables, no metanivel — exactamente el rol del eje `K` en WQuestions.

### Estructura event-centric

La mayoría de afirmaciones en CIDOC CRM se hacen *sobre eventos*, no directamente entre objetos. Por ejemplo:

```
No directamente: (cuadro, creado_por, leonardo)
Sino:
  evento_creacion_001
    P14 carried out by → leonardo
    P108 has produced  → cuadro
    P7 took place at   → florencia
    P4 has time-span   → 1503-1506
```

Esta indirección permite añadir testigos, motivos, atribuciones inciertas, condiciones — sin tocar el sujeto u objeto.

## Características clave

- **Standard ISO**: 20+ años de uso real, mantenido activamente.
- **Event-centric**: equivalente directo a la D2 de WQuestions.
- **E55 Type**: reifica clasificaciones, análogo directo a `K`.
- **Extensible**: familia de extensiones para dominios específicos (ciencia, biblioteca, archivos digitales).
- **Mapping-friendly**: pensado para interoperar con Dublin Core, EAD, FRBR, etc.
- **Implementaciones**: OWL, RDF, GraphDB, ArcheS, ResearchSpace.

## Aplicaciones

- Museos: Smithsonian, British Museum, Louvre.
- Bibliotecas y archivos digitales.
- Proyectos académicos de humanidades digitales.
- Knowledge graphs de patrimonio cultural.

## Posicionamiento frente a WQuestions

| Aspecto | CIDOC CRM | WQuestions |
|---|---|---|
| Modelo base | ~80 clases + ~190 propiedades | 8 ejes |
| Punto de partida | Patrimonio cultural | Cualquier dominio |
| Event-centric | Sí (D2 equivalente) | Sí (D2) |
| Tipos reificados | Sí (E55 Type) | Sí (K) |
| Agencia | E39 Actor estricto | Q + agencia contextual (D5) |
| Lugar | E53 Place | L |
| Tiempo | E52 Time-Span | T |
| Magnitudes | E60 Number / E59 Primitive Value | Eje N propio |
| Apertura semántica | Cerrada por estándar (extensible) | Cerrada por diseño (8 ejes) |
| Formalismo | OWL/RDFS | Pendiente; conjuntos y tuplas |
| Consulta | SPARQL | Pendiente; consultas por proyección |
| Madurez | Alta (20+ años, producción) | Inicial (diseño) |

## Convergencias importantes

- **E55 Type ≈ eje K**: ambos resuelven el mismo problema (tipos como datos) de la misma forma (reificación). La existencia de E55 valida la decisión D4 de WQuestions.

- **Event-centric**: la indirección de WQuestions ("la venta es una situación, los demás colgamos de ella") es exactamente el patrón CIDOC. Misma intuición, misma solución.

- **Catálogo de propiedades P-N**: las ~190 propiedades de CIDOC son una **biblioteca probada** de etiquetas para `P` de WQuestions. `P14 carried out by`, `P7 took place at`, `P4 has time-span` son candidatos directos a etiquetas estándar.

- **Inmutabilidad y trazabilidad**: CIDOC modela los hechos como afirmaciones históricas inmodificables; los cambios se modelan como nuevos eventos. Esa filosofía es compatible y deseable para WQuestions.

## Divergencias importantes

- **Tamaño del esquema base**: CIDOC tiene 80 clases. WQuestions tiene 8 ejes. CIDOC distingue Person de Group de Legal Body; WQuestions los mete todos en Q (con `instancia_de` apuntando al tipo en K). Es una apuesta más radical de "menos es más".

- **Jerarquía de clases vs ejes disjuntos**: CIDOC usa herencia OWL (E21 Person `subclass_of` E39 Actor). WQuestions evita herencia; los ejes son disjuntos y `K` reifica las clases sin metanivel.

- **Apertura por extensión vs cierre por diseño**: CIDOC se extiende creando subclases nuevas (CRMsci, CRMdig). WQuestions no se extiende — se puebla. Si surge un dominio nuevo, no se agregan ejes, se agregan individuos.

- **Audiencia**: CIDOC es para profesionales de patrimonio cultural (librarianship, archival). WQuestions es para IA y consulta universal.

- **Why explícito**: CIDOC tiene propiedades como `P17 was motivated by`. WQuestions trata "Why" como relación causal en `M`.

## Qué tomar prestado

- **El catálogo de propiedades P1-P190**: representa décadas de modelado de eventos del mundo real. WQuestions debería revisarlo como punto de partida para definir su biblioteca estándar de etiquetas en `P` y `M`. En particular:
  - Roles humanos (P14 carried out by, P11 had participant).
  - Espaciotemporal (P7 took place at, P4 has time-span).
  - Producción y modificación (P108 has produced, P31 has modified).
  - Identificación y referencia (P67 refers to, P70 documents, P1 is identified by).
  - Clasificación (P2 has type, P137 exemplifies).

- **El patrón `P2 has type` ↔ E55 Type**: ya adoptado como `instancia_de : V → K` (D4).

- **Las extensiones existentes** (CRMsci para ciencia, CRMdig para digital): muestran cómo otros dominios extendieron el núcleo. Para WQuestions son evidencia de que el patrón event-centric escala a dominios no humanísticos.

- **El compromiso con interoperabilidad**: CIDOC se diseñó para mapear hacia/desde otros estándares. WQuestions debería pensar en mappers desde el principio (CIDOC → WQuestions, RDF → WQuestions, JSON → WQuestions).

## Qué NO tomar prestado

- **La jerarquía de clases OWL**: introduce metanivel que WQuestions decidió evitar. Si CIDOC tiene `E21 Person ⊂ E39 Actor ⊂ E77 Persistent Item ⊂ E1 CRM Entity`, en WQuestions eso se aplana: todas las personas son individuos en Q, con `instancia_de` apuntando a tipos en K (persona_natural, persona_juridica, agente_organizacional).

- **El número de clases**: 80 clases es demasiado para un esquema universal. La apuesta de WQuestions es que **8 ejes + un catálogo abierto en K y P** son suficientes.

- **El acoplamiento a OWL/RDFS**: WQuestions puede implementarse en RDF pero su modelo base es independiente del stack semántico-web.

- **El sesgo cultural-histórico**: muchas clases CIDOC son demasiado específicas para patrimonio cultural y no tienen sentido fuera (E25 Human-Made Feature, E78 Curated Holding). Se descartan o se subsumen en K.

## Conclusión

CIDOC CRM es el **precedente industrial más fuerte** de WQuestions. Misma intuición (event-centric), misma solución para tipos (E55 ≈ K), 20+ años de validación en producción y un catálogo masivo de propiedades reusables.

La diferencia con WQuestions es de **escala y compromiso**:

- CIDOC apuesta a 80 clases + 190 propiedades + jerarquía OWL.
- WQuestions apuesta a 8 ejes + catálogo abierto + sin metanivel.

Ambas son apuestas legítimas. CIDOC ya demostró que la suya funciona en patrimonio cultural. WQuestions intenta demostrar que la suya funciona universalmente.

Para WQuestions, CIDOC es:

1. **Validación industrial**: el patrón event-centric con tipos reificados *sí* escala a producción real.
2. **Catálogo donante**: 190 propiedades modeladas con cuidado, listas para adaptarse a `P` y `M`.
3. **Punto de comparación obligado**: cuando WQuestions se presente como propuesta, la primera pregunta será "¿por qué no usar CIDOC CRM?". La respuesta es: por el compromiso con la **universalidad y la simplicidad first-order**.
4. **Objetivo de interoperabilidad**: idealmente, WQuestions debería tener un mapper bidireccional con CIDOC CRM para no quedar aislado del ecosistema de patrimonio cultural y datos abiertos.
