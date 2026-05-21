# Diagramas — WQuestions (libro completo, 30 capítulos)

## 1. Parte I — Las preguntas como invariantes (caps 1–3)

```
╔══════════════════════════════════════════════════════════════════════════╗
║              PARTE I — POR QUÉ las preguntas importan                    ║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌────────────────────────────────────────────────────────────────────┐
  │  cap 1 — La torre de Babel de las ontologías                       │
  │                                                                    │
  │   La sala de emergencias a las 2 AM: la paciente lleva su          │
  │   historia médica fragmentada entre 4 sistemas que no se hablan.   │
  │   ESTE es el problema operativo del libro.                         │
  │                                                                    │
  │   → El costo de la fragmentación es real, diario y enorme.         │
  └────────────────────────────────┬───────────────────────────────────┘
                                   │
  ┌────────────────────────────────▼───────────────────────────────────┐
  │  cap 2 — Aristóteles, el periodismo y la cognición                 │
  │                                                                    │
  │   1917: el aula norteamericana donde nacen las 5W1H.               │
  │   Mucho antes: Aristóteles, Cicerón, las "circunstancias"          │
  │   judiciales. Y a la vez: el cerebro del niño de 5 años.           │
  │                                                                    │
  │   → Las preguntas son INVARIANTES cognitivas y culturales.         │
  └────────────────────────────────┬───────────────────────────────────┘
                                   │
  ┌────────────────────────────────▼───────────────────────────────────┐
  │  cap 3 — Lo que ya intentamos                                      │
  │                                                                    │
  │   Tres intentos previos: 5W1H heurístico, web semántica RDF/OWL,   │
  │   ontologías por dominio (CIDOC, Schema.org, Biolink, FHIR…).      │
  │   Cada uno acertó algo y dejó algo abierto.                        │
  │                                                                    │
  │   → WQuestions parte de ahí, no contra ellos.                      │
  └────────────────────────────────────────────────────────────────────┘
```

## 2. Parte II — Los 8 ejes (caps 4–7)

```
╔══════════════════════════════════════════════════════════════════════════╗
║              PARTE II — QUÉ son los 8 ejes (introducción gradual)        ║
╚══════════════════════════════════════════════════════════════════════════╝

  cap 4 ─►  Los 4 pilares iniciales: Q (quién) O (qué) L (dónde) T (cuándo)
  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
  │    Q    │ │    O    │ │    L    │ │    T    │
  │ agentes │ │ objetos │ │ lugares │ │ momentos│
  └─────────┘ └─────────┘ └─────────┘ └─────────┘
        " Marta le regaló un libro a su sobrino ayer en su casa "

                            +
  cap 5 ─►  El zócalo categórico K (clase)
  ┌─────────┐
  │    K    │  "libro" no es solo un objeto: es una INSTANCIA del concepto.
  │  tipos  │  K es el catálogo de conceptos abstractos del dominio
  │/concep- │  (Schema.org, SNOMED, CIDOC, QUDT). instancia_de : V → K
  │ tos     │
  └─────────┘

                            +
  cap 6 ─►  Cuánto: el eje cuantitativo N
  ┌─────────┐
  │    N    │  La Mars Climate Orbiter se estrelló por confundir libras y
  │ números │  newtons. N son magnitudes con unidad; las unidades van en K;
  │ con uni-│  reificarlas como (cantidad, unidad) cuando hace falta.
  │ dad     │
  └─────────┘

                            +
  cap 7 ─►  Cuál y cómo: los ejes ESTRUCTURALES P y M
  ┌─────────────────────────────┐   ┌─────────────────────────────┐
  │           P (cual)          │   │           M (como)          │
  │  propiedades binarias       │   │  relaciones n-arias,        │
  │  funcionales                │   │  no funcionales             │
  │  edad, nombre, color, …     │   │  viaja_en, es_amigo_de, …   │
  └─────────────────────────────┘   └─────────────────────────────┘

                            =
                  ┌─────────────────────────────────┐
                  │   V = Q ∪ O ∪ L ∪ T ∪ N ∪ K     │
                  │   tau : V → {Q,O,L,T,N,K}       │
                  │   etiquetas P ∪ M con signatura │
                  └─────────────────────────────────┘
```

## 3. Parte III — El modelo en operación (caps 8–11)

```
╔══════════════════════════════════════════════════════════════════════════╗
║       PARTE III — CÓMO se conectan: hecho → grafo → reificación → por-qué║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌────────────────────────────────────────────────────────────────────┐
  │  cap 8 — El hecho atómico                                          │
  │                                                                    │
  │     sujeto              etiqueta              valor                │
  │       │                    │                    │                  │
  │       ▼                    ▼                    ▼                  │
  │   ┌──────┐            ┌──────────┐         ┌──────┐                │
  │   │ v_1  │── signa ──│ ∈ P ∪ M  │── signa │ v_2  │                 │
  │   │ ∈ V  │   tura     │          │  tura   │ ∈ V  │                │
  │   └──────┘            └──────────┘         └──────┘                │
  │                                                                    │
  │   h = (v_1, etiqueta, v_2)  — la única forma legal del dato.       │
  └────────────────────────────────┬───────────────────────────────────┘
                                   │  miles de hechos
                                   ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │  cap 9 — El espacio multidimensional                               │
  │                                                                    │
  │   Imagina una hoja de cálculo con 8 columnas (Q O L T N K P M).    │
  │   Los hechos forman un GRAFO donde cualquier individuo se          │
  │   alcanza desde cualquier otro siguiendo etiquetas.                │
  │                                                                    │
  │   Consultas = asignación parcial sobre ejes:                       │
  │     phi = { Q → juan, T → hoy }  →  proyecta sobre ejes libres.    │
  └────────────────────────────────┬───────────────────────────────────┘
                                   │  el grafo necesita "nudos"
                                   ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │  cap 10 — Situaciones reificadas                                   │
  │                                                                    │
  │   El español permite convertir verbos en sustantivos: vender →     │
  │   "la venta". Cuando una acción participa de 3+ roles, la          │
  │   REIFICAMOS como individuo en O. Esto evita la trampa de querer   │
  │   meter todo en una tripleta.                                      │
  │                                                                    │
  │   venta_001 ∈ O  ─┬─ vendedor: marta                               │
  │                   ├─ comprador: ana                                │
  │                   ├─ tema: libro_123                               │
  │                   ├─ momento: 2026-04-22                           │
  │                   └─ por_cuanto: 30 USD                            │
  └────────────────────────────────┬───────────────────────────────────┘
                                   │  ya queda el "por qué"
                                   ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │  cap 11 — El "por qué" no es una pregunta más                      │
  │                                                                    │
  │   El niño de 4 años pregunta "¿por qué?" y nos descubre algo: el   │
  │   "por qué" no es UN eje. Es una familia de relaciones porque sus  │
  │   valores son heterogéneos. D6:                                    │
  │                                                                    │
  │      causado_por  ── física, mecánica                              │
  │      motivado_por ── intención, deseo, decisión                    │
  │      con_finalidad── meta, objetivo                                │
  │      justificado_por ── regla, norma, autorización                 │
  └────────────────────────────────────────────────────────────────────┘
```

## 4. Parte IV — El lenguaje bajo presión (caps 12–14)

```
╔══════════════════════════════════════════════════════════════════════════╗
║       PARTE IV — CÓMO el lenguaje natural entra al modelo                ║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌────────────────────────────────────────────────────────────────────┐
  │  cap 12 — El verbo: la firma de contrato de la oración             │
  │                                                                    │
  │   Davidson (1967): un verbo es una función con SIGNATURA tipada.   │
  │   "dar" reclama (agente, tema, beneficiario). Si falta uno, la     │
  │   oración no cierra. Si entra alguien del tipo equivocado          │
  │   (paciente humano en campo de objeto), error de tipo.             │
  │                                                                    │
  │   → El verbo gobierna qué situación crear y qué cables enchufar.   │
  └────────────────────────────────┬───────────────────────────────────┘
                                   │
  ┌────────────────────────────────▼───────────────────────────────────┐
  │  cap 13 — El Lexicon: el traductor maestro                         │
  │                                                                    │
  │   "Pedro le dio la mano a su jefe" NO es accion_dar (transferir);  │
  │   es accion_saludar. El Lexicon registra patrones (verbo + comple- │
  │   mento) y los desambigua. D8: el catálogo canónico es invisible   │
  │   al usuario — el Lexicon traduce su jerga local.                  │
  │                                                                    │
  │        usuario  →  lexicon  →  catálogo D7  →  almacenamiento      │
  │       (su jerga)   (mapeo)   (38 roles fijos) (identificadores)    │
  └────────────────────────────────┬───────────────────────────────────┘
                                   │
  ┌────────────────────────────────▼───────────────────────────────────┐
  │  cap 14 — Cuando el lenguaje aprieta                               │
  │                                                                    │
  │   Tres trampas que harían explotar a un robot ingenuo:             │
  │                                                                    │
  │     1. NOMINALIZACIÓN — "la llegada del paciente" es un sustantivo │
  │        que ESCONDE un evento. → reificar en O.                     │
  │     2. MODALES — "debe pagar", "puede entrar", "intentó comprar".  │
  │        → estatus_factual: real | intencionado | obligatorio | …    │
  │     3. IDIOMAS — frases hechas y polisemia. → patrones del Lexicon │
  │        capturan la unidad mínima de significado, no la palabra.    │
  └────────────────────────────────────────────────────────────────────┘
```

## 5. Parte V — Modelando dominios reales (caps 15–24)

```
╔══════════════════════════════════════════════════════════════════════════╗
║   PARTE V — La prueba: 10 dominios reales, cada uno estresa una dimensión║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌──────────────────────────────┐    ┌──────────────────────────────┐
  │  cap 15 — SPA Oasis          │    │  cap 16 — TAXI (Uber-style)  │
  │                              │    │                              │
  │  Apertura de la Parte V.     │    │  Concurrencia en tiempo real │
  │  Ana, Beto, Carlos en un     │    │  + agentes de software (la   │
  │  spa con planes y fidelidad. │    │  app asignando viajes) +     │
  │  184 hechos = un mes entero. │    │  GPS, cadena causal de       │
  │  → ESTRENO del modelo en     │    │  eventos cada 5 segundos.    │
  │    código ejecutable.        │    │  → CONCURRENCIA + D5         │
  └──────────────────────────────┘    └──────────────────────────────┘

  ┌──────────────────────────────┐    ┌──────────────────────────────┐
  │  cap 17 — CLÍNICA            │    │  cap 18 — BANCO              │
  │                              │    │                              │
  │  Densidad semántica:         │    │  El más exigente: 3.500 ta-  │
  │  prescribir, contraindica-   │    │  blas en producción.         │
  │  ciones, rediagnóstico,      │    │  → BITEMPORALIDAD (lo que    │
  │  causalidad médica.          │    │    era cierto vs lo que se   │
  │  → "por qué" + D9 vigencia   │    │    afirmó cuándo) + traza    │
  │  (medicación con duración).  │    │    regulatoria.              │
  └──────────────────────────────┘    └──────────────────────────────┘

  ┌──────────────────────────────┐    ┌──────────────────────────────┐
  │  cap 19 — ERP multi-módulo   │    │  cap 20 — UNIVERSIDAD        │
  │                              │    │                              │
  │  Una venta cruza Comercial,  │    │  Timelines largos (5 años).  │
  │  Inventario, Contabilidad,   │    │  Grafos de prerrequisitos    │
  │  Tesorería. Cada módulo      │    │  parciales. Personas que     │
  │  habla su dialecto.          │    │  cambian de rol: estudiante  │
  │  → INTEGRACIÓN cross-módulo  │    │  → ayudante → docente.       │
  │    sin schema matching.      │    │  → DAG + D5 contextual       │
  └──────────────────────────────┘    └──────────────────────────────┘

  ┌──────────────────────────────┐    ┌──────────────────────────────┐
  │  cap 21 — MUNICIPALIDAD      │    │  cap 22 — MINERA             │
  │                              │    │                              │
  │  Lo normativo en CADA paso:  │    │  Lo físico, lo espacial, los │
  │  cada acto se justifica por  │    │  eventos sin agente humano.  │
  │  norma. Rectificación de     │    │  Sensores que reportan, com- |
  │  multas → inmutabilidad.     │    │  isionamiento de plantas.    │
  │  → justificado_por como      │    │  → eventos sin Q intencional │
  │    columna vertebral.        │    │    + reglas derivadas        │
  └──────────────────────────────┘    └──────────────────────────────┘

  ┌──────────────────────────────┐    ┌──────────────────────────────┐
  │  cap 23 — yaku (PRODUCCIÓN)  │    │  cap 24 — Cuatro dominios    │
  │                              │    │           incómodos          │
  │  El "otro lado del espejo"   │    │                              │
  │  del cap 15: NO modelamos    │    │  Música (composición), quí-  │
  │  desde cero, MAPEAMOS sobre  │    │  mica (combustión), fútbol   │
  │  un MySQL existente.         │    │  (eventos simétricos),       │
  │  Arqueología semántica de    │    │  contrato peruano (cláusula  │
  │  yaku: sauna+hostal+gym+     │    │  IPC). Dominios que NO son   │
  │  cafetín. Modalidades de     │    │  comerciales y donde igual   │
  │  cobertura como concepto     │    │  el modelo aguanta.          │
  │  nuevo (cubierto_por).       │    │  → AMPLITUD del catálogo     │
  │  → APLICACIÓN sobre LEGACY   │    │                              │
  └──────────────────────────────┘    └──────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────┐
  │              Lo que la Parte V demuestra en conjunto             │
  │                                                                  │
  │   1 modelo + 8 ejes + ~40 roles canónicos =                      │
  │       10 dominios disímiles modelados sin parches.               │
  │   Cada dominio agrega vocabulario al lexicon; ninguno requiere   │
  │   inventar ingeniería nueva sobre el catálogo D7.                │
  └──────────────────────────────────────────────────────────────────┘
```

## 6. Parte VI — Futuro: LLMs y qué falta (caps 25–27)

```
╔══════════════════════════════════════════════════════════════════════════╗
║              PARTE VI — Hacia dónde va el proyecto                       ║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌────────────────────────────────────────────────────────────────────┐
  │  cap 25 — WQuestions y los LLMs (la simbiosis natural)             │
  │                                                                    │
  │     usuario NL                                                     │
  │         │                                                          │
  │         ▼                                                          │
  │     ┌─────────┐  intención        ┌──────────────┐                 │
  │     │   LLM   │── estructurada ──►│   motor WQ   │                 │
  │     └─────────┘  (function call)  │ (determinís- │                 │
  │         ▲                          │  tico)      │                 │
  │         │       hechos atómicos   └──────┬──────┘                  │
  │         └───────────────────────────────┘ │                        │
  │                                            ▼                       │
  │                                       grafo persistente            │
  │                                                                    │
  │   El LLM NO escribe SQL. Emite estructura WQuestions. El motor     │
  │   ejecuta. Función calling + MCP estandarizan el cable.            │
  │                                                                    │
  │   Lexicon = function schema. Cada entrada del lexicon ES la        │
  │   firma de una función que el LLM puede invocar.                   │
  └────────────────────────────────┬───────────────────────────────────┘
                                   │
  ┌────────────────────────────────▼───────────────────────────────────┐
  │  cap 26 — Aplicaciones futuras: 5 familias que se vuelven viables  │
  │                                                                    │
  │   1. Búsqueda cross-dominio sin schema matching (Berners-Lee 25y)  │
  │   2. Auditoría retrospectiva con bitemporalidad                    │
  │   3. Razonamiento composicional sobre conocimiento                 │
  │   4. Multi-agente: humanos + LLMs como Q de pleno derecho          │
  │   5. Explicabilidad nativa via cadenas causado_por/justificado_por │
  └────────────────────────────────┬───────────────────────────────────┘
                                   │
  ┌────────────────────────────────▼───────────────────────────────────┐
  │  cap 27 — Qué falta (los 6 frentes pendientes)                     │
  │                                                                    │
  │   F1  Motor de inferencia ........... Datalog / SHACL / SWRL       │
  │   F2  Bitemporalidad completa ....... + transaction time           │
  │   F3  Persistencia industrial ....... Postgres / RDF / Datomic     │
  │   F4  Tooling ........................ lexicon ingestor, parser,   │
  │                                        IDE, validador, MCP gen     │
  │   F5  Lexicon poblado por idioma ..... ~2-5k entradas español      │
  │   F6  Comunidad ....................... gobernanza + contribución  │
  │                                                                    │
  │   El prototipo Python (~2.250 líneas) cubre lo CONCEPTUAL.         │
  │   La infraestructura industrial es el trabajo abierto.             │
  └────────────────────────────────────────────────────────────────────┘
```

## 7. Cierre + anexos (caps 28–30)

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    CIERRE + ANEXOS DE CÓDIGO                             ║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌────────────────────────────────────────────────────────────────────┐
  │  cap 28 — Conclusión: por qué importan las preguntas               │
  │                                                                    │
  │   Vuelta circular a la sala de emergencias del cap 1.              │
  │   La misma paciente, dos años después. Esta vez su historia        │
  │   clínica unificada llega a la guardia en segundos.                │
  │                                                                    │
  │   El libro no propone una ontología más — propone REEMPLAZAR la    │
  │   noción de ontología por-dominio con un esqueleto universal de    │
  │   8 ejes + lexicon por dominio. Las ontologías existentes          │
  │   sobreviven como vocabularios en K, no como arquitecturas.        │
  └────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────────┐
  │  cap 29 — Anexo: código por capítulo (Parte V consolidada)         │
  │                                                                    │
  │   Todos los fragmentos Python de los caps 15–24 reunidos en un     │
  │   solo lugar. Referencia rápida + vista panorámica del estilo.     │
  └────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────────┐
  │  cap 30 — Anexo: librería núcleo del prototipo (~850 líneas)       │
  │                                                                    │
  │   El código fuente íntegro de prototipo/wq/: 8 coordenadas,        │
  │   hechos atómicos con signatura, situaciones reificadas, catálogo  │
  │   D7, lexicon con resolución de polisemia, bitemporalidad ligera   │
  │   y motor de consulta. 9 archivos cortos. Ejecutable.              │
  └────────────────────────────────────────────────────────────────────┘
```

## 8. Las 9 decisiones de diseño acumuladas (D1–D9)

```
╔══════════════════════════════════════════════════════════════════════════╗
║         Las 9 decisiones que el libro construye y nunca abandona         ║
╚══════════════════════════════════════════════════════════════════════════╝

  D1  Un dato vive en UN SOLO eje.
      tau : V → {Q,O,L,T,N,K} es función total.
      (introducida en Parte II)

  D2  Contexto = situación reificada en O.
      No hay "campo de contexto"; el contexto se vuelve individuo.
      (cap 10)

  D3  P y M se unifican matemáticamente como etiquetas con signatura.
      La distinción es semántica, no estructural.
      (cap 7)

  D4  Conceptos abstractos viven en K. instancia_de : V → K
      es la relación universal entre individuos y tipos.
      (cap 5)

  D5  Agencia contextual: un mismo individuo puede actuar como agente
      en una situación sin reclasificarse a Q. Equipos, organizaciones,
      sensores, software, todos pueden ser agente sin moverse de eje.
      (cap 22 minera, cap 20 universidad)

  D6  El "por qué" no es eje. Es una familia canónica de relaciones:
      causado_por, motivado_por, con_finalidad, justificado_por.
      (cap 11)

  D7  Las preguntas refinadas (para qué, por dónde, con quién, con qué…)
      son ROLES, no ejes. Se modelan como etiquetas canónicas en P/M
      con signatura tipada al eje correspondiente. Catálogo de ~40
      roles, heredado de la tradición neo-davidsoniana.
      (cap 12)

  D8  El catálogo canónico es INVISIBLE al usuario final.
      El usuario habla su jerga; el lexicon traduce. Cuatro capas:
      canónica D7 invisible → lexicon → dialecto de dominio → UI.
      (cap 13)

  D9  Las propiedades cambiables se reifican como situaciones con
      inicio/fin. No se almacenan como atributos directos del sujeto.
      Habilita consultas "¿cuál era X en el momento Y?".
      (cap 17 historia clínica, cap 18 banco)
```
