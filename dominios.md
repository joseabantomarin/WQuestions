# Dominios analizados — registro literal

Este documento preserva el **texto exacto** de cada prueba de dominio que hicimos sobre WQuestions entre 2026-05-12 y 2026-05-14: tu prompt original y mi análisis completo en su momento. Es el material crudo, sin resumir, que después destilamos en `WQuestions.md` y que sirve de fuente para los capítulos de aplicación del libro.

## Nota sobre la nomenclatura

Los análisis de abajo usan la **nomenclatura original** del proyecto, anterior al renombramiento del 2026-05-14:

| Original | Actual | Significado |
|---|---|---|
| T | O | qué (*objectum*) |
| M | T | cuándo (*tempus*) |
| R | M | cómo (*modus*) |

Q, L, N, P, K no cambiaron. Donde el texto dice "T → Q" léase "O → Q"; donde dice "en M" léase "en T"; donde dice "etiqueta de R" léase "etiqueta de M".

## Nota sobre el primer bloque (aeropuerto, ventas, taxi)

Los tres primeros dominios fueron los primeros que probamos y se guardaron originalmente en [conversacion1.md](conversacion1.md). En el momento de guardar esa conversación, **partes de los análisis se condensaron entre corchetes** (`[Se modeló venta_001 con cliente, vendedor, líneas de venta…]`). Esos corchetes son el resumen-en-su-momento; el texto literal completo de esas porciones se perdió en ese paso. Conservo aquí el contenido tal como quedó en `conversacion1.md`, marcando las elipsis con `[...]`.

Los cinco dominios posteriores (historia clínica, música, contrato, química, fútbol) están recuperados literalmente desde el log de sesión, sin pérdida.

---


# Dominio 1 — Aeropuerto

## Prompt del usuario (turno 3 de conversacion1.md)

> Creo que antes de continuar tengo que darte el panorama completo de lo que pretendo, porque por ejemplo en las cualidades multivaluadas pueden haber 2 o más elementos. En ese caso ya está surgiendo una nueva propiedad o coordenada llamada "cuanto". En mi criterio quiero definir el siguiente multiverso formado por: quien (persona), que (objeto), donde (ubicacion), cuando (fecha-hora), cual (propiedad), cuanto (cantidad), como (enlace).
>
> Lo que pasa es que por ejemplo cualquiera de ellas puede tener propiedades (cual), o cualquiera puede ubicarse respecto a la otra. Para mejor comprensión voy a explicarte que lo que necesito es modelar la información basándome en esas coordenadas (preguntas) por ejemplo, estoy actualmente en el aeropuerto pensando viajar a Lima. En ese contexto hay varios quien: el pasajero (yo), el que me ha atendido, el piloto y habrá otros pero ya resultan irrelevantes para una futura consulta, salvo otros contextos.
>
> Hay varios que, entre otros, mi equipaje, el avión y mi tarjeta de embarque, el cuando es: hoy a las 10 el viaje, a las 12 el arribo, el donde puede ser donde me embarco y donde desembarco, el cuanto puede ser la cantidad de pasajeros, el numero que indica mi asiento, etc, el como es la definición de cómo es el viaje (puede tener varias características o "cualidades"), y así en diferentes contextos, la información resulta siendo acumulable, y la idea es en el futuro acceder a esa información ubicando solo puntos en esas coordenadas para agilizar las búsquedas, validar datos y otras operaciones con esas coordenadas.

## Mi análisis en su momento

Ahora veo el panorama. Lo que describes es un **modelo de hechos n-dimensional** donde cada unidad de información es una tupla que ocupa coordenadas en este espacio de 7 ejes, y un "contexto" (el aeropuerto, el viaje) es simplemente un subconjunto de tuplas que comparten anclajes en algunos de esos ejes.

### Mi lectura del modelo

Los 7 ejes **no son del mismo tipo**, y conviene reconocerlo desde ya:

**Ejes de valor** (contienen instancias del mundo):
- `quien` — agentes
- `que` — objetos / cosas
- `donde` — ubicaciones
- `cuando` — momentos / intervalos
- `cuanto` — magnitudes / cantidades

**Ejes estructurales** (no contienen instancias, sino *nombres* de relaciones entre instancias):
- `cual` — nombres de propiedades (relación 1-a-1 desde un valor hacia otro: `juan.edad = 35`)
- `como` — nombres de enlaces (relación entre instancias, posiblemente con matiz/manera: `juan viaja_en avión`, `juan es_amigo_de pedro`)

Esta distinción importa: `cual` y `como` no son lugares donde "vivan" cosas como Juan o Lima; son el **vocabulario** que permite conectar a Juan con Lima.

### Tu ejemplo del aeropuerto, modelado

Tomando el contexto `viaje_hoy` como un punto en `que` (un objeto-evento):

```
viaje_hoy ∈ que

  cual:
    pasajero            → yo            (quien)
    piloto              → ...           (quien)
    avión               → AV-1234       (que)
    tarjeta_embarque    → BP-987        (que)
    equipaje            → maleta-1      (que)
    origen              → AICC          (donde)
    destino             → LIM           (donde)
    salida              → hoy 10:00     (cuando)
    arribo              → hoy 12:00     (cuando)
    asiento             → 14B           (cuanto / que — ver abajo)
    total_pasajeros     → 180           (cuanto)

  como:
    se_realiza_en       → avión AV-1234
    embarca_en          → AICC
    desembarca_en       → LIM
```

Y a su vez `yo ∈ quien` tiene sus propias `cual` (nombre, documento, etc.) y `como` (`viaja_en viaje_hoy`, `porta tarjeta_embarque`).

### Tres tensiones que conviene resolver antes de seguir

**1. Un mismo dato puede modelarse en dos ejes distintos.**
El "asiento 14B" puede ser un `que` (el objeto físico) o un `cuanto` (el identificador/número que te asignaron). "Hoy a las 10" puede ser un `cuando` absoluto o un `cuanto` relativo ("dentro de 2 horas"). El estándar tiene que decidir: ¿se permite que la misma cosa exista en varios ejes, o cada cosa pertenece a uno solo y los demás son vistas derivadas?

**2. ¿Qué es un "contexto" formalmente?**
Tú dices que en este contexto el pasajero detrás de ti es irrelevante. Eso sugiere que un contexto no es una etiqueta vaga, sino un **punto-evento** (probablemente un `que` o un `cuando`) al que se "cuelgan" todas las tuplas relevantes. Resolver esto define cómo se filtra y se acumula: cada hecho lleva implícita o explícitamente la referencia al contexto en que es cierto.

**3. `como` vs `cual` — frontera fina.**
"avión" como medio de transporte puede expresarse:
- vía `cual`: `viaje.medio = avión` (propiedad funcional)
- vía `como`: `viaje se_realiza_en avión` (enlace)

Ambos son válidos. ¿La regla será sintáctica (todo enlace entre dos *instancias* es `como`, todo lo demás es `cual`) o semántica (el modelador elige según el matiz)? Esto define qué tan canónica/única es la representación de cada hecho.

### Formalización posterior (turno 5)

Tras la formalización LaTeX (turno 4) que no se pudo renderizar, el ejemplo del aeropuerto se reescribió en texto plano:

`viaje_hoy ∈ T`:

```
(viaje_hoy, pasajero,   yo)
(viaje_hoy, aeronave,   AV1234)
(viaje_hoy, origen,     AICC)
(viaje_hoy, destino,    LIM)
(viaje_hoy, salida,     hoy_10:00)
(viaje_hoy, asiento,    a14B)
(a14B,      codigo,     "14B")
```

Acá se ilustra D1 (un dato vive en un solo eje): el asiento 14B es **dos individuos** — `a14B ∈ T` (el objeto) y `"14B" ∈ N` (el código), conectados por la propiedad `codigo`.

---

# Dominio 2 — Ventas (sistema comercial)

## Prompt del usuario (turno 8 de conversacion1.md)

> Veamos la aplicación en otro contexto. Necesito diseñar un sistema de venta, tengo los quien: el cliente, el vendedor, la empresa; los que: los productos, las unidades; los donde: el local, la caja, la sucursal; los cuando: fecha de emisión, fecha de impresión, fecha de entrega; los cuanto: cantidad de producto, precio unitario, IGV; los cual: nombre del cliente, dirección del cliente, RUC del cliente, nombre del vendedor, licencia del vendedor, nombre del producto, unidad del producto, unidad al vender; los como: forma de pago, tipo de transacción.

## Mi análisis en su momento

Antes de modelar, voy a señalar un patrón importante en cómo organizaste las listas.

### El patrón: estás mezclando tres cosas distintas

En tus 7 listas aparecen mezclados:

- **(a) Individuos**: instancias concretas (Juan Pérez, Sucursal Miraflores, 2026-05-12 14:30).
- **(b) Tipos / clases / roles**: categorías que agrupan individuos (cliente, producto, sucursal).
- **(c) Nombres de propiedades**: etiquetas que conectan individuos (nombre del cliente, fecha de emisión, cantidad).

| Eje | Lo que listaste | Naturaleza |
|-----|-----------------|-----------|
| Q (quien) | cliente, vendedor, empresa | **Roles** — no individuos |
| T (que) | productos, unidades | **Clases** — no individuos |
| L (donde) | local, caja, sucursal | **Clases** — no individuos |
| M (cuando) | fecha de emisión, impresión, entrega | **Nombres de propiedades**, no momentos |
| N (cuanto) | cantidad, precio unitario, IGV | **Nombres de propiedades**, no cantidades |
| P (cual) | nombre del cliente, RUC, etc. | Correcto — son propiedades |
| R (como) | forma de pago, tipo de transacción | Correcto (o se pueden tratar como P) |

### Insight clave: los roles son propiedades, no individuos.

"Cliente" no es un `quien`. Es una propiedad `cliente : T → Q` que dice: "la venta `v` tiene como cliente a la persona Juan".

### La pieza central que falta: la venta

No mencionaste el `que` más importante del sistema: **la venta misma**. En el modelo, la venta es una situación (individuo en T) que sirve de ancla para colgar todos los hechos.

`[Se modeló venta_001 con cliente, vendedor, líneas de venta, productos como SKUs, fechas, montos, etc. El texto completo de este modelado se condensó en su momento al guardarse en conversacion1.md.]`

### Tres observaciones para discutir

1. **Roles vs Q múltiple**: una misma persona puede ser cliente en una venta y vendedor en otra.
2. **"Sucursal" en L o en T?**: es a la vez ubicación y entidad organizacional. La sucursal-organización es T, su ubicación física es L.
3. **"Productos" vs "unidades"**: SKU vs unidad de medida.

## Mi observación posterior sobre el "cuanto" y el dominio (turno 9)

`[El usuario observó que el "cuanto" tenía dos sabores — cardinalidad vs magnitud — y pidió formalizar la creación de "dominios" (categorías como kg, PEN, boleta). En respuesta se propuso agregar el 8º eje K (clase / concepto / categoría) para alojar todos los tipos abstractos. También se aclaró que la agencia del "quien" no se define por "ser persona" sino por capacidad de acción, y que cuando un T (robot, script, app) actúa como agente en un contexto específico no se lo mueve a Q sino que se marca contextualmente con la propiedad `agente`. Esto se consolidó como D4 (conceptos abstractos en K) y D5 (agencia contextual).]`

---

# Dominio 3 — App de taxi

## Prompt del usuario (turno 13 de conversacion1.md)

> Ahora veamos otro contexto: quiero hacer una app de taxis. El usuario abre la app, quien determina su punto de origen (por GPS), el usuario pone el destino, y el app busca un taxi disponible, al encontrarlo devuelve placa, nombre del taxista y tiempo de espera, también precio por la carrera. El usuario espera, llega a su destino y paga.
>
> Analiza también si podemos agregar el why (porqué) y cómo nos sirve para nuestro modelo.

## Mi análisis en su momento

Vamos por partes. Primero modelo el app de taxi con los 8 ejes, luego analizo si "why" merece eje propio.

### Modelado del app de taxi

`[Se modelaron 5 fases en T: solicitud_001, emparejamiento_001, info al usuario, viaje_001, pago_001. Cada una como situación con sus hechos (agente, paciente, origen, destino, instrumento, momento). Se ilustró D5 con app_taxi actuando como agente en la situación de emparejamiento. El texto completo de este modelado se condensó en su momento al guardarse en conversacion1.md.]`

### Análisis: ¿agregar "why" como eje?

Mi conclusión: **no**, pero **sí reconocer una familia canónica de "relaciones de por qué" dentro de R**.

#### Cuatro tipos de "why" y sus valores

| Pregunta | Valor del "por qué" | Eje del valor |
|---|---|---|
| 1. Cancelación | una **situación** previa | T |
| 2. Asignación | un **criterio / concepto** | K |
| 3. Solicitud | un **objetivo / situación futura** | T |
| 4. Tarifa | una **regla / norma** | T o K |

Los valores son **heterogéneos**. No hay un dominio coherente "lugares-donde-viven-los-porqués".

#### Mejor solución: "why" es una *categoría de relaciones* en R

```
causado_por      : T → T          // por-qué causal
motivado_por     : T → Q ∪ K      // por-qué motivacional
con_finalidad    : T → T ∪ K      // por-qué teleológico
justificado_por  : T → T ∪ K      // por-qué normativo
```

### Recomendación concreta

1. Mantener 8 ejes.
2. Añadir D6: las cuatro relaciones canónicas de por qué.
3. Documentarlo en WQuestions.md.

## Refinamiento posterior — preguntas refinadas como roles (turno 15)

A raíz de la pregunta del usuario sobre si "para qué, por dónde, de dónde, hacia dónde, con quién, con cuál, por cuánto" eran ejes nuevos, se concluyó que **son roles, no ejes**:

| Pregunta | Ejemplo de respuesta | Eje de la respuesta |
|---|---|---|
| **para qué** | "para llegar al aeropuerto" | T (intención) o K (concepto) |
| **por dónde** | "por la Vía Expresa" | L o T |
| **de dónde** | "desde Miraflores" | L |
| **hacia dónde** | "hacia el aeropuerto" | L |
| **con quién** | "con mi familia" | Q |
| **con cuál** | "con mi laptop" | T o K |
| **por cuánto** | "por 18.50 soles" | N |

**Ninguna de estas 7 preguntas pide un tipo de cosa que no exista ya en los 8 ejes.** Lo que las distingue es *qué rol cumple esa cosa* en la situación.

### Comparación con neo-davidsoniano

Las 7 preguntas coinciden 1-a-1 con roles temáticos canónicos:

```
Agent       ≈ agente
Patient     ≈ paciente
Source      ≈ origen           (de dónde)
Goal        ≈ destino          (hacia dónde)
Path        ≈ via              (por dónde)
Instrument  ≈ instrumento      (con cuál)
Beneficiary ≈ beneficiario     (para quién)
Comitative  ≈ acompañantes     (con quién)
Cause       ≈ causado_por
Purpose     ≈ con_finalidad    (para qué)
```

Esto se consolidó como **D7: catálogo canónico de roles**, materializados como etiquetas en P con signaturas tipadas. Las preguntas refinadas son ROLES, no ejes.

---

# Dominio 4 — Historia clínica

## Prompt del usuario

> empecemos con el NIVEL 1 de prueba, dominio: historia clinica

## Mi análisis en su momento

Empezamos. Voy a usar una narrativa concreta y compacta, modelar paso a paso, e ir señalando explícitamente cada fricción a medida que aparezca. Al final, inventario de las fricciones y propuestas de patch.

## Narrativa

> María Gonzales, 45 años, asiste al consultorio del Dr. Pedro Ramos en la Clínica San Pablo, Lima, el 13 de mayo de 2026 a las 10:00. Se queja de dolor de cabeza recurrente desde hace 2 semanas. El Dr. Ramos la examina: presión arterial 145/95 mmHg, temperatura 36.8°C. Le solicita análisis de sangre. La diagnostica con hipertensión grado 1. Le prescribe Losartán 50 mg, una pastilla cada mañana durante 30 días. Le indica volver en 3 semanas para control. María paga S/120 a la clínica.

## Individuos por eje

```
Q:  maria_gonzales, dr_ramos, clinica_san_pablo
T:  consulta_001, examen_001, diagnostico_001, prescripcion_001,
    pago_001, control_futuro_001, sintoma_maria_001
L:  av_javier_prado_1234 (dirección de la clínica)
M:  2026-05-13_10:00, 2026-04-29 (inicio del síntoma), 2026-06-03 (control)
N:  45, 145, 95, 36.8, 50, 1, 30, 3, 120, 2
K:  persona_natural, medico, paciente, clinica_privada,
    accion_consultar, accion_examinar, accion_diagnosticar,
    accion_prescribir, hipertension_grado_1, dolor_cabeza,
    recurrente, losartan_50mg, losartan, miligramo, pastilla,
    cada_mañana, dias, mmHg, celsius, soles, cardiologia
```

## Fase 1 — La consulta (situación contenedora)

```
(consulta_001, instancia_de,  accion_consultar)
(consulta_001, agente,        dr_ramos)            // quién atiende
(consulta_001, paciente,      maria_gonzales)      // a quién
(consulta_001, lugar_de,      clinica_san_pablo)
(consulta_001, momento,       2026-05-13_10:00)
```

> 🔸 **Fricción 1 — Clínica como Q y L a la vez**. `clinica_san_pablo` es una *persona jurídica* (Q) y también tiene una ubicación física. Por D1 vive en un solo eje. Resolución: `clinica_san_pablo ∈ Q` con propiedad `direccion : Q → L`. Esto **ya estaba resuelto** en el caso de ventas (mismo patrón con `acme_sac`). Sin patch nuevo.

```
(clinica_san_pablo, instancia_de, clinica_privada)
(clinica_san_pablo, direccion,    av_javier_prado_1234)
(dr_ramos, instancia_de, persona_natural)
(dr_ramos, especialidad, cardiologia)              // K
(maria_gonzales, instancia_de, persona_natural)
(maria_gonzales, edad, 45)                          // → N
```

> 🔸 **Fricción 2 — Especialidad médica**. `cardiologia` es propiedad estable de la persona, no rol contextual. Tratada como propiedad `especialidad : Q → K`. Distinto del rol `agente` que es contextual (D5). Sin patch nuevo.

## Fase 2 — El síntoma

```
(sintoma_maria_001, instancia_de,   dolor_cabeza)   // → K
(sintoma_maria_001, experimentador, maria_gonzales)
(sintoma_maria_001, inicio,         2026-04-29)
(sintoma_maria_001, patron,         recurrente)     // → K
(sintoma_maria_001, motivo_consulta_para, consulta_001)
```

> 🔸 **Fricción 3 — Síntoma: ¿K o T?** El "dolor de cabeza" como concepto general es K; la experiencia específica de María es T (con inicio, intensidad, patrón). Modelado: `sintoma_maria_001 ∈ T` con `instancia_de → dolor_cabeza ∈ K`. Sin patch, consistente con cómo modelamos cualquier situación.

> 🔸 **Fricción 4 — "Recurrente" como patrón temporal**. Vimos esto antes en "Juan corre por las mañanas". `M` admite puntos e intervalos, pero no patrones de recurrencia. Resolución temporal: tratar el patrón como una categoría en `K` (`recurrente`, `cada_mañana`, `cada_8_horas`). Suficiente para queries cualitativas, no para cálculo de fechas concretas.
>
> **Patch tentativo (anotar en pendientes)**: `M` debería admitir patrones temporales además de puntos e intervalos. Forma posible: un patrón temporal es un T-individuo con propiedades `frecuencia`, `unidad_frecuencia`, `inicio`, `fin`.

## Fase 3 — El examen físico

```
(examen_001, instancia_de,        accion_examinar)
(examen_001, agente,              dr_ramos)
(examen_001, paciente,            maria_gonzales)
(examen_001, parte_de,            consulta_001)        // mereología
(examen_001, presion_sistolica,   145)                 // mmHg
(examen_001, presion_diastolica,  95)
(examen_001, temperatura,         36.8)                // celsius
```

> 🔸 **Fricción 5 — Mediciones con unidad**. Acá hay que decidir entre opción simple (unidad en el nombre: `presion_sistolica_mmHg`) y rica (reificar la medición como mini-situación). Aplico la **opción simple por ahora**, anotando que medicina es uno de los dominios que **eventualmente** justifica reificar magnitudes (rangos de referencia, conversiones de unidades, intervalos de confianza son habituales).

> 🔸 **Fricción 6 — `parte_de` no está en el catálogo canónico (D7)**. La uso aquí sin haberla declarado. Es una relación mereológica universal (todo→parte). Aparece en cualquier dominio compuesto (venta→línea, viaje→fases, consulta→eventos clínicos).
>
> **Patch propuesto**: agregar **`parte_de : T → T`** al catálogo canónico (D7). Su inversa `contiene : T → T (multi)` también. Es trivial pero estaba ausente.

## Fase 4 — El diagnóstico

```
(diagnostico_001, instancia_de,     accion_diagnosticar)
(diagnostico_001, agente,           dr_ramos)
(diagnostico_001, paciente,         maria_gonzales)
(diagnostico_001, etiqueta,         hipertension_grado_1)  // → K
(diagnostico_001, parte_de,         consulta_001)
(diagnostico_001, justificado_por,  examen_001)            // D6
(diagnostico_001, momento,          2026-05-13_10:00)
```

> 🔸 **Fricción 7 — El "rol" del diagnóstico es nuevo**. La etiqueta diagnóstica (la categoría asignada a María) no es ni el sujeto, ni un participante físico, ni un instrumento. Es **lo que el acto de diagnosticar produce**.
>
> Posibles encajes:
> - `tema` (lo que se diagnostica) → no encaja, el tema es la persona o el síntoma.
> - `producto` (lo que el acto crea) → no está en el catálogo.
> - `etiqueta_asignada` → ad hoc.
>
> **Patch propuesto**: agregar **`producto : T → V`** al catálogo canónico (D7). Es el resultado/output de una situación productiva. Aplicaría también a "el panadero hizo un pan" (`producto → pan`), "el escritor escribió un libro" (`producto → libro`), "el sistema generó la factura" (`producto → factura`). Es un rol con larga historia en VerbNet (`Result`).

## Fase 5 — La prescripción

```
(prescripcion_001, instancia_de,    accion_prescribir)
(prescripcion_001, agente,          dr_ramos)
(prescripcion_001, beneficiario,    maria_gonzales)
(prescripcion_001, parte_de,        consulta_001)
(prescripcion_001, medicamento,     losartan_50mg)         // → K
(prescripcion_001, dosis_unidad,    1)                     // N
(prescripcion_001, dosis_forma,     pastilla)              // → K
(prescripcion_001, frecuencia,      cada_mañana)           // → K (patrón)
(prescripcion_001, duracion_dias,   30)                    // N
(prescripcion_001, justificado_por, diagnostico_001)       // D6
(prescripcion_001, momento,         2026-05-13_10:00)
```

Detalle del medicamento como entidad K compuesta:

```
(losartan_50mg, instancia_de,    medicamento_formulado)
(losartan_50mg, principio_activo, losartan)               // → K
(losartan_50mg, dosis,           50)
(losartan_50mg, unidad_dosis,    miligramo)               // → K
```

> 🔸 **Fricción 8 — Estructura interna de K**. `losartan_50mg` tiene propiedades propias (`principio_activo`, `dosis`, `unidad_dosis`). Eso significa que **K admite estructura interna** (no es un conjunto plano de etiquetas opacas).
>
> **Esto ya está habilitado por el modelo**: K es un eje de individuos como cualquier otro, y los individuos pueden tener propiedades. Pero **no estaba explicitado**. Vale la pena anotarlo como **observación/clarificación**: los elementos de K son individuos de primera clase y pueden tener su propia red de hechos.

## Fase 6 — Control futuro (situación hipotética/planeada)

```
(control_futuro_001, instancia_de,        accion_consultar)
(control_futuro_001, agente_planeado,     dr_ramos)
(control_futuro_001, paciente,            maria_gonzales)
(control_futuro_001, momento_planeado,    2026-06-03)
(control_futuro_001, lugar_de_planeado,   clinica_san_pablo)
(control_futuro_001, hecho_actual,        falso)            // todavía no ocurre
(control_futuro_001, con_finalidad,       monitorear_001)
(consulta_001, prevé,                     control_futuro_001)
```

> 🔸 **Fricción 9 — Eventos futuros / planeados**. Aparecen también en el taxi (`meta_llegar_19:00`). Ya tenemos el patrón `hecho_actual: falso` heredado de D7 (modales). Pero acá hay un matiz: el control futuro no es una *intención* del paciente, es una *prescripción/plan* del médico.
>
> Conviene distinguir **modalidades** en el patrón:
> - `volitiva` (alguien quiere): "Juan quiere viajar".
> - `deontica` (alguien debe): "Juan debe pagar".
> - `prevista` (alguien planea): "el médico programa el control".
>
> Sin patch profundo. Solo enriquecer el catálogo de valores de `modalidad` en K.

> 🔸 **Fricción 10 — Roles "potenciales" en eventos no ocurridos**. Usé `agente_planeado` y `momento_planeado` en vez de `agente`/`momento` para señalar que son tentativos, no confirmados. Esto sugiere que las propiedades de eventos futuros podrían tener un **modificador** (planeado, esperado, real) en vez de duplicar etiquetas.
>
> **Patch propuesto (más sutil)**: en lugar de duplicar etiquetas, marcar la situación con `estatus_factual: planeado|confirmado|real|cancelado` y dejar los roles normales (`agente`, `momento`). El motor sabe interpretarlos según el estatus. Más limpio.

## Fase 7 — El pago

```
(pago_001, instancia_de,  accion_pagar)
(pago_001, agente,        maria_gonzales)
(pago_001, beneficiario,  clinica_san_pablo)
(pago_001, sobre_situacion, consulta_001)        // ¿esta etiqueta es canónica?
(pago_001, por_cuanto,    120)
(pago_001, moneda,        soles)
(pago_001, momento,       2026-05-13_10:30)
(pago_001, parte_de,      consulta_001)
```

> 🔸 **Fricción 11 — `sobre_situacion` no es canónica**. La uso para indicar que el pago es *por* la consulta. En el caso del taxi usamos `sobre_viaje` (también ad-hoc). En realidad es un rol genérico de **referencia a la situación causante o motivadora**.
>
> **Patch propuesto**: agregar **`referencia : T → T`** o **`sobre : T → T`** al catálogo canónico. Es un rol bisagra entre situaciones que se citan mutuamente (pago→consulta, devolución→venta, comentario→post, cita→paper).

## Fase 8 — Secuencia temporal dentro de la consulta

Los eventos siguen un orden: examen → diagnóstico → prescripción. Hay dos formas de capturarlo:

A) **Implícito** (via `momento`/`inicio`/`fin`): el motor deriva el orden.
B) **Explícito** (vía `precede` / `sigue_a`): se afirma directamente.

```
(examen_001, precede, diagnostico_001)
(diagnostico_001, precede, prescripcion_001)
```

> 🔸 **Fricción 12 — `precede` / `sigue_a` no son canónicas**. Aparecen naturalmente en cualquier secuencia temporal (taxi: emparejamiento→recojo→llegada→pago; venta: pedido→despacho→entrega→pago).
>
> **Patch propuesto**: agregar **`precede : T → T`** y su inversa **`sigue_a : T → T`** al catálogo canónico. En FrameNet existe el frame `Temporal_collocation`; en CIDOC, propiedades como `P119 meets_in_time_with`. Hay precedente sólido.

---

## Consultas que esto habilita

```
¿Qué medicamentos toma actualmente María?
phi = { paciente: maria, instancia_de: accion_prescribir,
        momento: [hace 30 días, hoy] }
proyección sobre medicamento.

¿Quién diagnosticó la hipertensión a María?
phi = { paciente: maria, etiqueta: hipertension_grado_1, agente: ? }

¿Por qué se le prescribió Losartán?
phi = { medicamento: losartan_50mg, paciente: maria,
        justificado_por: ? }

¿Cuántas consultas tuvo María este año?
phi = { paciente: maria, instancia_de: accion_consultar,
        momento: [2026-01-01, 2026-12-31] }
agregación: contar.

¿Qué pacientes con hipertensión tienen pendiente un control?
phi = { etiqueta: hipertension_grado_1 }   // primero diagnósticos
... componer con consultas previstas no realizadas
```

---

## Inventario de fricciones y patches

| # | Fricción | Severidad | Patch |
|---|---|---|---|
| 1 | Clínica como Q+L | Baja | Resuelta antes (D1 + `direccion`) |
| 2 | Especialidad médica | Baja | Propiedad estable, no rol |
| 3 | Síntoma K vs T | Baja | T con `instancia_de → K` |
| 4 | Patrones temporales en M | **Media** | Por ahora K; eventualmente reificar |
| 5 | Mediciones con unidad | Baja | Opción simple; reificación posterior |
| 6 | `parte_de` no canónica | **Media** | **Agregar a D7** |
| 7 | `producto` no canónico | **Media** | **Agregar a D7** |
| 8 | Estructura interna de K | Baja | Clarificar (no requiere patch) |
| 9 | Modalidades del catálogo | Baja | Enriquecer K |
| 10 | Roles potenciales (`*_planeado`) | **Media** | Usar `estatus_factual` en vez de duplicar |
| 11 | `sobre` / `referencia` no canónica | **Media** | **Agregar a D7** |
| 12 | `precede` / `sigue_a` no canónicas | **Media** | **Agregar a D7** |

## Conclusión preliminar

**El modelo aguanta historia clínica.** No surgió ninguna inadecuación estructural que rompa D1-D7. Lo que sí surgió:

1. **Tres ausencias en el catálogo canónico**: `parte_de` (mereología), `producto` (resultado), `precede`/`sigue_a` (orden temporal), `sobre`/`referencia` (referencia entre situaciones). Todas universales, todas con precedente en VerbNet/CIDOC. Vale la pena ampliar D7 con estos roles.

2. **Una convención nueva sobre eventos no-actuales**: `estatus_factual: planeado|confirmado|real|cancelado` en lugar de duplicar etiquetas (`agente_planeado` vs `agente`).

3. **Una decisión pendiente reforzada**: los **patrones temporales** en M (la "recurrencia"). Ya estaba anotada; ahora aparece en dos dominios distintos (correr por las mañanas, tomar pastilla cada mañana). Se vuelve más urgente.

4. **K admite estructura interna**: los individuos en K (medicamentos, monedas, unidades) pueden tener su propia red de hechos. Estaba implícito; conviene explicitarlo en la documentación.

¿Querés que actualice `WQuestions.md` con estos patches (agregar 4 roles al catálogo D7 + convención de `estatus_factual` + clarificación sobre K), o preferís que sigamos con otro dominio del Nivel 1 antes de tocar el documento?

---

# Dominio 5 — Composición musical

## Prompt del usuario

> vamos por la composicion musical, entonces

## Mi análisis en su momento

Vamos. Voy a usar un caso histórico concreto que tiene la suficiente densidad para estresar el modelo sin volverse enciclopédico.

## Narrativa

> Ludwig van Beethoven compuso la Sinfonía No. 5 en Do menor, Op. 67, entre 1804 y 1808. La obra tiene cuatro movimientos: I. Allegro con brio (Do menor), II. Andante con moto (La bemol mayor), III. Scherzo (Do menor), IV. Allegro (Do mayor). El primer movimiento usa el famoso motivo "ta-ta-ta-taaa" (tres semicorcheas seguidas de una blanca). Se estrenó el 22 de diciembre de 1808 en el Theater an der Wien de Viena, con Beethoven dirigiendo. En 1955, Herbert von Karajan grabó la sinfonía con la Filarmónica de Berlín en EMI.

## Individuos por eje

```
Q:  beethoven, karajan, berliner_philharmoniker, emi
T:  sinfonia_5, mov_1, mov_2, mov_3, mov_4,
    motivo_destino, nota_001..nota_004,
    composicion_sinf5 (el acto de componer),
    estreno_1808, grabacion_1955, grabacion_disco_001
L:  theater_an_der_wien, viena, berlin
M:  1804, 1808 (intervalo composición), 1808-12-22, 1955
N:  67 (opus), 4 (movimientos), 1, 2, 3, 4 (posiciones)
K:  sinfonia, movimiento, motivo_musical, nota_musical,
    compositor, director, orquesta, sello_discografico,
    semicorchea, blanca, corchea,
    do_menor, la_bemol_mayor, do_mayor,
    sol_3, mi_bemol_3, fa_3, re_3,
    tempo_allegro_con_brio, tempo_andante_con_moto,
    tempo_scherzo, tempo_allegro,
    forte, piano, staccato, legato,
    periodo_clasico, periodo_romantico_temprano
```

## Nivel 1 — La obra como objeto compuesto

```
(sinfonia_5, instancia_de,       sinfonia)              // → K
(sinfonia_5, compositor,         beethoven)             // → Q
(sinfonia_5, opus,               67)                    // → N
(sinfonia_5, tonalidad_principal, do_menor)             // → K
(sinfonia_5, periodo,            periodo_clasico)       // → K
(sinfonia_5, instrumentacion,    orquesta_clasica)      // → K
```

> 🔸 **Fricción 1 — La obra como T, no como K**.
>
> Pregunta natural: ¿la Sinfonía No. 5 es un *tipo* (K, como un SKU) o un *individuo concreto* (T)?
>
> Por analogía con `coca_cola_500` (SKU en K) parecería ir en K. Pero la obra tiene **autor, fechas de creación, lugar de estreno** — propiedades que K no debería tener (K es de conceptos abstractos atemporales, no de creaciones específicas).
>
> Resolución: `sinfonia_5 ∈ T` (es un *individuo creado*, único, con historia), mientras que `sinfonia` (el género) sí va en K. La distinción es: **conceptos** (sinfonía, sonata, suite) → K; **obras concretas** (Sinfonía 5 de Beethoven, K. 550 de Mozart) → T.
>
> **Patch implícito**: K = conceptos atemporales; T = entidades creadas/instanciadas/situadas. Esta distinción ya estaba en D4 pero conviene reforzarla en el ejemplo musical porque la confusión es muy tentadora.

## Nivel 2 — La estructura interna (movimientos)

```
(mov_1, instancia_de,  movimiento)                // → K
(mov_1, parte_de,      sinfonia_5)                // mereología (D7 extendido)
(mov_1, numero_orden,  1)                         // → N
(mov_1, tempo,         tempo_allegro_con_brio)    // → K
(mov_1, tonalidad,     do_menor)                  // → K

(mov_2, parte_de,      sinfonia_5)
(mov_2, numero_orden,  2)
(mov_2, tempo,         tempo_andante_con_moto)
(mov_2, tonalidad,     la_bemol_mayor)

(mov_1, precede, mov_2)                           // orden temporal (D7 extendido)
(mov_2, precede, mov_3)
(mov_3, precede, mov_4)
```

> 🔸 **Sin fricción nueva**. `parte_de` y `precede` (recién agregados al catálogo) funcionan perfecto. Ya pagan dividendos: si no los hubiéramos canonizado en clínica, los inventaríamos acá igual.

## Nivel 3 — El motivo del destino y las notas

```
(motivo_destino, instancia_de, motivo_musical)
(motivo_destino, parte_de,     mov_1)
(motivo_destino, apodo,        "motivo del destino")

(nota_001, instancia_de,  nota_musical)
(nota_001, parte_de,      motivo_destino)
(nota_001, posicion,      1)                   // → N
(nota_001, figura,        semicorchea)         // → K (duración musical)
(nota_001, altura,        sol_3)               // → K (altura cromática)
(nota_001, dinámica,      forte)               // → K

(nota_004, parte_de,      motivo_destino)
(nota_004, posicion,      4)
(nota_004, figura,        blanca)
(nota_004, altura,        mi_bemol_3)
```

> 🔸 **Fricción 2 — El tiempo musical NO es M**.
>
> Una "semicorchea" no es un intervalo de tiempo de reloj; es una unidad de duración *relativa* dentro del marco rítmico (depende del tempo). Si modeláramos la duración real de la nota en M (segundos), perderíamos la información musical.
>
> Resolución: las duraciones musicales (`semicorchea`, `blanca`, `corchea`, `negra`) viven en **K** como categorías de duración. La conversión a tiempo de reloj depende del tempo de cada interpretación y se calcula, no se almacena.
>
> Esto **revela algo importante**: WQuestions tiene múltiples "tiempos" según el dominio:
> - Tiempo de reloj/calendario → M.
> - Tiempo musical relativo → K (categorías) o T (estructuras como compases).
> - Tiempo recurrente (cada mañana) → K (patrones).
>
> No es problema del modelo; es la realidad. Pero conviene **documentarlo**: M es para tiempo absoluto/lineal del mundo real; los otros "tiempos" se modelan como categorías o estructuras.

> 🔸 **Fricción 3 — Modelado de notas: verbosidad**.
>
> Reificar cada nota como T-individuo con `posición`, `figura`, `altura` es correcto pero verboso. Una obra entera tendría miles de notas-individuo. Está bien semánticamente, pero **operacionalmente** sugiere que el almacenamiento real debería tener compresión / agrupación (las "voces" musicales, los "compases" como contenedores).
>
> No es problema del modelo conceptual; es problema de la implementación futura. **Sin patch ahora**.

## Nivel 4 — El acto de composición

```
(composicion_sinf5, instancia_de, accion_componer)
(composicion_sinf5, agente,       beethoven)
(composicion_sinf5, producto,     sinfonia_5)        // ← producto (D7 extendido)
(composicion_sinf5, inicio,       1804)
(composicion_sinf5, fin,          1808)
```

> 🔸 **Fricción 4 — El atajo `compositor`**.
>
> Usé `(sinfonia_5, compositor, beethoven)` en el nivel 1, pero acá lo "correcto" según neo-davidsoniano es la versión reificada: `(composicion_sinf5, agente, beethoven)` + `(composicion_sinf5, producto, sinfonia_5)`.
>
> ¿Vivimos con redundancia o solo uno?
>
> Mi propuesta: **el atajo es derivable**. Hay una regla de inferencia:
>
> ```
> SI  ∃e : (e, instancia_de, accion_componer) ∧ (e, agente, A) ∧ (e, producto, W)
> ENTONCES (W, compositor, A)
> ```
>
> El motor genera automáticamente el atajo. No es un nuevo dato; es una proyección útil para consultas frecuentes.
>
> **Observación general**: este patrón aparece varias veces. "Editor de un libro", "creador de una obra", "fabricante de un producto" son todos atajos derivables del esquema **acto_X(agente, producto)**. Cuando WQuestions tenga capa de inferencia, esto es el caso canónico.

## Nivel 5 — El estreno

```
(estreno_1808, instancia_de, accion_estrenar)
(estreno_1808, agente,       beethoven)            // como director
(estreno_1808, interpreta,   sinfonia_5)           // domain-specific
(estreno_1808, lugar_de,     theater_an_der_wien)
(estreno_1808, momento,      1808-12-22)
```

> 🔸 **Fricción 5 — `interpreta` no es canónica**.
>
> Una performance se conecta a la obra mediante una relación que dice "esta interpretación es DE esa obra". Lo más cercano canónico es `referencia/sobre`, pero pierde matiz.
>
> Alternativa: añadir `interpreta : T → T` al catálogo. Pero esto es específico de artes performativas (música, teatro, danza). No es universal.
>
> Resolución: **dejar `interpreta` como etiqueta de dominio** (no canonizar). El catálogo canónico no debería absorber roles de cada actividad humana. Bastantes etiquetas de dominio son normales y deseables.

## Nivel 6 — La grabación

```
(grabacion_1955, instancia_de, accion_grabar)
(grabacion_1955, agente,       karajan)                  // principal: director
(grabacion_1955, ejecutante,   berliner_philharmoniker)  // domain
(grabacion_1955, productor,    emi)                       // domain
(grabacion_1955, interpreta,   sinfonia_5)               // domain
(grabacion_1955, lugar_de,     berlin)
(grabacion_1955, momento,      1955)
(grabacion_1955, producto,     grabacion_disco_001)      // ← canónico

(grabacion_disco_001, instancia_de, grabacion_audio)
(grabacion_disco_001, duracion_min, 32)
```

> 🔸 **Fricción 6 — Múltiples "agentes" en una situación**.
>
> Una grabación tiene varios actores funcionalmente distintos:
> - **Director** (Karajan): principal
> - **Ejecutante** (la orquesta): el que toca
> - **Productor** (EMI): el que organiza/financia/distribuye
> - **Ingeniero de sonido**: el que graba técnicamente
>
> `agente` es funcional (un sujeto principal). Si todos son "agentes", el rol pierde poder discriminante.
>
> Resolución propuesta (convención, no patch estructural):
>
> > El rol `agente` se reserva para el **agente principal** de la situación según la naturaleza del verbo. Para otros participantes funcionales se usan roles **específicos de dominio** (director, ejecutante, productor, etc.).
>
> Esto preserva la consultabilidad de `agente` (siempre devuelve UNA persona, el principal) y deja espacio para la riqueza específica de cada dominio. Ya lo hicimos implícitamente en la clínica (`paciente` para el receptor del cuidado, `agente` para el médico). Solo conviene **declararlo como convención explícita**.

> 🔸 **Fricción 7 — La obra sin ubicación geográfica clara**.
>
> `sinfonia_5` como obra no tiene `lugar_de`. Existió primero en la mente de Beethoven, luego en partituras, luego en performances. ¿Dónde está la obra?
>
> Mi observación: **no necesita un lugar**. Las obras abstractas son individuos en T que pueden no tener `lugar_de`. El compositor tiene lugar de nacimiento; el estreno tiene lugar; las partituras físicas tienen ubicación; pero la obra en sí, no.
>
> Esto es coherente con que **los roles canónicos son opcionales por defecto**. Solo los que el verbo / tipo de situación exige son obligatorios. La sinfonía como sustantivo (no verbo) tiene roles a través de su género (sinfonía → K), y el género no exige lugar.
>
> **Sin patch**. Solo aclaración: T no implica "objeto físico ubicable"; T son "individuos concretos creados o situados", algunos abstractos.

## Inventario de fricciones (música)

| # | Fricción | Severidad | Resolución |
|---|---|---|---|
| 1 | Obra como T vs K | Media | Convención: K=conceptos atemporales, T=entidades creadas. Reforzar D4 con ejemplo. |
| 2 | Tiempo musical ≠ M | Media | M es para tiempo absoluto; tiempo musical va en K (figuras) o T (estructuras como compases). Documentar. |
| 3 | Verbosidad al reificar notas | Baja | Problema de implementación, no de modelo. Posponer. |
| 4 | Atajo `compositor` vs acto reificado | Media | Atajos derivables por reglas de inferencia (futuro). Almacenar redundantemente por ahora. |
| 5 | `interpreta` no canónica | Baja | Dejar como dominio. No todo se canoniza. |
| 6 | Múltiples agentes funcionales | **Media-alta** | Convención: `agente` = principal; otros roles funcionales = dominio. **Explicitar como convención**. |
| 7 | Obra sin lugar | Baja | T no implica ubicación; roles opcionales por defecto. Solo documentar. |

## Conclusión preliminar

**El modelo aguanta música** — y eso es noticia importante porque música era el dominio más distinto a lo que habíamos probado (sin agentes humanos en el centro, sin lugar físico, con estructura recursiva profunda).

Las fricciones que aparecieron son **conceptuales / de documentación**, no estructurales:

1. **Refinar D4** con un ejemplo claro de obra-creada vs concepto-atemporal.
2. **Documentar la "pluralidad de tiempos"**: M es para tiempo de reloj; otros tiempos (musical, recurrente) viven en K.
3. **Adoptar convención sobre `agente`**: principal según el verbo; otros participantes funcionales como roles de dominio.
4. **Identificar el patrón "atajo derivable"** para reglas de inferencia futuras (composición → compositor, fabricación → fabricante, etc.).

**Lo nuevo más valioso del ejercicio**: el modelo demuestra que puede manejar dominios sin agentes humanos centrales y sin ubicación física inherente. Esto refuerza la **universalidad declarada** de WQuestions más allá de dominios transaccionales.

**Para el libro**: este caso es ideal como capítulo de validación cruzada porque (a) es culturalmente familiar (todo el mundo conoce la 5ª), (b) muestra el modelo en territorio "inesperado" y (c) revela patrones generalizables (atajos derivables, pluralidad de tiempos).

¿Querés que documente las tres convenciones nuevas en `WQuestions.md` antes de seguir, o pasamos al siguiente dominio (contrato de alquiler, fútbol, química) y consolidamos al final?

---

# Dominio 6 — Contrato de alquiler

## Prompt del usuario

> si, documenta y luego continuamos con el siguiente dominio: Contrato de alquiler

## Mi análisis en su momento

Sección 3 nueva insertada y referencias actualizadas. La estructura del documento queda:

```
 1. Conjuntos base
 2. Decisiones de diseño (D1-D7) + convenciones
 3. El espacio multidimensional         ← NUEVA
 4. Hecho atómico
 5. Consulta
 6. Ejemplo: aeropuerto
 7. Ejemplo: ventas
 8. Ejemplo: taxi
 9. Del lenguaje natural a los hechos
10. Decisiones pendientes
11. Pisos siguientes
```

La nueva sección 3 cubre: la metáfora geométrica formalizada, la distinción entre dimensiones (roles) y ejes (espacios de valor), las tres diferencias con ℝⁿ clásico (parcial, multi-valuado, tipado), la visualización como hoja de cálculo dispersa, las consultas como restricciones geométricas, una tabla comparativa con otros espacios multidimensionales, y los cinco puntos que cierran la intuición fundacional. Referencias en `related/neo-davidsonian.md`, `related/framenet-verbnet.md` y `diagram.md` actualizadas para apuntar a "sección 9".

---

# Siguiente dominio: Contrato de alquiler

Empezamos. Voy a usar un caso peruano realista para estresar al máximo D6 (normativo), validez temporal, y agentes jurídicos.

## Narrativa

> El 1 de junio de 2026, Juan Pérez (DNI 12345678) firma un contrato de alquiler con Inmobiliaria Lima Centro SAC (RUC 20123456789), representada por su gerente Ana López. El inmueble es un departamento de 80 m² en Av. Larco 1234, Miraflores. El contrato es por 12 meses (del 1 de julio de 2026 al 30 de junio de 2027), con renta mensual de S/2500, pagaderos los primeros 5 días de cada mes. Se requiere una garantía de S/5000 a la firma. El inquilino se compromete a pagar los servicios (luz, agua, internet). Si se retrasa más de 30 días en el pago, el arrendador puede resolver el contrato. La renta se reajusta anualmente según el índice de precios al consumidor (IPC). El contrato se firma en notaría ante el notario Carlos Ruiz.

## Individuos por eje

```
Q:  juan_perez, ana_lopez, inmobiliaria_lima_centro, carlos_ruiz
T:  contrato_001, inmueble_dpto_larco_1234,
    firma_001 (acto de firmar),
    obligacion_renta, obligacion_garantia, obligacion_servicios,
    clausula_resolucion, clausula_reajuste,
    pagos_001..012 (12 pagos mensuales esperados),
    pago_garantia_001
L:  av_larco_1234, miraflores, notaria_ruiz
M:  2026-06-01 (firma), 2026-07-01 (inicio vigencia),
    2027-06-30 (fin vigencia)
N:  80 (m²), 2500 (renta), 5000 (garantía), 12 (meses),
    5 (días gracia), 30 (días atraso)
K:  persona_natural, persona_juridica, notario, gerente,
    arrendador, arrendatario, fiador, representante_legal,
    contrato_alquiler, contrato_civil, departamento, inmueble,
    obligacion_pago, obligacion_uso, clausula_resolutoria,
    clausula_reajuste_ipc, indice_ipc, soles
```

## Nivel 1 — El contrato como entidad central

```
(contrato_001, instancia_de,        contrato_alquiler)        // → K
(contrato_001, arrendador,          inmobiliaria_lima_centro) // domain
(contrato_001, arrendatario,        juan_perez)               // domain
(contrato_001, inmueble,            inmueble_dpto_larco_1234)
(contrato_001, momento_firma,       2026-06-01)
(contrato_001, vigencia_inicio,     2026-07-01)
(contrato_001, vigencia_fin,        2027-06-30)
(contrato_001, renta_mensual,       2500)
(contrato_001, moneda,              soles)
(contrato_001, garantia,            5000)
(contrato_001, estatus_factual,     real)                     // ya firmado
```

> 🔸 **Fricción 1 — Múltiples agentes funcionales en el contrato**.
>
> Un contrato no tiene un "agente principal" único. Tiene dos partes: arrendador y arrendatario, ambos con igual peso. La convención de "agente = principal según el verbo" no se aplica limpiamente cuando el verbo es simétrico (firmar bilateralmente).
>
> Resolución: usar **roles de dominio simétricos** (`arrendador`, `arrendatario`) en vez de forzar `agente`. El verbo subyacente "firmar" es bilateral; el rol `agente` no encaja.
>
> **No es patch del modelo**, es ajuste de la convención: cuando el verbo es bilateral/multilateral, `agente` puede no usarse y los participantes ir directo a roles de dominio.

## Nivel 2 — El inmueble

```
(inmueble_dpto_larco_1234, instancia_de,  departamento)
(inmueble_dpto_larco_1234, direccion,     av_larco_1234)
(inmueble_dpto_larco_1234, distrito,      miraflores)        // → K
(inmueble_dpto_larco_1234, area,          80)                // m²
(inmueble_dpto_larco_1234, propietario,   inmobiliaria_lima_centro)
```

## Nivel 3 — Personas y representación legal

```
(juan_perez, instancia_de,    persona_natural)
(juan_perez, dni,             12345678)
(juan_perez, rol_en_contrato_001, arrendatario)     // rol_en (D7)

(inmobiliaria_lima_centro, instancia_de, persona_juridica)
(inmobiliaria_lima_centro, ruc,          20123456789)
(inmobiliaria_lima_centro, rol_en_contrato_001, arrendador)

(ana_lopez, instancia_de,    persona_natural)
(ana_lopez, representa_a,    inmobiliaria_lima_centro)   // domain
(ana_lopez, cargo,           gerente)                     // → K
```

> 🔸 **Fricción 2 — Representación legal**.
>
> Ana López firma EN NOMBRE DE la inmobiliaria. Hay una relación `representa_a : Q → Q` entre persona natural y persona jurídica.
>
> Esto es universal: cualquier persona jurídica actúa a través de personas naturales. En el dominio legal aparece con frecuencia.
>
> **¿Canónico o de dominio?** Es muy universal en cualquier contexto legal/comercial. Pero también es muy específico (no aplica a clínica o música directamente). Me inclino por **dejarlo de dominio** y eventualmente promoverlo si aparece en muchos más casos.

## Nivel 4 — Las cláusulas como entidades reificadas

Esto es lo que más estresa el modelo. Una cláusula contractual es:
- Una entidad propia (T)
- Que establece una obligación, condición o regla
- Con vigencia temporal
- Justificada por la ley aplicable o por las partes

```
(obligacion_renta, instancia_de,    clausula_obligacion_pago)
(obligacion_renta, parte_de,        contrato_001)
(obligacion_renta, obligado,        juan_perez)
(obligacion_renta, acreedor,        inmobiliaria_lima_centro)
(obligacion_renta, monto,           2500)
(obligacion_renta, moneda,          soles)
(obligacion_renta, frecuencia,      mensual)               // → K
(obligacion_renta, dia_vencimiento, 5)                     // primeros 5 días
(obligacion_renta, vigencia_inicio, 2026-07-01)
(obligacion_renta, vigencia_fin,    2027-06-30)
```

> 🔸 **Fricción 3 — Vigencia temporal de hechos (la decisión pendiente #4 surge en serio)**.
>
> La obligación de pagar renta no es un hecho instantáneo. Es **válido durante un intervalo**. Esto es exactamente la decisión pendiente sobre validez temporal de hechos.
>
> En este dominio podemos usar `vigencia_inicio` y `vigencia_fin` como propiedades de la situación-obligación. Funciona. Pero **el caso muestra que esto va a aparecer constantemente en derecho**: cada cláusula tiene una vigencia.
>
> Propuesta tentativa (a discutir): convertir `vigencia_inicio` y `vigencia_fin` en **roles canónicos** del catálogo D7, equivalentes a `inicio` y `fin` pero específicos para "duración de validez" de obligaciones/cláusulas. O incluso reciclar `inicio`/`fin` con interpretación distinta según el tipo de situación.
>
> Por ahora: `inicio` y `fin` aplican al evento; `vigencia_inicio` y `vigencia_fin` aplican a la obligación. Trato ambos como roles de dominio temporales. **Anotar como caso prioritario para resolver la decisión pendiente #4**.

## Nivel 5 — La cláusula resolutoria (condicional)

> "Si se retrasa más de 30 días en el pago, el arrendador puede resolver el contrato."

```
(clausula_resolucion, instancia_de,    clausula_resolutoria)
(clausula_resolucion, parte_de,        contrato_001)
(clausula_resolucion, condicion,       condicion_atraso_30d)
(clausula_resolucion, consecuencia,    facultad_resolver)
(clausula_resolucion, beneficiario,    inmobiliaria_lima_centro)

(condicion_atraso_30d, instancia_de,   condicion_temporal)
(condicion_atraso_30d, sobre,          obligacion_renta)
(condicion_atraso_30d, atraso_dias,    30)
(condicion_atraso_30d, operador,       mayor_a)             // → K

(facultad_resolver, instancia_de,      facultad_juridica)
(facultad_resolver, accion_permitida,  resolver_contrato)   // → K
(facultad_resolver, otorgada_a,        inmobiliaria_lima_centro)
```

> 🔸 **Fricción 4 — Condicionales (si X entonces Y)**.
>
> Las cláusulas condicionales (caso 11 del Nivel 2: "Si llueve, llevo paraguas") aparecen aquí en serio. Una cláusula resolutoria es un condicional reificado: la condición es una situación (incluso una situación hipotética), y la consecuencia es otra.
>
> Modelado: ambas (condición y consecuencia) reificadas como T-individuos con propiedades. La cláusula las une con dos roles: `condicion` y `consecuencia`.
>
> ¿Son canónicos? **Sí, propongo agregarlos al catálogo D7**: `condicion : T → T` y `consecuencia : T → T`. Aplican a cualquier modelado de reglas, no solo contratos. Una receta médica también es condicional ("tomar pastilla SI hay dolor"), un programa también ("si error entonces log").

> 🔸 **Fricción 5 — La "facultad" (deber/poder hacer algo)**.
>
> "El arrendador PUEDE resolver". Esto es una modalidad alética/deóntica: una facultad jurídica reservada para una parte.
>
> Lo modelo con `accion_permitida : K → K` apuntando a una categoría de acción ("resolver_contrato"). La facultad no es la acción ejecutada; es la *posibilidad legal* de ejecutarla.
>
> Conexión con D5 (agencia) y D7 (modales): "puede" como modal alético; la facultad es un *derecho potencial*.
>
> **Sin patch nuevo**. Pero observación: el derecho como dominio tiene MUCHAS facultades, obligaciones, prohibiciones. Cada una merecería ser modelada como entidad reificada (T) con su modalidad. Es densamente normativo.

## Nivel 6 — La cláusula de reajuste

> "La renta se reajusta anualmente según el IPC."

```
(clausula_reajuste, instancia_de,    clausula_reajuste_indexada)
(clausula_reajuste, parte_de,        contrato_001)
(clausula_reajuste, sobre_obligacion, obligacion_renta)
(clausula_reajuste, indice,          indice_ipc)            // → K
(clausula_reajuste, frecuencia,      anual)                 // → K
```

> 🔸 **Fricción 6 — Reglas que cambian otros hechos**.
>
> Esta cláusula no es estática: dice que `obligacion_renta.monto` cambiará cada año según un índice externo. Es una **regla de derivación**.
>
> El modelo actual puede expresar QUE existe la cláusula. Pero ¿cómo se actualiza efectivamente el `monto` de la obligación cuando se aplica el reajuste?
>
> Posibilidades:
> - Crear nuevos hechos: `(obligacion_renta, monto_vigente_desde_2027_07_01, 2625)` con su propia vigencia.
> - Versiones de la obligación: `obligacion_renta_v1` (2026-07 a 2027-06), `obligacion_renta_v2` (2027-07 en adelante).
> - Una capa de reglas/inferencia que computa el monto vigente en cada momento.
>
> **No hay resolución única en el modelo conceptual actual**. Es una pregunta de implementación + decisión sobre **versionado temporal de hechos**. Está relacionada con la decisión pendiente #4 (validez temporal).
>
> Por ahora: documentar la cláusula declarativamente. La aplicación efectiva del reajuste es una decisión pendiente.

## Nivel 7 — La firma como evento

```
(firma_001, instancia_de,    accion_firmar)
(firma_001, agente,          juan_perez)
(firma_001, co_agente,       ana_lopez)                     // domain
(firma_001, sobre,           contrato_001)                  // referencia (D7)
(firma_001, lugar_de,        notaria_ruiz)
(firma_001, momento,         2026-06-01)
(firma_001, notario,         carlos_ruiz)                   // domain
```

> 🔸 **Fricción 7 — La firma tiene dos agentes simétricos**.
>
> Misma fricción 1, pero ahora resuelta con `agente` + `co_agente`. Otra opción: `firmantes : T → Q (multi)`.
>
> Convención propuesta: cuando hay dos partes simétricas en una acción bilateral, usar **`partes : T → Q (multi)`** en vez de duplicar agentes.
>
> ```
> (firma_001, partes, {juan_perez, ana_lopez})
> ```
>
> Y mantener `agente`/`co_agente` solo cuando hay asimetría clara (un actor principal y uno secundario).

## Nivel 8 — Pagos esperados vs realizados

```
(pago_001, instancia_de,     pago_renta_mensual)
(pago_001, estatus_factual,  planeado)                       // todavía no ocurre
(pago_001, sobre_obligacion, obligacion_renta)
(pago_001, periodo_cubierto, 2026-07)
(pago_001, monto,            2500)
(pago_001, vencimiento,      2026-07-05)
(pago_001, pagador,          juan_perez)
(pago_001, receptor,         inmobiliaria_lima_centro)
```

Cuando se realiza:

```
(pago_001, estatus_factual,  real)
(pago_001, momento,          2026-07-03)
(pago_001, instrumento,      transferencia_bancaria)
```

> 🔸 **Fricción 8 — Hechos esperados que se "materializan"**.
>
> Empieza siendo `estatus_factual: planeado`. Cuando ocurre, se actualiza a `real`. Pero entonces el "mismo hecho" cambió de estatus, lo cual viola la inmutabilidad típica de modelos de hechos (como en CIDOC CRM).
>
> Alternativa: nunca actualizar; siempre crear nuevos hechos. La obligación-de-pagar (planeado) y el pago-real son **dos situaciones distintas** vinculadas por `cumple : T → T`:
>
> ```
> (pago_real_001, cumple, pago_planeado_001)
> ```
>
> Esto es más limpio teóricamente. **Convención propuesta**: los hechos son inmutables; los cambios de estatus se modelan creando una nueva situación que cumple/cancela/modifica la anterior.

## Inventario de fricciones (contrato)

| # | Fricción | Severidad | Resolución |
|---|---|---|---|
| 1 | Múltiples agentes simétricos | Baja | Usar roles de dominio o `partes : T → Q multi` |
| 2 | Representación legal | Baja | Rol de dominio `representa_a` por ahora |
| 3 | Vigencia temporal de obligaciones | **Alta** | Refuerza decisión pendiente #4; modelar con `vigencia_inicio`/`vigencia_fin` |
| 4 | Condicionales (si X entonces Y) | **Media** | **Agregar `condicion`/`consecuencia` al catálogo D7** |
| 5 | Facultades / modalidad deóntica | Media | Reificar la facultad como T con `accion_permitida` |
| 6 | Reglas que derivan otros hechos | **Alta** | Decisión pendiente nueva: cómo modelar reglas de derivación / versionado |
| 7 | Acciones bilaterales | Baja | `partes : T → Q multi` cuando es simétrico |
| 8 | Mutabilidad de hechos | **Media-alta** | Convención propuesta: hechos inmutables; cambios = nuevas situaciones con `cumple`/`cancela`/`modifica` |

## Conclusión preliminar

**El modelo aguanta contratos de alquiler**, pero el dominio normativo es el que más fricción ha generado hasta ahora. No porque rompa el modelo, sino porque **expone con fuerza decisiones pendientes que en otros dominios eran marginales**:

1. **Validez temporal de hechos** (decisión pendiente #4) pasa de "interesante" a "crítica". En derecho, cada cláusula y cada obligación tiene vigencia; no contemplarla pierde información esencial.

2. **Reglas de derivación** (cómo una cláusula afecta otros hechos a lo largo del tiempo) es una nueva pregunta no contemplada. El modelo conceptual puede expresar las reglas declarativamente, pero la *aplicación* de las reglas requiere una capa adicional.

3. **Condicionales** se vuelven canónicos: `condicion`/`consecuencia` deberían entrar al catálogo D7. Aparecen en contratos, reglas, programas, recetas médicas — son universales.

4. **Inmutabilidad de hechos** emerge como mejor práctica: no actualizar; siempre crear hechos nuevos que refieren al anterior. Esto es CIDOC CRM-style.

5. **Acciones bilaterales/multilaterales** sugieren refinar la convención sobre `agente`: cuando hay simetría entre partes, usar `partes` (multi-valuado) en vez de inventar `agente` artificial.

**Propuestas concretas que dejo sobre la mesa para documentar**:
- Agregar `condicion`/`consecuencia` al catálogo D7.
- Agregar `partes` al catálogo D7 (acción multilateral simétrica).
- Promover **vigencia temporal** desde "decisión pendiente" hacia **decisión activa** (D8 candidato): cada hecho puede llevar `vigencia_inicio`/`vigencia_fin`.
- Convención de inmutabilidad: documentar como buena práctica.
- Anotar **reglas de derivación** como nueva decisión pendiente (#6).

¿Quieres que documente estos cambios en `WQuestions.md`, o prefieres que probemos primero otro dominio (química o fútbol) para confirmar si estas fricciones se repiten antes de cristalizarlas?

---

# Dominio 7 — Reacción química (combustión del metano)

## Prompt del usuario

> si hay que analizar primero quimica,me das los detalles y te aviso si analizamos futbol y al final coordinamos para ver que modificaciones agregamos al documento

## Mi análisis en su momento

Vamos con química. Voy a usar una reacción clásica que estresa varios puntos: combustión completa del metano. Tiene estequiometría, energía, condiciones y, lo más importante, **ningún agente humano en la reacción misma**.

## Narrativa

> En un laboratorio, se realiza la combustión completa de 1 mol de metano (CH₄) con 2 moles de oxígeno (O₂), en condiciones de presión atmosférica (1 atm) y temperatura de ignición de aproximadamente 537 °C. La reacción produce 1 mol de dióxido de carbono (CO₂) y 2 moles de agua (H₂O), liberando 890 kJ/mol de energía. La reacción es exotérmica e irreversible. Se cataloga como reacción de combustión.
>
> La química Laura Mendoza inició la reacción a las 10:00 del 14 de mayo de 2026.

## Individuos por eje

```
Q:  laura_mendoza
T:  reaccion_001 (el evento de combustión),
    iniciacion_001 (el acto humano de iniciar),
    porcion_ch4_001, porcion_o2_001,
    porcion_co2_001, porcion_h2o_001,
    energia_liberada_001
L:  laboratorio_a
M:  2026-05-14_10:00
N:  1, 2, 537, 1, 890
K:  metano, oxigeno, dioxido_carbono, agua,
    reaccion_combustion, reaccion_combustion_metano,
    reaccion_quimica, fase_gaseosa,
    exotermica, irreversible,
    mol, atmosfera, grados_celsius, kilojulios_mol,
    quimico (rol profesional)
```

## Nivel 1 — La reacción como template (en K) vs la instancia (en T)

Acá aparece de entrada algo conceptualmente nuevo. La reacción "combustión del metano" existe en dos niveles:

**Nivel atemporal (la ecuación química como template, en K):**

```
(reaccion_combustion_metano, instancia_de,   reaccion_combustion)
(reaccion_combustion_metano, ecuacion,       "CH4 + 2 O2 → CO2 + 2 H2O")
(reaccion_combustion_metano, naturaleza,     exotermica)
(reaccion_combustion_metano, reversibilidad, irreversible)
(reaccion_combustion_metano, energia_kJ_mol, 890)
(reaccion_combustion_metano, reactivo_ratio, {metano: 1, oxigeno: 2})
(reaccion_combustion_metano, producto_ratio, {dioxido_carbono: 1, agua: 2})
(reaccion_combustion_metano, temp_ignicion_C, 537)
```

**Nivel instancia (esta combustión específica, en T):**

```
(reaccion_001, instancia_de,    reaccion_combustion_metano)
(reaccion_001, lugar_de,        laboratorio_a)
(reaccion_001, momento,         2026-05-14_10:00)
(reaccion_001, escala_mol,      1)                       // multiplicador
(reaccion_001, estatus_factual, real)
```

Las cantidades específicas son derivables: 1 × 1 = 1 mol de CH₄, 1 × 2 = 2 mol de O₂, etc.

> 🔸 **Fricción 1 — Patrón "Plantilla en K + Instancia en T con factor de escala"**.
>
> Este patrón es **conceptualmente nuevo** en nuestro recorrido. La reacción combustión-de-metano tiene una "forma" atemporal (la ecuación, las energías, los ratios) y muchas "ocurrencias" (cada vez que algo se quema en algún lugar). La forma vive en K; las ocurrencias en T.
>
> Lo que es nuevo es la **escala / multiplicador**: la instancia hereda toda la estructura del template y solo aporta cuándo, dónde, y *cuánto* (factor de escala).
>
> Este patrón aparece también en:
> - **Recetas** (template) + cocina específica (instancia con porciones).
> - **Procesos industriales** + corrida de producción.
> - **Algoritmos** + ejecución del algoritmo.
> - **Procedimientos médicos** + intervención específica en un paciente.
>
> **Propuesta**: documentar este patrón como **convención de modelado** en `WQuestions.md`. Útil para todos los dominios procedimentales/replicables.

## Nivel 2 — Los reactivos y productos (con porciones reificadas)

Si queremos llevar registro de las cantidades específicas de esta instancia (no solo derivarlas del template), reificamos cada porción:

```
(porcion_ch4_001, instancia_de, metano)
(porcion_ch4_001, cantidad,     1)
(porcion_ch4_001, unidad,       mol)
(porcion_ch4_001, fase,         fase_gaseosa)

(porcion_o2_001, instancia_de,  oxigeno)
(porcion_o2_001, cantidad,      2)
(porcion_o2_001, unidad,        mol)
(porcion_o2_001, fase,          fase_gaseosa)

(reaccion_001, reactivo, {porcion_ch4_001, porcion_o2_001})
(reaccion_001, producto, {porcion_co2_001, porcion_h2o_001})  // D7
```

> 🔸 **Fricción 2 — Generalización de `paciente`**.
>
> ¿Cómo se llama el rol "los reactivos" de una reacción? Son los que SE TRANSFORMAN. En neo-davidsoniano serían **patients** (los pacientes que sufren la acción), pero en nuestro catálogo `paciente : T → Q` está tipado a humanos.
>
> Los reactivos son T (porciones físicas de sustancia), no Q. No encajan en `paciente` actual.
>
> **Patch propuesto**: generalizar `paciente : T → V` (en vez de `T → Q`). Esto es coherente con la teoría neo-davidsoniana, donde Patient incluye cosas, no solo personas. "Juan rompió el vaso" — el vaso es paciente, está en T.
>
> Esto unifica:
> - "El médico examina al paciente" → paciente = persona (Q)
> - "El cirujano opera el tumor" → paciente = objeto físico (T)
> - "La reacción transforma metano" → paciente = sustancia (T)
> - "La ley regula el comercio" → paciente = concepto (K)
>
> **Patch concreto al catálogo D7**: cambiar `paciente : T → Q` por `paciente : T → V`.

> 🔸 **Fricción 3 — `reactivo` no es canónico**.
>
> Usé `reactivo` como rol, pero es específico de química. ¿Existe un genérico? "Lo que la situación consume/transforma" aparece en muchos dominios: química (reactivo), cocina (ingrediente), fabricación (insumo), software (entrada/input).
>
> Una opción es usar `paciente` (multi-valuado) cuando lo que entra se transforma. Otra es agregar **`insumo / consume`** al catálogo D7.
>
> Propuesta tentativa: **agregar `insumo : T → V (multi)`** al catálogo. Inverso de `producto`. La pareja `insumo`/`producto` describe situaciones productivas/transformacionales.

## Nivel 3 — Condiciones de reacción

```
(reaccion_001, temperatura_C,   537)              // → N
(reaccion_001, presion_atm,     1)                // → N
```

> 🔸 **Fricción 4 — Mediciones con unidad, otra vez (refuerza pendiente)**.
>
> Usé la opción simple (unidad en el nombre). Pero química amerita reificar mediciones porque hay conversiones constantes (°C ↔ K, atm ↔ Pa, mol ↔ g, etc.). Cuarto dominio que pide esto (medicina, música tangencialmente, contrato indirectamente, y ahora química).
>
> **Sigue como decisión pendiente #3**, pero la urgencia sube.

## Nivel 4 — La energía liberada

Dos formas:

**Opción A — propiedad del template:**
```
(reaccion_combustion_metano, energia_kJ_mol, 890)
```

**Opción B — entidad reificada por instancia:**
```
(energia_liberada_001, instancia_de, energia_calorica)
(energia_liberada_001, magnitud,     890)
(energia_liberada_001, unidad,       kilojulios_mol)
(reaccion_001, libera, energia_liberada_001)         // producto energético
```

> 🔸 **Fricción 5 — Energía: propiedad o entidad?**
>
> Opción A es más compacta. Opción B permite hablar *de la energía* (de dónde vino, a dónde fue, conservación, transferencia).
>
> Para física/química seria, Opción B es necesaria (flujo de energía es central). Para usos comunes, Opción A basta.
>
> **Sin patch al modelo** — depende del nivel de detalle del dominio. Pero confirma una **observación general**: muchas propiedades de situaciones admiten reificación cuando ganan importancia analítica.
>
> Esto se conecta con el patrón "plantilla + instancia": **reificar = subir resolución del modelo**. Conviene documentar que reificar es siempre posible y no rompe el modelo; solo lo enriquece.

## Nivel 5 — Iniciación humana vs reacción autónoma

La química Laura Mendoza no "ejecuta" la combustión — la inicia. La reacción ocurre por las leyes de la naturaleza. Esto es D5 (agencia contextual) **al extremo**.

Modelado con dos situaciones distintas vinculadas causalmente:

```
(iniciacion_001, instancia_de,  accion_iniciar_reaccion)
(iniciacion_001, agente,        laura_mendoza)        // Q
(iniciacion_001, sobre,         reaccion_001)         // referencia (D7)
(iniciacion_001, momento,       2026-05-14_10:00)
(iniciacion_001, lugar_de,      laboratorio_a)

(reaccion_001, causado_por, iniciacion_001)            // D6
```

> 🔸 **Fricción 6 — D5 al extremo**.
>
> La reacción misma `reaccion_001` no tiene `agente`. No es un "agente vacío", es la confirmación de que **hay situaciones sin agente**: sucesos naturales (combustión, lluvia, terremoto), cambios espontáneos (caída libre, decaimiento radioactivo), procesos sin sujeto (ebullición, oxidación).
>
> El modelo lo absorbe sin patch: `agente` es opcional. Lo que sí se confirma es la utilidad de separar "iniciación humana" de "evento natural" vía dos T-individuos enlazados por `causado_por`.
>
> Esto es **canónico** en filosofía de la causalidad y ya está en CIDOC CRM (eventos pueden ser activos o pasivos según tengan E7_Activity o E5_Event puro).
>
> **Sin patch, pero confirma fuertemente D5**.

## Nivel 6 — La reacción sin lugar inherente (a nivel template)

```
(reaccion_combustion_metano, instancia_de, reaccion_combustion)
// SIN lugar_de — la reacción como ecuación es atemporal y aespacial
```

Solo la instancia concreta tiene lugar y momento:

```
(reaccion_001, lugar_de, laboratorio_a)
(reaccion_001, momento,  2026-05-14_10:00)
```

> 🔸 **Sin fricción nueva**. Confirma D4 refinado (K = conceptos atemporales, T = instancias situadas).

## Nivel 7 — Conservación de masa (regla emergente)

La reacción balanceada respeta conservación de masa: la masa total de reactivos = la masa total de productos.

```
Reactivos: 1 mol CH4 (16 g) + 2 mol O2 (64 g) = 80 g
Productos: 1 mol CO2 (44 g) + 2 mol H2O (36 g) = 80 g  ✓
```

¿Cómo modela esto WQuestions?

> 🔸 **Fricción 7 — Reglas de invariante / conservación**.
>
> El modelo puede expresar las masas, los reactivos y los productos. Pero **NO PUEDE EXPRESAR DIRECTAMENTE LA REGLA** "la masa se conserva" como hecho consultable.
>
> Esta es la misma fricción que apareció en contratos (cláusula de reajuste = regla que afecta otros hechos). Es una **regla declarativa**.
>
> Posibilidades:
> - Reificar la regla como entidad K: `(reaccion_quimica, regla_aplicable, conservacion_masa)` donde `conservacion_masa ∈ K`.
> - Capa de inferencia que verifica el balance al validar reacciones.
>
> **Refuerza la nueva decisión pendiente que apareció en contratos**: cómo modelar reglas de derivación / invariantes. Aparece ahora en química también — ya no es exclusivo del derecho.

## Inventario de fricciones (química)

| # | Fricción | Severidad | Resolución |
|---|---|---|---|
| 1 | Patrón plantilla-K + instancia-T con escala | **Media — patrón nuevo** | **Documentar como convención de modelado** |
| 2 | `paciente : T → Q` muy restrictivo | **Media** | **Generalizar a `paciente : T → V`** |
| 3 | `reactivo` / `insumo` no canónico | **Media** | **Agregar `insumo : T → V (multi)` al catálogo D7** |
| 4 | Mediciones con unidad | Pendiente | Refuerza decisión pendiente #3 |
| 5 | Energía: propiedad o entidad | Baja | Ambas válidas; documentar "reificar = subir resolución" |
| 6 | Sin agente (D5 extremo) | Baja | Confirma D5; reificar iniciación humana aparte si la hay |
| 7 | Reglas de invariante (conservación) | **Alta** | Refuerza la nueva decisión pendiente que surgió en contratos |

## Lo nuevo respecto al contrato

Para que tengas claro qué aporta este dominio que el contrato no había mostrado:

1. **Patrón "plantilla + instancia"** ← nuevo, claro y generalizable.
2. **Generalización de `paciente`** ← contrato no lo mostró tan claramente porque sus pacientes son humanos.
3. **`insumo` como rol genérico** ← cocina, química, manufactura, software lo necesitan.
4. **D5 al extremo (sin agente real)** ← confirmación útil; contrato siempre tiene partes humanas/jurídicas.
5. **Reglas de invariante físicas** ← misma forma que reglas legales pero en contexto natural; refuerza que el "problema de las reglas" es transversal y no solo legal.

## Conclusión preliminar

**El modelo aguanta química**, y revela cuatro cosas nuevas: el patrón plantilla-instancia, la necesidad de generalizar `paciente`, la necesidad de un rol `insumo`/`reactivo` genérico, y la confirmación de que las reglas declarativas (sea conservación de masa, sea cláusula contractual) son un dominio compartido aún no resuelto.

---

¿Pasamos a **fútbol** ahora para tener el tercer dominio antes de coordinar las modificaciones? O si crees que ya tenemos suficientes fricciones recolectadas para hacer el ajuste consolidado a `WQuestions.md`, podemos cerrar acá.

---

# Dominio 8 — Partido de fútbol (eliminatorias Argentina vs Perú)

## Prompt del usuario

> listo, continuamos con futbol entonces

## Mi análisis en su momento

Vamos con fútbol. Voy a usar un partido real-imaginado de eliminatorias con goles, tarjetas y sustituciones para estresar concurrencia, sucesión rápida y aplicación de reglas.

## Narrativa

> Perú vs Argentina, eliminatorias mundialistas. 14 de octubre de 2026, Estadio Nacional de Lima, 20:00. Resultado final: Perú 1 – Argentina 2.
>
> Goles: minuto 23, Messi (Argentina) tras pase de Di María; minuto 67, Lapadula (Perú) de cabeza tras córner ejecutado por Carrillo; minuto 89, Messi de penal cobrado por falta de Tapia sobre Álvarez.
>
> Tarjetas: minuto 45, amarilla a Yotún (Perú) por falta sobre Mac Allister; minuto 89, roja directa a Tapia tras el penal cometido.
>
> Sustituciones: minuto 60, sale Carrillo, entra Polo (Perú); minuto 75, sale Di María, entra Lo Celso (Argentina).

## Individuos por eje

```
Q:  messi, di_maria, alvarez, mac_allister, lo_celso,
    lapadula, carrillo, yotun, tapia, polo, gallese,
    fossati, scaloni, arbitro_principal,
    federacion_peruana, federacion_argentina
T:  partido_001, primer_tiempo, segundo_tiempo,
    equipo_peru_2026_10_14, equipo_argentina_2026_10_14,
    gol_001, gol_002, gol_003,
    pase_dimaria_messi, centro_carrillo, falta_tapia_alvarez,
    penal_001, tarjeta_amarilla_yotun, tarjeta_roja_tapia,
    expulsion_tapia, sustitucion_001, sustitucion_002
L:  estadio_nacional_lima, lima
M:  2026-10-14_20:00, ..._20:23, ..._20:48, ..._21:00, ...
N:  23, 45, 60, 67, 75, 89, 1, 2
K:  partido_eliminatorias, fase_partido, gol_jugada_abierta,
    gol_de_cabeza, gol_de_penal, pase, centro, corner, falta,
    tarjeta_amarilla, tarjeta_roja, expulsion, sustitucion_jugador,
    delantero, mediocampista, defensor, arquero, entrenador, arbitro
```

## Nivel 1 — El partido como contenedor bilateral

```
(partido_001, instancia_de,     partido_eliminatorias)
(partido_001, partes,           {equipo_peru_2026_10_14,
                                 equipo_argentina_2026_10_14})
(partido_001, lugar_de,         estadio_nacional_lima)
(partido_001, inicio,           2026-10-14_20:00)
(partido_001, fin,              2026-10-14_22:00)
(partido_001, arbitro,          arbitro_principal)
(partido_001, estatus_factual,  real)
```

> 🔸 **Fricción 1 — `partes` necesita generalizarse a `T → V`**.
>
> En la convención que documentamos tras contrato, `partes : T → Q (multi)` era para acciones bilaterales/simétricas con participantes humanos (firmar, casarse). En fútbol, las partes simétricas son **equipos**, que son individuos T, no Q.
>
> Mismo patrón que con `paciente` en química. La signatura es demasiado restrictiva.
>
> **Patch propuesto**: generalizar `partes : T → V (multi)` (de Q a V). Aplica a:
> - Firma de contrato: partes son Q (personas).
> - Partido de fútbol: partes son T (equipos).
> - Encuentro internacional: partes pueden ser Q (estados como personas jurídicas).
> - Negociación entre naciones, alianzas, fusiones empresariales: partes son Q.
> - Reacción química bilateral simétrica (raro): partes serían T.

## Nivel 2 — Las fases (primer tiempo, segundo tiempo)

```
(primer_tiempo, instancia_de,    fase_partido)
(primer_tiempo, parte_de,        partido_001)            // D7
(primer_tiempo, orden,           1)
(primer_tiempo, inicio,          2026-10-14_20:00)
(primer_tiempo, fin,             2026-10-14_20:48)       // 45 + 3 add.

(segundo_tiempo, instancia_de,   fase_partido)
(segundo_tiempo, parte_de,       partido_001)
(segundo_tiempo, orden,          2)

(primer_tiempo, precede, segundo_tiempo)                  // D7
```

> 🔸 **Sin fricción**. `parte_de` y `precede` (catálogo D7) funcionan perfecto. Confirma que la mereología y la secuencia son universales.

## Nivel 3 — El primer gol (con cadena causal)

```
(pase_dimaria_messi, instancia_de, accion_pase)
(pase_dimaria_messi, agente,       di_maria)
(pase_dimaria_messi, beneficiario, messi)
(pase_dimaria_messi, parte_de,     primer_tiempo)
(pase_dimaria_messi, minuto,       23)

(gol_001, instancia_de,    gol_jugada_abierta)
(gol_001, agente,          messi)
(gol_001, favorece_a,      equipo_argentina_2026_10_14)   // domain
(gol_001, parte_de,        primer_tiempo)
(gol_001, minuto,          23)
(gol_001, momento,         2026-10-14_20:23)
(gol_001, causado_por,     pase_dimaria_messi)             // D6
(pase_dimaria_messi, precede, gol_001)
```

> 🔸 **Fricción 2 — Dos relojes coexisten**.
>
> Cada evento tiene **minuto de partido** (0-90+) y **momento absoluto** (wall clock). Son dos coordenadas temporales distintas. El minuto vive en N (es un número), el momento en M.
>
> ¿Es un problema? No. El minuto es una propiedad numérica derivable de `momento - partido_001.inicio` convertido a minutos. Pero es operacionalmente útil tenerlo redundantemente.
>
> Esto es una **manifestación del patrón "pluralidad de tiempos"** ya documentado (música tiene semicorcheas; medicina tiene "cada mañana"; fútbol tiene "minuto del partido"). Sin patch nuevo.

## Nivel 4 — Gol de cabeza tras córner

```
(centro_carrillo, instancia_de, accion_centro)
(centro_carrillo, agente,       carrillo)
(centro_carrillo, parte_de,     segundo_tiempo)
(centro_carrillo, minuto,       67)
(centro_carrillo, tipo_jugada,  corner)                    // → K

(gol_002, instancia_de,    gol_de_cabeza)
(gol_002, agente,          lapadula)
(gol_002, favorece_a,      equipo_peru_2026_10_14)
(gol_002, parte_de,        segundo_tiempo)
(gol_002, minuto,          67)
(gol_002, causado_por,     centro_carrillo)
```

> 🔸 **Sin fricción nueva**. Ya está todo cubierto por D6 + D7 extendido.

## Nivel 5 — La cadena causal del minuto 89 (la más densa)

Una única falta produce **tres consecuencias simultáneas**: el penal, la tarjeta roja, la expulsión.

```
(falta_tapia_alvarez, instancia_de,   accion_falta)
(falta_tapia_alvarez, agente,         tapia)
(falta_tapia_alvarez, paciente,       alvarez)            // V (en este caso Q)
(falta_tapia_alvarez, lugar_de,       area_penal_peru)
(falta_tapia_alvarez, parte_de,       segundo_tiempo)
(falta_tapia_alvarez, minuto,         89)

(penal_001, instancia_de,    accion_penal)
(penal_001, causado_por,     falta_tapia_alvarez)         // D6
(penal_001, favorece_a,      equipo_argentina_2026_10_14)
(penal_001, ejecutor,        messi)
(penal_001, defensor,        gallese)

(tarjeta_roja_tapia, instancia_de,   tarjeta_roja)
(tarjeta_roja_tapia, agente,         arbitro_principal)
(tarjeta_roja_tapia, paciente,       tapia)
(tarjeta_roja_tapia, causado_por,    falta_tapia_alvarez) // D6
(tarjeta_roja_tapia, justificado_por, regla_penal_area)   // D6
(tarjeta_roja_tapia, consecuencia,   expulsion_tapia)     // D7 nuevo!

(expulsion_tapia, instancia_de, expulsion_jugador)
(expulsion_tapia, paciente,     tapia)
(expulsion_tapia, equipo,       equipo_peru_2026_10_14)

(gol_003, instancia_de,    gol_de_penal)
(gol_003, agente,          messi)
(gol_003, favorece_a,      equipo_argentina_2026_10_14)
(gol_003, causado_por,     penal_001)
(gol_003, minuto,          89)
```

> 🔸 **Fricción 3 — Múltiples consecuencias de una misma causa**.
>
> La falta de Tapia es `causado_por` tanto del penal como de la tarjeta roja. No es un problema, son DOS hechos atómicos que apuntan al mismo sujeto-causa. El modelo lo absorbe naturalmente. Confirma que `causado_por` admite múltiples consecuencias (cardinalidad: muchos a uno).
>
> **Sin patch**. Buena confirmación.

> 🔸 **Fricción 4 — `consecuencia` (D7 nuevo) se ejercita aquí**.
>
> La tarjeta roja TIENE como consecuencia la expulsión. Esto es **regla del fútbol aplicada**: roja → expulsión obligatoria. Es el patrón condicional que canonizamos tras contrato. Aquí se ve en su versión más limpia.
>
> Confirma que `consecuencia` era necesaria. Buen uso real.

## Nivel 6 — Sustituciones (cambios de estado)

```
(sustitucion_001, instancia_de,  sustitucion_jugador)
(sustitucion_001, equipo,        equipo_peru_2026_10_14)
(sustitucion_001, sale,          carrillo)               // domain
(sustitucion_001, entra,         polo)                   // domain
(sustitucion_001, parte_de,      segundo_tiempo)
(sustitucion_001, minuto,        60)
```

> 🔸 **Fricción 5 — `sale`/`entra` son domain-specific**.
>
> Estos roles describen un patrón generalizable: **reemplazo**. Aparece en:
> - Fútbol: sustitución de jugadores.
> - Trabajo: reemplazo de personal en un turno.
> - Reuniones: cambio de representante.
> - Empresas: cambio de presidente, gerente.
> - Política: sucesión en cargos.
>
> Posibles nombres canónicos: `saliente` y `entrante`. Por ahora **dejarlo como domain**, anotar como candidato a canonicalización futura si aparece en más dominios.

## Nivel 7 — El marcador como estado derivado

¿Cómo respondemos "¿cuál era el marcador al minuto 80?"?

**No se almacena el marcador**. Se deriva por consulta:

```
phi = { instancia_de: gol_jugada_abierta | gol_de_cabeza | gol_de_penal,
        parte_de: partido_001,
        minuto: <= 80 }
agrupar por favorece_a, contar
→ {equipo_peru: 1, equipo_argentina: 1}
```

> 🔸 **Fricción 6 — Estado derivado a lo largo del tiempo**.
>
> Esto NO es un problema nuevo: es la misma fricción que apareció en contratos (renta vigente en cada momento) y química (composición del sistema en cada instante). El marcador en un minuto dado es **estado derivado** acumulando eventos.
>
> El modelo conceptual lo soporta vía consultas con filtros temporales. La eficiencia/practicidad depende del motor.
>
> **Confirma la decisión pendiente #6** (reglas de derivación e invariantes). Es transversal: derecho, química, deporte, todos lo necesitan.

## Nivel 8 — Concurrencia

En el minuto 23, mientras Messi marca, 21 jugadores más están haciendo cosas. Solo registramos lo significativo. No hay friction: la granularidad la decide el modelador, no el modelo.

## Inventario de fricciones (fútbol)

| # | Fricción | Severidad | Resolución |
|---|---|---|---|
| 1 | `partes : T → Q` muy restrictiva | **Media** | **Patch: generalizar a `partes : T → V`** |
| 2 | Dos relojes coexisten | Baja | Confirma "pluralidad de tiempos" ya documentada |
| 3 | Múltiples consecuencias de una causa | Cero | El modelo lo absorbe naturalmente |
| 4 | `consecuencia` (D7) en acción | Cero | Ejercicio real del patch añadido en contratos |
| 5 | `sale`/`entra` domain-specific | Baja | Candidato a `saliente`/`entrante` canónicos en el futuro |
| 6 | Marcador como estado derivado | Baja | Refuerza decisión pendiente #6 (reglas/inferencia) |

## Lo nuevo respecto a contratos y química

- **Una sola fricción genuinamente nueva**: la generalización de `partes` (paralela a la de `paciente`). Es un patrón claro: roles que en su versión Q son demasiado estrechos.
- **Confirmaciones útiles**: `consecuencia`, `causado_por`, `parte_de`, `precede`, `justificado_por` se ejercitan masivamente y funcionan.
- **Refuerzo, no descubrimiento**: la pluralidad de tiempos, el estado derivado, la inmutabilidad — todos ya conocidos.

## Conclusión preliminar

**El modelo aguanta fútbol con apenas un patch**: generalizar `partes`. El resto del dominio se modela limpiamente con el catálogo extendido tras los dominios previos.

Lo más interesante es **la frecuencia con que aparece el "estado derivado a lo largo del tiempo"**. Tres dominios distintos (contratos, química, fútbol) lo piden con fuerza diferente pero misma forma estructural: necesitamos una capa de inferencia o de consulta temporal que reconstruya el estado del mundo en un momento dado a partir de los eventos acumulados.

## Patch único propuesto

Una sola modificación al documento:

> Cambiar `partes : T → Q (multi)` por **`partes : T → V (multi)`** en el catálogo D7. Razón: los participantes simétricos pueden ser personas (Q), entidades compuestas (T como equipos, alianzas), o conceptos (raro pero posible en derecho abstracto).

¿Lo aplico ya, o esperamos más datos? Como es un cambio muy pequeño y muy claro (mismo patrón que ya aplicamos con `paciente`), recomiendo aplicarlo ahora.

---


# Dominio 9 — Sauna (servicio recreativo con planes y fidelización)

> **Nota de nomenclatura.** Este análisis se hizo el 2026-05-15, posterior al renombramiento de ejes. Aquí ya se usa la nomenclatura actual: **O** (qué/*objectum*), **T** (cuándo/*tempus*), **M** (cómo/*modus*). Q, L, N, K, P no cambiaron.

## Prompt del usuario (2026-05-15)

> en mi sauna las personas ingresan por sesion, cada sesion de sauna cuesta 20 dolares, los usuarios reciben toallas, sandalias y ropa de baño. dentro hay dos camaras de vapor y cámara seca. en ambas la temperatura ronda los 60 grados centigrados, lo recomendable es estar 20 minutos por cada cámara o hasta que el cuerpo lo soporte, es recomendable darse una ducha de agua fria (española) para cerrar los polos, eso causa satisfacción y relajamiento. Se recomienda tomar agua para hidratarse. Los clientes tienen la oportunida de llevarse una sesión gratuita por cada 7 veces que asisten a nuestras instalaciones. Tambien hay promociones como sauna mas gimnasio, sauna mas masaje y sauna más una jarra de agua de cebada. Dentro de las instalaciones se venden jugos, ensaladas de frutas y helados, lo que hace de la experiencia agradable parecida a estar en la playa. En algunos casos el cliente contrata un plan mensual de gimnasio el cual incluye 2 sesiones de sauna por semana.
>
> Este contexto hay que agregarlo en nuestras pruebas de friccion

## Mi análisis

El dominio "sauna" es un buen test porque combina cosas que ya vimos por separado pero raramente todas juntas en un mismo lugar: servicio cobrado por unidad de uso (como el taxi), protocolos recomendados (como una historia clínica light), promociones combinadas (como un sistema de ventas), un programa de fidelización con estado derivado (cuenta de visitas), y consumibles vendidos por separado. Es un dominio comercial pequeño pero rico.

### Mapa de los ejes

**Q (quien)** — agentes:
- `cliente_001`, `cliente_002`, ... — los usuarios humanos.
- `recepcionista_anita`, `masajista_jose` — el personal.
- `sauna_oasis` (la empresa, agente jurídico).
- Algunos artefactos como el `medidor_temperatura_camara_vapor_1` que registran lecturas; agencia contextual D5 — son agentes cuando la situación pide quién hizo la medición.

**O (qué)** — entidades situadas:
- Las **sesiones**: `sesion_2026_05_15_cliente_003` — el evento reificado central del dominio.
- Las **cámaras** físicas: `camara_vapor_1`, `camara_vapor_2`, `camara_seca` — son a la vez objetos (en O) y ubicaciones (jugaríamos con sus aliases `lugar_de` cuando aparecen como L de una sesión).
- Las **adquisiciones** de consumibles: `compra_jugo_017` (jugo de naranja consumido durante la sesión).
- Los **planes mensuales**: `plan_mensual_017` (que se vuelve la fuente de derecho de N sesiones gratuitas/incluidas).
- Las **promociones**: `promo_sauna_gimnasio`, `promo_sauna_masaje`, `promo_sauna_jarra_cebada` — son ofertas reificadas (no instancias de uso, sino tipos comerciales).
- Las **recomendaciones**: `recomendacion_20_min_camara`, `recomendacion_ducha_fria_final` — reglas con `estatus_factual: recomendacion`.

**L (donde)**:
- `sauna_oasis_local_central`, `camara_vapor_1`, `camara_seca`, `ducha_03`, `area_descanso`.
- Aquí aparece el patrón habitual: las cámaras son objetos físicos (entrarían en O si las consideramos como cosas con propiedades — su temperatura, su capacidad), pero también son ubicaciones (entrarían en L cuando son el `lugar_de` de una sesión). El modelo no obliga a elegir: el mismo individuo puede vivir en O como objeto-mantenimiento y en L como lugar-de-uso. Las consultas distinguen por rol, no por eje.

**T (cuándo)**:
- Momentos puntuales: `2026-05-15T18:30Z` (inicio de sesión), `2026-05-15T19:10Z` (fin).
- Intervalos: `semana_2026_w20`, `mes_2026_05`.
- Calendarios del plan: períodos de validez del plan mensual.

**N (cuánto)**:
- Magnitudes con unidad QUDT: `20 USD` (precio), `60 °C` (temperatura), `20 min` (duración recomendada), `2 sesiones/semana` (cuota incluida).
- Conteos: `7` (cantidad de visitas para una sesión gratuita), `42 kWh` (consumo eléctrico de la caldera, si llegara a importar).

**K (clase)** — el zócalo categórico, denso aquí:
- Tipos de servicio: `servicio_sauna`, `servicio_gimnasio`, `servicio_masaje`.
- Tipos de cámara: `tipo_camara_vapor`, `tipo_camara_seca`.
- Equipamiento entregado: `toalla`, `sandalia`, `ropa_de_bano` — objetos por categoría, no por instancia individual (no rastreamos cada toalla).
- Estados de sesión: `iniciada`, `en_curso`, `finalizada`, `cancelada`.
- Tipos de consumibles: `jugo`, `ensalada_frutas`, `helado`.
- Estados del cliente respecto al programa de fidelidad: `visitas_acumuladas_actuales` (atributo derivable), `tiene_sesion_gratis_disponible`.
- Unidades QUDT estándar (`Currency:USD`, `Temperature:Cel`, `Time:Minute`).

**P (cuál)** y **M (cómo)** — predicados ya cubiertos en el catálogo D7:
- `cliente`, `servicio_prestado`, `cantidad_pagada`, `inicio`, `fin`, `lugar_de`, `temperatura_medida`, `duracion`, `parte_de`, `incluye`, `causado_por`, `con_finalidad`, `justificado_por`.

### Cinco situaciones canónicas

**1. Una sesión normal cobrada directamente.**

```
(sesion_2026_05_15_c003) ∈ O
  instancia_de    : servicio_sauna       ∈ M(O, K)
  cliente         : cliente_003          ∈ M(O, Q)
  lugar_de        : sauna_oasis_central  ∈ P(O, L)
  inicio          : 2026-05-15T18:30Z    ∈ P(O, T)
  fin             : 2026-05-15T19:10Z    ∈ P(O, T)
  estatus_factual : finalizada           ∈ P(O, K)

(pago_001) ∈ O
  parte_de        : sesion_2026_05_15_c003
  pagado_por      : cliente_003
  monto           : 20                   ∈ P(O, N)
  unidad          : Currency:USD         ∈ P(O, K)
```

Sin fricción: el patrón es idéntico al de "ventas" pero con una `instancia_de` distinta.

**2. El cliente se ducha en frío al final.**

```
(ducha_fria_001) ∈ O
  parte_de        : sesion_2026_05_15_c003
  instancia_de    : accion_ducha
  agua_temperatura : 12 °C
  agente          : cliente_003
  momento         : 2026-05-15T19:08Z

(satisfaccion_001) ∈ O
  instancia_de    : estado_subjetivo
  sujeto          : cliente_003
  intensidad      : alta
  causado_por     : ducha_fria_001       ∈ M(O, O)
```

Aquí entra D6 (cap 11) con `causado_por`. El modelo soporta limpiamente que un estado subjetivo posterior se atribuya a una acción anterior. La recomendación misma (la regla del local) vive aparte:

```
(recomendacion_ducha_fria) ∈ O
  instancia_de    : recomendacion
  alcance         : servicio_sauna
  contenido       : "Tomar ducha fría al final de la sesión."
  efecto_esperado : satisfaccion_y_relajamiento

(ducha_fria_001, justificado_por, recomendacion_ducha_fria)
```

Un mismo evento (la ducha) tiene **dos** relaciones del "por qué" simultáneas: lo causó la recomendación que el cliente decidió seguir (`justificado_por`) y a su vez **causó** una satisfacción (`causado_por`). El modelo lo expresa sin tensión.

**3. Promoción combinada — sauna + masaje.**

```
(uso_promo_017) ∈ O
  instancia_de    : aplicacion_de_promocion
  promocion       : promo_sauna_masaje   ∈ M(O, O)
  cliente         : cliente_003
  fecha           : 2026-05-15

(sesion_2026_05_15_c003, parte_de, uso_promo_017)
(masaje_2026_05_15_c003, parte_de, uso_promo_017)

(pago_002) ∈ O
  parte_de  : uso_promo_017
  monto     : 50  (en lugar de 20 + 35)
  unidad    : Currency:USD
```

Lo importante: la **agrupación bajo la promoción** se reifica (uso_promo_017), y los dos servicios atómicos cuelgan de ella por `parte_de`. El descuento conjunto se expresa como un pago único asociado al uso de la promoción, no como dos pagos parciales. Esto es lo mismo que vimos en "ventas" con líneas de venta agrupadas — no agrega fricción nueva.

**4. Programa de fidelización — 7 visitas, 1 gratis.**

Acá hay un patrón que ya conocemos: **estado derivado a partir de eventos acumulados**, exactamente la misma forma estructural que el marcador de un partido de fútbol o el estado actual de un contrato. El modelo registra los hechos atómicos:

```
(sesion_..._c003, instancia_de, servicio_sauna)
(sesion_..._c003, cliente, cliente_003)
(sesion_..._c003, estatus_factual, finalizada)
```

...repetidos N veces. La pregunta *"¿cuántas sesiones lleva cliente_003?"* es una consulta de agregación: contar las situaciones que satisfacen `instancia_de = servicio_sauna AND cliente = cliente_003 AND estatus_factual = finalizada`. Cuando ese conteo llega a 7, se habilita una sesión gratuita. Esa habilitación se reifica también:

```
(beneficio_gratis_017) ∈ O
  instancia_de       : beneficio_fidelidad
  beneficiario       : cliente_003
  consecuente        : sesion_gratuita_pendiente
  generado_por       : [sesion_001, sesion_002, ..., sesion_007]  ← multi-valor en M
  fecha_emision      : 2026-04-22
  estatus_factual    : pendiente_de_usar
```

Y luego, cuando el cliente lo redime:

```
(sesion_..._c003_gratis) ∈ O
  instancia_de   : servicio_sauna
  cliente        : cliente_003
  redime         : beneficio_gratis_017
  costo_efectivo : 0
```

**Confirmación, no fricción nueva**: el dominio refuerza por enésima vez que el modelo necesita un evaluador externo capaz de recalcular conteos. La regla *"7 visitas → 1 gratis"* es una norma reificada (D6 + capítulo 11) que ese evaluador interpreta; el modelo de datos no ejecuta nada por sí mismo.

**5. Plan mensual con sesiones incluidas.**

```
(plan_mensual_017) ∈ O
  instancia_de    : plan_gym_mensual
  cliente         : cliente_003
  inicio          : 2026-05-01
  fin             : 2026-05-31
  incluye         : 2 sesiones_sauna por semana
  precio          : 80 USD

(sesion_..._c003_del_plan) ∈ O
  instancia_de   : servicio_sauna
  cliente        : cliente_003
  cubierto_por   : plan_mensual_017    ← M(O, O)
  costo_efectivo : 0
```

La cuota *"2 sesiones por semana"* es interesante: no es un valor fijo en N, es un **derecho de uso periódico**. En el modelo se expresa como una propiedad del plan (`asignacion_semanal: 2 sesiones`) y la lógica de validación — *"¿puede el cliente_003 entrar gratis hoy, o ya consumió sus 2 esta semana?"* — vive en el evaluador, no en el dato. Vuelve a aparecer la misma necesidad: una capa de reglas declarativas que se aplica sobre el grafo.

### Inventario de fricciones (sauna)

| # | Fricción | Severidad | Resolución |
|---|---|---|---|
| 1 | Cámaras como objeto y lugar simultáneamente | Cero | El modelo lo permite por rol; no por eje |
| 2 | Conteo de visitas para fidelidad | Cero (refuerzo) | Misma necesidad de evaluador de reglas (D6 + cap 11) |
| 3 | Cuota semanal del plan mensual | Cero (refuerzo) | El derecho de uso periódico se declara, el evaluador lo aplica |
| 4 | Promoción combinada con precio único | Cero | Patrón `parte_de` ya validado en ventas |
| 5 | Recomendaciones como reglas blandas | Cero | `instancia_de: recomendacion` + `justificado_por` cubre el caso |

### Lo nuevo y lo viejo

**Lo nuevo**: nada estructural. El dominio se modela limpiamente con el catálogo actual.

**Lo confirmado**:
- D5 — agencia contextual — al considerar a las cámaras y los medidores como agentes en contextos específicos (la medición de temperatura).
- D6 + cap 11 — las cuatro relaciones del "por qué" — todas activas en este dominio: `causado_por` (ducha → satisfacción), `motivado_por` (cliente quiere relajarse → toma sesión), `con_finalidad` (ducha fría para cerrar poros), `justificado_por` (sesión sigue la recomendación del local).
- D7 — el catálogo de roles canónicos — `cliente`, `lugar_de`, `inicio`, `fin`, `parte_de`, `incluye`, `cubierto_por` se reutilizan sin extensión.
- Patrón de **estado derivado por agregación de eventos**: visto en contratos, fútbol, química, y ahora aquí con el contador de fidelidad. Tercera o cuarta vez que aparece; el evaluador externo es una necesidad genuina, no una hipótesis.

### Conclusión preliminar

**El modelo absorbe sauna sin un solo parche.** Es un dominio comercial mediano que funciona como buen ejemplo *pedagógico* — más cercano a la vida diaria del lector que la combustión del metano — pero estructuralmente no estresa el catálogo. Lo que sí confirma, una vez más, es la importancia de la capa de **reglas declarativas y evaluador** que el capítulo 11 introdujo como puente; el sauna, con su contador "7 → 1 gratis" y su cuota "2 por semana", es probablemente el ejemplo más intuitivo del libro para esa idea.

---
