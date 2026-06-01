# Capítulo 18 — Un software ERP: el caso multi-módulo

## Por qué un ERP estresa al modelo

El **ERP** (*Enterprise Resource Planning*) — el software que coordina la operación interna de una empresa mediana o grande — es un caso distinto a todos los anteriores. Lo que estresa al modelo no es ningún rasgo individual; es la **convivencia simultánea** de varios módulos que tradicionalmente se construyeron como sistemas separados:

- **Recursos humanos**: empleados, jerarquías, salarios, evaluaciones.
- **Finanzas y contabilidad**: asientos, presupuestos, cuentas por pagar y cobrar.
- **Inventario y almacén**: stocks, movimientos, valorizaciones.
- **Ventas**: pedidos, comisiones, clientes.
- **Compras**: órdenes, proveedores, aprobaciones.
- **Manufactura**: BOM (bill of materials), órdenes de producción, consumos.

En arquitecturas tradicionales — SAP, Oracle, Dynamics —, cada uno de estos módulos es un mundo aparte con su propio esquema, sus propias tablas, sus propios procesos. Las integraciones entre módulos son el principal proyecto de cualquier consultor de ERP, y representan, históricamente, el 60-70% del esfuerzo total de implementación. Si quieres saber **cuánta comisión generó la venta que movió tantas unidades del almacén central**, necesitas cruzar tres bases de datos distintas con sus propias reglas de identidad.

Lo que WQuestions promete acá — y vamos a demostrar — es que la integración entre módulos **no exige ningún sistema de unificación**: cuando todos los hechos del negocio comparten la misma estructura atómica `(sujeto, rol, valor)`, el grafo *ya es* la integración. Una venta no genera "registros en tres tablas distintas"; genera **una situación reificada con tres sub-situaciones ligadas por `parte_de`**. Y todas viven en el mismo grafo.

Este capítulo modela seis escenarios reales de un ERP. Cada uno ilustra una dimensión donde el modelo paga su diseño.

## La arquitectura conceptual del ERP en WQuestions

Antes de meternos en los escenarios, conviene aterrizar cómo se mapean los conceptos del ERP a las siete coordenadas:

- **Empleados, clientes, proveedores y la empresa misma** viven todos en **Q**. La empresa como persona jurídica es un agente igual de válido que un empleado humano (D5).
- **Productos, órdenes, asientos, comisiones, evaluaciones de desempeño** viven en **O**. Todo lo que tiene fecha de creación, historia y trazabilidad es una entidad de primera clase.
- **Departamentos, almacenes, sucursales, oficinas** viven en **L**. Forman una jerarquía territorial-organizacional.
- **Fechas, períodos, vencimientos** viven en **T**.
- **Cantidades vendidas, montos, horas hombre, kilos de materia prima** viven en **N**, siempre con su unidad anclada en **K**.
- **Tipos de producto, categorías de empleado, estados de orden, monedas** viven en **K**.

Las decisiones de diseño que más se ejercitan en un ERP son: **D3** (todo es tripleta atómica), **D4** (las operaciones que generan registros en varios módulos se reifican como una situación con sub-situaciones), **D6** (los estados de las órdenes, los salarios, los precios cambian en el tiempo y guardamos historial), **D7** (cada acción tiene su `motivado_por` y su `justificado_por` — la auditoría es nativa, no se agrega encima) y **D8** (38 roles canónicos alcanzan; lo específico del ERP se extiende sin tocar el catálogo).

## Caso 1 — La jerarquía organizacional

Todo ERP empieza por el organigrama. Una empresa tiene un director, varios gerentes, sus equipos, y a veces sub-equipos. En SAP, esto vive en una tabla `HRP1001` con un esquema gimnástico de "relations". En WQuestions, **es un solo rol**:

```python
u.assert_fact(pedro, "reporta_a", maria)
u.assert_fact(laura, "reporta_a", maria)
u.assert_fact(maria, "reporta_a", carlos)
u.assert_fact(carlos, "reporta_a", empresa)
```

Cuatro tripletas. La jerarquía completa. Y la empresa también está en Q — es un agente legal igual de válido que Carlos.

La consulta "¿quién es el jefe del jefe de Pedro?" es un recorrido transitivo de dos saltos sobre el rol `reporta_a`. Si quieres "todo el árbol bajo Carlos", recorres recursivamente la relación inversa. No hace falta una tabla auxiliar de "transitive closure": el motor la calcula al vuelo. Y como `reporta_a` no está en el catálogo D8 (es un rol de dominio), el sistema lo acepta por **política liberal** sin protestar.

Asignar empleados a departamentos físicos es igual de simple:

```python
u.assert_fact(pedro, "trabaja_en", dpto_ventas)
u.assert_fact(laura, "trabaja_en", dpto_produccion)
```

Cada departamento vive en L. Si más adelante quieres modelar que un departamento *contiene* sub-departamentos, usas `parte_de` exactamente como con cualquier otra jerarquía. Lo mismo aplica a regiones, sucursales, plantas de producción.

## Caso 2 — Bill of Materials (BOM) recursivo

Acá el modelo brilla. Un BOM — la descomposición jerárquica de un producto en sus subproductos y componentes — es uno de los conceptos más típicamente difíciles de implementar en sistemas relacionales. En MRP clásicos exige tablas como `mast` + `matl` + `caps` con joins complicados.

Modelamos una bicicleta MTB: tiene un cuadro y dos ruedas; cada rueda tiene una llanta y un conjunto de rayos; el set de rayos está hecho de acero inoxidable. Cinco niveles de jerarquía anidada:

```
bicicleta_mtb  ────┬─── cuadro_aluminio
                   ├─── rueda_completa (×2)  ───┬─── llanta_26
                   │                            └─── rayos  ─── acero_inox
                   └─── ...
```

En WQuestions cada nivel es **una sola tripleta** con `parte_de`:

```python
u.assert_fact(cuadro, "parte_de", bicicleta)
u.assert_fact(rueda,  "parte_de", bicicleta)
u.assert_fact(llanta, "parte_de", rueda)
u.assert_fact(rayos,  "parte_de", rueda)
u.assert_fact(acero,  "parte_de", rayos)
```

La cantidad de cada subproducto se modela como un atributo del enlace, con su unidad:

```python
u.assert_fact(rueda, "cantidad_en_bom", n(2, "unidades", "n_2_uds_rueda"))
```

Para responder *"¿qué materia prima necesita la bicicleta?"* basta con recorrer recursivamente `parte_de` hasta llegar a las hojas. El test del prototipo lo verifica:

```
BOM recursivo: acero → rayos → rueda → bicicleta
cadena: mp_acero_inox → prod_rayos → prod_rueda_completa → prod_bicicleta_mtb
```

Lo mismo aplica a cualquier producto manufacturado: un automóvil, un electrodoméstico, un mueble modular, un componente electrónico. La recursión arbitraria del BOM no requiere ningún esquema especial — es un caso particular de `parte_de`.

## Caso 3 — La venta cross-módulo: el patrón que vale oro

Acá viene el caso emblemático del ERP. Una sola venta — cinco bicicletas a BetAuto S.A. por 7.500 dólares — toca, al mismo tiempo, **tres módulos** del software empresarial:

- **Inventario**: hay que descontar 5 unidades del almacén central.
- **Contabilidad**: hay que registrar el ingreso de 7.500 USD con su asiento.
- **Recursos humanos**: el vendedor (Pedro) genera una comisión del 5% sobre la venta.

En un ERP tradicional, este flujo dispara tres procesos separados con tres registros en tres tablas distintas, ligados por *foreign keys* y unidos por convenciones de naming. La auditoría — *"explícame qué pasó con esta venta puntual"* — exige cruzar las tres bases.

En WQuestions el modelado es directo: **una situación reificada con tres sub-situaciones**:

```python
venta = ingest_situation(u, lex, "vender", roles={
    "agente": pedro,
    "tema": bicicleta,
    "cliente": cliente_betauto,
    "monto": n(7500, "USD"),
    "unidad": usd,
    "momento": at("2026-07-15T11:20"),
    "lugar_de": dpto_ventas,
}, sit_id="venta_001")

# Sub-situación 1: movimiento de inventario
u.assert_fact(mov_inv, "parte_de", venta)
u.assert_fact(mov_inv, "tema", bicicleta)
u.assert_fact(mov_inv, "cantidad", n(5, "unidades"))
u.assert_fact(mov_inv, "origen", almacen_central)

# Sub-situación 2: asiento contable
u.assert_fact(asiento, "parte_de", venta)
u.assert_fact(asiento, "monto", n(7500, "USD"))
u.assert_fact(asiento, "tipo_movimiento", ingreso_por_venta)

# Sub-situación 3: comisión del vendedor
u.assert_fact(comision, "parte_de", venta)
u.assert_fact(comision, "beneficiario", pedro)
u.assert_fact(comision, "monto", n(375, "USD"))
u.assert_fact(comision, "calculado_segun", politica_comisiones_v2)
```

Tres sub-situaciones, una situación articuladora, **ningún cruce de tablas necesario**. La consulta *"explícame todo lo que pasó con la venta 001"* es una proyección directa por `parte_de`:

![La venta cross-módulo del ERP: una situación central (`venta_001`) con tres sub-situaciones — inventario, contabilidad y comisión — colgando por `parte_de`. En arquitecturas tradicionales esto exige tres tablas y un ETL para reportes integrados; en WQuestions el grafo ya integra los tres módulos sin intermediarios.](../diagrams/png/45_erp_venta_cross_modulo.png)


```python
sub_situaciones = [
    f.subject for f in u.facts_with_role("parte_de")
    if f.value.id == "venta_001"
]
# devuelve [mov_inventario_001, asiento_venta_001, comision_pedro_001]
```

Y como cada sub-situación tiene su propia identidad, podemos hacer preguntas finas: *"¿qué comisión generó esta venta?"*, *"¿cuál es el asiento contable de esta operación?"*, *"¿de qué almacén salió la mercancía?"*. Todas son recorridos de un salto. Sin ETL, sin sistema intermedio, sin tabla de unificación. **El grafo ya es la integración.**

## Caso 4 — El workflow de aprobación bitemporal

Las órdenes de compra grandes — en este caso 48.000 USD de acero al proveedor — no se ejecutan al instante. Pasan por un ciclo: alguien las redacta, alguien las envía a aprobación, alguien con autoridad las aprueba (o rechaza). Cada estado tiene una fecha de entrada y una de salida.

En sistemas tradicionales, esto se modela con una columna `estado` que **se sobreescribe** en cada transición. Cuando alguien pregunta *"¿en qué estado estaba esta OC el 20 de julio a las 13:00?"*, hay que revisar la tabla de auditoría — si existe — o estimar a partir de los logs.

En WQuestions el estado es un hecho con vigencia temporal (D6):

```python
u.assert_fact(oc, "estado", borrador,
              valid_from=t_creacion, valid_to=t_envio_aprob)
u.assert_fact(oc, "estado", pendiente_aprobacion,
              valid_from=t_envio_aprob, valid_to=t_aprobacion)
u.assert_fact(oc, "estado", aprobada,
              valid_from=t_aprobacion)
```

Tres tripletas en lugar de tres updates destructivos. La consulta bitemporal *"¿en qué estado estaba el 20 de julio a las 13:00?"* devuelve `pendiente_aprobacion`; *"¿y el 22 de julio?"*, devuelve `aprobada`. El historial completo es nativo, no un módulo aparte.

La aprobación misma es una situación reificada con su agente y su justificación normativa (D7):

```python
aprobacion = ingest_situation(u, lex, "aprobar", roles={
    "agente": carlos,
    "tema": oc,
    "momento": at("2026-07-21T15:30"),
    "justificado_por": politica_aprobacion_oc_v4,
}, sit_id="aprobacion_oc_001")
```

Carlos no aprueba "porque sí": aprueba **porque la política corporativa lo autoriza** para órdenes mayores a 30.000 USD. La política es otra situación reificada con su umbral y vigencia. Si mañana cambia el umbral, la nueva versión de la política se reifica como objeto nuevo y las aprobaciones anteriores siguen apuntando a la vieja — sin alterar el historial.

## Caso 5 — La orden de producción que consume materia prima

La planta de Laura va a producir 50 bicicletas. Cada bicicleta consume cierta cantidad de acero (para los rayos) y cierta cantidad de horas-hombre. El ERP necesita registrar:

- La orden de producción como evento principal.
- Los **consumos** de materia prima asociados.
- Los **consumos** de mano de obra (horas-hombre) asociados.

El patrón es el mismo que la venta cross-módulo: una situación reificada con sub-situaciones de consumo:

```python
op = ingest_situation(u, lex, "producir", roles={
    "agente": laura,
    "tema": bicicleta,
    "cantidad": n(50, "unidades"),
    "lugar_de": dpto_produccion,
}, sit_id="op_001")

# Consumo de materia prima
u.assert_fact(consumo_acero, "parte_de", op)
u.assert_fact(consumo_acero, "tema", acero)
u.assert_fact(consumo_acero, "cantidad", n(120, "kg"))

# Consumo de mano de obra
u.assert_fact(consumo_hh, "parte_de", op)
u.assert_fact(consumo_hh, "cantidad", n(180, "horas"))
u.assert_fact(consumo_hh, "ejecutado_por", laura)
```

Lo notable: la **misma estructura** modela bicicletas (donde el agente humano produce con materia prima) y, sin cambiar nada, podría modelar una reacción química industrial (donde *no hay agente humano*, los reactivos se transforman por sí solos siguiendo la estequiometría). El catálogo D8 ya admite que `agente` sea opcional cuando el verbo lo permite (D5).

La consulta *"¿cuántos kilos de acero consumió esta orden de producción?"* es una proyección directa: encuentra las sub-situaciones de `op_001` cuyo `instancia_de` sea `consumo_materia_prima`, filtra por `tema = acero`, suma los `cantidad`. Tres operaciones simples sobre el grafo. Cero ETL.

## Caso 6 — El audit trail bitemporal del salario

Aquí va una situación que en cualquier ERP es notoriamente difícil. Pedro fue contratado el 10 de enero con un salario de 2.500 USD. El 1 de abril le subieron a 2.800. El 1 de agosto, tras una evaluación de desempeño con calificación "excelente", le subieron de nuevo a 3.200.

La pregunta que el modelo tiene que responder sin esfuerzo: **¿cuál era el salario de Pedro el 15 de marzo? ¿Y el 15 de junio? ¿Y el 15 de septiembre?** Estas son preguntas reales, las que un auditor laboral hace cuando revisa un legajo. En un ERP tradicional, requieren una tabla histórica auxiliar (`emp_salary_hist`) que la mitad de las implementaciones nunca termina de mantener.

En WQuestions, **tres tripletas** bastan:

```python
u.assert_fact(pedro, "salario_mensual", n(2500, "USD"),
              valid_from=t_contrato, valid_to=t_aumento1)
u.assert_fact(pedro, "salario_mensual", n(2800, "USD"),
              valid_from=t_aumento1, valid_to=t_aumento2)
u.assert_fact(pedro, "salario_mensual", n(3200, "USD"),
              valid_from=t_aumento2)
```

Las tres conviven en el grafo. La consulta `query(..., at=fecha)` filtra por vigencia y devuelve el valor correcto:

```
marzo  → 2500
junio  → 2800
septiembre → 3200
```

El último aumento se conecta con su **causa motivacional** (D7): hubo una evaluación de desempeño con calificación excelente, reificada como objeto propio, y el ajuste de salario está `motivado_por` esa evaluación. Si el auditor pregunta *"¿por qué le subieron el salario a Pedro en agosto?"*, el grafo entrega la respuesta sin gimnasia.

## Resultado del prototipo

El ejemplo Python que acompaña el capítulo (`prototipo/ejemplos/erp.py`) materializa los seis casos con 78 individuos repartidos en seis ejes y 93 hechos atómicos. Las once validaciones automáticas pasan:

```
✓  Jerarquía: Pedro reporta a María, María a Carlos
✓  BOM recursivo: acero → rayos → rueda → bicicleta
✓  Venta cross-módulo: 3 sub-situaciones (inventario + asiento + comisión)
✓  D6: OC pendiente_aprobacion el 20-Jul 13:00
✓  D6: OC aprobada el 22-Jul
✓  D7: la aprobación está justificada_por la política corporativa
✓  Producción: consume materia prima + mano de obra
✓  Audit trail bitemporal (D6): salario en marzo=2500, junio=2800, sept=3200
✓  WH: ¿quién aprobó la orden de compra?
✓  WH: ¿cuánto se le vendió a BetAuto?
✓  D5: ajuste de salario — agente=María, beneficiario=Pedro
✓  Política liberal: rol de dominio `calculado_segun` admitido sin declarar

Resultado: 12/12 validaciones pasadas.
```

## Qué quedó probado en este capítulo

El ERP es probablemente el dominio donde la promesa de WQuestions paga su mayor dividendo concreto: **la integración cross-módulo deja de ser un proyecto y se vuelve gratis**. La venta no genera "registros en tres tablas"; genera una situación con tres sub-situaciones. El BOM no necesita esquemas auxiliares; es un caso de `parte_de` recursivo. El audit trail bitemporal no es un módulo aparte; es la forma normal de modelar hechos con vigencia (D6). La aprobación no es un workflow externo; es una situación reificada con su justificación normativa (D7).

Y todo esto se modela con los mismos **38 roles canónicos** del catálogo D8 más un puñado de roles de dominio (`reporta_a`, `trabaja_en`, `calculado_segun`, `cantidad_en_bom`, `ejecutado_por`) admitidos por la política liberal. El motor no creció ni una línea para absorber el ERP. Lo único que creció fue el lexicon — seis verbos nuevos (`vender`, `ordenar_compra`, `aprobar`, `producir`, `contratar`, `ajustar_salario`) con sus signaturas.
