# Capítulo 21 — Una municipalidad: lo normativo en cada paso

## Por qué una municipalidad estresa al modelo

Hasta ahora la Parte V vio dominios donde lo predominante era la operación: un Spa que cobra sesiones, un taxi que mueve gente, una clínica que diagnostica, un banco que mueve plata, un ERP que coordina módulos, una universidad que enseña. En todos ellos, "lo que pasa" — el evento — era el centro de gravedad.

Una **municipalidad** introduce una dimensión distinta. Acá, lo que sucede no se entiende sin la **norma que lo autoriza**. Una licencia de funcionamiento no se emite "porque sí": se emite **porque la ordenanza 237-2024 establece los requisitos y un funcionario verificó que se cumplieron**. Una multa de tránsito no se aplica caprichosamente: se aplica **porque el artículo 42 de la ordenanza 158-2023 lo habilita y el infractor cometió el supuesto que la norma describe**. Una resolución municipal no rectifica una multa por gusto: la rectifica **porque el recurso ciudadano fue declarado procedente conforme al artículo 15 del procedimiento administrativo**.

En todos estos casos, el "porque" del Estado tiene dos caras simultáneas: una cara **fáctica** (qué ocurrió en el mundo) y una cara **normativa** (qué regla lo autoriza). Cualquier sistema municipal serio tiene que registrar las dos, y poder responder por separado a preguntas como:

- *¿Por qué se aplicó esta multa?* — Por el hecho de estacionar en zona prohibida.
- *¿Bajo qué autoridad legal se aplicó esta multa?* — Por el artículo 42 de la ordenanza 158-2023.

WQuestions las separa exactamente con las relaciones de **D7**: `causado_por` apunta a la causa fáctica; `justificado_por` apunta a la norma. Las dos coexisten sin pisarse y, lo más importante, **el grafo permite reconstruir cualquier acto del Estado hacia atrás hasta su fundamento legal** con un par de saltos.

Este capítulo modela cinco escenarios típicos del gobierno local. Lo que vamos a ver es que la maquinaria del modelo ya alcanza para representar lo normativo sin extensiones especiales — basta con que las ordenanzas y los artículos vivan en O como cualquier otra entidad, y que las relaciones del "por qué" se usen sistemáticamente.

## La arquitectura del dominio municipal

El mapeo a las ocho coordenadas:

- **Funcionarios, alcalde, inspectores, policías municipales, ciudadanos, empresas** viven en **Q**. La municipalidad misma es persona jurídica (otro Q).
- **Ordenanzas, artículos, expedientes, solicitudes, licencias, multas, resoluciones, recursos, denuncias** viven en **O**. Cada uno con identidad propia y trazabilidad.
- **Distritos, barrios, manzanas, lotes, avenidas** viven en **L**, organizados en una jerarquía territorial vía un rol de dominio `dentro_de` (L→L), porque `parte_de` canónico es O→O.
- **Fechas de emisión, vigencia, infracción, resolución** viven en **T**.
- **Montos de multas, cantidades** viven en **N**.
- **Estados (en_revisión, aprobada, vigente, suspendida, revocada), conclusiones (procedente, improcedente), tipos de infracción** viven en **K**.

Las decisiones de diseño que más se ejercitan aquí son: **D7** (las dos relaciones del "por qué" operan en paralelo, una fáctica y una normativa), **D4** (cada acto administrativo — solicitud, inspección, emisión, denuncia, multa, resolución — es una situación reificada con identidad propia), **D6** (los estados de un expediente cambian en el tiempo y se preservan), y **D8** (la política liberal admite roles específicos como `dentro_de`, `vigente_en`, `emitida_por`, `tipo_solicitado` sin tocar el catálogo).

## Caso 1 — Las ordenanzas como autoridad normativa

El primer punto importante: **las ordenanzas viven en el grafo igual que cualquier otra entidad**. Una ordenanza es un objeto en O con sus propios atributos: número, fecha de emisión, autoridad que la dictó, tema sobre el que regula. Sus artículos son sub-objetos vinculados por `parte_de` — la misma relación que usamos para BOM en el ERP o para la jerarquía académica en la universidad.

```python
ordenanza_transito = u.add_individual(Individual(
    id="ord_158_2023_transito", axis=Axis.O,
    label="Ordenanza 158-2023 (tránsito)"))

articulo_42 = u.add_individual(Individual(
    id="art_42_ord_158", axis=Axis.O,
    label="Artículo 42 (estacionamiento prohibido)"))
u.assert_fact(articulo_42, "parte_de", ordenanza_transito)
u.assert_fact(articulo_42, "monto_multa", n(450, "USD"))
```

Una ordenanza tiene fecha de vigencia, autor (la municipalidad), y un tema normativo. Si mañana se modifica, la nueva versión es otra ordenanza con su propia identidad — y la modificación queda registrada como una relación entre ambas. La maquinaria de D6 garantiza que las multas aplicadas bajo la versión vieja sigan siendo trazables hacia el texto que las habilitó.

## Caso 2 — Subdivisiones territoriales jerárquicas

La municipalidad gestiona territorio. El territorio se subdivide en distritos; los distritos en barrios; los barrios en manzanas; las manzanas en lotes. Cada uno es un punto en L. La jerarquía se establece con `dentro_de`:

```python
u.assert_fact(distrito_centro, "dentro_de", ciudad_norte)
u.assert_fact(barrio_san_jose, "dentro_de", distrito_centro)
u.assert_fact(manzana_12,      "dentro_de", barrio_san_jose)
u.assert_fact(lote_4,          "dentro_de", manzana_12)
```

Nota técnica: `parte_de` está declarado en el catálogo D8 como `O → O`. Para jerarquías de lugares (L → L), usamos un rol de dominio `dentro_de` que la **política liberal** acepta sin validar — el motor no protesta y la semántica queda clara para humanos y LLMs. La cadena se puede recorrer recursivamente para responder cualquier consulta tipo *"¿qué lote es este?"* devolviendo `lote_4 → manzana_12 → barrio_san_jose → distrito_centro → ciudad_norte` con un solo recorrido.

## Caso 3 — Una licencia de funcionamiento: solicitud → revisión → emisión

Café del Norte SAC quiere abrir un local de café en el lote 4 del barrio San José. El proceso real tiene tres actos administrativos encadenados, cada uno reificado:

1. **Solicitud**: la empresa solicita la licencia, indicando dónde quiere operar.
2. **Inspección**: un inspector municipal visita el local y certifica que cumple los requisitos.
3. **Emisión**: la municipalidad emite la licencia, válida por un año.

Cada acto es una situación con su `agente`, `momento`, `lugar_de` y resultado. Las tres se conectan con `motivado_por`: la inspección está `motivado_por` la solicitud; la emisión está `motivado_por` tanto la solicitud como la inspección. Y la emisión cierra con el cable más importante: `justificado_por`, apuntando a la ordenanza:

```python
licencia = ingest_situation("emitir", roles={
    "agente": municipalidad,
    "tipo_emitido": category("licencia_funcionamiento"),
    "beneficiario": cafe_norte,
    "momento": at("2026-03-25T16:00"),
    "justificado_por": ordenanza_funcionamiento,
    "valido_desde": at("2026-04-01T00:00"),
    "valido_hasta": at("2027-03-31T23:59"),
})
u.assert_fact(licencia, "motivado_por", solicitud)
u.assert_fact(licencia, "motivado_por", inspeccion)
```

Lo notable: **el grafo permite responder con precisión** preguntas tipo *"¿bajo qué ordenanza fue emitida la licencia de Café del Norte?"* con un único salto desde la licencia siguiendo `justificado_por`. Y *"¿qué motivó la emisión?"* devuelve dos respuestas — la solicitud original y la inspección — porque `motivado_por` es multi-valor.

Mientras tanto, el estado de la solicitud cambia con vigencia (D6): estuvo `en_revision` entre el 5 y el 25 de marzo; quedó `aprobada` desde entonces. Ambos estados conviven en el grafo, y la pregunta *"¿en qué estado estaba la solicitud el 15 de marzo?"* tiene una respuesta exacta.

## Caso 4 — Una denuncia ciudadana abre un expediente

Sofía Romero, vecina del barrio San José, denuncia que el local del Café del Norte genera ruidos molestos por la noche. La denuncia se modela como una situación con agente (Sofía) y `paciente` (el café denunciado), más un `tema` que reifica el ruido específico observado:

```python
denuncia = ingest_situation("denunciar", roles={
    "agente": sofia,
    "tema": motivo_denuncia,        # ruido nocturno reificado
    "paciente": cafe_norte,
    "lugar_de": lote_4,
    "momento": at("2026-06-16T09:00"),
})
```

La denuncia dispara un **expediente administrativo** — otra entidad en O — que agrupa por `parte_de` todas las diligencias que el municipio realice para procesarla. La inspección nocturna que el inspector Quispe hace cinco días después es `parte_de` el expediente. Si después se agregan más diligencias (citación al denunciado, descargo, resolución), todas viven dentro del mismo expediente.

```python
expediente = u.add_individual(Individual(id="exp_2026_001", axis=Axis.O))
u.assert_fact(expediente, "motivado_por", denuncia)
u.assert_fact(insp_nocturna, "parte_de", expediente)
```

El expediente como entidad articuladora es exactamente el patrón que vimos con el `viaje_001` del taxi y la `transferencia_001` del banco: una situación superior que reúne todos sus actos secundarios. La consulta *"¿qué diligencias se hicieron en este expediente?"* es una proyección directa por `parte_de`.

## Caso 5 — Multa de tránsito con doble "por qué"

Acá viene el caso paradigmático del capítulo. Juan Mendoza estaciona su vehículo en zona prohibida sobre la Avenida Principal el 8 de julio a las 14:32. Tres minutos después, el policía municipal le aplica una multa de 450 dólares. El modelado registra la cadena completa:

- La **infracción** misma se reifica como una situación con tema (el vehículo de Juan), lugar (Av. Principal), momento, y tipo categórico (estacionamiento prohibido).
- La **multa** se reifica como otra situación, con su agente (el policía), paciente (Juan), monto, lugar, momento y — esto es lo crucial — **dos relaciones del "por qué"**:

```python
multa = ingest_situation("multar", roles={
    "agente": policia_mun,
    "paciente": juan,
    "monto": n(450, "USD"),
    "lugar_de": av_principal,
    "momento": at("2026-07-08T14:35"),
    "causado_por": infraccion,         # CAUSA FÁCTICA
    "justificado_por": articulo_42,    # AUTORIDAD NORMATIVA
})
```

Esta es la forma del modelo que solo D7 permite. La multa **es causada por** la infracción (sin ella no habría motivo para sancionar) y **es justificada por** el artículo 42 (sin él, el funcionario no tendría base legal para sancionar). Las dos relaciones son verdaderas a la vez y dicen cosas distintas. En sistemas tradicionales, esto se modela típicamente con una columna `motivo` que mezcla las dos cosas — un texto libre que el ciudadano no puede impugnar y el sistema no puede consultar limpiamente.

![La cadena normativa de una multa municipal: dos `por qué` en paralelo. La multa está conectada por `causado_por` hacia la infracción fáctica (izquierda) y por `justificado_por` hacia el artículo de la ordenanza (derecha). Abajo, el recurso de reconsideración y la resolución que la deja sin efecto cierran el ciclo. Toda acción del Estado tiene fundamento factual y fundamento legal — D7 los registra como cables distintos.](../diagrams/png/47_municipalidad_cadena_normativa.png)

## Caso 6 — Recurso de reconsideración y rectificación

Juan no está de acuerdo con la multa. El 15 de julio presenta un recurso de reconsideración argumentando que la zona no estaba debidamente señalizada. El recurso se modela como una situación nueva:

```python
recurso = Individual(id="recurso_juan_001", axis=Axis.O)
u.assert_fact(recurso, "agente", juan)
u.assert_fact(recurso, "tema", multa)     # apunta a la multa que impugna
u.assert_fact(recurso, "motivado_por", motivo_falta_senalizacion)
```

Tres semanas después, el alcalde resuelve el recurso. Lo declara **procedente**, lo que significa que la multa queda sin efecto:

```python
resolucion = ingest_situation("resolver", roles={
    "agente": alcalde,
    "tema": recurso,
    "conclusion": procedente,
    "momento": at("2026-08-05T16:00"),
    "justificado_por": art_15_norma_proc_admin,
})
u.assert_fact(resolucion, "rectifica", multa)
u.assert_fact(multa, "estado", revocada,
              valid_from=datetime(2026, 8, 5, 16, tzinfo=timezone.utc))
```

Dos cosas pasan en paralelo: la resolución `rectifica` la multa (es la trazabilidad explícita: este acto cambió aquel acto), y el estado de la multa cambia a `revocada` desde el momento exacto de la resolución (D6). La multa **no se borra** del grafo — sigue ahí, sigue siendo consultable, sigue formando parte del expediente del ciudadano. Lo que cambia es su validez vigente. Y, gracias a D6, todavía podemos responder *"¿estaba esa multa vigente el 1 de agosto?"* (sí) y *"¿y el 10 de agosto?"* (no, revocada).

Esta es la promesa concreta del modelo para el sector público: **ningún acto administrativo se borra; cada uno deja rastro completo, con sus motivos, sus fundamentos, su resultado y su eventual rectificación**. Cualquier auditor — un órgano de control interno, un tribunal contencioso administrativo, un periodista de investigación — puede reconstruir el historial completo sin perderse en versiones inconsistentes de tablas que se sobreescribieron.

## Resultado del prototipo

El ejemplo Python ([`prototipo/ejemplos/municipalidad.py`](https://github.com/joseabantomarin/WQuestions/blob/main/prototipo/ejemplos/municipalidad.py)) modela los seis casos con 75 individuos en seis ejes y 88 hechos atómicos. Las once validaciones pasan:

```
✓  Subdivisión territorial: lote → manzana → barrio → distrito → ciudad
✓  D7: licencia justificada_por la ordenanza 237-2024
✓  D7: licencia motivada_por solicitud + inspección
✓  D6: solicitud en_revision el 15-Mar, aprobada el 1-Abr
✓  Cadena causal de la multa: causado_por infracción + justificado_por art.42
✓  Expediente administrativo motivado_por la denuncia ciudadana
✓  Inspección nocturna parte_de el expediente 2026-001
✓  Recurso procedente → multa revocada (D6 + rectifica)
✓  Resolución rectifica la multa original
✓  WH: ¿quién emitió la licencia a Café del Norte?
✓  Política liberal: valido_desde/valido_hasta/vigente_en admitidos sin declarar

Resultado: 11/11 validaciones pasadas.
```

## Qué quedó probado en este capítulo

El dominio municipal pone a trabajar **D7 en su forma más exigente**: cada acto del Estado tiene fundamento factual y fundamento normativo, y el modelo los preserva como dos relaciones distintas que se pueden consultar independientemente. La pregunta *"¿por qué se aplicó esta multa?"* tiene dos respuestas válidas según se interprete el "porque" — y el modelo distingue cuál se está pidiendo.

Las **jerarquías territoriales en L**, los **expedientes que articulan múltiples diligencias**, y los **recursos que rectifican actos previos sin borrarlos** son patrones que aparecen también en otros dominios del sector público — sanitario, judicial, tributario, ambiental. Lo que probamos acá no es solo "el modelo absorbe una municipalidad"; es que **una familia completa de aplicaciones gov-tech encaja con el mismo motor**, sin extensiones especiales, sin proyectos de integración entre módulos administrativos.

Y, una vez más, **el motor no creció ni una línea**. Lo único que creció fue el lexicon — siete verbos administrativos (`solicitar`, `revisar`, `emitir`, `denunciar`, `inspeccionar`, `multar`, `resolver`) con sus signaturas, más un dialecto municipal que mapea "ciudadano", "vecino", "denunciante", "infractor" a sus roles canónicos.

## Lo que viene

El último dominio gigante de esta serie es probablemente el más alejado del mundo de oficina: una **operación minera**. Lo que estresa al modelo allá no es ni la integración cross-módulo del ERP, ni los timelines largos de la universidad, ni la fundamentación normativa de la municipalidad. Es una mezcla nueva: **dimensiones físicas y espaciales** (yacimientos, niveles de tajo, turnos), **incidentes de seguridad sin agente humano** (la roca que se desprendió, el cable que falló), **mantenimiento de equipos con ciclos de vida largos** (un camión minero que opera 15 años), y **producción registrada en múltiples unidades de medida** que tienen que poder convertirse. Veremos cómo el modelo absorbe ese mundo aplicando exactamente las mismas piezas que hemos usado hasta aquí.
