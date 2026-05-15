# Teoría de situaciones — Barwise & Perry / Devlin

Documento de referencia sobre la teoría de situaciones, el ancestro filosófico-matemático más profundo de WQuestions y la formulación más explícita de "información como unidades estructuradas".

## Datos bibliográficos

- **Foundational**: Barwise, J. & Perry, J. (1983) — *Situations and Attitudes*. MIT Press.
- **Extensión matemática**: Barwise, J. & Etchemendy, J. (1987) — *The Liar*; Aczel, P. (1988) — *Non-well-founded Sets*.
- **Reformulación moderna y mejor expuesta**: Devlin, K. (1991) — *Logic and Information*; Devlin, K. (varios) — *Situation Theory and Situation Semantics*.
- **Enciclopedia**: Stanford Encyclopedia of Philosophy — *Situations in Natural Language Semantics*.

## Motivación declarada

Barwise y Perry rechazan la semántica de mundos posibles (Montague, Kripke) por ser demasiado abstracta y no captar dos fenómenos centrales del lenguaje:

1. **La información parcial**: los hablantes nunca describen "mundos completos"; describen fragmentos o **situaciones**.
2. **El contexto**: el significado de una expresión depende sistemáticamente de la situación en que se profiere.

Su propuesta es una teoría matemática general de la **información** entendida como flujo entre situaciones, no como verdad en mundos.

## Núcleo del framework

### Situaciones

Una **situación** `s` es una parte del mundo: limitada en espacio, tiempo y participantes. No es un "mundo posible" entero. El mundo real es la unión (no estructurada) de todas las situaciones reales.

### Infones

La unidad atómica de información es el **infón**, con la forma:

```
σ = << R, a₁, a₂, ..., aₙ ; i >>
```

donde:

- `M` es una relación de aridad `n`.
- `a₁, ..., aₙ` son los argumentos (individuos, ubicaciones, momentos, propiedades).
- `i ∈ {0, 1}` es la **polaridad** (1 = afirmativo, 0 = negativo).

Una situación `s` **soporta** un infón si el infón es información que la situación contiene:

```
s ⊨ σ
```

Ejemplo:

```
s ⊨ << durmiendo, juan, 3pm ; 1 >>
```

significa "en la situación s, es información que Juan está durmiendo a las 3pm".

### Tipos

Los objetos básicos se clasifican por **tipos** (TYPE):

- `IND` — individuos
- `LOC` — ubicaciones
- `TIM` — tiempos
- `REL` — relaciones
- `SIT` — situaciones (recursivo)
- `POL` — polaridades

Los tipos pueden ser primitivos o derivados (tipos de situación: "la situación de Juan durmiendo").

### Restricciones (constraints)

Las relaciones entre situaciones se rigen por **restricciones**, que dicen cosas como "siempre que ocurre una situación de tipo A, hay (o es probable que haya) una situación de tipo B". Son la base del flujo de información.

### Conjuntos no bien fundados

Para manejar autorreferencia (el mentiroso, situaciones que contienen información sobre sí mismas), Barwise y Aczel adoptan teoría de conjuntos **no bien fundados** (Antifoundation Axiom).

## Características clave

- **Información parcial**: las situaciones son fragmentos, no totalidades.
- **Polaridad explícita**: cada infón puede ser positivo o negativo.
- **Tipos como ciudadanos**: forman parte del vocabulario formal.
- **Restricciones como mecanismo causal**: el flujo de información se modela con reglas de inferencia entre tipos de situación.
- **Reificación radical**: las situaciones son objetos de primer orden, manipulables.

## Posicionamiento frente a WQuestions

| Aspecto | Barwise-Perry | WQuestions |
|---|---|---|
| Unidad atómica | Infón `<<M, a₁..aₙ; i>>` | Hecho `(s, etiqueta, v₁..vₙ)` |
| Polaridad | Explícita (1/0) | Implícita (hechos negativos requieren modelar) |
| Tipos | Sistema de tipos primitivos (IND, LOC, TIM, REL, SIT, POL) | Ejes (Q, O, L, T, N, K, P, M) |
| Situaciones | Primarias y recursivas | Primarias en O, recursivas |
| Restricciones / inferencia | Centrales | Pendientes de diseño |
| Apertura | Tipos abiertos | Ejes cerrados |
| Formalismo | Conjuntos (no bien fundados) | Conjuntos (clásicos por ahora) |
| Propósito | Filosofía de la información | Infraestructura de datos para IA |

## Convergencias importantes

- **El infón es esencialmente el hecho atómico de WQuestions** con polaridad añadida. La estructura es la misma: una etiqueta de relación con argumentos.

- **El paralelismo entre tipos**:

  ```
  Barwise-Perry          WQuestions
  ------------------     ------------------
  IND (individuos)       Q ∪ O (agentes y cosas)
  LOC (ubicaciones)      L
  TIM (tiempos)          M
  REL (relaciones)       P ∪ M
  SIT (situaciones)      T (subset: situaciones)
  POL (polaridad)        (no explícito todavía)
  ```

  WQuestions distingue Q de O y agrega N y K — refinamientos sobre el esquema de Barwise-Perry. Pero los ejes son herederos directos de los tipos básicos de la teoría de situaciones.

- **Reificación de la situación**: ambos tratan la situación como objeto manipulable, no como "contexto opaco".

- **Información parcial**: WQuestions también es "parcial" — uno puebla los hechos que conoce, no se asume mundo cerrado.

## Divergencias importantes

- **Apertura vs cierre de ejes**: Barwise-Perry deja los tipos abiertos (uno puede inventar tipos derivados). WQuestions cierra los ejes en 8 — apuesta más restrictiva.

- **Polaridad explícita**: Barwise-Perry distingue afirmar `σ` de afirmar `¬σ` con polaridad embebida. WQuestions lo deja sin resolver — actualmente todo hecho es afirmativo; los negativos habría que modelarlos como propiedades booleanas o reificar la negación.

- **Restricciones / inferencia**: la teoría de situaciones tiene una maquinaria formal para modelar cómo una situación implica información sobre otra (restricciones, condicionalidad). WQuestions todavía no tiene capa de inferencia formal — es una decisión pendiente.

- **Conjuntos no bien fundados**: Barwise/Aczel necesitan AFA para manejar autorreferencia (situaciones que contienen información sobre sí mismas). WQuestions actualmente no necesita ir tan lejos; la autorreferencia ocurre vía punteros (un hecho refiere a una situación por identidad), sin necesidad de cambiar la teoría de conjuntos base.

- **Propósito y audiencia**: filosofía / lógica matemática vs ingeniería de datos.

## Qué tomar prestado

- **La estructura del infón con polaridad**: añadir un campo de polaridad a cada hecho de WQuestions es una extensión natural y bien fundamentada. Permitiría representar negación sin reificar.

- **El sistema de tipos como guía**: la disyunción IND / LOC / TIM / REL / SIT valida la decisión de WQuestions de tener ejes disjuntos. Y sugiere que TIM (tiempos) merece eje propio, lo que ya está hecho en `T`.

- **El mecanismo de restricciones**: cuando WQuestions diseñe su capa de inferencia, las restricciones de Barwise-Perry son un modelo natural. Tienen 40 años de literatura formal detrás.

- **La noción de "soporte" (`s ⊨ σ`)**: WQuestions puede adoptar la relación de soporte como semántica formal de "qué hechos pertenecen a qué situación".

## Qué NO tomar prestado

- **La maquinaria de conjuntos no bien fundados**: salvo que aparezcan necesidades de autorreferencia genuina, complica más de lo que ayuda.

- **La apertura ilimitada de tipos**: WQuestions ya decidió cerrar los ejes; esa decisión es parte de su valor.

- **El bagaje filosófico**: temas como referencia directa, actitudes proposicionales, paradoja del mentiroso — interesantes pero ortogonales a la misión de WQuestions.

## Conclusión

La teoría de situaciones es el **antecedente conceptual más profundo** de WQuestions. El infón es prácticamente el hecho atómico; las situaciones son las situaciones de WQuestions; los tipos básicos prefiguran los ejes. Barwise y Perry construyeron en los 80 el aparato filosófico-matemático que WQuestions hoy intenta convertir en infraestructura de datos.

Para WQuestions, la teoría de situaciones es:

1. **Justificación filosófica**: el modelo no es ad hoc; tiene 40 años de pedigree formal.
2. **Donante de mecanismos**: polaridad, soporte, restricciones, tipos.
3. **Recordatorio de límites**: WQuestions toma decisiones más restrictivas (ejes cerrados, sin AFA) que la teoría general, y eso es deliberado — el costo es expresividad, el beneficio es operatividad.

Si en algún momento WQuestions necesita probar propiedades formales (consistencia, completitud, complejidad de consultas), la teoría de situaciones es el marco natural en el que hacerlo.
