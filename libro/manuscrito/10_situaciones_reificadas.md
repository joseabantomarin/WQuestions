# Capítulo 10 — Situaciones reificadas: los puntos articuladores

## Por qué algunas cosas merecen ser sustantivos

Hay una operación gramatical sutil que el español hace con extraordinaria facilidad: convertir un verbo en sustantivo. *Correr* se vuelve *la corrida*. *Vender* se vuelve *una venta*. *Operar* se vuelve *la operación*. *Decidir* se vuelve *la decisión*. *Componer* se vuelve *la composición*. Estos sustantivos no nombran objetos físicos como una taza o un coche; nombran **acciones, eventos o procesos** que adquirieron suficiente identidad como para hablar de ellos.

La transformación no es decorativa. Decir "*María vendió un libro a Juan*" o decir "*la venta de María a Juan ocurrió ayer y la registró el sistema 14*" significa cosas estructuralmente distintas. En la primera versión, la venta es un evento pasajero que la oración nombra. En la segunda, **la venta es una entidad** — tiene fecha, agente que la registró, identidad propia — y puede ser objeto de nuevas afirmaciones: se canceló, se rectificó, se devolvió.

Este paso — convertir un evento o acción en una entidad de primera clase con identidad propia — es lo que el modelo llama **reificación**. Y la entidad resultante es una **situación reificada**: un individuo en O que aloja los participantes, el momento, el lugar, el modo, la finalidad y todo lo demás que el evento tiene.

Las situaciones reificadas son **los puntos articuladores del grafo**: nodos donde múltiples hechos convergen porque hablan de lo mismo. Sin ellas, el modelo solo puede expresar tripletas simples. Con ellas, puede expresar cualquier cosa que el lenguaje natural describa, por compleja que sea.

Este capítulo se ocupa de cuatro preguntas: *¿cuándo conviene reificar?*, *¿cómo se ve una situación reificada por dentro?*, *¿cómo se modela su validez en el tiempo?* y *¿cómo se conectan unas con otras?*.

## La regla de oro: cuándo reificar

Una pregunta razonable que el lector probablemente trae desde capítulos anteriores: *¿toda relación entre cosas se reifica?* No. Reificar tiene un costo — multiplica entidades en el universo V, agrega un salto adicional en las consultas, exige asignar un identificador interno (UUID v7, en la implementación que propusimos). Si todo se reifica, el modelo se infla con objetos abstractos que no aportan información.

La regla de oro del modelo es: **reificar solo cuando se da al menos una de cuatro condiciones**.

1. **La relación tiene propiedades propias** que no caben en una tripleta plana — tiempo, lugar, modo, instrumento, agente adicional. Un gol no es solo `(messi, marca, gol_argentina)`; tiene minuto, asistente, pierna, ubicación del remate. Esas propiedades necesitan colgar de algún nodo. Reificar el gol da ese nodo.

2. **La relación es n-aria** (más de dos participantes con roles distintos). Una venta tiene vendedor, comprador, producto, monto, fecha. Como vimos en el capítulo 8, una tripleta plana solo retiene dos. La reificación es la forma estándar de modelar n-aridad sin abandonar la estructura de hechos atómicos.

3. **Hay que referirse a la relación misma** desde otro hecho. *"La venta fue anulada"*, *"el gol fue revisado por el VAR"*, *"el diagnóstico está siendo cuestionado"*. Si una relación es objeto de otra relación, necesita identidad — porque algo tiene que ser el sujeto del segundo hecho.

4. **El hecho cambia de valor en el tiempo** y hace falta preservar el historial. El "dónde vive Marta" cambia: hasta 2025 vivía en una ciudad, desde 2026 vive en otra. Si almacenamos solo el valor actual, perdemos el histórico. Si reificamos la situación de residencia con `inicio` y `fin`, lo conservamos. Este es el caso que llamamos **D9 — vigencia**, y volveremos sobre él en breve.

Si no se cumple ninguna de las cuatro, **no reifiques**. *"Juan mide 1.80"* como tripleta `(juan, estatura, 1.80)` está perfecto y vive en V sin inflar nada. Esto es lo que mantiene la limpieza algebraica del modelo sin sacrificar expresividad cuando hace falta.

## Anatomía de una situación reificada

Cuando una situación se reifica, ¿cómo se ve por dentro? Tomemos un caso concreto: la consulta médica de María Gonzales del 14 de mayo de 2026 con la Dra. Torres. La consulta es un evento complejo: tiene paciente, médico, fecha, lugar, motivo, mediciones, diagnóstico, prescripción, pago.

```
(consulta_2026_05_14) ∈ O
```

Ese sujeto, `consulta_2026_05_14`, es el punto articulador. Todos los hechos de la consulta cuelgan de él vía hechos atómicos.

```
(consulta_2026_05_14, instancia_de,   accion_consultar)        ∈ M(O, K)
(consulta_2026_05_14, agente,         dra_torres)              ∈ M(O, Q)
(consulta_2026_05_14, paciente,       maria_gonzales)          ∈ M(O, Q)
(consulta_2026_05_14, momento,        2026-05-14T10:30:00Z)    ∈ P(O, T)
(consulta_2026_05_14, lugar_de,       consultorio_03)          ∈ P(O, L)
(consulta_2026_05_14, motivo,         control_rutinario)       ∈ P(O, K)
(consulta_2026_05_14, diagnostico,    hipertension_grado_1)    ∈ P(O, K)
(consulta_2026_05_14, estatus_factual, real)                   ∈ P(O, K)
```

Ocho hechos atómicos. Cada uno se sostiene por sí solo; juntos describen la consulta. Y como `consulta_2026_05_14` tiene identidad propia, otras situaciones pueden referirla:

```
(prescripcion_017,  parte_de,        consulta_2026_05_14)      ∈ M(O, O)
(pago_001,          sobre_situacion, consulta_2026_05_14)      ∈ M(O, O)
(control_futuro_001, prevista_por,   consulta_2026_05_14)      ∈ M(O, O)
```

La prescripción, el pago y el control futuro son cada uno **sus propias situaciones reificadas**, conectadas a la consulta original por relaciones canónicas. El grafo crece naturalmente: situaciones reificadas conectadas por relaciones reificadas, sin que la forma del hecho atómico cambie nunca.

![Anatomía de una situación reificada: la consulta médica como nodo central con todos sus participantes, momentos, lugares y propósito colgando como hechos atómicos. Las situaciones derivadas (prescripción, pago, control) se conectan al nodo por relaciones canónicas.](../diagrams/png/17_situacion_reificada.png)

## Estatus factual: situaciones que no han ocurrido todavía

Una situación reificada no necesariamente describe algo que **ya pasó**. Puede describir algo que está planeado, algo que se esperaba pero se canceló, algo hipotético, algo cuestionado. El modelo necesita poder distinguir estos modos sin tener que duplicar etiquetas (`agente` vs `agente_planeado`, `momento` vs `momento_planeado`).

La convención que emergió de las pruebas de dominio — particularmente en historia clínica y en contratos — es marcar la situación con una propiedad explícita de **estatus factual**:

```
estatus_factual : O → K
  valores: real | planeado | confirmado | hipotético | cancelado | rectificado
```

Una consulta médica programada para el mes próximo se modela igual que una consulta real, pero con `estatus_factual: planeado`. Si el paciente la cumple, se crea una *nueva* situación con `estatus_factual: real` y se la conecta con `(real_001, cumple, planeada_001)`. Si la cancela, se agrega `(planeada_001, estatus_factual, cancelada)` o, mejor, se crea una situación de cancelación que apunta a la planeada.

```
(control_futuro_001) ∈ O
  instancia_de    : accion_consultar
  agente          : dra_torres
  paciente        : maria_gonzales
  momento         : 2026-06-04T10:00:00Z
  estatus_factual : planeado                    ← clave
  prevista_por    : consulta_2026_05_14
```

Esta convención preserva la **inmutabilidad** de los hechos pasados — un hecho real registrado no se reescribe — y permite, al mismo tiempo, modelar la red de expectativas, intenciones y planes que orbitan toda actividad humana real.

## Vigencia y D9: propiedades que cambian en el tiempo

Llegamos a una de las decisiones de diseño más sutiles del modelo. Algunas propiedades no son fijas. La dirección de Marta cambia cuando se muda. El monto de la renta cambia cuando se aplica el reajuste por IPC. El medicamento que toma un paciente cambia cuando el médico ajusta el tratamiento. El precio de un producto cambia con la inflación. Si estas propiedades se almacenaran como tripletas planas, el histórico se perdería: al guardar el valor nuevo, el viejo desaparecería.

El modelo resuelve esto con **D9 — vigencia temporal mediante reificación**.

> **D9 — Las propiedades que cambian en el tiempo se reifican como situaciones con `inicio` y `fin` (o `valido_desde` y `valido_hasta`), no se almacenan como atributos directos del sujeto.**

En lugar de:

```
(marta, vive_en, ciudad_a)    ← se sobreescribe cuando se muda
```

Se modela:

```
(residencia_001) ∈ O
  sujeto         : marta
  ciudad         : ciudad_a
  inicio         : 2010-03-15
  fin            : 2025-12-31

(residencia_002) ∈ O
  sujeto         : marta
  ciudad         : ciudad_b
  inicio         : 2026-01-01
  fin            : null          ← vigencia actual
```

Cualquier consulta sobre "dónde vive Marta" se vuelve una consulta tipo *"residencia con sujeto=marta, vigente en el momento X"*. El motor recupera la situación cuya `inicio ≤ X ≤ fin` (o `fin = null`). Si X es 2024, devuelve `ciudad_a`; si X es hoy, devuelve `ciudad_b`.

![D9 en acción: una propiedad que cambia en el tiempo se modela como una sucesión de situaciones reificadas, cada una con su rango de vigencia. La consulta temporal recupera la situación válida en el momento solicitado.](../diagrams/png/18_d9_vigencia.png)

La ganancia es enorme y se ve mejor con consultas reales. Preguntas como *"¿qué medicamentos tomaba el paciente en marzo de 2024?"*, *"¿cuál era el monto de la renta cuando se firmó el aviso de desalojo?"*, *"¿qué versión del modelo GPT se usaba el día de la decisión?"* se vuelven triviales. Sin D9, son imposibles sin un journal aparte.

La regla práctica para decidir si una propiedad merece D9: **¿necesito alguna vez saber su valor en un momento pasado?** Si sí, reificar con vigencia. Si no — si solo importa el valor actual y reescribir el anterior es seguro —, propiedad simple.

## Cómo se conectan las situaciones entre sí

Las situaciones reificadas no viven aisladas. Se conectan unas con otras por un conjunto pequeño de relaciones canónicas que el modelo provee de fábrica.

**`parte_de`** y su inversa **`contiene`**: la situación menor pertenece a la mayor. Una jugada es parte de un partido. Una prescripción es parte de una consulta. Un movimiento contable es parte de una venta.

```
(gol_001,         parte_de, partido_arg_per_2026)
(prescripcion_017, parte_de, consulta_2026_05_14)
```

**`precede`** y su inversa **`sigue_a`**: una situación ocurre antes de otra, con orden lógico aunque no necesariamente temporal estricto.

```
(examen_001,    precede, diagnostico_001)
(diagnostico_001, precede, prescripcion_001)
```

**`causado_por`**, **`motivado_por`**, **`con_finalidad`**, **`justificado_por`**: las cuatro relaciones canónicas de "por qué", que conectan situaciones por causalidad, motivo, propósito o justificación normativa. Veremos estas en detalle en el próximo capítulo.

**`cumple`**, **`cancela`**, **`modifica`**, **`rectifica`**: una situación nueva opera sobre una previa. El pago cumple la obligación. La cancelación deja sin efecto la reserva. La rectificación corrige el comprobante.

```
(pago_renta_julio,    cumple,  obligacion_renta_julio)
(cancelacion_001,     cancela, reserva_017)
(boleta_rectificativa_007, rectifica, boleta_007)
```

Con este pequeño catálogo de relaciones inter-situacionales, el grafo entero del sistema se vuelve un **grafo de situaciones** densamente interconectado. Cada situación es un nodo; cada relación canónica es una arista. Y el formato — tripletas atómicas con signatura — es siempre el mismo.

## Reificación como continuo

Una observación que conviene hacer explícita. Reificar no es una decisión binaria entre "sí" y "no": es un continuo de **resolución**. Un mismo fenómeno del mundo puede modelarse a distintos niveles de detalle según lo que el sistema necesite.

Tres niveles ascendentes de resolución para el "consumo eléctrico mensual de un edificio":

**Nivel 1 — tripleta plana.**
```
(edificio_017, consumo_octubre, 1240)    ∈ P(O, N)
(edificio_017, unidad_consumo,  kWh)     ∈ P(O, K)
```
Suficiente si solo importa el total.

**Nivel 2 — medición reificada.**
```
(consumo_oct_017) ∈ O
  edificio   : edificio_017
  cantidad   : 1240
  unidad     : kWh
  periodo    : 2026-10
  medido_por : empresa_distribuidora
```
Necesario si hay que conocer el medidor, el período exacto, la fuente.

**Nivel 3 — consumos discriminados.**
```
(consumo_oct_017) ∈ O
  edificio    : edificio_017
  total       : 1240 kWh
  ...

(consumo_oct_017_dia_03) ∈ O    ← parte_de consumo_oct_017
  fecha    : 2026-10-03
  cantidad : 42 kWh
  ...
```
Necesario si hay que detectar picos diarios o aplicar tarifas horarias.

Cada nivel **es legítimo**. La elección depende del uso. Y — esta es la propiedad valiosa — pasar de un nivel a otro **no rompe el modelo**: simplemente se agregan más hechos atómicos sobre nuevas situaciones reificadas. Las consultas más simples siguen funcionando; las más detalladas se vuelven posibles.

## Lo que viene

Las situaciones reificadas son los puntos articuladores del grafo. Pero entre ellas hay un tipo particularmente importante de conexión que merece su propio capítulo: las relaciones de "por qué". *Causado por*, *motivado por*, *con finalidad*, *justificado por*. Estas cuatro relaciones canónicas son las que permiten que el grafo no sea solo una colección de hechos, sino una **explicación**: una estructura donde unos eventos dan razón de otros.

Es lo que el capítulo 11 — el último de la Parte III — desarrolla.
