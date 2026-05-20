# Capítulo 22 — Una operación minera: lo físico, lo espacial y los eventos sin agente

## Por qué la minera es distinta a todo lo anterior

Los siete dominios que llevamos modelados — Spa, taxi, clínica, banco, ERP, universidad, municipalidad — tienen algo en común que pasa desapercibido: **suceden en oficinas, comercios o sistemas digitales**. Los eventos son acciones humanas o de software intencional: alguien vende, otra persona paga, una doctora diagnostica, un funcionario emite. Hasta cuando no hay agente humano explícito — la app del taxi asignando un conductor, el motor antifraude del banco, el sensor que monitorea el aire — siempre hay un **agente con intencionalidad** detrás de la acción.

Una operación minera de gran escala cambia esa premisa. En la minería pasan muchas cosas que **ningún agente "hace"**: la roca se desprende, el suelo cede, una pared geomecánica se debilita con el tiempo, una corriente subterránea altera la calidad del agua. Son eventos físicos puros que ocurren porque las condiciones materiales se cumplen. Y, sin embargo, son tan importantes como cualquier acción intencional — porque cuando esos eventos físicos lesionan a un trabajador o contaminan un río, **la cadena causal completa debe quedar trazada para auditoría, para responsabilidad legal y para prevención futura**.

Además, la minería trae otros desafíos propios:

- **Estructura espacial profunda**: yacimiento → tajo → nivel → banco → frente. Cinco niveles jerárquicos físicos, cada uno con sus propios metros cúbicos extraíbles y sus propias condiciones geomecánicas.
- **Equipos con ciclos de vida muy largos**: un camión CAT 793F cuesta tres millones de dólares y opera durante quince años, con docenas de mantenimientos preventivos y correctivos a lo largo de su vida útil.
- **Producción medida en múltiples unidades convertibles**: toneladas métricas de mineral extraído, gramos por tonelada de ley aurífera, onzas troy de oro fino producido. Cada cifra tiene su unidad y se convierte a la siguiente por multiplicación.
- **Turnos como entidades articuladoras**: una operación opera 24/7 dividida en turnos de 12 horas; cada turno reúne trabajadores, equipos, producción e incidentes en un mismo nodo de grafo.
- **Cumplimiento ambiental gatillado por umbrales**: cuando un sensor mide arsénico por encima del límite normativo, el reporte regulatorio se dispara automáticamente.
- **Comisionamiento y punchlist**: antes de que un equipo nuevo entre en operación comercial, atraviesa una batería de tests de aceptación con criterios de tolerancia, firmas múltiples y un seguimiento estricto de defectos pendientes clasificados por severidad.

Este capítulo modela seis escenarios donde el dominio minero pone a trabajar todas las decisiones de diseño que llevamos, en una combinación que ningún capítulo anterior había exigido a la vez.

## La arquitectura conceptual del dominio minero

Mapeo a las ocho coordenadas:

- **Operadores, supervisores, mecánicos, inspectores ambientales, sensores ambientales, la empresa y el regulador** viven en **Q**. Los sensores entran a Q por D5 — son agentes que registran mediciones.
- **Camiones, palas, turnos, extracciones, producción, mantenimientos, incidentes, mediciones, normas ambientales, reportes** viven en **O**.
- **Yacimiento, tajos, niveles, bancos, frentes de trabajo, estaciones de monitoreo, ríos** viven en **L** organizados jerárquicamente con `dentro_de` (rol de dominio L→L admitido por política liberal).
- **Fechas de adquisición de equipo, inicio y fin de turnos, momento de incidentes, fechas de mantenimiento** viven en **T**.
- **Toneladas, gramos por tonelada, onzas troy, miligramos por litro, dólares, años de vida útil** viven en **N** con su unidad.
- **Estados del equipo (operativo, en_mantenimiento, dado_de_baja), tipos de incidente, tipos de mantenimiento, minerales, contaminantes** viven en **K**.

Las decisiones de diseño que más se ejercitan acá son: **D5 al extremo** (eventos físicos sin ningún agente humano), **D7** (cadenas causales largas con `causado_por` sin intencionalidad y reportes regulatorios `justificado_por` normas ambientales), **D6** (estados del equipo a lo largo de quince años), y el patrón de **situación articuladora** que ya vimos en taxi y banco aplicado al turno.

## Caso 1 — La estructura espacial profunda

Una mina no es un lugar; es **una jerarquía de lugares**. El nivel más alto es el yacimiento entero (el "Yacimiento San Marcos", por ejemplo). Dentro de él hay uno o más tajos (Tajo Norte, Tajo Sur). Cada tajo tiene niveles geográficos definidos por altitud (Nivel 4250 m.s.n.m., Nivel 4300). Cada nivel se subdivide en bancos (Banco 03, Banco 04 — escalones físicos del tajo). Y cada banco tiene varios frentes de trabajo activos al mismo tiempo (Frente A, Frente B, Frente C).

Modelamos exactamente igual que la subdivisión territorial de la municipalidad: un rol de dominio `dentro_de` que la política liberal acepta:

```python
u.assert_fact(tajo_norte, "dentro_de", yacimiento)
u.assert_fact(nivel_4250, "dentro_de", tajo_norte)
u.assert_fact(banco_3, "dentro_de", nivel_4250)
u.assert_fact(frente_a, "dentro_de", banco_3)
```

La consulta *"¿dónde ocurrió este accidente exactamente?"* devuelve la cadena entera con un solo recorrido: `Frente A → Banco 03 → Nivel 4250 → Tajo Norte → Yacimiento San Marcos`. Toda la información geográfica jerárquica disponible para cualquier reporte de seguridad, cualquier auditoría regulatoria, cualquier análisis de productividad por zona.

## Caso 2 — Equipo con ciclo de vida largo

Un camión minero Caterpillar 793F se adquiere en abril de 2018. Tiene una vida útil planeada de quince años. Durante esos años atraviesa muchos estados: opera, entra a mantenimiento programado, sale, vuelve a operar, sufre una falla, se repara, sigue operando. El modelado registra todo ese ciclo con vigencia temporal (D6):

```python
u.assert_fact(camion_007, "estado", operativo,
              valid_from=t_op_inicial, valid_to=t_mant_2024)
u.assert_fact(camion_007, "estado", mantenimiento_prog,
              valid_from=t_mant_2024, valid_to=t_post_mant)
u.assert_fact(camion_007, "estado", operativo,
              valid_from=t_post_mant, valid_to=t_falla)
u.assert_fact(camion_007, "estado", mantenimiento_correctivo,
              valid_from=t_falla, valid_to=t_post_falla)
u.assert_fact(camion_007, "estado", operativo,
              valid_from=t_post_falla)
```

Cinco tripletas. El historial completo del camión a lo largo de ocho años. La consulta *"¿el camión 007 estaba operativo el 15 de marzo de 2024?"* devuelve `en_mantenimiento_programado`. *"¿Y el 1 de junio de 2026?"* devuelve `operativo`. La trazabilidad para auditoría es nativa, no un módulo añadido.

## Caso 3 — Producción con múltiples unidades convertibles

La minería de oro registra producción en una cascada de unidades. Una extracción se mide en **toneladas métricas** de mineral. Ese mineral tiene una **ley** expresada en gramos de oro por tonelada (g/t). Multiplicando ambos se obtiene la cantidad bruta de oro contenido; tras el proceso metalúrgico se obtienen las **onzas troy** de oro fino vendible. Tres unidades distintas, cada una con su semántica:

```python
extraccion = ingest_situation("extraer", roles={
    "agente": operador1,
    "extraido": mineral_oro,
    "monto": n(2400, "toneladas"),
    "unidad": tonelada_metrica,
    "lugar_de": frente_a,
    "ley_mineral": n(8.2, "g/t"),
    "ley_unidad": gramo_por_tonelada,
})
```

Y la producción de oro fino se modela como **sub-situación parte_de la extracción**, calculada del mineral y la ley:

```python
u.assert_fact(produccion_oro, "parte_de", extraccion)
u.assert_fact(produccion_oro, "monto", n(632.7, "onzas_troy"))
u.assert_fact(produccion_oro, "unidad", onza_troy)
u.assert_fact(produccion_oro, "calculado_de", extraccion)
```

El cálculo (2.400 t × 8.2 g/t ÷ 31.1 g/oz ≈ 632.7 oz) se registra como una situación articuladora que apunta hacia atrás a la extracción con `calculado_de`. Esto importa: el grafo no pierde la trazabilidad. Si mañana alguien pregunta *"¿de qué extracción específica salieron estas 632.7 onzas?"*, la respuesta es directa. Si se descubre que la ley estaba mal medida y hay que recalcular, la nueva producción se modela como un hecho nuevo que `rectifica` el anterior — el modelo de auditoría minera del banco aplicado a la minería de minerales.

## Caso 4 — El turno como entidad articuladora

Una operación minera trabaja 24 horas al día divididas en dos o tres turnos. Cada turno reúne un puñado de operadores, varios equipos y toda la producción y los incidentes que ocurran en ese lapso. Modelar el turno como entidad articuladora — exactamente como hicimos con el `viaje_001` del taxi o la `transferencia_001` del banco — permite que todo lo que pasa quede vinculado al mismo nodo:

```python
turno = u.add_individual(Individual(id="turno_dia_2026_05_19", axis=Axis.O))
u.assert_fact(turno, "inicio", at("2026-05-19T06:00"))
u.assert_fact(turno, "fin",    at("2026-05-19T18:00"))
u.assert_fact(turno, "lugar_de", tajo_norte)
u.assert_fact(turno, "supervisor", supervisor)
u.assert_fact(turno, "operador_asignado", operador1)
u.assert_fact(turno, "operador_asignado", operador2)
u.assert_fact(turno, "operador_asignado", operador3)
```

Y la extracción, la producción derivada, el accidente, las mediciones — todos quedan `parte_de` el turno:

```python
u.assert_fact(extraccion, "parte_de", turno)
u.assert_fact(accidente, "parte_de", turno)
```

La consulta *"¿qué pasó en el turno del 19 de mayo?"* devuelve la cadena completa: tres operadores trabajaron, hubo una extracción exitosa de 2.400 toneladas, hubo un accidente en el Frente A, hubo mediciones ambientales. Todo en una sola proyección por `parte_de`. Sin tablas, sin joins. Solo el grafo.

## Caso 5 — Cadena causal sin agente humano

Acá viene el caso emblemático del dominio. A las 11:40 del 19 de mayo, mientras el operador Quispe trabaja en el Frente A del Banco 03, **una roca se desprende de la pared del banco y lo golpea**. Sufre una contusión en el brazo derecho.

La pregunta crítica para auditoría: **¿quién causó el accidente?**

La respuesta honesta — y la que el grafo tiene que registrar fielmente — es: **nadie**. La roca se desprendió. Nadie la tiró. Pero la roca no se desprendió "de la nada" tampoco: hubo una condición previa, un debilitamiento estructural de la pared del Banco 03 que la inspección geomecánica anterior **debió** haber detectado.

El modelo lo registra con dos cadenas causales encadenadas, ninguna con agente:

```python
# El debilitamiento es una condición geomecánica preexistente
debilitamiento = u.add_individual(Individual(
    id="debilitamiento_pared_b03", axis=Axis.O,
    label="Debilitamiento estructural Banco 03"))
u.assert_fact(debilitamiento, "instancia_de",
              category("condicion_geomecanica"))

# El desprendimiento es un evento físico SIN AGENTE,
# causado por el debilitamiento
desprendimiento = u.add_individual(Individual(
    id="evento_desprendimiento_001", axis=Axis.O))
u.assert_fact(desprendimiento, "lugar_de", frente_a)
u.assert_fact(desprendimiento, "momento", at("2026-05-19T11:40"))
u.assert_fact(desprendimiento, "causado_por", debilitamiento)
# Nota: NO HAY u.assert_fact(desprendimiento, "agente", ...)

# El accidente que sufre Quispe, causado_por el desprendimiento
u.assert_fact(accidente, "paciente", operador1)
u.assert_fact(accidente, "causado_por", desprendimiento)
u.assert_fact(accidente, "parte_de", turno)
```

D5 (agencia contextual) lo absorbe sin esfuerzo: el rol `agente` simplemente **no aparece** en las situaciones físicas. Y D7 con `causado_por` reconstruye la cadena causal hacia atrás hasta su origen — la condición preexistente que el sistema geomecánico no detectó.

![Cadena causal sin agente: el accidente está conectado hacia atrás con `causado_por` al desprendimiento de roca, que a su vez está conectado al debilitamiento estructural. Ninguno de los tres tiene agente — son eventos físicos puros — y, sin embargo, el grafo permite reconstruir la responsabilidad completa.](../diagrams/png/48_minera_cadena_causal.png)

Cualquier auditor de seguridad puede recorrer esta cadena hacia atrás con un solo recorrido sobre el grafo: *"¿qué causó el accidente?"* → desprendimiento. *"¿Y qué causó el desprendimiento?"* → debilitamiento estructural. *"¿Y por qué no se detectó ese debilitamiento?"* → siguiente capítulo de la investigación. La pregunta forense — *¿quién es responsable?* — se vuelve precisa porque el grafo entrega la cadena exacta, no una explicación mezclada en texto libre.

## Caso 6 — Reporte regulatorio ambiental disparado por umbral

Las operaciones mineras grandes están sujetas a regulación ambiental estricta. Sensores automáticos monitorean la calidad del aire y del agua en estaciones distribuidas por el yacimiento, midiendo concentraciones de contaminantes específicos cada cierto intervalo.

El 15 de mayo, el sensor de la Estación 3 mide 0.32 mg/L de arsénico en el río Quebrada Chica — **por encima del umbral normativo de 0.10 mg/L** establecido por la norma de calidad ambiental. La medición se reifica como cualquier otra situación, con el sensor como agente:

```python
medicion_alta = ingest_situation("medir_calidad", roles={
    "agente": sensor_pm,          # sensor en Q (D5)
    "medido_de": arsenico,
    "monto": n(0.32, "mg/L"),
    "unidad": miligramo_por_litro,
    "lugar_de": estacion_monitoreo,
    "momento": at("2026-05-15T14:00"),
})
```

El sensor entra a Q como agente válido — D5 una vez más. La norma ambiental vive en O con su umbral declarado:

```python
norma_ambiental = u.add_individual(Individual(
    id="ds_004_2017_minam", axis=Axis.O,
    label="DS 004-2017-MINAM (ECA agua)"))
u.assert_fact(norma_ambiental, "umbral_arsenico", n(0.10, "mg/L"))
```

Cuando el motor de reglas (que no implementamos en este prototipo pero está documentado en el cap. 27) detecta que el valor medido supera el umbral, dispara automáticamente un reporte regulatorio:

```python
reporte = ingest_situation("reportar", roles={
    "agente": minera_andes,           # la empresa reporta
    "tema": medicion_alta,
    "beneficiario": ente_regulador,   # al OEFA
    "momento": at("2026-05-15T18:00"),
    "motivado_por": medicion_alta,
    "justificado_por": norma_ambiental,
})
```

D7 una vez más con sus dos caras: el reporte está `motivado_por` la medición específica que superó el umbral, y `justificado_por` la norma que lo exige. El grafo registra ambas vinculaciones por separado. Si dentro de cinco años un auditor pregunta *"¿por qué se hizo este reporte ambiental?"*, hay dos respuestas precisas: por la medición concreta, y porque la norma DS 004-2017-MINAM lo exigía. No hay ambigüedad.

## Caso 7 — Comisionamiento: el contrato técnico antes de la operación comercial

Hay una fase de cualquier proyecto minero — y, más en general, de cualquier proyecto industrial pesado — que merece su propia sección porque expone fricciones nuevas: el **comisionamiento**. Antes de que un equipo nuevo (un molino, una correa transportadora, una planta de procesamiento) entre en operación comercial, debe pasar por una batería de tests de aceptación. Cada test tiene un **criterio formal** (presión, caudal, temperatura, tonelaje, vibración) con sus tolerancias. Si el test pasa, lo firman varias partes — el contratista que entrega el equipo, el ingeniero del *owner* que recibe, el inspector de QA/QC que audita. Si el test no pasa, se levantan **punchitems** (defectos identificados que hay que resolver antes de la aceptación final).

Modelamos un escenario completo: el molino de bolas nº 005 entra en comisionamiento el 1 de abril de 2026. El paquete entero se reifica como una entidad articuladora superior, igual que el turno minero del caso 4:

```python
comisionamiento = u.add_individual(Individual(
    id="comisionamiento_molino_005", axis=Axis.O))
u.assert_fact(comisionamiento, "tema", molino_005)
u.assert_fact(comisionamiento, "agente", contratista)
u.assert_fact(comisionamiento, "inicio", at("2026-04-01T08:00"))
```

Todo lo que pase durante el comisionamiento queda `parte_de` esta entidad: los tests, los sign-offs, los punchitems, los cierres de punchitems. Recorrer `parte_de` sobre el comisionamiento devuelve **el estado completo del proyecto**.

### Acceptance criterion: el criterio separado del valor medido

Acá aparece una fricción que vale la pena nombrar. Un test de comisionamiento típico — la prueba hidrostática del molino — exige *"presión mayor o igual a 8 bar sostenida 30 minutos con una caída máxima del 2%"*. Es decir, es un **criterio con tolerancia numérica**: tres valores límite, tres valores reales medidos, y una comparación entre ambos para decidir si pasa o falla.

El modelo separa el criterio del resultado en dos entidades distintas:

```python
# El criterio, como objeto reificado, vive por separado.
# Se puede versionar, citar y reusar para múltiples tests.
criterio_hidro = u.add_individual(Individual(
    id="criterio_hidrostatica_v1", axis=Axis.O))
u.assert_fact(criterio_hidro, "presion_minima", n(8.0, "bar"))
u.assert_fact(criterio_hidro, "duracion_minima", n(30, "min"))
u.assert_fact(criterio_hidro, "caida_maxima_pct", n(2.0, "%"))

# El test ejecutado, con sus valores reales y un puntero al criterio.
test_hidro = ingest_situation("ejecutar_test", roles={
    "agente": contratista,
    "tema": molino_005,
    "valor_medido": n(8.4, "bar"),
    "momento": at("2026-04-05T10:00"),
})
u.assert_fact(test_hidro, "verifica_criterio", criterio_hidro)
u.assert_fact(test_hidro, "caida_medida", n(1.3, "%"))
u.assert_fact(test_hidro, "duracion_medida", n(32, "min"))
u.assert_fact(test_hidro, "resultado", category("test_aprobado"))
```

Lo que el modelo **no hace** y conviene admitir: el cálculo *"8.4 ≥ 8.0 ∧ 1.3 ≤ 2.0 ∧ 32 ≥ 30 → APROBADO"* no es un hecho atómico que el sistema deduzca solo. Es lógica que vive en un **motor de reglas externo** (Datalog, SHACL, o una función Python) que el cap. 27 declara como pendiente del proyecto. Por ahora el `resultado` se asienta explícitamente como hecho. Esta es la misma fricción que ya veremos con el marcador de fútbol en el cap. 24: el modelo aloja los datos, las reglas derivadas necesitan un motor que el prototipo todavía no trae.

### Sign-off paralelo: tres firmas independientes sobre el mismo test

El test no pasa con una sola firma; necesita tres aprobaciones independientes — contratista, *owner*, QA — emitidas en momentos distintos y por agentes distintos. Cada aprobación es una **situación reificada propia** apuntando al mismo test por `tema`:

```python
aprob_contratista = ingest_situation("aprobar_checkpoint", roles={
    "agente": contratista, "tema": test_hidro,
    "momento": at("2026-04-05T11:00")})
aprob_owner = ingest_situation("aprobar_checkpoint", roles={
    "agente": ing_owner, "tema": test_hidro,
    "momento": at("2026-04-05T15:30")})
aprob_qa = ingest_situation("aprobar_checkpoint", roles={
    "agente": qa_inspector, "tema": test_hidro,
    "momento": at("2026-04-06T09:00")})
```

La consulta *"¿quiénes firmaron este test?"* es una proyección directa: encuentra todas las situaciones de tipo `accion_aprobar_checkpoint` cuyo `tema` sea el test, proyectá su `agente`. Devuelve los tres. Cada firma tiene su propio momento, su propia conclusión y eventualmente sus propias observaciones. **El modelo no necesita una tabla `test_signoffs` con FK múltiples**; cada firma es un hecho independiente que apunta al test.

### Severidad ordenada: una fricción que vale la pena nombrar

Los punchitems se clasifican típicamente en tres severidades: **A** (crítico — bloquea el comisionamiento), **B** (debe resolverse antes de operación comercial pero no la bloquea hoy), **C** (estético — no impide operar). La palabra clave de esa lista es **ordenada**: A es más severo que B, B más que C, y muchas reglas del proyecto dependen del orden ("el comisionamiento está listo cuando 0 items A están abiertos").

El modelo declara K como **categorías planas** — el catálogo D8 no trae noción de orden entre individuos de K. Esto es una fricción real, y conviene resolverla con un patrón explícito en lugar de inventar una pseudo-jerarquía. El patrón: **cada categoría de K lleva un atributo numérico `nivel_severidad` que define su posición en el orden**:

```python
sev_a = u.add_individual(category("severidad_A"))
u.assert_fact(sev_a, "nivel_severidad", n(1, "ord"))

sev_b = u.add_individual(category("severidad_B"))
u.assert_fact(sev_b, "nivel_severidad", n(2, "ord"))

sev_c = u.add_individual(category("severidad_C"))
u.assert_fact(sev_c, "nivel_severidad", n(3, "ord"))
```

Ahora cualquier consulta que necesite ordenar — *"dame todos los punchitems abiertos ordenados por severidad descendente"* — tiene un campo numérico para hacer el `sort`. Es un patrón sencillo, pero merece quedar declarado en el libro porque es la solución general cuando un dominio necesita categorías ordenadas (severidades, prioridades, niveles, grados de calidad, escalas de Likert). El modelo no impone el orden; el dominio lo declara explícitamente.

### Punchitem: tres roles Q distintos sobre la misma entidad

Un punchitem tiene una particularidad: involucra a **tres personas distintas con tres roles distintos**:

- **Quien lo encontró** (típicamente el QA en la inspección).
- **El responsable** de resolverlo (contratista o vendor).
- **El verificador** que cierra el item una vez resuelto (típicamente el *owner*).

```python
punch_001 = ingest_situation("registrar_punchitem", roles={
    "agente": qa_inspector,         # quien lo encontró
    "tema": fuga_aceite,            # qué se encontró
    "equipo_afectado": molino_005,  # qué equipo lo tiene
    "severidad": sev_a,
    "responsable": contratista,
    "verificador": ing_owner,
    "fecha_limite": at("2026-04-22T00:00"),
})
```

Tres roles Q sobre la misma entidad — encontrado, responsable, verificador — más uno O (`equipo_afectado`, rol de dominio porque `paciente` exige Q). El catálogo D8 no trae `responsable` ni `verificador`; la política liberal los admite sin protestar. El modelo no necesita ningún concepto nuevo; basta usar la maquinaria estándar con roles específicos del dominio.

El estado del punchitem evoluciona con D6:

```python
u.assert_fact(punch_001, "estado", abierto,
              valid_from=t_inspeccion, valid_to=t_inicio_trabajo)
u.assert_fact(punch_001, "estado", en_progreso,
              valid_from=t_inicio_trabajo, valid_to=t_cierre)
u.assert_fact(punch_001, "estado", cerrado,
              valid_from=t_cierre)
```

Y el cierre del item es otra situación reificada que `rectifica` el punchitem, ligada a la reparación que lo resolvió:

```python
cierre = ingest_situation("cerrar_punchitem", roles={
    "agente": contratista,
    "tema": punch_001,
    "verificado_por": ing_owner,
    "motivado_por": reparacion_ejecutada,
})
u.assert_fact(cierre, "rectifica", punch_001)
```

Igual que en el rediagnóstico médico del cap. 17 y la rectificación de multa del cap. 21: el item original **no se borra**, queda en el grafo con su historial. Si dentro de cinco años un auditor revisa el comisionamiento, encuentra que el punchitem 001 fue abierto el 15 de abril, atendido entre el 16 y el 20, y cerrado el 20 — con la reparación específica que lo motivó. Trazabilidad nativa.

### Estado agregado derivado: el comisionamiento "está listo"

La última fricción que aparece es la más interesante. Una pregunta de negocio típica: *"¿está el molino listo para operación comercial?"* La regla del proyecto: **sí, si y solo si hay cero punchitems severidad A abiertos**. Es decir, el estado del comisionamiento entero **se deriva** del estado de sus partes.

El modelo permite consultar todos los punchitems abiertos clase A con una proyección directa:

```python
abiertos_A = 0
for situ in u.facts_with_role("instancia_de"):
    if situ.value.id == "accion_registrar_punchitem":
        estado_actual = [...]   # filtra por at=hoy
        severidad = [...]
        if estado_actual != "cerrado" and severidad == "severidad_A":
            abiertos_A += 1

listo_para_operacion = (abiertos_A == 0)
```

Pero — y acá viene la fricción honesta — **el resultado "listo_para_operacion" no es un hecho atómico que el grafo guarde**. Es lógica derivada que se computa al vuelo, igual que el marcador del partido de fútbol (cap. 24) o el balance de una cuenta bancaria (cap. 18). El cap. 27 marca esta pieza — el motor de inferencia que evalúa reglas declarativas sobre el grafo y materializa resultados derivados — como el primer trabajo pendiente del proyecto.

Lo que el modelo **sí** garantiza es que los datos para esa derivación están ahí, completos, sin pérdida. La regla puede ejecutarse en Python ad-hoc, en Datalog cuando llegue el motor, o en un LLM que entienda el lexicon. La separación entre "el dato como hecho" y "el resultado derivado por regla" es deliberada y limpia.

## Resultado del prototipo

El ejemplo Python ([`prototipo/ejemplos/minera.py`](https://github.com/joseabantomarin/WQuestions/blob/main/prototipo/ejemplos/minera.py)) modela los nueve casos con 139 individuos en seis ejes y 172 hechos atómicos. Las 18 validaciones pasan:

```
✓  Jerarquía espacial: frente → banco → nivel → tajo → yacimiento
✓  D6: camión operativo→mantenimiento→operativo (a lo largo de años)
✓  Turno con 3 operadores asignados (rol de dominio multi-valor)
✓  Producción con múltiples unidades: 2400 t @ 8.2 g/t
✓  Producción de oro calculada como sub-situación parte_de extracción
✓  D5: desprendimiento de roca SIN agente humano, con causa física
✓  Cadena causal: accidente ← desprendimiento ← debilitamiento estructural
✓  Accidente parte_de el turno articulador
✓  D7: reporte ambiental motivado_por medición + justificado_por norma
✓  D5: sensor de calidad de aire como agente Q (no humano)
✓  WH: ¿cuánto mineral extrajo el operador Quispe?
✓  Política liberal: ley_mineral / ley_unidad / extraido admitidos sin declarar
✓  Acceptance criterion separado del valor medido (8 bar mín. vs 8.4 bar real)
✓  Tres sign-offs paralelos sobre el mismo test (contratista + owner + QA)
✓  Severidad ordenada en K vía atributo `nivel_severidad`: A=1 < B=2 < C=3
✓  Punchitem con 3 roles Q distintos: agente + responsable + verificador
✓  D6: punchitem A pasó por abierto → en_progreso → cerrado
✓  Estado agregado derivado: comisionamiento OK cuando 0 punchitems A abiertos

Resultado: 18/18 validaciones pasadas.
```

## Qué quedó probado en este capítulo

La minería pone a trabajar a **D5 en su forma más radical**: hay eventos físicos puros — el desprendimiento de roca, el debilitamiento estructural — que **ningún agente humano hizo**, y sin embargo son tan importantes como cualquier acción intencional. El modelo los acepta sin gimnasia porque la signatura no exige agente; basta con `causado_por` para reconstruir la cadena causal completa hasta su origen.

La **estructura espacial profunda** (cinco niveles jerárquicos) se modela igual que las subdivisiones territoriales municipales: con un rol de dominio `dentro_de` admitido por política liberal. El **equipo con ciclo de vida de 15 años** queda trazable con la maquinaria bitemporal de D6, que ya usamos en el banco para préstamos y en la universidad para salarios y calificaciones. Los **sensores como agentes no humanos** son la misma idea que la app del taxi y el motor antifraude del banco, aplicada al monitoreo ambiental. Los **reportes regulatorios gatillados por umbrales** son el patrón de D7 que ya vimos en la municipalidad, ahora con normas ambientales en lugar de ordenanzas.

Las **fricciones nuevas** que aportaron commissioning y punchlist quedaron resueltas con patrones ya conocidos, pero merecen estar nombradas porque aparecerán en cualquier proyecto industrial pesado:

- **Acceptance criterion con tolerancia separado del valor medido** — el criterio vive como objeto reificado con sus límites; el test apunta al criterio por `verifica_criterio` y registra sus valores reales aparte. El "pasa/falla" sigue siendo lógica de regla externa.
- **Sign-off paralelo de múltiples partes** sobre el mismo test — cada firma es una situación reificada con `agente` distinto que apunta al test por `tema`. Tres firmas, tres situaciones, una sola consulta para reconstruirlas.
- **Severidad ordenada en K** vía un atributo numérico `nivel_severidad` — patrón genérico para cualquier categoría que necesite orden (prioridades, grados, escalas Likert). El catálogo K no impone orden; el dominio lo declara.
- **Tres roles Q distintos sobre la misma entidad** (encontrado / responsable / verificador) — la política liberal acepta los roles de dominio sin protestar, y el grafo conserva las tres perspectivas separadas para auditoría.
- **Estado agregado derivado** — el "comisionamiento listo" no es un hecho atómico, es el resultado de una regla evaluada sobre los punchitems clase A abiertos. El modelo guarda los datos completos; el motor de inferencia que cap. 27 marca como pendiente es el encargado de materializar los derivados.

Es decir: **el dominio minero no exigió ninguna pieza nueva del modelo**. Lo absorbió combinando piezas que ya conocemos. El motor sigue siendo el mismo. Lo único que crece es el lexicon (cinco verbos: `extraer`, `operar_equipo`, `dar_mantenimiento`, `medir_calidad`, `reportar`) y la lista de roles de dominio (`dentro_de`, `ley_mineral`, `operador_asignado`, `calculado_de`, `umbral_arsenico`, etc.) que la política liberal acepta sin chistar.

## Cierre de la serie de dominios profundos

Con la minera cerramos la **serie completa de ocho dominios industriales** modelados en profundidad: Spa, taxi, clínica, banco, ERP, universidad, municipalidad, minera. Cada uno empujó al modelo en una dimensión distinta y cada uno fue absorbido sin extensiones especiales. La arquitectura conceptual no cambió ni una línea entre el Spa más simple y la minera más exigente — lo único que cambió fue el lexicon y los roles de dominio.

## Lo que viene

Acabamos de probar que el modelo aguanta ocho dominios industriales en profundidad. Pero un libro honesto debe ir más allá de los casos cómodos. El próximo capítulo cambia deliberadamente el ritmo: en lugar de meternos a fondo en un noveno negocio, vamos a someter al modelo a **cuatro dominios cualitativamente distintos en serie corta — música, química, fútbol y contratos** —, buscando explícitamente dónde se resiste. Algunos casos se resuelven con elegancia; otros exigen extensiones al catálogo o dejan pendientes que documentamos sin disimular. Es el capítulo donde el libro deja de mostrar lo que funciona y empieza a admitir lo que duele — porque solo conociendo los límites reales del modelo se puede saber dónde aún falta trabajo.
