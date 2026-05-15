# Capítulo 16 — Un servicio on-demand: el app de taxi

## El gesto que dispara una cadena

Valeria sale de un edificio en la plaza principal a las dos y media de la tarde, abre el app del servicio de taxis y toca el botón rojo. Treinta y cinco minutos después, está en el aeropuerto. Entre los dos momentos pasaron muchas cosas: el sistema buscó conductores cerca, asignó uno, ese conductor aceptó, condujo a la plaza, recogió a Valeria, manejó hasta el aeropuerto, llegó. Cada uno de esos eventos sucedió, fue registrado, dejó huellas, generó un cobro, eventualmente fue revisado por un equipo de soporte que respondió un reclamo.

Visto desde adentro, **un único viaje del app es una cadena de seis a siete situaciones distintas que se siguen unas a otras**, con agentes que entran y salen, con momentos cronometrados al segundo, con dependencias entre eventos que el sistema necesita preservar. El capítulo anterior modeló un negocio donde cada sesión era una única situación de cliente único en cámara única. Este capítulo cambia la escala: un viaje no es una situación — **es una secuencia**.

Para el modelo, la pregunta es: ¿cómo se ve esto cuando lo escribimos como hechos atómicos? Anticipando la respuesta — bien — vale la pena ver el detalle, porque tres cosas que el sauna no estresaba aparecen acá con fuerza: la **pluralidad de agentes**, el **encadenamiento de situaciones**, y la **causalidad emergente** del estado del mercado (el famoso *surge pricing*).

## Cuatro agentes en una sola transacción

Si uno se pregunta *"¿quién está participando del viaje?"*, la primera respuesta es Valeria. La segunda es Luis, el conductor que la lleva. Pero hay dos participantes más cuya agencia tiende a quedar invisible: **el app** (una pieza de software que toma decisiones autónomas) y **el vehículo** (un objeto físico que media la acción). Los cuatro están en escena. El modelo necesita poder hablar de cada uno.

Acá entra D5 — agencia contextual — en su forma más interesante. El app no es solo una herramienta: es **agente del verbo *asignar***. Es el app — no Valeria, no Luis — quien decide qué conductor recibe la solicitud. Esa decisión es una situación reificada cuyo agente es el software. El modelo lo refleja sin contorsiones:

```python
asig = ingest_situation(u, lex, "asignar", roles={
    "agente":       app,            # ¡APP COMO Q!
    "tema":         sol,            # asigna la solicitud previa
    "beneficiario": luis,           # al conductor disponible
    "instrumento":  vehiculo,       # con su vehículo
    "momento":      at(1),
}, sit_id="asig_001")
```

Cuatro participantes, cuatro roles distintos. El app entra al eje Q como un agente más — capaz de actuar, de tomar decisiones, de quedar como sujeto del verbo. El vehículo entra como instrumento (eje O — el objeto que media la acción). Y los dos humanos están en sus roles habituales: Valeria solicitó antes, Luis recibe la asignación como beneficiario.

![La asignación de un viaje involucra cuatro participantes con roles distintos: el app como agente (toma la decisión), el conductor como beneficiario, la solicitud previa como tema, el vehículo como instrumento. Tres viven en Q, uno en O.](../diagrams/png/30_asignacion_multi_agente.png)

Vale aclarar algo que el prototipo me obligó a notar: **el vehículo termina viviendo en O**, no en Q. La intuición *"el vehículo registra su ubicación, su agencia es como la de un sensor"* es real, pero la mayor parte del tiempo el vehículo aparece como objeto-instrumento, no como sujeto de la acción. Si alguna vez necesitamos hablar del vehículo *como agente* — *"el GPS del vehículo registró un giro brusco a las 14:42"* — podemos darle un identificador paralelo en Q (`gps_vehiculo_abc123 ∈ Q`) y conectarlo al vehículo físico con un rol de pertenencia. El modelo no fuerza un solo eje; permite la convivencia.

## La cadena de seis situaciones

El viaje de Valeria genera, en orden cronológico, seis situaciones reificadas:

```
solicitar  →  asignar  →  aceptar  →  recoger  →  trasladar  →  completar
   14:30      14:31      14:32      14:38       14:40         15:05
```

Cada flecha del esquema es una relación canónica explícita en el grafo: `precede` y su inversa `sigue_a` conectan cada situación con la siguiente. Esto es importante porque la cadena no vive solo en los momentos T (que también están), sino en las aristas del grafo. Una consulta tipo *"¿qué situación viene después de aceptar para este viaje?"* es un recorrido de un salto, no un cálculo de fechas.

Pero cronología no es lo único. Algunas situaciones se siguen porque están **motivadas** por las anteriores. La asignación no ocurre por casualidad después de la solicitud: ocurre **porque hubo solicitud**. Eso se expresa con `motivado_por`:

```
(asig_001, motivado_por, sol_001)
```

Y la recogida no es solo cronológicamente posterior a la aceptación: es **consecuencia** de ella. La aceptación crea una obligación que el conductor cumple recogiendo:

```
(rec_001, sigue_a,        acep_001)
(rec_001, motivado_por,   sol_001)    # último motivo upstream
```

Las dos relaciones — temporal y motivacional — coexisten sin pisarse. El sistema preserva ambas porque ambas tienen valor consultivo distinto. La temporal es útil para reconstruir el orden de eventos; la motivacional, para auditar por qué algo pasó.

![Las seis situaciones de un viaje encadenadas por `sigue_a` (temporal) y `motivado_por` (causal). El viaje completo vive como entidad superior que agrupa todo por `parte_de`.](../diagrams/png/29_cadena_viaje.png)

Sobre todo, vale la pena destacar la **entidad articuladora superior**. Las seis situaciones no flotan sueltas: todas son `parte_de` un mismo `viaje_001` reificado. El viaje completo es un O que las contiene a todas; consultar *"todo lo que ocurrió en el viaje de Valeria al aeropuerto"* es una proyección directa por `parte_de`:

```python
partes = [f.subject for f in u.facts_with_role("parte_de")
          if f.value.id == "viaje_001"]
# devuelve las 6 situaciones + la tarifa
```

Esa entidad articuladora es la unidad operativa del negocio: el viaje es lo que se factura, lo que se reembolsa, lo que se revisa cuando hay un reclamo, lo que se analiza para optimizar tiempos. El modelo le da identidad propia desde el primer hecho.

## Surge pricing: causalidad emergente

Hay una pieza del dominio que pone a prueba D6 — las cuatro relaciones del "por qué" — de una manera particularmente directa: el precio dinámico. Cuando hay alta demanda en una zona, la tarifa sube. El modelo necesita registrar **por qué** un viaje específico costó veinticinco dólares cuando el viaje equivalente del día anterior costó quince.

La opción ingenua es agregar un atributo `multiplicador_surge: 1.67` al pago. Funciona como dato pero pierde la explicación. La opción del modelo es **reificar el estado de mercado** que causó la tarifa elevada, y conectar tarifa a estado con `causado_por`:

```python
estado_demanda = u.add_individual(Individual(
    id="alta_demanda_2026_05_16_14_30", axis=Axis.O,
    label="alta demanda 16/5 14:30"))
u.assert_fact(estado_demanda, "instancia_de", alta_demanda)
u.assert_fact(estado_demanda, "lugar_de", plaza)
u.assert_fact(estado_demanda, "momento", at(0))

tarifa = u.add_individual(Individual(id="tarifa_viaje_001", axis=Axis.O))
u.assert_fact(tarifa, "instancia_de", category("tarifa"))
u.assert_fact(tarifa, "monto", n_25_usd)
u.assert_fact(tarifa, "causado_por", estado_demanda)
```

La diferencia es enorme cuando aparece una reclamación. Un usuario que escribe *"¿por qué me cobraron $25 hoy si normalmente cuesta $15?"* recibe una respuesta inmediata del grafo: la tarifa está causada por un estado de alta demanda con momento y lugar precisos. El cliente puede inspeccionar ese estado: cuándo empezó, cuándo terminó, cuántas solicitudes activas había. Sin reificación, esa explicación tendría que reconstruirse de logs sueltos; con reificación, es una consulta de dos saltos.

Lo mismo aplica a cualquier dominio donde el precio sea contextual: subastas, mercados volátiles, ventas con descuentos por temporada. La regla del modelo es la misma: **si el "porque" del precio importa, reificar la causa y conectarla con `causado_por`**.

## Cancelaciones, rectificaciones, modificaciones

Un dominio on-demand vive con cancelaciones constantes. Un usuario que solicita un viaje y se arrepiente; un conductor que acepta y luego declina; un viaje que el sistema cancela por zona insegura. La pregunta arquitectónica es: ¿qué hacemos con la situación cancelada? ¿La borramos? ¿La marcamos? ¿Le agregamos un campo?

La convención del modelo, vista en el capítulo 10 y validada acá, es **hechos inmutables**: nunca borrar, nunca sobreescribir. Una cancelación es **una situación nueva** que opera sobre la previa. El catálogo D7 trae el rol exacto para esto:

```python
canc = ingest_situation(u, lex, "cancelar", roles={
    "agente":   valeria,
    "tema":     viaje2,
    "momento":  at(62),
}, sit_id="canc_001")
u.assert_fact(canc, "cancela", viaje2)
u.assert_fact(viaje2, "estatus_factual", cancelado)
```

Dos hechos nuevos: la cancelación reificada (con agente, momento y motivo si lo hay), y la marca `estatus_factual: cancelado` sobre el viaje. El viaje original sigue ahí con todos sus hechos; lo que cambia es su estado. Cualquier consulta posterior sobre viajes activos filtra por `estatus_factual: real`; cualquier auditoría puede recuperar todo el rastro.

Para variantes — rectificación de un cobro, modificación de un destino — el catálogo trae `rectifica`, `modifica`. La forma estructural es siempre la misma: nueva situación que opera sobre la previa. El grafo se vuelve un registro contable inmutable, no una base de datos mutable.

## Consultas operativas

Tres consultas que un sistema de taxi necesita responder, traducidas a `Pattern` del prototipo:

**Consulta 1 — ¿Adónde llevó Luis a Valeria?**

```python
r = query(u, Pattern(
    fixed={"agente": luis, "paciente": valeria},
    ask={"destino": Var()},
    type_constraint=u.ind("accion_trasladar"),
))
# r[0]["destino"].id == "aeropuerto"
```

Una pregunta-WH directa. El motor encuentra las situaciones de `accion_trasladar` donde Luis es agente y Valeria es paciente, y proyecta sobre el rol `destino`.

**Consulta 2 — ¿Cuántos viajes completó Luis hoy?**

```python
n = count(u, Pattern(
    fixed={"agente": luis, "estatus_factual": completado},
    type_constraint=u.ind("viaje"),
))
```

Idéntica en estructura a la consulta de fidelidad del sauna. La uniformidad del modelo se cobra acá: el mismo código que cuenta sesiones de un sauna cuenta viajes de un conductor.

**Consulta 3 — ¿Por qué la tarifa fue $25?**

```python
explicaciones = u.facts_about(tarifa_viaje_001)
causa = [f for f in explicaciones if f.role == "causado_por"]
# causa[0].value.id == "alta_demanda_2026_05_16_14_30"
```

La auditoría de un cobro es un recorrido por relaciones canónicas. El sistema puede contestar al cliente, al regulador, al equipo de soporte interno, con la misma estructura.

## Lo que el taxi prueba que el sauna no

El sauna fue gentil. El taxi pone a prueba tres cosas distintas que merecen quedar dichas en limpio.

**Pluralidad de agentes y D5 al extremo.** El sauna tenía clientes, recepcionistas, masajistas — todos humanos, todos en Q sin discusión. El taxi tiene un *app* — software — que toma decisiones autónomas y aparece como agente del verbo `asignar`. Esto no rompe el modelo, lo consagra: D5 *agencia contextual* permite que cualquier entidad capaz de actuar — humana, algorítmica, organizacional — entre como sujeto de una situación cuando el contexto lo requiere. La maquinaria de consulta no distingue agentes humanos de agentes software; los trata uniformemente.

**Encadenamiento operativo.** El sauna tenía sesiones aisladas. El taxi tiene viajes que son cadenas de seis situaciones con dependencias cronológicas y motivacionales explícitas. Esto exigió ejercitar `precede`/`sigue_a`/`motivado_por` masivamente y reveló que la **entidad articuladora superior** (`viaje_001`) es indispensable: sin ella, las seis situaciones flotarían sin un nodo único al cual referirse al facturar, refundir o auditar.

**Causalidad emergente del estado de mercado.** El sauna tenía precios fijos. El taxi tiene precios que dependen del estado del entorno, y ese estado merece ser reificado. La pareja `(estado_demanda, tarifa, causado_por)` es la forma estándar de capturar contextualidad de precio sin enturbiar el hecho monetario.

El prototipo confirmó cinco validaciones automáticas: la app como agente de asignar, las seis situaciones parte_de viaje_001, la tarifa causada por la alta demanda, la cancelación que cambia `estatus_factual`, y la consulta WH que recupera el destino correcto. Cero parches al catálogo. Cero contorsiones de modelado.

## Lo que viene

El capítulo 17 cambia otra vez de dominio: una **historia clínica**. El cambio acá no es de complejidad operativa — la clínica tiene cadenas de eventos también — sino de **densidad semántica**. Un diagnóstico, una prescripción, una contraindicación, son objetos que cargan estructura intrínseca. La pregunta será si el modelo, hasta ahora probado en negocios comerciales, aguanta un dominio donde el contenido mismo de cada situación es lo más rico.
