# Diagramas — WQuestions

Vista visual del proyecto WQuestions en su estado actual: 8 ejes, decisiones D1–D7, unidad atómica, ejemplo aplicado y pipeline desde lenguaje natural.

## 1. Arquitectura de los 8 ejes

```
╔══════════════════════════════════════════════════════════════════════╗
║                       WQuestions — 8 ejes                            ║
╚══════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────┐
│                    EJES DE VALOR  (individuos)                       │
│                                                                      │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐                              │
│   │    Q    │  │    O    │  │    L    │                              │
│   │  quien  │  │   que   │  │  donde  │                              │
│   │         │  │         │  │         │                              │
│   │ agentes │  │ objetos │  │ lugares │                              │
│   │ con     │  │ y       │  │         │                              │
│   │ agencia │  │ situa-  │  │         │                              │
│   │         │  │ ciones  │  │         │                              │
│   └─────────┘  └─────────┘  └─────────┘                              │
│                                                                      │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐                              │
│   │    T    │  │    N    │  │    K    │                              │
│   │ cuando  │  │ cuanto  │  │  clase  │                              │
│   │         │  │         │  │         │                              │
│   │ momen-  │  │ números │  │ tipos / │                              │
│   │ tos     │  │ puros   │  │ catego- │                              │
│   │         │  │         │  │ rías    │                              │
│   └─────────┘  └─────────┘  └─────────┘                              │
│                                                                      │
│   V = Q ∪ O ∪ L ∪ T ∪ N ∪ K   (universo de individuos)               │
│   tau : V → {Q,O,L,T,N,K}    (cada individuo en UN eje)              │
└──────────────────────────────────────────────────────────────────────┘
                              ▲   ▲
                              │   │
                              │   │ etiquetas con
                              │   │ signatura tipada
                              │   │
┌──────────────────────────────────────────────────────────────────────┐
│                  EJES ESTRUCTURALES  (etiquetas)                     │
│                                                                      │
│   ┌────────────────────────┐   ┌────────────────────────┐            │
│   │           P            │   │           M            │            │
│   │         (cual)         │   │         (como)         │            │
│   │                        │   │                        │            │
│   │  propiedades binarias  │   │  relaciones n-arias    │            │
│   │  funcionales           │   │  no funcionales        │            │
│   │                        │   │                        │            │
│   │  ej: edad, nombre,     │   │  ej: viaja_en,         │            │
│   │      origen, momento   │   │      es_amigo_de       │            │
│   └────────────────────────┘   └────────────────────────┘            │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────────┐ │
│   │  Catálogo canónico de roles (D7) — ≈30-50 etiquetas fijas:     │ │
│   │  agente, paciente, origen, destino, via, momento, inicio, fin, │ │
│   │  instrumento, beneficiario, acompañantes, por_cuanto, lugar_de │ │
│   │                                                                │ │
│   │  Relaciones de por qué (D6):                                   │ │
│   │  causado_por, motivado_por, con_finalidad, justificado_por     │ │
│   │                                                                │ │
│   │  Etiqueta universal:                                           │ │
│   │  instancia_de : V → K                                          │ │
│   └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│   + etiquetas de dominio (placa, IGV, licencia, ...) extensibles     │
└──────────────────────────────────────────────────────────────────────┘
```

## 2. El hecho atómico y la consulta

```
╔══════════════════════════════════════════════════════════════════════╗
║                    UNIDAD ATÓMICA Y CONSULTA                         ║
╚══════════════════════════════════════════════════════════════════════╝

HECHO ATÓMICO

       sujeto              etiqueta              valor
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐          ┌──────────┐         ┌─────────┐
    │  v_1    │──signa───│ ∈ P ∪ M  │──signa──│  v_2    │
    │ ∈ V     │  tura    │          │  tura   │ ∈ V     │
    └─────────┘          └──────────┘         └─────────┘
                         h = (v_1, etiqueta, v_2)


CONSULTA  (asignación parcial sobre ejes)

       phi = { eje_a → val_a,  eje_b → val_b,  ...  }
              ╲                                  ╱
               ╲          MOTOR                 ╱
                ╲─────────────────────────────╱
                              │
                              ▼
              proyección sobre los ejes libres
                              │
                              ▼
                       {resultados...}
```

## 3. Ejemplo: el viaje del taxi (situación con roles)

```
╔══════════════════════════════════════════════════════════════════════╗
║          viaje_001 ∈ O  —  modelado con roles canónicos              ║
╚══════════════════════════════════════════════════════════════════════╝


                       ┌────────────────────────┐
                       │      viaje_001         │
                       │       (∈ O)            │
                       └────────────────────────┘
            ┌────────────┬──────┴──────┬─────────────┐
            │            │             │             │
       instancia_de    agente      paciente     instrumento
            │            │             │             │
            ▼            ▼             ▼             ▼
       viaje_taxi   pedro_taxi   juan_usuario  vehiculo_abc
        (∈ K)        (∈ Q)         (∈ Q)         (∈ O)

            ┌────────────┬─────────────┬─────────────┐
            │            │             │             │
         origen       destino         via         distancia
            │            │             │             │
            ▼            ▼             ▼             ▼
       punto_juan   aeropuerto   via_expresa       8.3
        (∈ L)        (∈ L)         (∈ O)         (∈ N)

            ┌────────────┬─────────────┐
            │            │             │
         inicio         fin     con_finalidad  ◄── (D6)
            │            │             │
            ▼            ▼             ▼
        18:37        18:52      meta_llegar_19:00
        (∈ T)        (∈ T)         (∈ O)
```

## 4. Pipeline: del lenguaje natural a los hechos

```
╔══════════════════════════════════════════════════════════════════════╗
║                INGESTA  NL → HECHOS  (sección 9)                     ║
╚══════════════════════════════════════════════════════════════════════╝

      ╭──────────────────────────────────────────────────╮
      │  "Juan le dio un libro a María ayer en su casa"  │
      ╰──────────────────────────────────────────────────╯
                              │
                              ▼
                  ┌────────────────────────┐
                  │   parsing sintáctico   │
                  └────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
     sujeto                 verbo               predicado
     "Juan"                 "dio"          "un libro a María
                              │             ayer en su casa"
                              │
                              ▼
                  ┌────────────────────────┐
                  │       lexicon.md       │
                  │  dar →                 │
                  │   tipo: accion_dar     │
                  │   obligatorios:        │
                  │     [agente, tema,     │
                  │      beneficiario]     │
                  │   opcionales:          │
                  │     [momento, lugar_de]│
                  └────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
     mapeo a               creación             roles de
     rol canónico          de situación         complementos
        │                  en O                    │
        ▼                     ▼                    ▼
     agente             dar_001 ∈ O           tema = libro
                                              beneficiario = maria
                                              momento = ayer
                                              lugar_de = casa
                              │
                              ▼
                  ┌────────────────────────┐
                  │      HECHOS WQ         │
                  │ (dar_001, instancia_de,│
                  │           accion_dar)  │
                  │ (dar_001, agente,      │
                  │           juan)        │
                  │ (dar_001, tema, libro) │
                  │ (dar_001, beneficiario,│
                  │           maria)       │
                  │ (dar_001, momento,     │
                  │           ayer)        │
                  │ (dar_001, lugar_de,    │
                  │           casa_juan)   │
                  └────────────────────────┘
```

## 5. Vista integrada — todo conectado

```
╔══════════════════════════════════════════════════════════════════════╗
║                       VISIÓN GLOBAL                                  ║
╚══════════════════════════════════════════════════════════════════════╝

  LENGUAJE NATURAL                              CONSULTAS NL
       │                                           ▲
       │ parsing                                   │ "¿quién hizo X?"
       ▼                                           │ → phi
  ┌──────────┐                                ┌──────────┐
  │ lexicon  │◄────── alimenta ─────────── ───│  motor   │
  └──────────┘                                │ de query │
       │                                      └──────────┘
       │ verbo → tipo + roles                       ▲
       ▼                                            │
  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │                  H E C H O S                             │
  │            h = (sujeto, etiqueta, valor)                 │
  │                                                          │
  │  ┌──────────────────────────────────────────────────┐    │
  │  │  EJES DE VALOR  (donde viven los individuos)     │    │
  │  │                                                  │    │
  │  │     Q       O       L       T       N       K    │    │
  │  │   quien   que    donde   cuando  cuanto  clase   │    │
  │  └──────────────────────────────────────────────────┘    │
  │                                                          │
  │  ┌──────────────────────────────────────────────────┐    │
  │  │  EJES ESTRUCTURALES  (vocabulario de conexión)   │    │
  │  │                                                  │    │
  │  │     P (cual)         M (como)                    │    │
  │  │     propiedades      relaciones                  │    │
  │  │                                                  │    │
  │  │     ┌──────────────────────────────┐             │    │
  │  │     │ Catálogo canónico (D7)       │             │    │
  │  │     │ + por-qué (D6)               │             │    │
  │  │     │ + etiquetas de dominio       │             │    │
  │  │     └──────────────────────────────┘             │    │
  │  └──────────────────────────────────────────────────┘    │
  │                                                          │
  │  DECISIONES DE DISEÑO                                    │
  │   D1: un dato vive en un solo eje                        │
  │   D2: contexto = situación en O                          │
  │   D3: P y M se unifican matemáticamente                  │
  │   D4: conceptos abstractos van en K                      │
  │   D5: agencia es contextual                              │
  │   D6: por-qué es relacional, no eje                      │
  │   D7: preguntas refinadas son ROLES, no ejes             │
  │                                                          │
  └──────────────────────────────────────────────────────────┘

  ARTEFACTOS DEL PROYECTO
   • WQuestions.md ........ formalización + 3 ejemplos
   • lexicon.md ........... verbo → tipo + roles
   • related/* ............ 8 fichas de precedentes
   • conversacion1.md ..... registro de diseño
```
