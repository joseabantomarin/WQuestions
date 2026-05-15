# WQuestions — Modelo de información basado en coordenadas-pregunta

## Visión

Definir un estándar para modelar información de cualquier contexto usando un conjunto fijo de coordenadas-pregunta. Cada hecho del mundo se ubica como una tupla en un espacio multidimensional cuyos ejes son las preguntas fundamentales: quién, qué, dónde, cuándo, cuál, cuánto, cómo, y la nueva pregunta de clasificación (qué tipo / qué clase).

Objetivo final: que sistemas de IA puedan acceder, validar y razonar sobre información de forma más rápida y precisa, buscando por "puntos" parciales en este espacio.

## 1. Conjuntos base

### Ejes de valor (contienen individuos, disjuntos entre sí)

```
Q  (quien)   — agentes capaces de acción
O  (que)     — objetos / cosas / eventos / situaciones (instancias concretas)
L  (donde)   — ubicaciones físicas
T  (cuando)  — momentos o intervalos temporales
N  (cuanto)  — magnitudes / cantidades (números puros)
K  (clase)   — tipos / categorías / conceptos abstractos
```

Sea `V = Q ∪ O ∪ L ∪ T ∪ N ∪ K` el universo de individuos.

Cada individuo pertenece a *exactamente un* eje, vía una función de tipo:

```
tau : V -> {Q, O, L, T, N, K}
tau(juan_perez)    = Q
tau(chile)         = L
tau(2026-05-13)    = T
tau(100)           = N
tau(kilogramo)     = K
tau(boleta)        = K
tau(coca_cola_500) = K     // el SKU como tipo
tau(botella_007)   = O     // la botella física
```

**Nota sobre la estructura interna de los ejes**: los individuos de cualquier eje, incluido K, son ciudadanos de primera clase. Pueden tener su propia red de hechos. Por ejemplo, `losartan_50mg ∈ K` tiene propiedades internas:

```
(losartan_50mg, instancia_de,     medicamento_formulado)
(losartan_50mg, principio_activo, losartan)        // → K (otro K)
(losartan_50mg, dosis,            50)              // → N
(losartan_50mg, unidad_dosis,     miligramo)       // → K
```

K no es un conjunto plano de etiquetas opacas; es una red de tipos con propiedades.

### Ejes estructurales (contienen etiquetas, no individuos)

```
P  (cual)  — nombres de propiedades (binarias funcionales)
M  (como)  — nombres de relaciones (n-arias, no funcionales)
```

Cada etiqueta tiene una **signatura** que dice qué ejes conecta:

```
sigma(lugar_nacimiento) = (Q, L)     // de un quien a un donde
sigma(edad)             = (Q, N)     // de un quien a un cuanto
sigma(unidad_medida)    = (O, K)     // de un que a una clase
sigma(instancia_de)     = (V, K)     // universal: cualquier individuo a su tipo
sigma(viaja_en)         = (Q, O)     // de un quien a un que
sigma(ocurre_entre)     = (T, T)     // entre dos momentos
```

## 2. Decisiones de diseño

**D1 — Un dato vive en un solo eje.**
"Asiento 14B" se modela como dos individuos: `a14B ∈ O` (el objeto) y `"14B" ∈ N` (el código), conectados por `codigo(a14B) = "14B"`. Evita ambigüedades.

**D2 — Un contexto es una situación en O.**
Una *situación* es un individuo en `O` con rol especial: sirve de ancla para colgar hechos. Una venta, un viaje, una reunión son situaciones. Se conectan con `parte_de`.

**D3 — `cual` y `como` se unifican matemáticamente.**
Ambas son relaciones binarias tipadas. La distinción es pragmática:

- `P` cuando se siente como **atributo** ("edad", "nombre").
- `M` cuando se siente como **enlace** ("viaja_en", "es_amigo_de").

El motor las trata igual.

**D4 — Los conceptos abstractos viven en K, no en O.**
"kg", "PEN", "boleta", "cliente", "efectivo" son tipos, no objetos concretos. Van en `K`. Se conectan al resto vía propiedades estándar:

```
unidad_medida    : O → K
tipo_comprobante : O → K
forma_pago       : O → K
moneda           : N → K   // si N admite anotación
rol_en           : O × Q → K
```

La etiqueta universal `instancia_de : V → K` permite preguntar el tipo de cualquier individuo.

**Refinamiento (frontera K vs O para entidades culturales)**: la distinción operativa es:

- **K** = conceptos / tipos / categorías **atemporales** (sinfonía, boleta, kilogramo, cardiología, persona_natural). No tienen autor, ni fecha de creación, ni historia.
- **O** = entidades **creadas, instanciadas, o situadas** (la Sinfonía No. 5 de Beethoven, la boleta BV001-001234, el viaje_001). Tienen autor / momento de creación / historia.

Esta distinción evita la tentación de meter obras concretas (libros, sinfonías, películas, leyes) en K. Una obra es siempre O; su género es K.

**D5 — La agencia se modela contextualmente, no por reclasificación.**
`Q` es estable y agrupa "agentes naturales/legales" (personas, organizaciones, sistemas autónomos designados). Cuando un `O` (un robot, un script) actúa como agente en una situación específica, **no se reclasifica**: se marca la agencia *en esa situación* con un hecho:

```
(emision_factura_42, agente, script_facturador)   // script_facturador ∈ O
```

Esto mantiene `Q` estable y permite agencia contextual.

**D6 — El "por qué" es relacional, no domanial.**
WQuestions deliberadamente **no tiene eje de "why"**. La razón: los valores que responden "por qué" son heterogéneos (a veces una situación causante, a veces un concepto/criterio, a veces una intención, a veces una regla); no forman un dominio coherente. Cada uno ya tiene su lugar natural en O o K.

En su lugar, se reserva en `M` una **familia canónica de relaciones de por qué** con semántica especial para el motor de consulta y explicación:

```
causado_por      : O → O          // por-qué causal:       "se canceló porque..."
motivado_por     : O → Q ∪ K      // por-qué motivacional: "lo hizo porque quería..."
con_finalidad    : O → O ∪ K      // por-qué teleológico:  "para llegar a..."
justificado_por  : O → O ∪ K      // por-qué normativo:    "porque la regla dice..."
```

Estas cuatro relaciones le dan al motor:

- Consultas de por qué tipadas (`phi = { causado_por: ?, sujeto: viaje_001 }`).
- Cadenas explicativas (transitividad en `causado_por`).
- Distinción semántica entre causa, motivo, finalidad y justificación sin colapsar a una sola etiqueta.

**D7 — Las preguntas refinadas son ROLES, no ejes.**
Las preguntas naturales adicionales (*para qué, por dónde, de dónde, hacia dónde, con quién, con cuál, por cuánto*) no piden tipos de cosa nuevos: piden cosas que ya viven en los 8 ejes, pero desempeñando un **rol** específico en la situación.

Se materializan como etiquetas canónicas en `P` (o `M`) con signaturas tipadas hacia el eje correspondiente. El modelo se mantiene en 8 ejes; la riqueza vive en el catálogo de roles. Este catálogo coincide casi 1-a-1 con los **roles temáticos** del análisis neo-davidsoniano, de donde se hereda directamente.

### Catálogo canónico de roles

```
Roles espaciales (→ L):
  lugar_de            : O → L         // dónde (general)
  origen              : O → L         // de dónde
  destino             : O → L         // hacia dónde
  via / por_donde     : O → L ∪ O     // por dónde (ruta puede ser objeto)

Roles humanos / participantes (→ Q):
  agente / protagonista : O → Q       // quién (principal)
  acompañantes        : O → Q (multi) // con quién
  beneficiario        : O → Q         // para quién (humano)
  partes              : O → V (multi) // partes de una acción bilateral/multilateral
                                      // simétrica. Generalizada de Q a V: las
                                      // partes pueden ser personas (firmar), equipos
                                      // (partido), entidades compuestas (fusión),
                                      // o cualquier individuo del universo

Rol de afección (→ V — generalizado):
  paciente            : O → V         // a quién/qué se afecta o transforma
                                      // generalizado de Q a V: paciente puede ser
                                      // humano (Q), objeto (O) o concepto (K).
                                      // ej: "el médico examina al paciente" (Q),
                                      //     "la reacción transforma metano" (O),
                                      //     "la ley regula el comercio" (K)

Roles instrumentales (→ O ∪ K):
  instrumento / con_cual : O → O ∪ K  // con qué
  medio                  : O → O ∪ K

Roles cuantitativos (→ N):
  cantidad            : O → N         // cuánto
  precio / por_cuanto : O → N         // por cuánto monetario
  duracion            : O → N         // cuánto tiempo
  distancia           : O → N

Roles causales / intencionales (D6):
  causado_por         : O → O
  motivado_por        : O → Q ∪ K
  con_finalidad / para_que : O → O ∪ K
  justificado_por     : O → O ∪ K

Roles condicionales:
  condicion           : O → O         // antecedente de una regla / cláusula
  consecuencia        : O → O         // consecuente derivado de la condición
                                      // ej: cláusula resolutoria contractual,
                                      //     indicación médica condicional,
                                      //     regla "si X entonces Y"

Roles temporales (→ T):
  momento / cuando    : O → T
  inicio              : O → T
  fin                 : O → T
  intervalo           : O → T         // par o intervalo
  precede             : O → O         // orden temporal entre situaciones
  sigue_a             : O → O         // inversa de precede

Roles mereológicos (→ O):
  parte_de            : O → O         // todo-parte: una situación contiene a otra
  contiene            : O → O (multi) // inversa de parte_de

Roles de transformación / producción (→ V):
  insumo              : O → V (multi) // lo que la situación consume/transforma
                                      // ej: química (reactivos), cocina (ingredientes),
                                      //     manufactura (materias primas),
                                      //     software (entrada)
  producto            : O → V         // lo que la situación produce / output
                                      // ej: diagnóstico produce etiqueta_K;
                                      // panificación produce pan ∈ O;
                                      // emisión produce factura ∈ O

Roles referenciales (→ O):
  referencia / sobre  : O → O         // una situación refiere a otra
                                      // ej: pago→consulta, devolución→venta,
                                      // comentario→post, cita→paper

Roles clasificatorios (→ K):
  instancia_de        : V → K         // universal
  rol_en              : O × Q → K     // rol contextual de un Q en una situación
```

El catálogo es **canónico pero ampliable**: cada dominio puede agregar etiquetas con signatura propia (`asiento`, `placa`, `IGV`, etc.), pero las preguntas universales usan los nombres de arriba.

Ventajas:

- **Vocabulario común**: modelados distintos del mismo dominio convergen a las mismas etiquetas → interoperabilidad gratis.
- **Consultas semánticamente tipadas**: `phi = { origen: ?, destino: ? }` tiene la misma forma para viajes, envíos, migraciones, transferencias bancarias.
- **Motor más inteligente**: el engine sabe que `origen` y `destino` son inversos espaciales, que `con_finalidad` es teleológico, que `inicio` y `fin` delimitan intervalos, que `parte_de` es transitiva, que `precede` es transitiva y antisimétrica.

### Convención: `estatus_factual` para situaciones no-actuales

No todas las situaciones reificadas son hechos consumados. Algunas son **planeadas, esperadas, hipotéticas o canceladas**. En vez de duplicar el catálogo de roles (ej. `agente_planeado` vs `agente`), se marca la situación con una propiedad de estatus y se dejan los roles normales:

```
estatus_factual : O → K
  valores: real | planeado | confirmado | hipotetico | cancelado
```

Ejemplo (consulta médica con control futuro):

```
(control_futuro, instancia_de,    accion_consultar)
(control_futuro, estatus_factual, planeado)        // la situación aún no ocurre
(control_futuro, agente,          dr_ramos)        // rol estándar, no "agente_planeado"
(control_futuro, paciente,        maria)
(control_futuro, momento,         2026-06-03)      // momento estándar
```

El motor interpreta los roles según el estatus: en `planeado`, "agente" significa "agente previsto", no "agente que actuó".

### Convención: pluralidad de tiempos

`T` está reservado para **tiempo absoluto/lineal del mundo real** — instantes y intervalos del calendario y del reloj. Pero algunos dominios usan tiempos de otra naturaleza, que NO viven en T:

- **Tiempo relativo musical** (semicorchea, blanca, compás 32): son categorías de duración relativa al tempo. Viven en **K** como tipos rítmicos, o se reifican como O-individuos (compases, frases) cuando tienen identidad.
- **Tiempo recurrente / cíclico** (cada mañana, cada 8 horas, anualmente): son patrones, no instantes. Viven en **K** como patrones temporales (`cada_mañana`, `frecuencia_diaria`), o eventualmente como O-individuos con estructura (frecuencia + inicio + fin).
- **Tiempo narrativo** ("al principio", "luego", "finalmente"): orden relativo sin anclaje absoluto. Se modela con la relación `precede` (catálogo D7) entre situaciones.

La conversión entre tiempos (ej. semicorchea en tempo allegro = X milisegundos) se calcula, no se almacena. El modelo no fuerza unificar todos los tiempos en T; respeta que la realidad tiene varios tiempos cualitativamente distintos.

### Convención: `agente` es el principal

Cuando una situación tiene **múltiples participantes funcionales** (típico en performances, producciones, equipos), el rol canónico `agente` se reserva para el **agente principal según la naturaleza del verbo / tipo de situación**. Los demás participantes funcionales usan **roles de dominio** específicos.

Ejemplos:

```
GRABACIÓN MUSICAL:
  (grabacion_1955, agente,      karajan)              // principal: el director
  (grabacion_1955, ejecutante,  berliner_phil)        // rol de dominio
  (grabacion_1955, productor,   emi)                  // rol de dominio
  (grabacion_1955, ingeniero,   ...)                  // rol de dominio

CONSULTA MÉDICA:
  (consulta_001, agente,    dr_ramos)                 // principal: el médico
  (consulta_001, paciente,  maria_gonzales)           // canónico (no agente)
  (consulta_001, asistente, enfermera_ana)            // rol de dominio

OPERACIÓN QUIRÚRGICA:
  (cirugia_001, agente,           dr_smith)           // cirujano principal
  (cirugia_001, asistente_primer, dr_jones)
  (cirugia_001, anestesiólogo,    dr_lee)
  (cirugia_001, paciente,         maria)
```

Esto preserva la consultabilidad de `agente` (siempre devuelve UNA persona, el principal) y deja espacio para la riqueza específica de cada dominio sin sobrecargar el catálogo canónico.

### Convención: atajos derivables

Para acortar consultas comunes, se admiten **atajos derivables** a partir de reificaciones canónicas. Ejemplo:

```
PATRÓN GENERAL (canónico):
  acto_X(agente=A, producto=W)

ATAJO DERIVABLE:
  W.creador = A
  A.creó = W   (multivaluado)
```

Casos de aplicación:

- composición → compositor (música)
- escritura → autor (literatura)
- fabricación → fabricante (producción)
- emisión → emisor (documentos)
- programación → desarrollador (software)
- diseño → diseñador (industria creativa)

Los atajos pueden almacenarse redundantemente (más simple) o computarse vía reglas de inferencia (más limpio). La decisión es de implementación, no de modelo: el modelo conceptual los considera **derivados de la reificación canónica**, no primitivos.

### Convención: acciones bilaterales/multilaterales simétricas

Cuando una situación tiene **dos o más participantes simétricos** (sin agente principal claro), no se fuerza el rol `agente`. Se usa `partes : O → V (multi)`. Las partes pueden ser de cualquier eje según el dominio:

```
FIRMA DE CONTRATO (partes ∈ Q):
  (firma_001, partes, {juan_perez, ana_lopez})
  (firma_001, sobre,  contrato_001)
  (firma_001, momento, 2026-06-01)

MATRIMONIO (partes ∈ Q):
  (matrimonio_001, partes,    {persona_a, persona_b})
  (matrimonio_001, oficiante, registrador)            // sí hay agente externo

ACUERDO COMERCIAL (partes ∈ Q jurídicas):
  (acuerdo_001, partes, {empresa_a, empresa_b, empresa_c})

PARTIDO DEPORTIVO (partes ∈ O — equipos como entidades compuestas):
  (partido_001, partes, {equipo_peru_2026_10_14,
                         equipo_argentina_2026_10_14})

FUSIÓN EMPRESARIAL (partes ∈ Q jurídicas):
  (fusion_001, partes,    {empresa_x, empresa_y})
  (fusion_001, producto,  empresa_z)
```

Esto preserva la regla de que `agente` siempre es UN actor principal. Cuando hay simetría, `partes` captura la pluralidad sin distorsionar la semántica, y la generalización a V permite que las partes sean del eje que el dominio requiera.

### Convención: hechos inmutables (cambios = nuevas situaciones)

Los hechos almacenados **no se actualizan**: una vez registrado un hecho, queda fijo en el tiempo. Los cambios de estado del mundo se modelan como **nuevas situaciones que refieren a las anteriores**, no como actualizaciones de hechos existentes.

```
INCORRECTO:
  (pago_001, estatus_factual, planeado)
  (pago_001, estatus_factual, real)            // actualizar campo → no
  (pago_001, momento, 2026-07-03)

CORRECTO:
  (pago_planeado_001, instancia_de,   pago_renta_mensual)
  (pago_planeado_001, estatus_factual, planeado)
  (pago_planeado_001, vencimiento,    2026-07-05)

  (pago_real_001, instancia_de,   pago_renta_mensual)
  (pago_real_001, estatus_factual, real)
  (pago_real_001, cumple,         pago_planeado_001)  // nuevo rol
  (pago_real_001, momento,        2026-07-03)
```

Roles canónicos asociados al patrón de inmutabilidad:

```
cumple    : O → O   // una situación real satisface una situación planeada
cancela   : O → O   // una situación cancela/anula otra
modifica  : O → O   // una situación supersede a otra con cambios
```

Esto es el patrón CIDOC CRM en producción y permite auditoría/trazabilidad completas.

### Convención: plantilla en K + instancia en O con factor de escala

Muchos procesos del mundo tienen una **forma replicable** y muchas **ocurrencias** concretas. La forma vive en `K` (atemporal, con estructura interna); las ocurrencias en `O` (situadas, con factor de escala).

```
PLANTILLA (K) — atemporal, estructural:
  (reaccion_combustion_metano, instancia_de,   reaccion_combustion)
  (reaccion_combustion_metano, ecuacion,       "CH4 + 2 O2 → CO2 + 2 H2O")
  (reaccion_combustion_metano, energia_kJ_mol, 890)
  (reaccion_combustion_metano, reactivo_ratio, {metano: 1, oxigeno: 2})
  (reaccion_combustion_metano, producto_ratio, {dioxido_carbono: 1, agua: 2})

INSTANCIA (O) — situada, con escala:
  (reaccion_001, instancia_de, reaccion_combustion_metano)
  (reaccion_001, lugar_de,     laboratorio_a)
  (reaccion_001, momento,      2026-05-14_10:00)
  (reaccion_001, escala_mol,   1)                  // multiplicador
```

Las cantidades concretas son derivables del ratio en K × la escala en O. Casos de aplicación:

- **Recetas** (K) + cocción específica (O) — porciones a partir de la escala.
- **Procesos industriales** (K) + corrida de producción (O).
- **Algoritmos** (K) + ejecución (O).
- **Procedimientos médicos** (K) + intervención específica (O).
- **Reacciones químicas** (K) + reacción específica (O).
- **Contratos tipo** (K) + contratos firmados (O) — con partes y montos específicos.

### Convención: reificar = subir resolución

Cualquier propiedad de una situación puede **reificarse** (volverse entidad propia con sus propias propiedades) cuando se necesita más detalle analítico.

```
Resolución baja (propiedad):
  (reaccion_001, energia_liberada_kJ_mol, 890)

Resolución alta (entidad reificada):
  (energia_001, instancia_de, energia_calorica)
  (energia_001, magnitud,     890)
  (energia_001, unidad,       kilojulios_mol)
  (reaccion_001, producto,    energia_001)         // ahora la energía es producto
```

Reificar permite hablar **de** la propiedad (de dónde vino, a dónde va, conservación, transferencia, intervalo de confianza, fuente de medición). No reificar es más compacto pero pierde esa flexibilidad.

**Regla práctica**: empezar sin reificar; reificar cuando la propiedad necesita propiedades propias o cuando va a ser objeto de razonamiento (conservación, conversión, agregación).

### Convención: mediciones con unidad reificadas

Una medición con unidad se reifica como O-individuo cuando se necesita razonar sobre ella (conversiones, propagación, agregación, comparación cross-unidad). Cuando es un valor de uso simple, se mantiene como propiedad directa con unidad en el nombre.

Estructura canónica del individuo-medición:

```
medicion ∈ O
(medicion, instancia_de,   magnitud_medida)  // → K
(medicion, valor,          N)                // → N: el número
(medicion, unidad,         K)                // → K: kilogramo, soles, mmHg
(medicion, tipo,           K)                // → K: opcional (presion, peso)
(medicion, incertidumbre,  N)                // → N: opcional (margen de error)
(medicion, fuente,         O)                // → O: opcional (instrumento)
(medicion, momento,        T)                // → T: opcional (cuándo se midió)
```

**Cuándo reificar**: comparaciones cross-unidad (cm vs m), conversión de moneda, agregación con propagación de error, mediciones temporales que cambian, valores con incertidumbre relevante.

**Cuándo NO reificar**: valores fijos del dominio (precios en soles en un sistema doméstico), one-offs sin necesidad analítica posterior. La opción simple (unidad en el nombre: `peso_kg`, `presion_sistolica_mmHg`) sigue siendo válida y preferible cuando es suficiente.

### Convención: usar QUDT como K canónico para unidades de medida

Cuando se reifique una medición de naturaleza estándar (científica, técnica, ingenieril), se usan los URIs de **QUDT** (Quantities, Units, Dimensions, Types — https://qudt.org) como individuos canónicos en K para unidades y tipos de cantidad, en lugar de strings ad-hoc.

QUDT es una ontología OWL mantenida por una organización sin fines de lucro 501(c)(3), implementa los estándares BIPM/SI, ISO y NIST, y contiene cientos de `QuantityKind` y miles de `Unit`. Es el donante natural para K-mediciones.

```
ANTES (ad-hoc):
  (medicion_pres_001, valor,  145)
  (medicion_pres_001, unidad, "mmHg")
  (medicion_pres_001, tipo,   "presion_sistolica")

DESPUÉS (con QUDT):
  (medicion_pres_001, valor,         145)
  (medicion_pres_001, unidad,        qudt-unit:MilliM_HG)             // → K (URI QUDT)
  (medicion_pres_001, tipo,          qudt-qk:BloodPressureSystolic)   // → K (URI QUDT)
  (medicion_pres_001, incertidumbre, 5)
```

Es D8 aplicado a mediciones: QUDT vive abajo (canónico de mediciones); el usuario habla en lenguaje natural ("presión 145 mmHg") en la capa superior. Ver [related/qudt-measurements.md](related/qudt-measurements.md) para detalles.

Esta convención **no es obligatoria** para todo dominio: en sistemas donde las unidades son ad-hoc o no estándar (calificaciones internas, métricas de negocio), seguir usando K propio del dominio.

### Convención: reglas reificadas como O-individuos

Las reglas (derivación, invariante, condicional) se reifican como O-individuos con estructura canónica. Esto da una representación declarativa consultable; la *aplicación* o *verificación* de las reglas requiere una capa de motor de inferencia que es trabajo de implementación (ver sección 11).

```
(regla, instancia_de,    tipo_regla)         // → K
(regla, condicion,       situacion)          // → O (D7)
(regla, consecuencia,    situacion)          // → O (D7)
(regla, aplicabilidad,   contexto)           // → O ∪ K
(regla, formulacion,     "descripción NL")
(regla, fuente,          autoridad)          // → O ∪ Q
```

**Tipos canónicos de regla** (valores en K):

- `regla_derivacion`: produce hechos nuevos a partir de otros (precio = base + km × tarifa).
- `regla_invariante`: restricción que debe mantenerse (conservación de masa).
- `regla_condicional`: si X entonces Y, aplicada caso por caso.

**Casos modelados**:

```
CLÁUSULA DE REAJUSTE IPC:
  (regla_ipc, instancia_de,  regla_derivacion)
  (regla_ipc, sobre,         obligacion_renta)
  (regla_ipc, condicion,     paso_un_año)
  (regla_ipc, consecuencia,  ajuste_monto_segun_ipc)
  (regla_ipc, fuente,        contrato_001)

CONSERVACIÓN DE MASA:
  (regla_conserv_masa, instancia_de, regla_invariante)
  (regla_conserv_masa, sobre,        reaccion_quimica)
  (regla_conserv_masa, formulacion,  "masa(reactivos) = masa(productos)")
  (regla_conserv_masa, fuente,       ley_natural_quimica)

ROJA → EXPULSIÓN EN FÚTBOL:
  (regla_roja_expulsion, instancia_de, regla_condicional)
  (regla_roja_expulsion, condicion,    recibir_tarjeta_roja)
  (regla_roja_expulsion, consecuencia, expulsion_jugador)
  (regla_roja_expulsion, fuente,       reglamento_FIFA)
```

**Lo que ESTA convención resuelve**: representación declarativa de reglas, consultable y manipulable como cualquier otro O-individuo.

**Lo que NO resuelve (movido a "pisos siguientes")**: la aplicación efectiva de las reglas. Computar el monto reajustado cada año, verificar conservación de masa al ingresar una reacción, deducir expulsión cuando se ingresa una tarjeta roja — todo eso requiere un **motor de inferencia** que opere sobre el almacenamiento. Tecnologías candidatas: Datalog (RDFox, Soufflé), SHACL para constraints, SWRL para reglas OWL.

**D8 — Invisibilidad del catálogo canónico (D7 es interno).**
El catálogo canónico de roles (D7) es un mecanismo interno de canonicalización, no una interfaz de usuario. Aprender 40-50 etiquetas técnicas para modelar es fricción que el proyecto absorbe, no traslada al usuario. El usuario modela usando lenguaje natural, vocabulario de su dominio, o etiquetas familiares de su UI. La traducción al canónico ocurre en una capa intermedia.

**Arquitectura de capas**:

```
LAYER 4 — UI / lenguaje natural
  "Pedro vendió un libro a María por 20 soles"
  Formulario: vendedor=Pedro, producto=libro, comprador=María, ...
                              ↕
LAYER 3 — Dialecto de dominio (aliases)
  vendedor, cliente, factura, IGV, placa, RUC, licencia, ...
  Cada dominio declara su vocabulario familiar.
                              ↕
LAYER 2 — Lexicon (traducción verbo + rol)
  vender → accion_vender
    vendedor → agente
    producto → tema
    comprador → beneficiario
    precio   → por_cuanto
                              ↕
LAYER 1 — Canónica (D7) — INVISIBLE AL USUARIO
  agente, paciente, tema, origen, destino, momento, ...
```

El usuario interactúa con las capas 3 y 4. El sistema canonicaliza al almacenar (sube hacia layer 1) y decanonicaliza al mostrar (baja hacia layers 3-4).

**Consecuencias operativas**:

1. **El lexicon es la pieza central del proyecto** (no D7). D7 da el vocabulario interno; el lexicon da la traducción.
2. Cada entrada del lexicon lista, además de su tipo de situación y roles canónicos, los **aliases** naturales por rol.
3. Cada dominio puede declarar sus propios aliases sin tocar el canónico.
4. Las consultas también pasan por la traducción: el usuario pregunta "¿qué le vendió Pedro a María?", el motor canonicaliza a `phi = { instancia_de: accion_vender, agente: pedro, beneficiario: maria, tema: ? }`, ejecuta sobre el almacenamiento canónico, y muestra resultados con vocabulario del dominio.

Ejemplo de entrada de lexicon con aliases (forma expandida):

```yaml
verbo: vender
  tipo_situacion: accion_vender
  roles:
    agente:
      canónico:  agente
      aliases:   ["vendedor", "el que vende", "quien vende"]
    tema:
      canónico:  tema
      aliases:   ["producto", "lo vendido", "item", "mercancía"]
    beneficiario:
      canónico:  beneficiario
      aliases:   ["comprador", "cliente", "el que compra"]
    por_cuanto:
      canónico:  por_cuanto
      aliases:   ["precio", "monto", "costo"]
```

D8 declara que **D7 sin lexicon es solo media solución**: el catálogo canónico necesita una capa de aliases naturalmente expresivos para ser usable. La interoperabilidad cross-dominio (motivación de D7) se preserva intacta, pero la usabilidad (motivación de D8) se gana al ocultar el canónico tras una capa de lenguaje cotidiano.

**D9 — Las propiedades temporales se reifican como situaciones con vigencia.**
Cualquier propiedad que **cambia con el tiempo** NO se almacena como atributo directo del sujeto; se reifica como una situación O con `inicio`, `fin`, y los roles relevantes. Esto preserva la historia y habilita consultas temporales del tipo "¿cuál era X en el momento Y?".

```
INCORRECTO (pierde historia, no permite consulta temporal):
  (juan, direccion,   av_larco_123)
  (juan, monto_renta, 2500)
  (juan, cargo,       gerente)

CORRECTO (preserva historia, soporta consulta temporal):
  (residencia_001, instancia_de, residencia)
  (residencia_001, agente,       juan)
  (residencia_001, lugar_de,     av_larco_123)
  (residencia_001, inicio,       2020-01-01)
  (residencia_001, fin,          2024-12-31)

  (residencia_002, instancia_de, residencia)
  (residencia_002, agente,       juan)
  (residencia_002, lugar_de,     calle_x_456)
  (residencia_002, inicio,       2025-01-01)
  (residencia_002, fin,          null)               // todavía vigente

  (cargo_002, instancia_de,   cargo_empresarial)
  (cargo_002, agente,         juan)
  (cargo_002, organizacion,   empresa_y)
  (cargo_002, denominacion,   gerente)
  (cargo_002, inicio,         2023-03-01)
  (cargo_002, fin,            null)
```

**Cuándo aplica D9**: propiedades cambiables — dirección, estado civil, cargo profesional, salario, monto de renta vigente, propietario actual de un bien, peso corporal, calificación crediticia, miembros activos de un equipo, vigencia de una cláusula contractual.

**Cuándo NO aplica**: propiedades estables o inmutables — DNI, fecha de nacimiento, lugar de nacimiento, género asignado al nacer, autoría de una obra publicada, identidad estructural.

**Consultas temporales habilitadas**:

```
¿Cuál era el monto de la renta en julio de 2027?
phi = { instancia_de: obligacion_renta,
        sobre_contrato: contrato_001,
        inicio: <= 2027-07-01,
        fin:    >= 2027-07-01 }
proyección sobre monto.

¿Dónde vivía Juan en 2015?
phi = { instancia_de: residencia,
        agente: juan,
        inicio: <= 2015-12-31,
        fin:    >= 2015-01-01 }
proyección sobre lugar_de.

¿Quiénes eran gerentes activos en 2024?
phi = { instancia_de:  cargo_empresarial,
        denominacion: gerente,
        inicio: <= 2024-12-31,
        fin:    >= 2024-01-01 (o null) }
proyección sobre agente.
```

D9 cierra la decisión pendiente sobre validez temporal. La idea estaba latente desde D2 (contexto = situación en O); D9 la eleva a regla explícita: **toda propiedad cambiable se modela como situación con vigencia**.

## 3. El espacio multidimensional

Antes de pasar a la unidad de información, vale la pena cerrar la metáfora fundacional del proyecto: las coordenadas-pregunta efectivamente definen un **espacio multidimensional** donde la información se ubica. Esta sección explicita qué tipo de espacio es.

### La metáfora geométrica, formalizada

> Cada situación (o cualquier individuo) es un **punto** en un espacio multidimensional. Sus **coordenadas** son los valores de sus roles. Los **ejes** (Q, O, L, T, N, K) son los espacios de valor donde caen esas coordenadas.

Ejemplo: la situación `viaje_001 ∈ O` tiene coordenadas accedidas por roles:

```
viaje_001
  agente        → pedro_taxi     (coordenada en Q)
  paciente      → juan_usuario   (coordenada en Q)
  origen        → punto_juan     (coordenada en L)
  destino       → aeropuerto     (coordenada en L)
  inicio        → 18:37          (coordenada en T)
  fin           → 18:52          (coordenada en T)
  distancia     → 8.3            (coordenada en N)
  instancia_de  → viaje_taxi     (coordenada en K)
```

Es un punto multidimensional, con coordenadas accedidas por **nombre de rol** en vez de por posición.

### Las dimensiones son los **roles**, no los ejes

Los 8 ejes NO son las "dimensiones" del espacio. Son **los espacios donde viven los valores** de las dimensiones. Las dimensiones del espacio son los **roles** del catálogo canónico (D7) más los roles de dominio:

```
DIMENSIONES (roles)                    EJE DE LOS VALORES
─────────────────────────────────────────────────────────
agente, paciente, beneficiario, …      → Q
instrumento, tema, via, parte_de, …    → O (o K)
origen, destino, lugar_de, …           → L
momento, inicio, fin, …                → T
por_cuanto, cantidad, duracion, …      → N
instancia_de, moneda, forma_pago, …    → K
```

Hay ≈30-50 dimensiones canónicas más las dimensiones de dominio (`placa`, `IGV`, `compositor`, etc.). Cada situación toma valores en un subconjunto de esas dimensiones — las que su tipo de situación requiere o admite.

### Tres diferencias con un ℝⁿ clásico

**1. El espacio es parcial.** En ℝⁿ todo punto tiene `n` coordenadas. En WQuestions, un punto solo tiene coordenadas en los roles que su tipo requiere. Una venta no tiene `via`; una lluvia no tiene `agente`; una sinfonía no tiene `lugar_de`. Esto refleja la realidad: el mundo es heterogéneo, no toda situación participa de toda dimensión.

**2. Algunas dimensiones admiten valores múltiples.**

```
(viaje_001, acompañantes, {juan, maria, pedro})       // 3 valores en Q
(viaje_001, via,          {via_expresa, panamericana}) // 2 valores en O
```

**3. El espacio es tipado.** Cada dimensión tiene una **signatura** (en qué eje viven sus valores). No es geometría euclidiana, es geometría algebraica tipada: el rol `origen` solo admite valores en L; el rol `agente` solo en Q.

### El espacio como hoja de cálculo dispersa

La visualización más cercana a la intuición práctica:

```
            agente    paciente  origen   destino  inicio   por_cuanto  ...
            (∈Q)      (∈Q)      (∈L)     (∈L)     (∈T)     (∈N)
          ┌─────────┬─────────┬────────┬────────┬────────┬──────────┬───
viaje_001 │ pedro_t │ juan_u  │origen1 │aerop   │18:37   │   —      │ ...
venta_007 │ maria   │   —     │   —    │   —    │   —    │  21.20   │ ...
sinf_5    │   —     │   —     │   —    │   —    │1804    │   —      │ ...
consul_x  │dr_ramos │ maria   │   —    │   —    │10:00   │ 120.00   │ ...
          └─────────┴─────────┴────────┴────────┴────────┴──────────┴───
```

Cada fila = un punto. Cada columna = una dimensión. Cada celda = una coordenada. Las celdas vacías = dimensiones no aplicables a ese punto.

Pero WQuestions excede la hoja de cálculo en cuatro aspectos: **tipado** (cada columna conoce su eje), **multi-valuado** (algunas celdas son conjuntos), **recursivo** (una celda puede contener otra fila/situación), y **disperso por diseño** (la mayoría de celdas están vacías porque cada punto solo usa las dimensiones que necesita).

### Consultas como restricciones geométricas

La búsqueda parcial que motivó el proyecto desde el inicio funciona como restricción sobre coordenadas:

```
phi = { agente: juan, momento: hoy }

= "Encuentra todos los puntos cuya coordenada-agente sea Juan
   Y cuya coordenada-momento sea hoy"

= un HIPERPLANO en el espacio multidimensional
  (fijamos 2 dimensiones, dejamos libres las demás)
```

La proyección sobre dimensiones libres es la **proyección geométrica clásica**: agrupar/sumar/listar los valores de una coordenada para todos los puntos que caen en el hiperplano. Es exactamente el álgebra de un cubo OLAP o un data warehouse multidimensional.

### Comparación con otros espacios multidimensionales

| Espacio | Naturaleza | Dimensiones | Coordenadas |
|---|---|---|---|
| ℝⁿ clásico | Continuo, geométrico | Fijas, indexadas por número | Reales, totales, únicas |
| Tabla relacional | Discreto, posicional | Fijas, por columna | Tipadas, totales, únicas |
| Cubo OLAP | Discreto, jerárquico | Fijas, con jerarquías | Tipadas, agregables |
| Espacios conceptuales (Gärdenfors) | Continuo, perceptual | Cualidades sensoriales | Reales, con distancia |
| **WQuestions** | Discreto, simbólico | Roles, **abierto** | Tipadas, **parciales**, **multi-valuadas**, **recursivas** |

WQuestions ocupa un nicho propio: **espacio multidimensional simbólico, tipado y disperso**, con coordenadas accedidas por roles nombrados.

### Lo que esto cierra de la intuición fundacional

La pregunta original del proyecto era: *¿puedo ubicar información en un espacio definido por las preguntas-coordenada?* La respuesta formalizada es **sí**:

1. Cada situación (o individuo) es un punto multidimensional. ✓
2. Los ejes (Q, O, L, T, N, K) organizan los valores por naturaleza. ✓
3. Los roles son las dimensiones por las cuales se accede a las coordenadas. ✓
4. Una búsqueda parcial fija algunas coordenadas y proyecta las libres. ✓
5. Cualquier información del mundo cabe en este espacio: la apuesta del proyecto, que cada nuevo dominio validado (aeropuerto, ventas, taxi, clínica, música, ...) refuerza.

La metáfora original se respeta. Lo que el desarrollo agregó es **flexibilidad** (parcialidad, multivaluación, recursión) y **tipado** (cada dimensión sabe en qué eje viven sus valores).

## 4. Hecho atómico

Un **hecho** es una tupla:

```
h = (sujeto, etiqueta, valor1, valor2, ..., valork)
```

Caso binario (el más común):

```
h = (s, etiqueta, v)
```

donde `s` y `v` son individuos en `V`, y `etiqueta ∈ P ∪ M`.

**Ejemplo:** "Juan nació en Chile en 1990" se reifica como una situación `s1 ∈ O` (un evento de nacimiento):

```
(s1, instancia_de,  nacimiento)   // O -> K
(s1, protagonista,  juan)         // O -> Q
(s1, lugar,         chile)        // O -> L
(s1, momento,       1990)         // O -> T
```

## 5. Consulta

Una **consulta** es una asignación parcial sobre los ejes:

```
phi = { eje1 -> valor1, eje2 -> valor2, ... }
```

El motor devuelve todas las situaciones consistentes con `phi`, proyectadas sobre los ejes que `phi` deja libres.

**Ejemplo "¿quién nació en Chile?":**

```
phi = { P: lugar_nacimiento,  L: chile }
```

→ proyecta sobre `Q` → devuelve `{juan, pedro, ...}`.

## 6. Ejemplo: el aeropuerto

`viaje_hoy ∈ O` (la situación-contexto):

```
(viaje_hoy, instancia_de, viaje_aereo)      // O -> K
(viaje_hoy, pasajero,     yo)                // O -> Q
(viaje_hoy, aeronave,     AV1234)            // O -> O
(viaje_hoy, origen,       AICC)              // O -> L
(viaje_hoy, destino,      LIM)               // O -> L
(viaje_hoy, salida,       hoy_10:00)         // O -> T
(viaje_hoy, asiento,      a14B)              // O -> O
(a14B,      codigo,       "14B")             // O -> N
```

## 7. Ejemplo: sistema de ventas

### Individuos por eje

```
Q:  juan_perez, maria_lopez, acme_sac
O:  venta_001, linea_001_a, linea_001_b, sucursal_mira, caja_3,
    botella_007 (la unidad física vendida)
L:  av_larco_123
T:  2026-05-13_14:30
N:  2, 5, 100.00, 18.00, 21.20
K:  persona_natural, persona_juridica, cliente, vendedor,
    coca_cola_500 (el SKU), pan_baguette (el SKU),
    sucursal_tipo, caja_tipo, venta_minorista,
    boleta, factura, efectivo, tarjeta, PEN, unidad, kilogramo
```

### Hechos sobre `venta_001`

```
(venta_001, instancia_de,     venta_minorista)   // O -> K
(venta_001, tipo_comprobante, boleta)            // O -> K
(venta_001, cliente,          juan_perez)        // O -> Q
(venta_001, vendedor,         maria_lopez)       // O -> Q
(venta_001, empresa_emisora,  acme_sac)          // O -> Q
(venta_001, sucursal,         sucursal_mira)     // O -> O
(venta_001, caja,             caja_3)            // O -> O
(venta_001, fecha_emision,    2026-05-13_14:30)  // O -> T
(venta_001, forma_pago,       efectivo)          // O -> K
(venta_001, moneda,           PEN)               // O -> K
(venta_001, total,            21.20)             // O -> N
(venta_001, igv_total,        3.23)              // O -> N
```

### Hechos sobre líneas

```
(linea_001_a, instancia_de,     linea_de_venta)
(linea_001_a, pertenece_a_venta, venta_001)
(linea_001_a, producto,         coca_cola_500)   // O -> K (SKU)
(linea_001_a, cantidad,         2)
(linea_001_a, unidad_venta,     unidad)          // O -> K
(linea_001_a, precio_unitario,  8.50)
(linea_001_a, subtotal,         17.00)
```

### Hechos sobre personas

```
(juan_perez,  instancia_de, persona_natural)
(juan_perez,  nombre,       "Juan Pérez")
(juan_perez,  dni,          12345678)
(juan_perez,  direccion,    av_larco_123)
(acme_sac,    instancia_de, persona_juridica)
(acme_sac,    ruc,          20123456789)
```

### Hechos sobre conceptos en K

```
(kilogramo,  simbolo,        "kg")
(kilogramo,  sistema,        sistema_internacional)
(PEN,        simbolo,        "S/")
(PEN,        emisor,         bcr_peru)
(boleta,     codigo_sunat,   "03")
(efectivo,   liquidez,       inmediata)
```

### Consultas habilitadas

```
¿Qué le compró Juan en mayo?
phi = { cliente: juan_perez, fecha_emision: [2026-05-01, 2026-05-31] }

¿Quién más vendió Coca-Cola 500?
phi = { producto: coca_cola_500 }
proyección sobre vendedor.

¿Qué se vendió en la caja 3 hoy?
phi = { caja: caja_3, fecha_emision: hoy }

¿Qué unidades de medida existen?
phi = { instancia_de: unidad_de_medida }   // K filtrado
```

## 8. Ejemplo: app de taxi (D6 y D7 aplicadas)

Este caso ilustra (a) un dominio de servicios on-demand con varias situaciones encadenadas, (b) el uso de las relaciones canónicas de por qué (D6) y (c) el uso sistemático del catálogo canónico de roles (D7).

### Individuos por eje

```
Q:  juan_usuario, pedro_taxista, plataforma_taxi
O:  vehiculo_abc123, solicitud_001, emparejamiento_001,
    viaje_001, pago_001, app_taxi, cancelacion_007,
    meta_llegar_19:00, regla_tarifa_estandar_2026,
    tarjeta_juan, via_expresa
L:  punto_juan_18:30 (GPS), aeropuerto_jorge_chavez
T:  2026-05-13_18:30, 18:30:30, 18:37, 18:52, 18:53
N:  5, 18.50, 8.3, 4.8
K:  pasajero, conductor, sedan, persona_natural, persona_juridica,
    solicitud_viaje, evento_emparejamiento, viaje_taxi, pago_viaje,
    pendiente, emparejado, en_curso, completado, cancelado,
    efectivo, tarjeta, soles, mas_cercano, intencion, regla_tarifaria
```

### Fase 1: solicitud — quién, de dónde, hacia dónde, cuándo, para qué

```
(solicitud_001, instancia_de,   solicitud_viaje)         // → K
(solicitud_001, agente,         juan_usuario)            // quién  → Q
(solicitud_001, origen,         punto_juan_18:30)        // de dónde → L
(solicitud_001, destino,        aeropuerto_jorge_chavez) // hacia dónde → L
(solicitud_001, momento,        2026-05-13_18:30)        // cuándo → T
(solicitud_001, con_finalidad,  meta_llegar_19:00)       // para qué → O (D6)
(solicitud_001, estado,         pendiente)               // → K
```

### Fase 2: emparejamiento (agencia contextual — D5)

```
(emparejamiento_001, instancia_de,       evento_emparejamiento)
(emparejamiento_001, agente,             app_taxi)        // O como agente (D5)
(emparejamiento_001, sobre_solicitud,    solicitud_001)
(emparejamiento_001, asigna_agente,      pedro_taxista)   // quién conducirá
(emparejamiento_001, asigna_instrumento, vehiculo_abc123) // con cuál vehículo
(emparejamiento_001, momento,            2026-05-13_18:30:30)
(emparejamiento_001, duracion_estimada,  5)               // cuánto tiempo → N
(emparejamiento_001, precio_estimado,    18.50)           // por cuánto → N
(emparejamiento_001, motivado_por,       mas_cercano)     // D6: por qué se asignó
```

### Fase 3: información expuesta al usuario

```
(vehiculo_abc123, instancia_de, sedan)
(vehiculo_abc123, placa,        "ABC-123")
(vehiculo_abc123, marca,        toyota_yaris)

(pedro_taxista, instancia_de, persona_natural)
(pedro_taxista, nombre,       "Pedro García")
(pedro_taxista, licencia,     "L-12345")
(pedro_taxista, calificacion, 4.8)
```

### Fase 4: viaje — agente, paciente, instrumento, por dónde, intervalo

```
(viaje_001, instancia_de,  viaje_taxi)
(viaje_001, deriva_de,     solicitud_001)
(viaje_001, agente,        pedro_taxista)         // quién traslada → Q
(viaje_001, paciente,      juan_usuario)          // a quién traslada → Q
(viaje_001, instrumento,   vehiculo_abc123)       // con cuál → O
(viaje_001, origen,        punto_juan_18:30)
(viaje_001, destino,       aeropuerto_jorge_chavez)
(viaje_001, via,           via_expresa)           // por dónde → O
(viaje_001, inicio,        2026-05-13_18:37)      // → T
(viaje_001, fin,           2026-05-13_18:52)      // → T
(viaje_001, distancia,     8.3)                   // cuánto → N
(viaje_001, estado,        completado)
```

### Fase 5: pago — agente, beneficiario, instrumento, por cuánto

```
(pago_001, instancia_de,    pago_viaje)
(pago_001, sobre_viaje,     viaje_001)
(pago_001, agente,          juan_usuario)         // quién paga → Q
(pago_001, beneficiario,    plataforma_taxi)      // para quién → Q
(pago_001, instrumento,     tarjeta_juan)         // con cuál → O
(pago_001, por_cuanto,      18.50)                // por cuánto → N
(pago_001, moneda,          soles)                // → K
(pago_001, momento,         2026-05-13_18:53)
(pago_001, justificado_por, regla_tarifa_estandar_2026)   // D6: por qué esa tarifa

(regla_tarifa_estandar_2026, instancia_de, regla_tarifaria)
(regla_tarifa_estandar_2026, formula,      "base + km * 2.23")
```

### Detalles de intenciones y reglas

```
(meta_llegar_19:00, instancia_de, intencion)
(meta_llegar_19:00, lugar_de,     aeropuerto_jorge_chavez)
(meta_llegar_19:00, antes_de,     2026-05-13_19:00)

// Por qué se canceló (causal, hipotético)
(cancelacion_007, instancia_de, cancelacion_viaje)
(cancelacion_007, sobre_viaje,  viaje_007)
(cancelacion_007, causado_por,  no_llegada_conductor_007)
```

### Consultas habilitadas (con vocabulario canónico)

```
¿Cuántos viajes hizo Pedro hoy?
phi = { agente: pedro_taxista, instancia_de: viaje_taxi,
        fin: hoy }

¿Cuánto ganó la plataforma en viajes al aeropuerto en mayo?
phi = { destino: aeropuerto_jorge_chavez, instancia_de: pago_viaje,
        momento: [2026-05-01, 2026-05-31] }
agregación: sumar por_cuanto.

¿Qué viajes están en curso?
phi = { instancia_de: viaje_taxi, estado: en_curso }

¿Para qué fue la solicitud?    (uso de D6)
phi = { sujeto: solicitud_001, con_finalidad: ? }

¿Por qué se asignó este taxi?  (uso de D6)
phi = { sujeto: emparejamiento_001, motivado_por: ? }

¿Por qué se canceló?           (uso de D6)
phi = { sobre_viaje: viaje_007, causado_por: ? }

¿Por dónde pasó el viaje?      (uso de D7: rol via)
phi = { sujeto: viaje_001, via: ? }

¿Con quién viajó Juan?         (uso de D7: rol acompañantes)
phi = { paciente: juan_usuario, acompañantes: ? }
```

### Lo que ilustra este ejemplo

- **D5**: `app_taxi ∈ O` actúa como `agente` en `emparejamiento_001` sin reclasificarse.
- **D6**: cuatro tipos de por-qué (`motivado_por`, `con_finalidad`, `justificado_por`, `causado_por`) se modelan limpiamente como relaciones, no como un eje hipotético.
- **D7**: el mismo conjunto de etiquetas canónicas (`agente`, `paciente`, `origen`, `destino`, `instrumento`, `via`, `por_cuanto`, `momento`, `inicio`, `fin`) atraviesa todas las situaciones del dominio. La solicitud, el emparejamiento, el viaje y el pago se "leen" con el mismo vocabulario.

## 9. Del lenguaje natural a los hechos: el verbo como tipo de situación

WQuestions tiene una conexión natural con el lenguaje humano. La estructura clásica **sujeto + verbo + predicado** se traduce de forma casi mecánica a hechos del modelo. Esta sección documenta ese frame; el diccionario de verbos canónicos vive aparte en [lexicon.md](lexicon.md).

### El mapeo

```
Verbo     → identifica el tipo de situación (instancia_de en K)
            y reifica un nuevo individuo en O (la situación misma)

Sujeto    → típicamente llena un rol canónico (agente, experimentador,
            paciente para verbos inacusativos, tema para estados)

Predicado → es un paquete de roles canónicos (D7): paciente, lugar_de,
            momento, instrumento, beneficiario, con_finalidad, etc.
```

### Ejemplo paso a paso

> "Juan le dio un libro a María ayer en su casa para sorprenderla"

```
dar_001 ∈ O

(dar_001, instancia_de,   accion_dar)      // K: el verbo nombra el tipo
(dar_001, agente,         juan)            // sujeto → agente (Q)
(dar_001, tema,           libro_007)       // OD → tema (O)
(dar_001, beneficiario,   maria)           // OI → beneficiario (Q)
(dar_001, momento,        2026-05-12)      // adv. temporal → momento (T)
(dar_001, lugar_de,       casa_juan)       // adv. locativo → lugar_de (L)
(dar_001, con_finalidad,  sorprender_001)  // adv. final → finalidad (O)

(sorprender_001, instancia_de, accion_sorprender)
(sorprender_001, paciente,     maria)
```

Una oración del español → 6 hechos atómicos + 1 sub-situación. Sin pérdida de información.

### El verbo como signatura de tipo

Cada verbo del léxico funciona como una declaración de qué roles esperar — análoga a una firma de función:

```
dar(agente, tema, beneficiario, [momento], [lugar], [con_finalidad])
ir(agente, origen, destino, [momento], [via], [instrumento])
llover(momento, lugar)                      // sin agente
soñar(experimentador, tema, [momento])
costar(tema, por_cuanto)
```

Esto se vuelve un **diccionario léxico** (lexicon) que mapea cada verbo o unidad léxica a:
- su tipo de situación en K
- los roles obligatorios
- los roles opcionales

Catálogo inicial en [lexicon.md](lexicon.md).

### Tipos de verbos y sus roles típicos

| Tipo de verbo | Rol del sujeto | Roles típicos del predicado | Ejemplos |
|---|---|---|---|
| Acción transitiva | agente | tema, beneficiario, instrumento | dar, comer, escribir |
| Acción intransitiva | agente | (lugar, momento) | correr, dormir |
| Movimiento | agente | origen, destino, via | ir, llegar, salir |
| Estado | tema | lugar_de, momento | ser, estar, existir |
| Experiencia | experimentador | tema | ver, amar, recordar |
| Suceso natural | (nadie) | lugar, momento | llover, amanecer |
| Comunicación | agente | beneficiario, tema (= situación) | decir, prometer |
| Cambio de estado | paciente/agente | estado_inicial, estado_final | romper, fundir |

### Las preguntas-WH son consultas-WQuestions

Las palabras interrogativas del español mapean 1-a-1 a proyecciones sobre roles:

```
"¿Quién dio el libro?"
phi = { instancia_de: accion_dar, tema: libro, agente: ? }    → Q

"¿Qué dio Juan?"
phi = { instancia_de: accion_dar, agente: juan, tema: ? }     → O

"¿A quién le dio Juan el libro?"
phi = { ..., beneficiario: ? }                                → Q

"¿Cuándo dio Juan el libro?"
phi = { ..., momento: ? }                                     → T

"¿Dónde se lo dio?"
phi = { ..., lugar_de: ? }                                    → L

"¿Para qué se lo dio?"
phi = { ..., con_finalidad: ? }                               → O/K
```

El lenguaje natural ya viene con un sistema de consulta sobre estos roles. No es accidente: las preguntas-WH son una herencia que los roles temáticos formalizaron.

### Cláusulas embebidas

Las situaciones pueden ser valores de otras situaciones. Esto cubre actitudes proposicionales, reportes y subordinación:

> "Juan dijo que María come pan"

```
(decir_001, instancia_de, accion_decir)
(decir_001, agente,       juan)
(decir_001, tema,         comer_001)        // otra situación

(comer_001, instancia_de, accion_comer)
(comer_001, agente,       maria)
(comer_001, tema,         pan)
```

Composable arbitrariamente: "María dijo que Juan piensa que Pedro creía que...".

### Tiempo, aspecto, voz, modo

Los matices gramaticales se acomodan como propiedades de la situación:

```
(dar_001, tiempo,    pasado)
(dar_001, aspecto,   perfectivo)
(dar_001, voz,       activa)
(dar_001, modo,      indicativo)
(dar_001, polaridad, afirmativa)
```

La voz pasiva es especialmente elegante: "María recibió un libro de Juan" y "Juan le dio un libro a María" producen **exactamente los mismos hechos**. WQuestions captura el contenido, no la forma.

### Polisemia y unidades léxicas

Un mismo verbo de superficie puede mapearse a tipos distintos según el complemento. "Dar la mano" no es `accion_dar` sino `accion_saludar` con modo `dar_la_mano`. "Dar una conferencia" es `evento_conferencia`, no `accion_dar`.

**Regla práctica**: el lexicon mapea **unidades léxicas** (verbo + patrón de complemento), no verbos sueltos. Coincide con cómo FrameNet identifica sus *lexical units*.

### Modales

Verbos como *querer, deber, poder, soler* no son situaciones independientes; modifican otra situación. Se modelan como **propiedades modales** sobre la situación principal:

```
"Juan quiere viajar a Cusco"

(viajar_001, instancia_de, accion_viajar)
(viajar_001, agente,       juan)
(viajar_001, destino,      cusco)
(viajar_001, modalidad,    volitiva)        // K: querer, desear, ...
(viajar_001, hecho_actual, falso)           // todavía no ocurre
```

Distinción tentativa (a ajustar con más casos):
- **Modalidad volitiva**: querer, desear, planear.
- **Modalidad deóntica**: deber, tener que, haber de.
- **Modalidad alética**: poder (en sentido de capacidad).
- **Modalidad epistémica**: poder (en sentido de probabilidad), parecer.

### Implicaciones operativas

Esta frame habilita cuatro capacidades concretas:

1. **Ingesta desde lenguaje natural**: texto → parsing → mapping vía lexicon → hechos WQuestions.
2. **Validación gramatical-semántica**: si alguien pone `(dar_001, agente, casa)` el sistema lo rechaza vía la signatura del rol y del verbo.
3. **Generación de lenguaje natural**: dado un conjunto de hechos, reconstruir la oración consultando el lexicon inverso.
4. **Consultas conversacionales**: una pregunta en lenguaje natural se traduce determinísticamente a `phi` usando el catálogo canónico.

### Precedentes industriales

Esta línea coincide con tres familias de recursos lingüísticos ya construidos:

- **FrameNet** (Berkeley): catálogo de frames semánticos y sus elementos.
- **VerbNet** (UPenn): clasificación de verbos por signatura sintáctico-semántica.
- **PropBank**: anotaciones de roles temáticos sobre corpus.

Ver [related/framenet-verbnet.md](related/framenet-verbnet.md) para análisis y mapeo a WQuestions.

## 10. Decisiones pendientes

1. ¿Las situaciones (eventos) viven en `O` junto a los objetos físicos, o conviene un 7º eje de valor `E` para eventos? (Argumento a favor: simplifica "todos los eventos de hoy".)
2. ¿Las consultas son solo por igualdad puntual, o admitimos desde ya operadores: rangos en `T`/`N`, pertenencia a conjuntos, negación, agregaciones (suma, conteo)?
3. **Patrones temporales en `T`** (urgencia media). Aparecen en correr por las mañanas, tomar pastilla cada mañana, minuto de partido. Por ahora se modelan como K (`cada_mañana`, `recurrente`), suficiente para queries cualitativas pero no para cálculo de fechas. Eventualmente: reificar como O-individuos con estructura (frecuencia, unidad_frecuencia, inicio, fin).
4. **Bitemporalidad completa: valid time + transaction time** (urgencia media-alta para dominios regulados). D9 captura *valid time* (cuándo el hecho es cierto en el mundo) pero no *transaction time* (cuándo fue afirmado en el sistema). La tradición Snodgrass / SQL:2011 / BiTRDF (ver [related/bitemporal-snodgrass.md](related/bitemporal-snodgrass.md)) demuestra que ambas dimensiones son necesarias para auditoría legal, retractación trazable, y consultas tipo "qué sabíamos cuándo". Posible patch: agregar `asercion_inicio`/`asercion_fin` a las situaciones reificadas, o reificar la afirmación misma como O-individuo enlazado por `afirma`. Postergada hasta confirmar casos de uso concretos en dominios como salud y derecho.

**Decisiones resueltas tras pruebas de Nivel 1**:

- ~~#3 anterior — mediciones con unidad~~ → resuelta como **convención: mediciones con unidad reificadas** (en sección 2).
- ~~#4 anterior — validez temporal de hechos~~ → resuelta como **D9: las propiedades temporales se reifican como situaciones con vigencia**.
- ~~#6 anterior — reglas de derivación e invariantes~~ → resuelta parcialmente como **convención: reglas reificadas como O-individuos**; la aplicación efectiva (motor de inferencia) movida a "pisos siguientes".

## 11. Pisos siguientes

- Composición de situaciones: qué hace válida o bien formada una situación.
- Álgebra de consultas: operadores, proyecciones, agregaciones, filtros temporales.
- **Motor de inferencia**: aplicación efectiva de reglas declarativas. Cómputo de hechos derivados (reajustes IPC, marcadores acumulativos), verificación de invariantes (conservación de masa, balance contable), derivación condicional (roja → expulsión). Tecnologías candidatas: Datalog (RDFox, Soufflé), SHACL para constraints, SWRL para reglas OWL, o motor custom de WQuestions.
- **Parser texto → hechos**: implementar el pipeline NL → lexicon → hechos canónicos (sección 9).
- **Capa de aliases por dominio**: implementación del layer 3 de D8 (dialectos de dominio).

---

# Trabajos relacionados

El precedente más cercano en intención es el framework 5W1H de Yang & Hu. Su análisis detallado y comparación con WQuestions vive en un documento aparte: [related/yang-hu-5w1h.md](related/yang-hu-5w1h.md). En síntesis: Yang & Hu usa 5W1H como **metodología de elicitación** para construir ontologías OWL por-dominio; WQuestions lo eleva a **estructura de datos persistente** universal, añadiendo `K`, `N` y `P` como ejes propios y reemplazando el eje "Why" por una familia canónica de relaciones de por qué en `M` (D6).

## Otros precedentes

Cada precedente tiene una ficha dedicada en `related/` con datos bibliográficos, núcleo del framework, tabla comparativa, qué tomar prestado y qué no. Resumen aquí:

- **[Mahmood et al. (ADBIS 2021)](related/mahmood-5w1h-events.md)** — 5W1H aplicado a detección de eventos en multimedia. Validación empírica de que 5W1H sirve como índice de eventos reales. Donante natural de pipeline de extracción texto→hechos.

- **[Semántica de eventos neo-davidsoniana](related/neo-davidsonian.md)** — Davidson, Parsons, Kratzer. El formalismo lingüístico más cercano al hecho atómico: eventos reificados con participantes vía roles temáticos. Donante natural del vocabulario de etiquetas en `P` (Agent, Theme, Location, Time, Manner...).

- **[Teoría de situaciones (Barwise & Perry)](related/barwise-perry-situations.md)** — El ancestro filosófico-matemático más profundo. El **infón** `<<M, a₁..aₙ; i>>` es prácticamente el hecho atómico de WQuestions con polaridad explícita. Donante de mecanismos: polaridad, soporte, restricciones, tipos.

- **[Espacios Conceptuales (Gärdenfors)](related/gardenfors-conceptual-spaces.md)** — La metáfora geométrica de "conocimiento como coordenadas". Continuo y geométrico vs. discreto y simbólico de WQuestions. Complemento natural: si WQuestions necesita búsqueda aproximada, viene de aquí.

- **[CIDOC CRM](related/cidoc-crm.md)** — Estándar ISO con 20+ años en producción. Event-centric (≈ D2), `E55 Type` ≈ K, ~190 propiedades modeladas. El precedente industrial más fuerte. Catálogo donante de etiquetas para `P` y `M`.

- **[RDF / RDF-star / N-ary relations](related/rdf-and-reification.md)** — El stack técnico natural para implementar WQuestions. Triple ≈ hecho atómico binario. N-ary pattern ≈ situaciones en O. SPARQL como modelo de consulta. Camino de implementación pero NO modelo conceptual.

---

## Posicionamiento final

Lo nuevo de WQuestions no es ninguna pieza aislada — todas tienen precedente — sino la **combinación específica**:

1. **8 coordenadas universales fijas** (no abiertas, no por dominio) como base de todo el modelo.
2. `K` como **eje de tipos** que mantiene el modelo first-order y plano (sin metanivel).
3. `cual` y `como` como **ejes de primera clase** y no solo vocabulario.
4. **Agencia contextual** (D5) en lugar de reclasificación rígida.
5. Diseñado desde el inicio como **infraestructura de consulta para IA**, no como teoría lingüística ni ontología por dominio.

---

## Referencias

- [5W1H-based Conceptual Modeling Framework for Domain Ontology (Yang & Hu, IEEE/SKG 2011)](https://ieeexplore.ieee.org/document/6088118/)
- [Conceptual Modelling for Domain Ontology Using a 5W1H Six-Layer Framework (Yang & Hu, AMR 2012)](https://www.scientific.net/AMR.282-283.68)
- [5W1H Aware Framework for Representing and Detecting Real Events (Mahmood et al., ADBIS 2021)](https://dl.acm.org/doi/10.1007/978-3-030-82472-3_6)
- [5W1H Extraction With Large Language Models (arXiv 2024)](https://arxiv.org/html/2405.16150v1)
- [Five Ws — Wikipedia](https://en.wikipedia.org/wiki/Five_Ws)
- [Situation Semantics — Wikipedia](https://en.wikipedia.org/wiki/Situation_semantics)
- [Situation Theory and Situation Semantics (Devlin, Stanford)](https://web.stanford.edu/~kdevlin/Papers/HHL_SituationTheory.pdf)
- [Situations in Natural Language Semantics — Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/situations-semantics/)
- [Neo-Davidsonian Event Semantics (Landman, course notes)](https://www.tau.ac.il/~landman/Online%20Class%20Notes/2%20ADVANCED%20SEMANTICS/8%20Neo-davidsonian%20event%20semantics.pdf)
- [Neo-Davidsonian-Based Event Class Semantic Representation (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S187705092030154X)
- [Conceptual Spaces: The Geometry of Thought (MIT Press)](https://mitpress.mit.edu/9780262572194/conceptual-spaces/)
- [CIDOC CRM — reified association vs sub-event](https://cidoc-crm.org/Issue/ID-266-reified-association-vs-sub-event)
- [Representing Cultural Heritage Knowledge Graphs in CIDOC-CRM (MDPI)](https://www.mdpi.com/1999-5903/13/11/277)
- [RDF-star — Ontotext Fundamentals](https://www.ontotext.com/knowledgehub/fundamentals/what-is-rdf-star/)
- [Knowledge Representation and Reasoning — Wikipedia](https://en.wikipedia.org/wiki/Knowledge_representation_and_reasoning)
