# Capítulo 15 — Modelando un negocio completo: el caso de un sauna

## La Parte V empieza con código

Hasta acá el libro fue conceptual. Cada decisión de diseño se explicó con ejemplos puntuales — *Marta vende un libro*, *Ana ingresa a la cámara de vapor*, *Carlos cambia de ciudad* — pero ningún dominio se modeló de extremo a extremo. La Parte V cambia eso. Cada capítulo de esta parte toma un dominio completo y muestra cómo el modelo lo absorbe en su totalidad, con sus particularidades y sus zonas grises, **con código real que el lector puede ejecutar**.

El prototipo en Python que acompaña al libro vive en `prototipo/` y se corre con un comando. No es una biblioteca de producción — es una implementación honesta de unos 2.250 líneas que valida lo que el libro afirma del modelo. Cada concepto introducido hasta acá (las ocho coordenadas, los hechos atómicos, las situaciones reificadas, el catálogo D7, el lexicon, D9, las relaciones del "por qué") existe en el código y se ejercita con tests.

Para abrir la Parte V elegí un caso que es a la vez familiar y completo: un **sauna comercial de barrio**. Un negocio chico, accesible, donde el lector entiende el dominio sin explicación previa, pero que cruza casi todas las dimensiones del modelo. El sauna tiene clientes (Q), sesiones (O), cámaras y duchas (L), horarios (T), precios y temperaturas (N), categorías de servicio (K), promociones, planes mensuales, un programa de fidelidad, consumibles vendidos, recomendaciones del local, y propiedades que evolucionan en el tiempo. En un solo dominio aparecen casi todas las herramientas que la Parte II y III introdujeron.

A lo largo del capítulo iremos construyendo el modelo en paralelo con el código del prototipo. Al final, el lector tendrá una base ejecutable que puede modificar, extender y atacar con sus propias consultas.

## El negocio en una página

El **Sauna Oasis** opera una sede con dos cámaras de vapor y una cámara seca, todas a unos sesenta grados centígrados. Los clientes ingresan por sesión a un costo de veinte dólares. La recomendación del local es estar veinte minutos por cada cámara y terminar con una ducha fría — una ducha "española" que, dicen los habitués, produce satisfacción y relajamiento profundos.

Junto al servicio principal hay un programa de fidelidad: por cada siete sesiones, una gratis. Hay promociones combinadas: sauna más masaje, sauna más gimnasio, sauna más una jarra de agua de cebada. Hay un plan mensual de gimnasio que incluye dos sesiones de sauna por semana. Dentro de las instalaciones se venden jugos, ensaladas de frutas y helados, lo que hace de la experiencia algo parecido a estar en la playa.

Tres clientes recurrentes — Ana, Beto, Carlos — definirán los casos de prueba. Cada uno usa el sauna de una manera distinta y nos sirve para ejercitar facetas distintas del modelo.

## Mapeo a los seis ejes de valor

El primer paso al modelar un dominio es ubicar sus entidades en los ejes correctos. Esta no es una operación trivial: muchas confusiones de modelado nacen de poner una entidad en el eje equivocado. Para el sauna:

**Q (quién).** Los agentes humanos del negocio: clientes (*Ana*, *Beto*, *Carlos*), recepcionistas (*Anita*), masajistas, instructores de gimnasio. El **Sauna Oasis** como persona jurídica también es Q — el negocio mismo es un agente.

**O (qué).** Las entidades situadas o evento-como del modelo:
- Las **sesiones** individuales (`sesion_ana_01`, `sesion_ana_02`, ...).
- Los **pagos**, **promociones aplicadas**, **redenciones de beneficio**.
- Las **ofertas comerciales** del negocio reificadas (un *plan mensual* es una oferta concreta, no una categoría abstracta — vive en O).
- Las **recomendaciones del local** como reglas reificadas.
- Las **residencias** de los clientes (cuando importa el histórico).

**L (dónde).** El local central, las dos cámaras de vapor, la cámara seca, las duchas. Curiosamente, las cámaras viven a la vez en O (objetos físicos con mantenimiento, capacidad, temperatura) y en L (lugares de las sesiones). El modelo no obliga a elegir — el mismo individuo puede usarse en ambos roles, y la consulta distingue por rol no por eje.

**T (cuándo).** Momentos puntuales (`2026-04-22T18:30Z`), rangos (la semana del 20 al 26 de abril), intervalos del plan mensual.

**N (cuánto).** Los veinte dólares de la sesión, los sesenta grados de la cámara, los veinte minutos recomendados, el conteo de 7 visitas para el beneficio. Cada N va siempre acompañado de su unidad K.

**K (clase).** El zócalo categórico, denso en este dominio:
- Tipos de servicio: `servicio_sauna`, `servicio_gimnasio`, `servicio_masaje`.
- Tipos de cámara: `tipo_camara_vapor`, `tipo_camara_seca`.
- Estados de sesión: `iniciada`, `en_curso`, `finalizada`, `cancelada`.
- Estados modales: `real`, `intencionado`, `previsto`, `no_realizable`.
- Modalidades: `volitiva`, `deóntica`, `alética`, `epistémica`.
- Unidades QUDT: `Currency:USD`, `Temperature:Cel`, `Time:Minute`.

![Mapa del dominio sauna sobre los seis ejes de valor: clientes y personal en Q, sesiones y planes en O, cámaras y duchas en L, momentos en T, precios y temperaturas en N, tipos y estados en K. Los conectores P/M no se muestran — son los predicados que llenan los hechos atómicos.](../diagrams/png/27_mapa_sauna.png)

## La sesión: la situación articuladora

Si una sola entidad fuese el centro del grafo, sería la **sesión**. Todo lo demás cuelga de ella: el cliente que la toma (`cliente`), la cámara donde ocurre (`lugar_de`), el inicio y fin (`inicio`, `fin`), el pago asociado (parte_de), la promoción que la cubre (`parte_de`), la ducha posterior (parte_de), la satisfacción que produce (causado_por). Una sesión típica de Ana en el modelo se ve así:

```
(sesion_ana_07) ∈ O
  instancia_de    : servicio_sauna
  cliente         : ana                              ∈ M(O, Q)
  lugar_de        : camara_vapor_1                   ∈ P(O, L)
  inicio          : 2026-04-22T18:00Z                ∈ P(O, T)
  fin             : 2026-04-22T18:40Z                ∈ P(O, T)
  estatus_factual : finalizada                       ∈ P(O, K)
```

En el prototipo esto se construye con una llamada de seis líneas:

```python
sit = ingest_situation(u, lex, "tomar",
    roles={
        "cliente":  ana,
        "lugar_de": camara_vapor_1,
        "inicio":   t_inicio,
        "fin":      t_fin,
    },
    complements=["sesion"],          # dispara polisemia
    extra={"estatus_factual": finalizada},
    sit_id="sesion_ana_07",
)
```

`ingest_situation` hace exactamente lo que el capítulo 12 describe: resuelve el lexicon (con `complements=["sesion"]` para distinguir *tomar una sesión* de *tomar el pelo*), reifica la situación, asienta `instancia_de`, y aplica cada rol como hecho atómico validando contra el catálogo D7. Si pasáramos `lugar_de` con un valor en Q (un humano), la signatura del catálogo lanzaría `SignatureError` antes de almacenar el hecho.

## El lexicon del sauna

El lexicon del sauna registra siete verbos, lo suficiente para cubrir todas las situaciones del negocio. Tres llaman la atención por su tratamiento de polisemia:

```python
lex.register(LexiconEntry(
    verb="tomar",
    situation_type="servicio_sauna",
    obligatory=["cliente", "lugar_de"],
    pattern=("sesion",),                  # dispara cuando el complemento es "sesion"
))

lex.register(LexiconEntry(
    verb="tomar",
    situation_type="accion_bromear",
    obligatory=["agente", "paciente"],
    pattern=("el_pelo",),                 # locución idiomática
))

lex.register(LexiconEntry(
    verb="tomar",
    situation_type="accion_tomar",
    obligatory=["agente", "tema"],
    notes="genérico — recibir/asir",
))
```

Cuando alguien dice *"Ana tomó una sesión"*, el parser pasa `complements=["sesion"]`, el lexicon elige la primera entrada y la situación queda tipada como `servicio_sauna`. Cuando alguien dice *"la doctora le tomó el pelo al residente"* (frase que un médico podría escribir en un informe distinto), el complemento `el_pelo` dispara la segunda entrada. Cuando alguien dice *"Ana tomó la toalla"*, ningún patrón específico aplica y cae el genérico.

El dialecto de dominio extiende esto con aliases del negocio:

```python
lex.register_domain_dialect("sauna_oasis", {
    "cliente":         "agente",
    "sesion":          "servicio_sauna",
    "plan_mensual":    "contrato_servicio",
    "sesion_gratuita": "beneficio_fidelidad",
})
```

Esto habilita que el personal del Sauna Oasis hable y escriba con su vocabulario habitual ("cliente", "plan mensual", "sesión gratuita") sin tener que recordar los nombres canónicos. La traducción ocurre en la capa del lexicon, transparente al motor.

## Tres consultas reales

El valor de un modelo se mide cuando se le piden cosas. Veamos tres consultas que el negocio necesita responder y cómo el prototipo las resuelve.

**Consulta 1 — ¿Cuántas sesiones lleva Ana este mes?**

```python
n = count(u, Pattern(
    fixed={"cliente": ana, "estatus_factual": finalizada},
    type_constraint=u.ind("servicio_sauna"),
))
# n == 8
```

El patrón fija dos roles (cliente y estatus_factual), restringe el tipo a `servicio_sauna`, y cuenta cuántas situaciones del universo lo satisfacen. No hace falta tabla intermedia, no hace falta SQL personalizado. La consulta es la misma forma que la que respondería *"¿cuántas consultas atendió la doctora Torres este mes?"* en un sistema clínico, o *"¿cuántos viajes hizo José por la aerolínea X este año?"* en un sistema de viajes. La uniformidad del modelo hace que el código sea reutilizable.

**Consulta 2 — ¿Ana califica para el beneficio?**

```python
qualifies = n >= 7
# True
```

La regla del negocio — *siete visitas dan derecho a una gratis* — es declarativa y se evalúa contra el conteo. El modelo no la dispara solo; un evaluador externo (en este caso una línea de código) toma el resultado y decide. Si la regla fuera más compleja — *siete visitas en los últimos noventa días, exceptuando las redimidas por planes mensuales* — el evaluador la encapsula y el modelo sigue almacenando los hechos planos que necesita.

**Consulta 3 — ¿Dónde vivía Carlos en 2022?**

```python
res_2022 = query(u, Pattern(
    fixed={"agente": carlos},
    ask={"lugar_de": Var()},
    type_constraint=u.ind("residencia"),
), at=datetime(2022, 6, 1, tzinfo=timezone.utc))
# res_2022[0]["lugar_de"].id == "ciudad_a"

res_2027 = query(u, ..., at=datetime(2027, 6, 1, tzinfo=timezone.utc))
# res_2027[0]["lugar_de"].id == "ciudad_b"
```

Esta es D9 en acción. La residencia de Carlos cambia en enero de 2026 — de ciudad_a a ciudad_b. El grafo tiene dos `residencia` reificadas con rangos de vigencia distintos. La misma consulta, parametrizada por `at`, devuelve la respuesta correcta para cualquier momento del pasado o el presente. El sistema nunca olvida; el sistema responde lo que estaba vigente cuando se le pregunta.

![Una consulta WH como recorrido del grafo: el patrón fija dos roles, restringe por tipo, y proyecta sobre el rol pregunta. El motor recorre los hechos atómicos y agrega resultados.](../diagrams/png/28_query_trace.png)

## Cadenas causales en el negocio

Una de las cosas más útiles del modelo en un negocio real es poder reconstruir el "por qué" de cualquier evento. En el sauna esto aparece en dos momentos:

**La causalidad física del bienestar.** Ana se ducha en frío al final de su sesión; según la recomendación del local, esto produce satisfacción. En el modelo:

```
(ducha_ana_001, instancia_de,   accion_ducharse)
(ducha_ana_001, agente,         ana)
(ducha_ana_001, calificacion,   fria)
(ducha_ana_001, parte_de,       sesion_ana_08)
(ducha_ana_001, justificado_por, recomendacion_ducha_fria)

(satisfaccion_ana_001, instancia_de,    estado_subjetivo)
(satisfaccion_ana_001, experimentador,  ana)
(satisfaccion_ana_001, calificacion,    alta)
(satisfaccion_ana_001, causado_por,     ducha_ana_001)
```

Dos relaciones del "por qué" sobre la misma ducha: la cosa la **causó** (satisfacción → causado_por → ducha) y la cosa la **justificó** (ducha → justificado_por → recomendación). La diferencia semántica entre causalidad y justificación se preserva, como el capítulo 11 lo argumentó.

**El motivo de un cliente que no llegó a contratar.** Ana quería contratar el plan mensual pero todavía no pudo:

```
(intencion_ana_001, instancia_de,    contrato_servicio)
(intencion_ana_001, cliente,         ana)
(intencion_ana_001, tema,            plan_gym_mensual_offering)
(intencion_ana_001, modalidad,       volitiva)
(intencion_ana_001, estatus_factual, intencionado)
```

Una sola situación reificada, con `modalidad: volitiva` y `estatus_factual: intencionado` que la marcan como **deseo, no contrato real**. Cuando el negocio consulta "¿qué clientes tienen plan mensual activo?", filtra por `estatus_factual: real` y la intención de Ana queda fuera. Cuando consulta "¿qué clientes mostraron interés en el plan?", filtra por `estatus_factual: intencionado` y aparece. El mismo grafo, dos preguntas distintas, ninguna confusión.

## La pieza que falta: el evaluador externo

Lo que el modelo **no** hace por sí mismo, y conviene explicitar, es disparar las reglas. El conteo "siete visitas → una gratis" se evalúa con código aplicación. La verificación "este cliente excedió las dos sesiones semanales de su plan" se hace con una función que cuenta. La generación del beneficio cuando se cumple la condición tampoco es automática.

Lo que el modelo sí hace es **preservar todas las premisas en forma consultable**. La regla puede reificarse como una situación de tipo `regla` con condición, consecuente, vigencia y emisor. Los hechos atómicos que la regla evalúa están todos ahí. El evaluador externo — escrito como código Python, o como una llamada a un LLM con function calling, o como una rutina de un motor de inferencia — opera sobre la base que el modelo provee.

Esto es deliberado. WQuestions es una **arquitectura de información**, no un motor de razonamiento. El razonamiento se construye encima — y eso es bueno, porque distintos negocios necesitan distintos motores: SHACL para validación, Datalog para inferencia simbólica, código aplicación para reglas de negocio simples, LLM con catálogo de funciones para razonamiento difuso. El modelo soporta a todos sin acoplarse a ninguno.

## Lo que el sauna prueba

Cerremos el capítulo enumerando qué quedó validado, ya no en pizarra sino en código corriendo:

- **8 ejes de valor** en uso simultáneo: Q (4 personas), O (32 situaciones), L (7 lugares), T (43 momentos), N (8 magnitudes), K (17 categorías), más roles P y M en cada hecho.
- **184 hechos atómicos** describen un mes de operación con tres clientes recurrentes — un orden de magnitud menor de lo que un schema relacional ad-hoc requeriría para la misma información.
- **Diez validaciones automáticas** pasan: conteo de fidelidad, separación entre intención y contrato real, cadenas causales, polisemia, nominalización, D9 sobre residencia, sesiones cubiertas por plan, plan-como-oferta reificada.
- **Cero parches al catálogo**. El dominio se modela íntegro con los 38 roles canónicos más los roles de dominio que la política liberal admite sin tocar el catálogo D7.

El próximo capítulo cambia el dominio: un **servicio on-demand** — el clásico app de taxi — donde la concurrencia, los estados encadenados y la agencia repartida entre humano, app y vehículo (D5) ponen al modelo bajo otra clase de presión. El sauna fue gentil; el taxi pondrá a prueba la pluralidad de agentes y la dependencia temporal entre situaciones.
