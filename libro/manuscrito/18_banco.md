# Capítulo 18 — El dominio más exigente: un banco

## Por qué el banco es el caso límite

Una empresa cualquiera tiene quizás un schema relacional con ciento cincuenta tablas, un par de sistemas legacy, un par de integraciones externas. Un banco regional típico — el tamaño de una financiera con presencia en una capital y dos o tres ciudades del interior — tiene mil quinientas tablas en el core bancario, otro tanto en los sistemas de tarjetas, otro tanto en los de seguros, otro tanto en los de prevención de fraude, más una docena de aplicaciones satélites: originación de créditos, cobranza, contabilidad, regulatorio, riesgo, *digital banking*, billeteras, agencias corresponsales. Cada sistema con su schema; cada schema con su gobierno; cada cruce entre dos sistemas con su proyecto de integración.

Si el sauna era un negocio pequeño donde el modelo se entrenó liviano, y el taxi un servicio operativo con concurrencia, **el banco es el caso donde el modelo se gana o pierde su pretensión de utilidad real**. Es el dominio que más cuesta mantener en arquitecturas tradicionales, y por ende donde el ahorro de adoptar una arquitectura unificada es mayor. Es también el dominio donde la mayoría de las decisiones del libro — bitemporalidad (D9), reificación de situaciones, agencia contextual (D5), relaciones del "por qué" (D6) — pasan de ser elegantes a ser **exigencias regulatorias**.

Este capítulo no pretende modelar un banco completo. Pretende mostrar, sobre un puñado de casos seleccionados, cómo el modelo absorbe la complejidad específica del dominio bancario: las **operaciones con múltiples agentes y contrapartida contable**, el **ciclo de vida de un préstamo con cambios a lo largo del tiempo**, las **investigaciones de fraude que reconstruyen el pasado**, los **productos bancarios como ofertas reificadas**. Cada caso ilustra una arista; el conjunto dice si el modelo aguanta o no.

## Un mapa del dominio

Lo primero al abordar un banco es resistir la urgencia de bajar a detalle. El alto nivel importa porque el banco tiene **muchas familias de entidades a la vez**:

**Q — agentes.** Tres clases bien distintas. (1) Personas físicas: clientes retail, empleados, ejecutivos de cuenta. (2) Personas jurídicas: empresas clientes, corresponsales, regulador, procesadores (Visa, Mastercard), partners. (3) Sistemas con agencia (D5): el motor de scoring, el sistema antifraude, los autorizadores de tarjeta, los robots de cobranza. Los tres tipos entran a Q sin distinción especial — el modelo trata uniformemente a un humano y a un autorizador automático.

**O — entidades situadas.** Acá está el grueso del dominio. (1) Cuentas: corrientes, ahorros, plazo fijo, cuenta sueldo, cuenta corporativa, cuenta en moneda extranjera. (2) Productos crediticios: préstamos personales, hipotecarios, vehiculares, tarjetas de crédito, líneas comerciales, créditos por planilla. (3) Movimientos: cada depósito, retiro, transferencia, pago, cargo, abono. (4) Asientos contables: cada movimiento operativo tiene su contrapartida en cuentas de balance. (5) Productos como ofertas reificadas: *"Tarjeta Visa Platinum"*, *"Préstamo Hipotecario Tasa Fija 15 años"* — son entidades del catálogo comercial del banco, no categorías abstractas. (6) Investigaciones de fraude, reclamos, gestiones de cobranza, ajustes contables.

**L — lugares.** Sedes (casa matriz, sucursales urbanas, agencias del interior), ATMs, canales digitales (web banking, mobile, USSD), puntos de venta (POS) de la red. Cada operación tiene un canal — y eso es L. Un préstamo desembolsado en sucursal vs uno originado por web banking son operativamente distintos.

**T — momentos.** Triple registro: el momento del evento operativo (cuándo ocurrió la transacción en la realidad), el momento del registro contable (cuándo se asentó), el momento de cierre (cuándo se cerró el período). La diferencia entre los tres es lo que la auditoría interna persigue.

**N — cantidades.** Importes en distintas monedas, tasas, plazos, scores de riesgo. Cada N con su unidad K — y acá las unidades son críticas: confundir USD con EUR es el equivalente bancario al *Mars Climate Orbiter* citado en el capítulo 6.

**K — categorías.** El catálogo es enorme: tipos de cuenta, tipos de movimiento contable (códigos de transacción), monedas, segmentos de cliente, grados de riesgo, niveles de KYC, estados de un préstamo (vigente, mora, judicializado, castigado), códigos regulatorios. La política liberal del modelo brilla acá: cada banco extiende K con sus propias categorías sin tocar el catálogo D7.

![El dominio bancario sobre los ejes de valor: tres clases de agentes en Q, seis familias de entidades en O, multi-canal en L, tiempos triplemente registrados en T, importes y tasas en N, un catálogo K extenso. Los predicados P y M cablean todo.](../diagrams/png/41_mapa_banco.png)

## Caso 1 — Una transferencia con cinco agentes y dos contrapartidas contables

Una operación bancaria aparentemente trivial — *"Ana le transfiere $500 a Beto desde su cuenta de ahorros"* — es la oportunidad perfecta para ver cuántos participantes y dimensiones cruza un solo movimiento. Reificado:

```
(transferencia_001) ∈ O
  instancia_de:        accion_transferir
  agente:              ana                       ← cliente origen
  beneficiario:        beto                      ← cliente destino
  cuenta_origen:       cta_ana_001               ← O
  cuenta_destino:      cta_beto_007              ← O
  monto:               n_500_usd                 ← N
  unidad:              Currency:USD              ← K
  momento:             2026-06-12T14:32Z
  lugar_de:            web_banking               ← L (canal)
  estatus_factual:     ejecutada
  parte_de:            sesion_web_ana_001        ← contexto operativo
```

Cinco agentes implicados aunque solo dos aparecen como roles directos:

1. **Ana** — agente que inicia (`agente`).
2. **El sistema web banking** — agente que autoriza la sesión y la operación (rol de dominio `autorizador`).
3. **El motor antifraude** — agente que evaluó la operación antes de ejecutarla (rol `verificado_por`).
4. **Beto** — beneficiario que recibe.
5. **El banco mismo (jurídico)** — agente que asienta contablemente la operación.

La transferencia es una situación; pero **genera dos asientos contables** como sub-situaciones:

```
(asiento_debito_001) ∈ O                           // débito en cta_ana_001
  instancia_de:    asiento_contable
  parte_de:        transferencia_001
  cuenta_contable: ahorros_ana
  monto:           500
  unidad:          USD
  tipo_movimiento: debito
  momento:         2026-06-12T14:32:04Z            // momento contable

(asiento_credito_001) ∈ O                          // crédito en cta_beto_007
  instancia_de:    asiento_contable
  parte_de:        transferencia_001
  cuenta_contable: ahorros_beto
  monto:           500
  unidad:          USD
  tipo_movimiento: credito
  momento:         2026-06-12T14:32:04Z
```

La transferencia operativa y los dos asientos contables son **tres situaciones distintas** ligadas por `parte_de`. La operativa tiene los participantes humanos; los asientos tienen las cuentas contables. **La consulta de auditoría** *"¿qué movimientos contables corresponden a esta transferencia?"* es un recorrido directo por `parte_de`:

```python
asientos = [f.subject for f in u.facts_with_role("parte_de")
            if f.value.id == "transferencia_001"
            and f.subject.label.startswith("asiento_")]
# devuelve [asiento_debito_001, asiento_credito_001]
```

Y si más tarde la operación se **rectifica** — porque el monto era equivocado o la cuenta destino estaba mal — se genera una nueva transferencia que `rectifica` la previa, con sus propios asientos. Nada se borra; el rastro entero se preserva. **Esto no es lujo: es exigencia regulatoria** — todo banco supervisado tiene que poder reconstruir cualquier estado pasado para una inspección.

## Caso 2 — El ciclo de vida de un préstamo

Un préstamo personal no es un evento sino una **historia que se desenvuelve a lo largo de meses o años**. El modelo necesita capturar esa historia con tres exigencias simultáneas: estado actual, histórico completo, cambios consultables por fecha.

El otorgamiento es una situación. La aprobación del comité es otra. Cada cuota pagada es otra. Cada mora es otra. Una reestructuración es otra. El castigo (cuando se da por incobrable) es otra. **Todas conectadas a un préstamo articulador en O**:

```
(prestamo_personal_017) ∈ O
  instancia_de:           prestamo_personal
  cliente:                ana                       ← Q
  tipo_producto:          PP_Tasa_Fija_36m          ← O (oferta reificada)
  monto_otorgado:         n_5000_usd                ← N
  unidad:                 USD
  tasa_anual:             n_18_porciento            ← N
  plazo_cuotas:           36
  fecha_otorgamiento:     2026-01-15
  estado:                 vigente                    ← K, pero cambia con el tiempo
```

El campo `estado` cambia: vigente → mora_30 → mora_60 → judicializado → castigado, o vigente → vigente → ... → cancelado. La pregunta arquitectónica obvia: ¿cómo registrar esos cambios?

**Respuesta del modelo**: nunca sobreescribir. Cada cambio de estado es un hecho nuevo con su vigencia D9:

```
(prestamo_017, estado, vigente,          valid_from=2026-01-15, valid_to=2026-08-10)
(prestamo_017, estado, mora_30,          valid_from=2026-08-10, valid_to=2026-09-10)
(prestamo_017, estado, mora_60,          valid_from=2026-09-10, valid_to=2026-10-15)
(prestamo_017, estado, reestructurado,   valid_from=2026-10-15)
```

La consulta *"¿qué estado tenía el préstamo en septiembre de 2026?"* es directa: `at=2026-09-20` → `mora_30` (la franja del 10-Ago al 10-Sep había cerrado, la franja siguiente estaba vigente). Cinco años después, un litigio que pregunta *"¿desde cuándo dejó de pagar este cliente?"* obtiene la respuesta exacta.

Cada **cuota** es una sub-situación reificada con su pago (o falta de pago):

```
(cuota_017_03, parte_de,           prestamo_017)
(cuota_017_03, instancia_de,       cuota_prestamo)
(cuota_017_03, fecha_vencimiento,  2026-04-15)
(cuota_017_03, monto_total,        n_165_usd)
(cuota_017_03, estado,             pagada,  valid_from=2026-04-14, valid_to=null)

(pago_001, instancia_de,    accion_pagar)
(pago_001, agente,          ana)
(pago_001, parte_de,        cuota_017_03)
(pago_001, monto,           n_165_usd)
(pago_001, momento,         2026-04-14)
(pago_001, lugar_de,        web_banking)
```

Una **reestructuración** es donde el caso se pone interesante. No es modificación del préstamo original; es un préstamo nuevo que `cumple` y `cancela` el anterior con `motivado_por: mora` y `justificado_por: politica_reestructuracion_v3`:

```
(prestamo_017_re) ∈ O                              // préstamo nuevo
  instancia_de:        prestamo_personal
  cliente:             ana
  monto_otorgado:      saldo_capital_017            // del original
  tasa_anual:          n_25_porciento               // mayor por riesgo
  plazo_cuotas:        24
  fecha_otorgamiento:  2026-10-15
  motivado_por:        mora_017
  justificado_por:     politica_reestructuracion_v3
  rectifica:           prestamo_017
```

Cinco años después, un equipo de riesgo investigando reestructuraciones recupera **toda la cadena**: el otorgamiento original, la mora, la reestructuración, la política que la autorizó (con su versión vigente en ese momento), el comité que la aprobó. Sin grafo, esa investigación es un cruce de cinco sistemas; con grafo, es un recorrido transitivo de un nodo.

![El ciclo de vida de un préstamo: otorgamiento → cuotas → mora → reestructuración. Cada cambio de estado es un hecho nuevo con vigencia D9, cada transición tiene su motivado_por y justificado_por, el rastro entero se preserva.](../diagrams/png/42_ciclo_prestamo.png)

## Caso 3 — Investigación de fraude: reconstruyendo el pasado

Un cliente reporta que vio cargos por $1.840 en su tarjeta Visa la noche del 20 de mayo, en una ciudad donde no estuvo. El banco abre una investigación. Lo que la investigación necesita reconstruir es exactamente el tipo de pregunta que D9 + bitemporalidad responden mejor que cualquier otra arquitectura:

- *¿Dónde estaba registrada la dirección del cliente esa noche?*
- *¿Qué tarjetas activas tenía?*
- *¿Cuál era el límite y qué saldo disponible le quedaba?*
- *¿Se había emitido alguna alerta antifraude previa?*
- *¿Cuáles fueron las últimas autorizaciones aprobadas y rechazadas, y por qué?*
- *¿Qué sabía el motor antifraude sobre este cliente la noche del 20 de mayo, exactamente?*

Cada pregunta es una consulta con `at=2026-05-20T22:00Z`. El sistema responde con el estado del cliente en ese momento — no el estado de hoy, no una reconstrucción aproximada, sino lo que el sistema sabía en ese instante exacto. Esa última pregunta — *¿qué sabía el sistema?* — es donde bitemporalidad completa (cap 22) se vuelve crítica: si el motor antifraude actualizó el perfil del cliente el 22 de mayo (dos días después del incidente), el investigador necesita ver el perfil **vigente la noche del 20**, no el actualizado.

La cadena causal que el grafo permite construir:

```
(autorizacion_001, instancia_de, accion_autorizar_tarjeta)
(autorizacion_001, momento, 2026-05-20T21:47Z)
(autorizacion_001, agente, motor_autorizador_v7)        ← D5: software como Q
(autorizacion_001, monto, 1840)
(autorizacion_001, tarjeta, visa_ana_001)
(autorizacion_001, comercio, "Liquor Store XX")
(autorizacion_001, lugar_de, "Las Vegas")
(autorizacion_001, motivado_por, transaccion_pos_001)
(autorizacion_001, justificado_por, perfil_riesgo_ana_v3)

(perfil_riesgo_ana_v3, instancia_de, perfil_antifraude,
                       valid_from=2026-04-10, valid_to=2026-05-22)
(perfil_riesgo_ana_v3, viajes_recientes_declarados, [...])
(perfil_riesgo_ana_v3, score_riesgo, 0.31)
```

Cuando un mes después se sabe que era fraude:

```
(investigacion_fraude_001, instancia_de, investigacion_fraude)
(investigacion_fraude_001, motivado_por, reclamo_ana_001)
(investigacion_fraude_001, conclusion, fraude_confirmado)

(reverso_autorizacion_001, cancela, autorizacion_001)
(reverso_autorizacion_001, justificado_por, investigacion_fraude_001)
```

Lo que **no** ocurre: borrar la autorización original. La autorización fue real, fue ejecutada, dejó saldo descontado durante un mes. Lo que ocurre es **una nueva situación que la cancela** — el patrón de hechos inmutables que hemos visto desde el capítulo 10. El histórico queda intacto, la consulta posterior puede reconstruir lo que el cliente vio en su extracto en cualquier momento.

Esta es la propiedad por la que los reguladores bancarios exigen sistemas auditables. Y es exactamente lo que el modelo entrega como propiedad arquitectónica, no como funcionalidad agregada.

## Caso 4 — El producto bancario como oferta reificada

Una fricción que vimos por primera vez en el sauna y que vuelve con fuerza en el banco: el **producto comercial** como entidad. *"Tarjeta Visa Platinum"* no es una categoría abstracta (K); es una **oferta concreta** del banco con sus términos, beneficios, comisiones, fechas de vigencia. Ana no tiene "una Visa Platinum" como categoría — tiene **una instancia específica** de la oferta vigente cuando se la dieron, con sus condiciones congeladas en ese momento.

```
(visa_platinum_oferta_2026q1) ∈ O                  // la oferta comercial
  instancia_de:           tipo_oferta_tarjeta
  marca:                  Visa
  segmento:               Platinum
  cuota_manejo_mensual:   n_8_usd
  beneficios:             [millas_aerolinea, seguro_viaje, ...]
  comisiones:             [comision_internacional_3pct, ...]
  vigencia:               valid_from=2026-01-01, valid_to=2026-06-30

(tarjeta_ana_001) ∈ O                              // la instancia que Ana tiene
  instancia_de:           tarjeta_credito
  cliente:                ana
  cubierto_por:           visa_platinum_oferta_2026q1
  numero_enmascarado:     "**** 4521"
  fecha_emision:          2026-03-15
  limite_credito:         n_3000_usd
  estado:                 activa
```

¿Por qué importa la distinción? Porque cuando el banco **actualiza** la Visa Platinum (digamos, sube la cuota a $10 en julio 2026), las tarjetas ya emitidas no cambian automáticamente — siguen ligadas a la **versión de la oferta vigente al momento de la emisión**. La oferta nueva (`visa_platinum_oferta_2026q3`) aplica solo a tarjetas nuevas. La consulta *"¿bajo qué condiciones se le entregó esta tarjeta?"* devuelve la oferta histórica, no la actual.

Esto es exactamente el patrón **plantilla + instancia con vigencia** del capítulo 18: la oferta es plantilla; la tarjeta es instancia; los términos quedan congelados. La regla del modelo es la misma que para diagnósticos clínicos, contratos legales o tarifas dinámicas: **cuando un dato cambia, lo registramos como nueva situación, no como sobreescritura**.

## Lo que el banco demuestra

Si los capítulos 15-17 mostraban que el modelo absorbe dominios distintos, el banco muestra que **absorbe la complejidad industrial sin contorsiones**. Vale la pena enumerar lo que esta capítulo prueba:

1. **Multi-agente realista**: cinco agentes (cliente, sistema, motor, contraparte, banco) en una sola operación, todos tratados uniformemente bajo D5.
2. **Contrapartida contable como sub-situaciones**: cada movimiento operativo se conecta a sus asientos contables vía `parte_de`. La auditoría es un recorrido del grafo.
3. **D9 industrial**: el estado de un préstamo cambia siete veces a lo largo de su vida; las siete quedan consultables por fecha exacta. Sin D9, los bancos hoy mantienen tablas de historia paralelas a las tablas operativas — un overhead enorme.
4. **Bitemporalidad para fraude**: la investigación necesita saber no solo qué era cierto sino qué sabía el sistema. La pieza que el capítulo 22 marca como pendiente queda evidenciada acá como exigencia, no como nicho.
5. **Productos como ofertas reificadas**: la confusión "K abstracto vs O concreto" se resuelve igual que en el sauna y la clínica. El patrón es estable a través de dominios disímiles.
6. **Cadenas causales y normativas conviven**: un fraude tiene `motivado_por` (reclamo), `causado_por` (vulnerabilidad), `justificado_por` (política de reversos). Las cuatro relaciones de D6 operan en paralelo.

La pregunta honesta — *¿qué falta para modelar un banco real?* — tiene una respuesta clara: los seis frentes del capítulo 22 (motor de inferencia, bitemporalidad completa, persistencia industrial, tooling, lexicon poblado, comunidad). Pero **la arquitectura conceptual está completa**. Un banco que adopte WQuestions no tiene que esperar a que el modelo se extienda; tiene que esperar a que la implementación industrial madure.

## Lo que viene

Cerramos con esto la **secuencia de dominios profundos**: sauna, taxi, clínica, banco. Cuatro casos cada vez más exigentes, todos modelados con el mismo catálogo D7 y el mismo lexicon (extendido por dialecto en cada caso). El próximo capítulo cambia la estrategia una última vez en Parte V: en lugar de una inmersión profunda en otro dominio, somete al modelo a **cuatro dominios cualitativamente distintos en serie corta** — música, química, fútbol, contrato — buscando explícitamente lo que el modelo todavía no resuelve bien. Es el capítulo donde el libro deja de mostrar lo que funciona y empieza a admitir lo que duele.
