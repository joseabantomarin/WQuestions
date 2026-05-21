# WQuestions — Diagrama general del proyecto

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║                        WQuestions — visión de conjunto                          ║
║         Un estándar universal para modelar información con 8 coordenadas        ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

---

## El problema que resuelve

```
  Hoy:
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  Sistema │  │  Sistema │  │  Sistema │  │  Sistema │
  │    A     │  │    B     │  │    C     │  │    D     │
  │ (clínica)│  │  (banco) │  │  (ERP)   │  │ (estado) │
  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │              │              │              │
       ╳──────────────╳──────────────╳──────────────╳
              no se hablan — la paciente llega a urgencias
              y su historia clínica está repartida en 4 silos

  Con WQuestions:
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  Sistema │  │  Sistema │  │  Sistema │  │  Sistema │
  │    A     │  │    B     │  │    C     │  │    D     │
  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │              │              │              │
       └──────────────┴──────┬───────┴──────────────┘
                             │  mismo esqueleto de 8 ejes
                       ┌─────▼──────┐
                       │  WQuestions│
                       │  (índice   │
                       │  universal)│
                       └────────────┘
```

---

## Los 8 ejes (coordenadas-pregunta)

```
  ╔══════════════════════════════════════════════════════════════════════╗
  ║                   V = universo de individuos                         ║
  ╠══════════════════════════════════════════════════════════════════════╣
  ║                                                                      ║
  ║   EJES DE VALOR — dónde vive cada dato                               ║
  ║   ─────────────────────────────────────                              ║
  ║                                                                      ║
  ║   Q  ¿quién?    agentes, personas, orgs, software, sensores          ║
  ║      (quis)     Marta, Banco Central, el bot asignador de viajes     ║
  ║                                                                      ║
  ║   O  ¿qué?      objetos concretos y situaciones reificadas           ║
  ║      (objectum) libro_123, venta_001, consulta_médica_007            ║
  ║                                                                      ║
  ║   L  ¿dónde?    lugares, localizaciones, regiones                    ║
  ║      (locus)    Lima, sala_3, coordenada GPS                         ║
  ║                                                                      ║
  ║   T  ¿cuándo?   instantes, periodos, versiones temporales            ║
  ║      (tempus)   2026-04-22, turno_mañana, mes_enero                  ║
  ║                                                                      ║
  ║   N  ¿cuánto?   magnitudes numéricas (con unidad en K)               ║
  ║      (numerus)  30, 98.6, 1500.00                                    ║
  ║                                                                      ║
  ║   K  ¿qué tipo? conceptos abstractos, clases, categorías             ║
  ║      (kind)     Persona, Factura, Kilogramo, GradoCelsius            ║
  ║                                                                      ║
  ║   EJES ESTRUCTURALES — cómo se conectan los datos                    ║
  ║   ─────────────────────────────────────────────                      ║
  ║                                                                      ║
  ║   P  ¿cuál?     propiedades funcionales binarias                     ║
  ║      (proprie-  nombre, edad, precio, temperatura_corporal           ║
  ║       tas)                                                           ║
  ║                                                                      ║
  ║   M  ¿cómo?     relaciones n-arias, no funcionales                   ║
  ║      (modus)    vendedor_de, diagnosticado_con, precede_a            ║
  ║                                                                      ║
  ╚══════════════════════════════════════════════════════════════════════╝

       tau : V → {Q, O, L, T, N, K}    (función total — D1)
```

---

## La unidad mínima: el hecho atómico

```
       sujeto              etiqueta              valor
          │                   │                    │
          ▼                   ▼                    ▼
      ┌───────┐         ┌──────────┐          ┌───────┐
      │  v₁   │──signa──│  ∈ P∪M   │──signa──▶│  v₂   │
      │  ∈ V  │  tura   │          │  tura    │  ∈ V  │
      └───────┘         └──────────┘          └───────┘

      h = (v₁, etiqueta, v₂)   ← única forma legal del dato

  Ejemplo:
      venta_001  ──vendedor──▶  marta
      venta_001  ──comprador──▶ ana
      venta_001  ──tema──────▶  libro_123
      venta_001  ──por_cuanto──▶ 30          (N)
      venta_001  ──moneda────▶  USD          (K)
      venta_001  ──momento───▶  2026-04-22   (T)
```

---

## Cuándo reificar una situación

```
  Hecho simple (propiedad directa):
      marta ──nombre──▶ "Marta López"      ← P basta

  Hecho compuesto (acción con 3+ participantes):
      ¿quién vendió qué a quién por cuánto cuándo?
                     │
                     ▼
      venta_001 ∈ O   ←── nueva entidad en el eje O
           │
           ├── vendedor    : marta        (Q)
           ├── comprador   : ana          (Q)
           ├── tema        : libro_123    (O)
           ├── por_cuanto  : 30           (N)
           └── momento     : 2026-04-22   (T)

  Regla: cuando un verbo exige 3+ cables, crear un nodo en O.
         reificar = subir resolución del hecho.
```

---

## El "por qué" — D6

```
  El "por qué" NO es un eje. Sus valores son heterogéneos:

      causado_por   ──▶  física, mecánica, biología
      motivado_por  ──▶  intención, deseo, decisión
      con_finalidad ──▶  meta, objetivo, propósito
      justificado_por──▶ norma, regla, autorización

  Todos se modelan como relaciones M con signatura tipada,
  no como un octavo eje.
```

---

## Las 4 capas de uso (D8 — invisibilidad del catálogo)

```
  ┌──────────────────────────────────────────────────────────┐
  │  CAPA 4 — Usuario / lenguaje natural                     │
  │  "El cliente pagó la factura con tarjeta ayer"           │
  └───────────────────────────┬──────────────────────────────┘
                              │  habla su jerga
  ┌───────────────────────────▼──────────────────────────────┐
  │  CAPA 3 — Dialecto de dominio                            │
  │  alias: RUC, IGV, placa, CIE-10, SUNAT, partida         │
  └───────────────────────────┬──────────────────────────────┘
                              │  mapeo
  ┌───────────────────────────▼──────────────────────────────┐
  │  CAPA 2 — Lexicon (el traductor maestro)                  │
  │  verbo + complemento → tipo de situación + roles         │
  │  "pagar factura" → accion_pagar(agente, tema, medio, T)  │
  └───────────────────────────┬──────────────────────────────┘
                              │  desambigua
  ┌───────────────────────────▼──────────────────────────────┐
  │  CAPA 1 — Catálogo canónico D7 (invisible)               │
  │  ~40 roles neo-davidsonianos: agente, paciente, tema,    │
  │  beneficiario, instrumento, origen, destino, causa…      │
  └───────────────────────────┬──────────────────────────────┘
                              │
  ┌───────────────────────────▼──────────────────────────────┐
  │  ALMACENAMIENTO — grafo de hechos atómicos               │
  └──────────────────────────────────────────────────────────┘
```

---

## Integración con LLMs (visión operativa)

```
  usuario NL
      │
      ▼
  ┌─────────┐   intención estructurada    ┌──────────────────┐
  │   LLM   │── (function call / MCP) ──▶│  motor WQuestions │
  └─────────┘                            │  (determinístico) │
      ▲                                  └────────┬─────────┘
      │         hechos atómicos                   │
      └───────────────────────────────────────────┘
                                                  │
                                                  ▼
                                         grafo persistente
                                         (Postgres / RDF /
                                          Datomic / ...)

  El LLM no escribe SQL.
  Emite estructura WQuestions; el motor ejecuta.
  El lexicon IS the function schema.
```

---

## Las 9 decisiones de diseño

```
  ┌────┬──────────────────────────────────────────────────────┐
  │ D1 │ Un dato vive en UN SOLO eje (tau es función total)   │
  │ D2 │ Contexto = situación reificada en O                  │
  │ D3 │ P y M se unifican: etiquetas con signatura tipada    │
  │ D4 │ Conceptos abstractos en K; instancia_de : V → K      │
  │ D5 │ Agencia contextual — cualquier individuo puede ser   │
  │    │ agente sin cambiar de eje (orgs, bots, sensores)     │
  │ D6 │ "¿Por qué?" no es eje; es familia canónica en M      │
  │ D7 │ Preguntas refinadas son ROLES, no ejes (~40 roles)   │
  │ D8 │ Catálogo D7 invisible; usuario habla su jerga        │
  │ D9 │ Propiedades cambiables se reifican con inicio/fin    │
  │    │ → consultas temporales "¿cuál era X en momento Y?"   │
  └────┴──────────────────────────────────────────────────────┘
```

---

## Cobertura demostrada (dominios probados)

```
                         ┌─────────────────────┐
                         │   8 ejes + lexicon   │
                         └──────────┬──────────┘
          ┌───────────┬─────────────┼─────────────┬───────────┐
          │           │             │             │           │
          ▼           ▼             ▼             ▼           ▼
      ┌───────┐  ┌────────┐  ┌──────────┐  ┌────────┐  ┌────────┐
      │  SPA  │  │  TAXI  │  │  CLÍNICA │  │  BANCO │  │  ERP   │
      │(fide- │  │(concur-│  │(densidad │  │(3500   │  │(cross- │
      │lidad) │  │rencia) │  │semántica)│  │tablas) │  │módulo) │
      └───────┘  └────────┘  └──────────┘  └────────┘  └────────┘
          ▼           ▼             ▼             ▼           ▼
      ┌───────┐  ┌────────┐  ┌──────────┐  ┌────────┐
      │ UNIV. │  │MUNICI- │  │  MINERA  │  │ yaku   │
      │(DAGs, │  │PALIDAD │  │(eventos  │  │(legacy │
      │ roles │  │(normas)│  │sin agente│  │ MySQL) │
      │ multi)│  │        │  │humano)   │  │        │
      └───────┘  └────────┘  └──────────┘  └────────┘

  + música, química, fútbol, contrato peruano (dominios incómodos)

  1 modelo · 8 ejes · ~40 roles canónicos = 14 dominios sin parches
```

---

## Frentes de trabajo abiertos

```
  ┌────────────────────────────────────────────────────────────────┐
  │  Lo que el prototipo Python (~2.250 líneas) ya cubre           │
  │                                                                │
  │   ✓ 8 coordenadas con tipado                                   │
  │   ✓ hechos atómicos con signatura                              │
  │   ✓ situaciones reificadas                                     │
  │   ✓ catálogo D7 (~40 roles)                                    │
  │   ✓ lexicon con resolución de polisemia                        │
  │   ✓ bitemporalidad ligera (valid time)                         │
  │   ✓ motor de consulta básico                                   │
  └────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────┐
  │  Lo que queda abierto (6 frentes)                              │
  │                                                                │
  │  F1  Motor de inferencia ............ Datalog / SHACL / SWRL  │
  │  F2  Bitemporalidad completa ........ + transaction time       │
  │  F3  Persistencia industrial ........ Postgres / RDF / Datomic │
  │  F4  Tooling ........................ ingestor, parser,        │
  │                                       IDE plugin, validador,  │
  │                                       generador MCP           │
  │  F5  Lexicon poblado (español) ...... ~2-5k entradas          │
  │  F6  Comunidad ...................... gobernanza + estándar    │
  └────────────────────────────────────────────────────────────────┘
```

---

## La apuesta central

```
  ╔══════════════════════════════════════════════════════════════════╗
  ║                                                                  ║
  ║   Las ontologías por dominio (FHIR, CIDOC, Schema.org, Biolink) ║
  ║   sobreviven como VOCABULARIOS en el eje K.                      ║
  ║                                                                  ║
  ║   La ARQUITECTURA que las aloja es siempre la misma:             ║
  ║                                                                  ║
  ║         8 ejes  +  lexicon por dominio  +  catálogo D7           ║
  ║                                                                  ║
  ║   No una ontología más.                                          ║
  ║   Un esqueleto universal donde toda ontología cabe.             ║
  ║                                                                  ║
  ╚══════════════════════════════════════════════════════════════════╝
```
