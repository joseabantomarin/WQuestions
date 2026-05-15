# Semántica de eventos neo-davidsoniana

Documento de referencia sobre la familia de teorías lingüístico-formales conocidas como *event semantics* o *neo-davidsonianas*, que ofrecen el aparato matemático más parecido al "hecho atómico" de WQuestions.

## Datos bibliográficos

- **Origen**: Davidson, D. (1967) — *The Logical Form of Action Sentences*.
- **Refinamiento neo-davidsoniano**: Parsons, T. (1990) — *Events in the Semantics of English: A Study in Subatomic Semantics*. MIT Press.
- **Reformulaciones modernas**: Kratzer, A. (2002) — *The Event Argument and the Semantics of Verbs*; Landman, F. — *Events and Plurality* (lecture notes, Tel Aviv).
- **Aplicación a knowledge bases**: *Neo-Davidsonian-Based Event Class Semantic Representation* (ScienceDirect, 2020).

## Motivación declarada

Davidson notó que las oraciones de acción ("Juan pateó la pelota con fuerza en el patio a las 3") no se reducen elegantemente a predicados de aridad fija sobre los participantes. La aridad varía con cada modificador. Su propuesta: introducir un **argumento de evento** existencialmente cuantificado, y dejar que cada modificador sea un predicado sobre ese evento.

Los neo-davidsonianos (Parsons, Castañeda, Higginbotham, Kratzer) llevan esta idea al extremo: **todos** los participantes — incluido el sujeto y el objeto directo — entran vía **roles temáticos** sobre el evento, no como argumentos directos del verbo.

## Núcleo formal

**Davidson original (verbos de aridad variable):**

```
"Juan pateó la pelota a las 3 con fuerza en el patio"
⇒ ∃e [ Patear(juan, pelota, e) ∧ A_las(e, 3) ∧ Con(e, fuerza) ∧ En(e, patio) ]
```

**Neo-Davidsonian (todos los argumentos como roles temáticos):**

```
∃e [ Patear(e)
    ∧ Agent(e, juan)
    ∧ Theme(e, pelota)
    ∧ Time(e, 3)
    ∧ Manner(e, fuerza)
    ∧ Location(e, patio) ]
```

## Roles temáticos canónicos

La literatura propone un inventario de roles (no hay consenso exacto, pero estos son los más estables):

- **Agent** — el que ejecuta la acción intencionalmente.
- **Patient / Theme** — el que sufre o es afectado por la acción.
- **Experiencer** — el que experimenta un estado mental.
- **Goal** — destino o objetivo.
- **Source** — origen.
- **Instrument** — medio usado.
- **Location** — dónde ocurre.
- **Time** — cuándo ocurre.
- **Manner** — cómo ocurre.
- **Cause** — qué lo causa.
- **Beneficiary** — para quién.

Cada rol es una **función parcial** del evento al individuo: `Agent : Event → Individual`.

## Características clave

- **Reificación del evento**: el evento es un individuo de primer orden, no un constructo derivado.
- **Apertura a modificadores**: cualquier modificador adverbial se añade como predicado sobre el evento sin cambiar la aridad del verbo.
- **Composicionalidad**: encaja con la semántica composicional estándar (λ-calculus + tipos).
- **Tratamiento uniforme de adverbios**: "rápidamente", "ayer", "en el patio" son todos predicados unarios sobre `e`.

## Aplicaciones

- **Análisis lingüístico**: tratamiento de anáforas verbales, pluralidad de eventos, perfectividad/imperfectividad, aspecto.
- **Procesamiento de lenguaje natural**: extracción de información, semantic role labeling, AMR (Abstract Meaning Representation).
- **Knowledge bases derivadas de texto**: el patrón neo-davidsoniano subyace en cómo se almacenan eventos extraídos de texto en grafos de conocimiento.

## Posicionamiento frente a WQuestions

| Aspecto | Neo-davidsoniano | WQuestions |
|---|---|---|
| Reificación de evento | Sí, central | Sí, central (situaciones en O) |
| Participantes vía roles | Sí, roles temáticos | Sí, propiedades `P` con signaturas |
| Conjunto de roles | Abierto, debatido (típicamente 8-12) | Cerrado al usuario, abierto en `P` |
| Tipos de individuos | Un solo dominio (Individual) | 6 ejes disjuntos (Q, O, L, T, N, K) |
| Conceptos abstractos | No reificados (clases del verbo) | Reificados en `K` |
| Magnitudes / cuantos | Tratados como individuos comunes | Eje propio `N` |
| Naturaleza | Teoría lingüística | Estándar de modelado de datos |
| Formalismo | Lógica de predicados de primer orden + lambda | Pendiente; conjuntos + tuplas |
| Consulta | No central | Central (proyecciones parciales) |

## Convergencias importantes

- **Patrón hecho atómico ≡ predicado de rol temático**:

  ```
  Neo-davidsonian:    Agent(e_42, juan)
  WQuestions:         (e_42, agente, juan)
  ```

  Son el mismo objeto matemático con notación distinta.

- **Roles ↔ etiquetas de propiedad**: Agent, Theme, Location, Time son ejemplos concretos de etiquetas en `P`. WQuestions hereda esa nomenclatura de forma natural.

- **Reificación como puente al razonamiento**: en ambos, el hecho de que el evento sea un individuo permite hablar *de él* (`e_42` puede ser modificado, contado, comparado).

## Divergencias importantes

- **Apertura del conjunto de roles**: la literatura neo-davidsoniana no cierra el inventario de roles temáticos; sigue siendo motivo de debate. WQuestions sí cierra los **ejes** pero deja `P` y `M` abiertos para que el usuario invente etiquetas con signatura.

- **Un solo dominio vs ejes disjuntos**: en neo-davidsonian, "Juan", "pelota", "patio", "3 PM" viven todos en el mismo dominio `Individual`. WQuestions los separa en Q/O/L/T, lo que permite typecheck más estricto y consultas tipadas.

- **Tipos como datos**: el neo-davidsoniano hereda el problema del metanivel del cálculo de predicados (los predicados son metanivel). WQuestions lo evita reificando tipos en K.

- **Propósito**: teoría lingüística *vs* infraestructura de datos. Ambos pueden coexistir; WQuestions podría usar neo-davidsonian como capa de extracción desde texto.

## Qué tomar prestado

- **El inventario de roles temáticos — *ya adoptado en D7***: el catálogo Agent/Theme/Patient/Location/Time/Manner/Instrument/Goal/Source/Path/Beneficiary/Comitative/Cause/Purpose es la base directa del catálogo canónico de roles de WQuestions (D7). La traducción es casi literal:

  ```
  Agent       → agente / protagonista
  Patient     → paciente
  Theme       → tema, objeto_de
  Experiencer → experimentador
  Source      → origen           (de dónde)
  Goal        → destino          (hacia dónde)
  Path        → via              (por dónde)
  Location    → lugar_de         (dónde)
  Time        → momento          (cuándo)
  Instrument  → instrumento      (con cuál)
  Manner      → modo             (cómo)
  Beneficiary → beneficiario     (para quién)
  Comitative  → acompañantes     (con quién)
  Cause       → causado_por      (D6)
  Purpose     → con_finalidad    (D6, para qué)
  ```

  Esta es la **contribución más directa** de neo-davidsoniano a WQuestions: el vocabulario de etiquetas en P y M no es invención del proyecto sino herencia de 60 años de análisis lingüístico-formal.

- **Las técnicas de extracción semántica**: el pipeline AMR / Semantic Role Labeling es un puente natural texto→WQuestions.

- **El tratamiento de la modificación**: cómo neo-davidsonian maneja adverbios, intensificadores, negación — todo eso es relevante cuando WQuestions soporte modificadores de hechos.

## Qué NO tomar prestado

- **El compromiso con la lógica de predicados clásica**: WQuestions decidió ser un modelo de datos (conjuntos, tuplas), no una lógica con cuantificadores. La traducción es posible pero el formalismo primario es distinto.

- **El dominio único `Individual`**: WQuestions gana mucho con la disyunción de ejes; no merece la pena uniformarlos.

- **La centralidad de la composicionalidad lingüística**: WQuestions no necesita componer significados de oraciones; necesita almacenar y consultar hechos.

## La doble lectura: roles (D7) y verbo-como-signatura (sección 9)

Neo-davidsoniano aporta a WQuestions **dos contribuciones complementarias** que se leen como dos caras de la misma moneda:

1. **Catálogo de roles temáticos → D7** (catálogo canónico): ya documentado arriba. Es la cara *estática* — el vocabulario de etiquetas con que se conectan los participantes a un evento.

2. **El verbo como signatura de tipo → sección 9 de WQuestions.md** (frame "del lenguaje natural a los hechos"): la cara *dinámica*. Para cada verbo:

   ```
   Verbo → declara el tipo de evento (instancia_de en K)
         + declara qué roles temáticos espera
         + permite/exige ciertos modificadores
   ```

   Es decir, el verbo neo-davidsoniano funciona como la firma de una función:

   ```
   give(e) such that Agent(e, ?), Theme(e, ?), Recipient(e, ?)
   ```

   Lo que WQuestions formaliza como una entrada del lexicon:

   ```
   dar
     tipo_situacion: accion_dar
     obligatorios:   [agente, tema, beneficiario]
     opcionales:     [momento, lugar_de, instrumento, con_finalidad]
   ```

Esta doble lectura cierra el círculo: **D7 da el vocabulario de roles, y la sección 9 da el procedimiento para usar ese vocabulario cuando se parte de lenguaje natural**. Ambos son herencia directa del análisis neo-davidsoniano.

El artefacto concreto de esa síntesis es `lexicon.md` en la raíz del proyecto, que pobla incrementalmente la signatura neo-davidsoniana de los verbos del español que aparecen en los dominios modelados.

## Conclusión

La semántica neo-davidsoniana es el **formalismo lingüístico más cercano** al hecho atómico de WQuestions: ambos reifican el evento, ambos cuelgan participantes vía etiquetas, ambos permiten apertura sin tocar el verbo/predicado central. La diferencia clave es de propósito: neo-davidsoniano explica cómo significan los verbos del lenguaje natural; WQuestions especifica cómo se almacenan y consultan hechos del mundo.

Para WQuestions, neo-davidsoniano es **el donante natural de vocabulario para `P`** (los roles temáticos), de **la noción de verbo como signatura** (sección 9) y de **algoritmos de extracción** (Semantic Role Labeling). Si en algún momento construimos un ingestor texto→WQuestions, casi seguro pasará por una etapa neo-davidsoniana intermedia.
