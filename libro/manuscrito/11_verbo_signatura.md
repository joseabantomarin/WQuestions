# Capítulo 11 — El verbo: La firma de contrato de la oración

## Lo que descubrió Davidson (Y por qué nos importa)

En 1967, un filósofo llamado Donald Davidson publicó un artículo de veinte páginas que le voló la cabeza a los lingüistas y lógicos de su época `[12]`. El problema que planteó parecía un juego de niños, pero escondía un abismo matemático. Tomemos una oración simple:

> *Juan pateó la pelota.*

Si le pedimos a un programador clásico que guarde esto, probablemente escriba una función rápida de dos variables: `Patear(juan, pelota)`. Funciona perfecto. Pero observemos qué pasa si empezamos a añadirle detalles naturales a la frase:

> *Juan pateó la pelota con fuerza, en el patio, a las tres de la tarde, para asustar al perro.*

Si seguimos la lógica del programador, ¿cómo escribimos esto ahora? ¿Será `Patear(juan, pelota, con_fuerza, patio, 15:00, asustar_perro)`? ¿Una función gigante de seis variables? ¿Y si luego decimos *"con el pie izquierdo"*? ¿Se vuelve de siete? 
Bajo esa lógica, el verbo "patear" tendría que cambiar su código interno cada vez que a una persona se le ocurra añadir un adjetivo. Eso es absurdo y computacionalmente inviable.

La genialidad de Davidson fue proponer algo distinto: sugirió que en cada oración de acción existe un protagonista fantasma, un argumento oculto que no pronunciamos pero que está ahí. Ese protagonista es **el evento en sí mismo**. 

La oración no dice simplemente que Juan conectó su pie con una pelota; lo que la oración afirma realmente es que **existió un evento oficial llamado "patear"**. Y a ese evento, Juan le prestó su rol de *agente*, la pelota su rol de *objeto*, el patio su rol de *lugar*, y las tres de la tarde su rol de *tiempo*. El verbo se mantiene siempre igual; los modificadores son simplemente "cables" que se enchufan a ese evento central.

Esto es exactamente lo que vimos en el Capítulo 9 cuando hablamos de la **reificación**. Nuestro modelo convierte las acciones en objetos del eje `O`. Y luego, usa hechos atómicos (tripletas) para enchufarle el agente, el lugar y el tiempo. 

La lingüística lleva sesenta años demostrando que el lenguaje humano funciona "reificando" eventos de forma natural. Y nosotros, desde la ingeniería de datos, acabamos de descubrir que esa es la única forma de construir una base de datos universal que no colapse. No es coincidencia. Es la demostración de que la estructura del cerebro y la estructura del software, cuando están bien diseñadas, son exactamente la misma.

## El verbo no es una acción, es un molde

El primer concepto que debemos tatuarnos como ingenieros es este: cuando el idioma español usa un verbo, ese verbo no representa una acción individual que ocurrió en la vida real. El verbo es simplemente un **molde** (un tipo o categoría). 

Verbos como *patear*, *vender*, *consultar* o *llover* no viven en el eje de las cosas físicas (`O`). Viven en el eje de los conceptos (`K`). Cada molde viene de fábrica con una lista de requisitos: te dice qué tipo de participantes y qué circunstancias acepta para funcionar.

Cuando alguien habla y usa un verbo en una oración concreta, ocurren dos cosas matemáticamente en milisegundos:

1.  **Se "fabrica" un evento nuevo:** El sistema crea una situación fresca en la caja `O` (le da un código único de identidad).
2.  **Se etiqueta:** El sistema conecta ese evento nuevo con su molde en `K` para saber de qué trata.

```text
(dar_001) ∈ O
(dar_001, instancia_de, accion_dar)   ∈ M(O, K)
```

Si sabes programar, esto te resultará idéntico a crear clases y objetos. El verbo "dar" es la función principal que vive en la biblioteca de código; cada vez que alguien habla, el sistema *llama* a esa función y crea una ejecución particular en la memoria, anotando qué variables se le pasaron.

## El verbo exige una "Firma de Contrato"

Para entender por qué esto vuelve invencible a nuestro modelo, miremos qué pasa cuando "llamamos" a un verbo. El verbo *dar* no es un cajón de sastre que acepta cualquier basura. Exige reglas estrictas: necesita un *agente* (alguien que entrega), un *tema* (la cosa entregada) y un *beneficiario* (el que recibe). Opcionalmente, puede aceptar un *momento*, un *lugar* o una *finalidad*. 

Pero la exigencia va más allá. El verbo exige que cada rol provenga de un eje específico: el *agente* tiene que venir de la caja de personas (`Q`); el *lugar* tiene que venir de la caja de locaciones (`L`). 

A esta lista estricta de requisitos la llamamos **signatura tipada** (la firma del contrato). Se ve exactamente igual a la declaración de una función en código moderno:

```text
dar(agente: Q, tema: O, beneficiario: Q,
    momento?: T, lugar?: L, con_finalidad?: O) → Fabrica una situación
```

Cada verbo del idioma tiene su propia signatura. Algunas son minúsculas y solitarias:

```text
llover(momento?: T, lugar?: L) → Fabrica una situación     // Ojo: la lluvia no exige agente
soñar(experimentador: Q, tema: O, momento?: T) → Fabrica una situación
```

Otras son bestias complejas de facturación:

```text
vender(agente: Q, tema: O, comprador: Q, monto: N,
       unidad: K, momento?: T, lugar?: L) → Fabrica una situación
```

![Tres verbos del español como signaturas tipadas: cada verbo declara qué roles obligatorios y opcionales acepta, y de qué eje viene cada uno. Igual que una función en un lenguaje de programación.](../diagrams/png/21_verbo_signatura.png)

Tratar a los verbos como "contratos de código" nos regala tres superpoderes automáticos:

**1. Protección Anti-Tonterías:** Si un usuario escribe *"el estadio de fútbol pateó la pelota"*, el sistema aborta la operación antes de guardarla. ¿Por qué? Porque la signatura del verbo *patear* exige que el `agente` sea una persona (`Q`), y el estadio es un lugar (`L`). El sistema no necesita saber de fútbol para bloquear el error; la matemática de la signatura lo frena en seco.

**2. Flexibilidad real:** Decir *"llovió"* es una frase perfecta. No hace falta obligar al usuario a llenar los campos de "dónde" y "cuándo" si no le interesan. La signatura del verbo ya marca que esos campos son opcionales (`?`), dándole a la base de datos la capacidad de tragar información incompleta sin romperse.

**3. Autocontrol de modificadores:** El verbo *patear* acepta que le conectes un `instrumento` (con el pie) o una `finalidad` (para hacer un gol). El verbo *llover* acepta `intensidad` o `duración`. Si alguien intenta escribir *"pateó con intensidad de tres milímetros por hora"*, el sistema explota de inmediato. La signatura del verbo controla qué adjetivos son legales y cuáles son ridículos, sin que tengas que programar reglas manuales para cada caso.

## La regla D8: El menú oficial de roles

A estas alturas te habrás dado cuenta de que palabras como `agente`, `tema`, `beneficiario` o `instrumento` no nos las estamos inventando al azar en cada ejemplo. Vienen de un **menú oficial y cerrado** que nuestro sistema trae de fábrica.

Oficialicemos esto como nuestra octava decisión de diseño:

> **D8 — El modelo trabaja con un catálogo oficial, cerrado y muy reducido de roles (cables conectores). Los protagonistas siempre se llamarán `agente`, `tema`, `beneficiario`, `lugar_de`, `momento`, etc. Cada rol tiene una regla que dicta de qué eje debe sacar la información. Los programadores no pueden inventar roles nuevos a menos que sea un caso de extrema especialización industrial.**

Nuestro sistema base funciona con apenas 38 roles oficiales. Parece un número bajísimo, ¿verdad? Pues resulta que con esas 38 palabras alcanza y sobra para modelar bases de datos de fútbol, medicina, banca, petroquímica y contratos legales. ¿El motivo? Porque el cerebro humano, sin importar su profesión, utiliza ese mismo número reducido de roles para procesar toda la realidad que lo rodea.

## El catálogo completo: las 38 piezas del Lego

A continuación va el catálogo entero, agrupado por familias. Para cada rol verás su nombre canónico, su signatura (qué cajas conecta) y para qué sirve en la práctica. La notación `O → Q` se lee como *"el sujeto del hecho vive en O y el valor del hecho vive en Q"*. Cuando un rol es **funcional** (`func`), un sujeto solo puede tener un valor (una consulta médica tiene un solo paciente, una sola fecha). Cuando es **no funcional** (`mult`), un sujeto admite múltiples valores (una receta tiene varios ingredientes; un evento puede tener varias causas).

### Familia 1: Estructurales — los cables que arman el esqueleto

Son los cables más básicos: sin ellos, no hay grafo. Permiten conectar instancias con sus categorías y formar jerarquías de pertenencia.

| Rol | Signatura | Para qué sirve |
|---|---|---|
| `instancia_de` | V → K (mult) | Marca que un individuo —de cualquier eje— es un ejemplar de una categoría. *"esta consulta (O) es una instancia de `accion_consultar`"; "Messi (Q) es una instancia de `jugador_de_futbol`"*. |
| `subtipo_de` | K → K (mult) | Construye jerarquías de categorías. *"`jugador_de_futbol` es subtipo de `atleta_profesional`"*. |
| `parte_de` | O → O (mult) | Indica que algo forma parte de un evento o entidad mayor. *"esta prescripción es parte de la consulta del 14 de mayo"*. |
| `contiene` | O → O (mult) | El inverso del anterior. *"la consulta contiene esta prescripción"*. |

**El comodín `V`.** Quizá notaste que `instancia_de` dice `V → K` y no `O → K`. Es deliberado: **clasificar es universal**. No solo los objetos (O) pertenecen a una categoría — también un agente (Messi, en Q), un lugar (Lima, en L) o un instante (T) responden a la pregunta "¿de qué concepto sos instancia?". `V` es el comodín de signatura que significa *cualquier eje de valor*: es el **universo V** del Capítulo 5 — los seis ejes tomados como conjunto. Cuidado de no confundirlo con K: **K es un eje** —el lugar donde viven las categorías—; **V es "todos los ejes" a la vez** —un cuantificador, no un sitio donde algo vive—. Por eso `instancia_de` es `V → K`: *cualquier individuo* hacia *una categoría*. El mismo comodín sirve en el rango cuando un rol necesita admitir varios ejes a la vez: por ejemplo, generalizar `partes` o `tema` a `O → V` para que acepten lo mismo un objeto que una categoría (lo retomamos en el Capítulo 28).

### Familia 2: Participantes — el "quién" y "qué" del verbo

Estos son los protagonistas de cualquier acción. Vienen directamente de la lingüística (los famosos "roles temáticos") y son la columna vertebral de todo el modelo.

| Rol | Signatura | Para qué sirve |
|---|---|---|
| `agente` | O → Q (func) | Quien ejecuta la acción de forma intencional. *"María vendió"* → agente es María. |
| `paciente` | O → Q (func) | Quien recibe o sufre la acción. *"el médico atendió al paciente"*. |
| `tema` | O → O (func) | El objeto o sub-situación sobre el que recae la acción. *"prescribió un medicamento"*. |
| `beneficiario` | O → Q (func) | El destinatario o quien se beneficia. *"le dio un libro a María"* → María es beneficiaria. |
| `experimentador` | O → Q (func) | Quien vive un estado mental. *"Juan teme"*, *"Marta cree"*. Distingue al sentidor del agente activo. |
| `instrumento` | O → O (func) | El objeto que media la acción. *"pateó con la pierna izquierda"*, *"escribió con un bolígrafo"*. |
| `comprador` | O → Q (func) | Comprador en una venta — alias especializado de beneficiario. |
| `cliente` | O → Q (func) | Cliente de un servicio — alias frecuente en negocios. |

### Familia 3: Lugar — el "dónde"

| Rol | Signatura | Para qué sirve |
|---|---|---|
| `lugar_de` | O → L (func) | Lugar donde ocurre la situación. *"la consulta fue en el consultorio 03"*. |
| `origen` | O → L (func) | Punto de partida en movimientos o transferencias. |
| `destino` | O → L (func) | Punto de llegada. *"el taxi va al aeropuerto"*. |
| `lugar_destino` | O → L (func) | Alias de destino, útil cuando el verbo lo exige explícito (`ingresar`). |

### Familia 4: Tiempo — el "cuándo"

| Rol | Signatura | Para qué sirve |
|---|---|---|
| `momento` | O → T (func) | Instante puntual. *"firmó el contrato el 14 de mayo a las 10:30"*. |
| `inicio` | O → T (func) | Comienzo de un rango temporal. *"el préstamo vigente desde junio"*. |
| `fin` | O → T (func) | Fin de un rango temporal. Junto con `inicio` arma la bitemporalidad (D6). |

### Familia 5: Cantidad — el "cuánto"

| Rol | Signatura | Para qué sirve |
|---|---|---|
| `monto` | O → N (func) | Cantidad numérica con unidad. *"costó 49.90 dólares"*. |
| `cantidad` | O → N (func) | Alias de monto, más natural en contextos físicos (gramos, litros). |
| `por_cuanto` | O → N (func) | Precio o medida unitaria asociada. *"a 12 dólares la docena"*. |
| `unidad` | O → K (func) | Unidad de medida — siempre apunta a una categoría QUDT. |

### Familia 6: Clasificatorios — el "modo" del hecho

Estos cables permiten al modelo distinguir hechos del mundo real de hechos hipotéticos, planeados, prohibidos o negados.

| Rol | Signatura | Para qué sirve |
|---|---|---|
| `estatus_factual` | O → K (func) | Marca si la situación es `real`, `intencionada`, `planeada`, `cancelada`, `hipotetica`. |
| `modalidad` | O → K (func) | Tipo de modalidad: volitiva (deseo), deóntica (deber), alética (necesidad), epistémica (conocimiento). |
| `polaridad` | O → K (func) | Afirmativa o negativa. Permite registrar *"el paciente NO tiene fiebre"* como un hecho positivo. |
| `calificacion` | O → K (func) | Atributo cualitativo libre. *"clasificación de riesgo: alto"*. |

### Familia 7: Las cuatro relaciones del "por qué" (D7)

Ya las estudiamos en el capítulo 10, pero las incluimos aquí porque son parte oficial del catálogo.

| Rol | Signatura | Para qué sirve |
|---|---|---|
| `causado_por` | O → O (mult) | Causalidad mecánica/física. *"el incendio causó el derrumbe"*. |
| `motivado_por` | O → O (mult) | Motivo intencional. *"vendió la casa motivada por el deseo de mudarse"*. |
| `con_finalidad` | O → O (mult) | Propósito teleológico — apunta a un estado futuro. *"abrió la vía con finalidad de acceder al pulmón"*. |
| `justificado_por` | O → O (mult) | Autoridad normativa. *"la rescisión está justificada por la cláusula 14"*. |

### Familia 8: Inter-situacionales — eventos que se hablan entre sí

Permiten que las situaciones formen secuencias, se anulen, se corrijan o se contradigan entre ellas.

| Rol | Signatura | Para qué sirve |
|---|---|---|
| `precede` | O → O (mult) | Orden lógico o temporal. *"la aceptación precede al traslado"*. |
| `sigue_a` | O → O (mult) | Inverso de precede. |
| `cumple` | O → O (mult) | Una situación cumple una obligación o regla previa. |
| `cancela` | O → O (mult) | Deja sin efecto una situación anterior. *"la cancelación cancela la reserva"*. |
| `rectifica` | O → O (mult) | Corrige una situación previa sin borrarla (nunca borramos: rectificamos). |
| `contrasta_con` | O → O (mult) | Relación adversativa, equivalente al "pero" del lenguaje. *"el paciente mejoró, pero contrasta con la elevación de la presión"*. |

### Familia 9: Atributos del sujeto Q

Los únicos roles que no tienen un sujeto en O. Sirven para describir a los agentes mismos.

| Rol | Signatura | Para qué sirve |
|---|---|---|
| `nombre` | Q → K (func) | Nombre legible de un agente. *"el agente `q_447` tiene nombre `María Gonzales`"*. |
| `identificador` | Q → K (func) | Identificador documental (DNI, RUC, número de empleado). |

## ¿Son solo 38? ¿Puedo agregar más?

La respuesta corta es: **sí, puedes agregar más, pero con criterio**. El catálogo canónico está pensado para mantenerse pequeño y estable, exactamente como el inventario de roles temáticos que la lingüística viene refinando hace medio siglo. Sin embargo, el sistema implementa una política deliberadamente flexible que el código llama **"política liberal"**:

- Si un rol está en el catálogo canónico, el sistema **valida** que los ejes coincidan con la signatura.
- Si un rol **no** está declarado, el sistema lo **acepta sin validar**, en lugar de rechazarlo.

¿Por qué este criterio? Porque ningún catálogo central puede anticipar todas las palabras técnicas de todos los dominios. Si un químico necesita el rol `reactivo: O → N`, o un musicólogo necesita `obra_interpretada: O → K`, deben poder usarlos sin pedir permiso. El catálogo no es una camisa de fuerza; es un **núcleo estable** alrededor del cual cada dominio extiende.

La regla práctica que el libro defiende es:

1. **Usa primero los 38 canónicos.** Cubren la gran mayoría de los casos.
2. **Si tu dominio necesita un rol específico** (un médico necesita `principio_activo`, un banco necesita `cuenta_origen`), agrégalo como rol de dominio. El sistema lo aceptará sin protestar.
3. **Cuando un rol de dominio aparece tres veces en tres dominios diferentes**, es candidato a promoverse al catálogo canónico. Ese es el mecanismo evolutivo del catálogo.

Los capítulos de la Parte V muestran este patrón en acción: el dominio musical agrega `obra_interpretada`, el químico agrega `insumo` y `reactivo`, el bancario agrega `cuenta_origen` y `cuenta_destino`. Ninguno toca los 38 canónicos; cada uno extiende lo que necesita y deja documentado el patch.

## Cinco situaciones inventadas: el catálogo en acción

Para que el catálogo no se quede como una lista abstracta, vamos a aterrizarlo con cinco escenarios completamente nuevos — situaciones que no aparecen en el resto del libro. La idea es que veas cómo los mismos 38 roles canónicos cubren contextos absolutamente dispares sin esfuerzo extra. Si el modelo es universal de verdad, debería poder absorber estos casos exactamente con las piezas que ya tiene.

### Escenario 1 — Una familia adopta a un perro de un refugio

> *El sábado por la mañana, Carolina y Diego fueron al refugio "Patitas del Norte" y adoptaron a una perrita llamada Lola. La razón principal fue que su hija de seis años, Mariana, llevaba meses pidiendo una mascota.*

Modelado completo:

```text
(adopcion_001, instancia_de,    accion_adoptar)              ∈ M(O, K)
(adopcion_001, agente,          carolina)                    ∈ M(O, Q)
(adopcion_001, agente,          diego)                       ∈ M(O, Q)
(adopcion_001, tema,            lola)                        ∈ M(O, O)
(adopcion_001, beneficiario,    mariana)                     ∈ M(O, Q)
(adopcion_001, lugar_de,        refugio_patitas_del_norte)   ∈ M(O, L)
(adopcion_001, momento,         2026-05-16T10:00:00Z)        ∈ M(O, T)
(adopcion_001, motivado_por,    pedido_mariana_001)          ∈ M(O, O)
(adopcion_001, estatus_factual, real)                        ∈ M(O, K)
```

Y la situación que la motivó vive aparte, con su propia identidad:

```text
(pedido_mariana_001, instancia_de,    accion_pedir)          ∈ M(O, K)
(pedido_mariana_001, agente,          mariana)               ∈ M(O, Q)
(pedido_mariana_001, tema,            mascota_familiar)      ∈ M(O, K)
(pedido_mariana_001, inicio,          2026-01-15)            ∈ M(O, T)
```

**Lo interesante**: aparecieron dos agentes en una misma situación (Carolina y Diego como pareja). El modelo lo soporta sin queja porque `agente` es un rol multi-valor (M, no funcional). La perra Lola es **tema** (O→O), porque es el objeto de la acción; Mariana es **beneficiaria**, porque la adopción es "para ella". Y el motivo se modela como otra situación reificada conectada por `motivado_por`.

### Escenario 2 — Una multa de tránsito por exceso de velocidad

> *El oficial Ramírez detectó con un radar Doppler que la camioneta del señor Mendoza circulaba a 92 km/h en una zona limitada a 60. Le aplicó una multa de 180 dólares según el artículo 138 del Código de Tránsito.*

```text
(multa_001, instancia_de,      accion_multar)                ∈ M(O, K)
(multa_001, agente,            oficial_ramirez)              ∈ M(O, Q)
(multa_001, paciente,          sr_mendoza)                   ∈ M(O, Q)
(multa_001, instrumento,       radar_doppler_zona_norte)     ∈ M(O, O)
(multa_001, tema,              vehiculo_mendoza_abc123)      ∈ M(O, O)
(multa_001, lugar_de,          av_central_km_12)             ∈ M(O, L)
(multa_001, momento,           2026-05-12T08:43:00Z)         ∈ M(O, T)
(multa_001, monto,             180)                          ∈ M(O, N)
(multa_001, unidad,            dolar_estadounidense)         ∈ M(O, K)
(multa_001, causado_por,       infraccion_velocidad_001)     ∈ M(O, O)
(multa_001, justificado_por,   articulo_138_ct)              ∈ M(O, O)
```

Y la infracción que disparó la multa también se reifica:

```text
(infraccion_velocidad_001, instancia_de,  evento_exceso_velocidad)  ∈ M(O, K)
(infraccion_velocidad_001, agente,        sr_mendoza)               ∈ M(O, Q)
(infraccion_velocidad_001, tema,          vehiculo_mendoza_abc123)  ∈ M(O, O)
(infraccion_velocidad_001, monto,         92)                       ∈ M(O, N)
(infraccion_velocidad_001, unidad,        km_por_hora)              ∈ M(O, K)
```

**Lo interesante**: aquí trabajan al mismo tiempo las cuatro grandes familias. El **agente** (oficial) y el **paciente** (conductor) son humanos diferentes. El **instrumento** (radar) es un objeto físico; el **tema** (vehículo) también, pero ocupa otro rol. El **monto** + **unidad** registran el dinero de la multa, y existen *dos* relaciones del "por qué" simultáneamente: `causado_por` apunta a la causa fáctica (la infracción ocurrió antes), y `justificado_por` apunta a la regla legal que faculta al oficial a multar. El mundo real exige las dos.

### Escenario 3 — Una devolución en una tienda online

> *El 14 de mayo, Sofía devolvió a la tienda online "EcoMarket" un cargador inalámbrico que había comprado dos semanas antes, porque el producto llegó dañado. La tienda le reembolsó 28.50 dólares a su tarjeta. La devolución estaba permitida por la política de "30 días sin preguntas".*

```text
(devolucion_001, instancia_de,    accion_devolver)            ∈ M(O, K)
(devolucion_001, agente,          sofia)                      ∈ M(O, Q)
(devolucion_001, tema,            cargador_inalambrico_X7)    ∈ M(O, O)
(devolucion_001, beneficiario,    ecomarket)                  ∈ M(O, Q)
(devolucion_001, momento,         2026-05-14T14:22:00Z)       ∈ M(O, T)
(devolucion_001, causado_por,     evento_producto_danado_001) ∈ M(O, O)
(devolucion_001, justificado_por, politica_30_dias_ecomarket) ∈ M(O, O)
(devolucion_001, cancela,         compra_001)                 ∈ M(O, O)

(reembolso_001, instancia_de,     accion_reembolsar)          ∈ M(O, K)
(reembolso_001, agente,           ecomarket)                  ∈ M(O, Q)
(reembolso_001, beneficiario,     sofia)                      ∈ M(O, Q)
(reembolso_001, monto,            28.50)                      ∈ M(O, N)
(reembolso_001, unidad,           dolar_estadounidense)       ∈ M(O, K)
(reembolso_001, sigue_a,          devolucion_001)             ∈ M(O, O)
(reembolso_001, justificado_por,  politica_30_dias_ecomarket) ∈ M(O, O)
```

**Lo interesante**: nota cómo `ecomarket` (una empresa, no una persona) aparece tanto como **agente** del reembolso como **beneficiario** de la devolución. La caja Q acepta entidades jurídicas sin problema (D5 en acción). También aparecen tres relaciones inter-situacionales muy potentes: `cancela` (la devolución anula la compra), `sigue_a` (el reembolso ocurre después de la devolución) y `causado_por` (el daño físico provocó la devolución).

### Escenario 4 — Una consulta médica por telemedicina con asistente de IA

> *El doctor González atendió por videoconferencia a su paciente Renata Ojeda el 10 de mayo a las 16:00. Antes de iniciar, un asistente de IA (Claude Medical) había resumido para el doctor los últimos análisis y antecedentes de la paciente.*

Tenemos dos situaciones encadenadas:

```text
(resumen_ia_001, instancia_de,    accion_resumir)              ∈ M(O, K)
(resumen_ia_001, agente,          claude_medical)              ∈ M(O, Q)
(resumen_ia_001, tema,            historia_clinica_ojeda)      ∈ M(O, O)
(resumen_ia_001, beneficiario,    dr_gonzalez)                 ∈ M(O, Q)
(resumen_ia_001, momento,         2026-05-10T15:58:00Z)        ∈ M(O, T)
(resumen_ia_001, con_finalidad,   consulta_001)                ∈ M(O, O)

(consulta_001, instancia_de,      accion_consultar)            ∈ M(O, K)
(consulta_001, agente,            dr_gonzalez)                 ∈ M(O, Q)
(consulta_001, paciente,          renata_ojeda)                ∈ M(O, Q)
(consulta_001, instrumento,       plataforma_telemed_zoom)     ∈ M(O, O)
(consulta_001, lugar_de,          ubicacion_remota)            ∈ M(O, L)
(consulta_001, momento,           2026-05-10T16:00:00Z)        ∈ M(O, T)
(consulta_001, modalidad,         remota_sincrona)             ∈ M(O, K)
(consulta_001, estatus_factual,   real)                        ∈ M(O, K)
(consulta_001, precede,           prescripcion_001)            ∈ M(O, O)
```

**Lo interesante**: el `agente` de la primera situación es **un modelo de IA** (Claude Medical) — D5 hecho realidad. El sistema no distingue entre humanos, organizaciones y software; cualquiera que actúe entra en Q. Además, el **`instrumento`** (Zoom) muestra cómo los objetos digitales pueden mediar acciones físicas. El `con_finalidad` que conecta el resumen con la consulta posterior es interesante: el resumen no causó la consulta (estaba programada antes), pero tenía como propósito prepararla.

### Escenario 5 — Un accidente sin agente humano: un cable suelto en una obra

> *El miércoles 7 de mayo a las 11:40, un cable eléctrico mal anclado de la grúa torre 3 se desprendió y golpeó al obrero Juan Vázquez, causándole una fractura en el brazo derecho. La investigación posterior determinó que el protocolo de seguridad N°14 había sido incumplido en la última inspección.*

```text
(accidente_001, instancia_de,    evento_accidente_laboral)    ∈ M(O, K)
(accidente_001, paciente,        juan_vazquez)                ∈ M(O, Q)
(accidente_001, instrumento,     cable_suelto_grua_torre_3)   ∈ M(O, O)
(accidente_001, lugar_de,        obra_residencial_norte_03)   ∈ M(O, L)
(accidente_001, momento,         2026-05-07T11:40:00Z)        ∈ M(O, T)
(accidente_001, causado_por,     desprendimiento_cable_001)   ∈ M(O, O)
(accidente_001, estatus_factual, real)                        ∈ M(O, K)

(desprendimiento_cable_001, instancia_de,  evento_fisico)      ∈ M(O, K)
(desprendimiento_cable_001, tema,          cable_suelto_grua_torre_3) ∈ M(O, O)
(desprendimiento_cable_001, momento,       2026-05-07T11:40:00Z)      ∈ M(O, T)
(desprendimiento_cable_001, causado_por,   inspeccion_omitida_001)    ∈ M(O, O)
```

**Lo interesante**: este es el caso donde **D5 brilla en su forma más extrema** — no hay ningún `agente` en la situación principal. El accidente *le ocurrió* a Juan; nadie lo *hizo*. El catálogo lo acepta sin marcar error porque `agente` es un rol opcional, no obligatorio. El `instrumento` es un objeto físico inanimado (un cable), y la cadena causal se reconstruye hacia atrás encadenando varios `causado_por`: el accidente fue causado por un desprendimiento, que a su vez fue causado por una inspección omitida. El grafo permite recorrer hacia atrás toda la cadena de responsabilidad sin necesidad de un agente humano explícito.

---

Si miras los cinco escenarios juntos, descubres algo: usamos prácticamente todos los roles del catálogo y, sin embargo, **no inventamos ninguno nuevo**. Los mismos 38 cables, organizados de formas distintas, capturan una adopción, una multa, una devolución, una consulta médica con IA y un accidente sin culpable. Esa es la prueba operativa de que el catálogo no es arbitrario: es un alfabeto suficiente.

## De oración humana a código informático (Paso a paso)

Para ver la magia en acción, desarmemos la oración de manual que usamos antes, esa que estaba cargada de detalles:

> *Juan le dio un libro a María ayer en su casa para sorprenderla.*

Veamos cómo el sistema convierte esto en bases de datos con un procedimiento mecánico, casi tonto de tan simple:

**Paso 1 — Detectar el molde.** El verbo principal es *dio* (de *dar*). El sistema busca la signatura de *dar* en su diccionario.

**Paso 2 — Reificar la situación.** El sistema crea un evento vacío en el eje `O` y le pone un código de barras. Llamémoslo `dar_001`.

**Paso 3 — Anclar el molde.** Le decimos al sistema de qué trata el evento:
```text
(dar_001, instancia_de, accion_dar)    ∈ M(O, K)
```

**Paso 4 — Enchufar los cables (Roles).** El sistema lee la oración y reparte los pedazos en los enchufes que la signatura del verbo *dar* dejó abiertos:
```text
Juan              → El que da      → agente         → va al eje Q
un libro          → La cosa dada   → tema           → va al eje O
a María           → La que recibe  → beneficiario   → va al eje Q
ayer              → El tiempo      → momento        → va al eje T
en su casa        → El sitio       → lugar_de       → va al eje L
para sorprenderla → El objetivo    → con_finalidad  → va al eje O
```

Cada línea de arriba se convierte automáticamente en un hecho atómico (una tripleta) pegado al evento central `dar_001`:

```text
(dar_001, agente,        juan)              
(dar_001, tema,          libro_007)         
(dar_001, beneficiario,  maria)             
(dar_001, momento,       2026-05-12)        
(dar_001, lugar_de,      casa_juan)         
(dar_001, con_finalidad, sorprender_001)    
```

**Paso 5 — El bucle (Inception).** Resulta que el pedazo *para sorprenderla* tiene un verbo oculto adentro ("sorprender"). El sistema no entra en pánico; simplemente repite los 4 pasos anteriores para crear un "sub-evento" de sorpresa y lo engancha al principal.

Resultado final: **una frase humana se transformó en diez líneas de código perfecto y validado**, sin perder un solo matiz, sin usar campos de "texto libre" y sin necesidad de que un programador construya tablas especiales. 

![De una oración en lenguaje natural a una situación reificada con sus hechos atómicos: el verbo determina el tipo, el sujeto se vuelve agente, los complementos llenan roles canónicos. Una sub-oración (la finalidad) genera una sub-situación.](../diagrams/png/22_oracion_a_situacion.png)

Y esto no es teoría: el prototipo que acompaña al libro lo ejecuta tal cual. Afirmar un hecho valida su signatura; consultar es buscar un patrón de cables:

```python
from wq import Axis, Individual, Universe, Catalog, Pattern, count, category

u = Universe(name="demo", catalog=Catalog())

# "Messi marcó un gol en el minuto 87" — una situación reificada
gol   = u.add_individual(Individual(id="gol_min87", axis=Axis.O, label="gol del minuto 87"))
messi = u.add_individual(Individual(id="messi",     axis=Axis.Q, label="Messi"))
u.add_individual(category("evento_gol"))

# Cada hecho es (sujeto, rol, valor); la signatura del rol se valida al afirmar.
u.assert_fact(gol, "instancia_de", u.ind("evento_gol"))   # M(O, K)
u.assert_fact(gol, "agente",       messi)                 # M(O, Q)

# Consultar = buscar un patrón: "¿cuántos goles marcó Messi?"
goles = count(u, Pattern(fixed={"agente": messi},
                         type_constraint=u.ind("evento_gol")))
print(goles)   # -> 1
```

## Funciona igual para el SPA de Ana

Para que veas que esto no es un truco arreglado, apliquemos este mismo proceso "tonto y mecánico" a una industria totalmente distinta. Una clienta en un Spa:

> *Ana ingresó a la cámara de vapor a las seis y media para relajarse.*

El molde es *ingresar*. Su signatura exige un agente, un destino y un momento. Aplicamos la reificación y los cables:

```text
(ingresar_017, instancia_de,    accion_ingresar)
(ingresar_017, agente,          cliente_ana)
(ingresar_017, lugar_destino,   camara_vapor_1)
(ingresar_017, momento,         2026-05-15T18:30Z)
(ingresar_017, con_finalidad,   relajacion_001)

(relajacion_001, instancia_de,   estado_relajacion)
(relajacion_001, experimentador, cliente_ana)
```

El verbo *ingresar* no se parece en nada al verbo *dar*, tienen reglas distintas. Pero **la tubería matemática para procesarlos fue exactamente la misma**. Esta es la prueba definitiva de que nuestro modelo puede absorber los datos de una clínica, un banco o un restaurante sin obligar a los ingenieros a reescribir el motor de la base de datos cada vez que abren una empresa nueva.

## Cuando las preguntas de la vida son simplemente "Huecos en el código"

La belleza de este diseño cierra su círculo cuando nos damos cuenta de qué pasa cuando en lugar de afirmar algo, *hacemos una pregunta*. 

Las palabras que usamos los humanos para preguntar (*quién, qué, dónde, cuándo*) no son palabras mágicas; **son simplemente los cables de nuestro sistema a los que les hemos borrado el destino**. 

Si tomamos el evento `dar_001` de arriba, mira cómo cualquier pregunta que haga un humano se traduce a una tripleta donde tapamos un hueco con un signo de interrogación:

```text
"¿Quién le dio el libro a María?"
   { Busco: accion_dar, tema: libro, beneficiario: maria, agente: ? } → (El sistema buscará en Q)

"¿Qué le dio Juan a María?"
   { Busco: agente: juan, beneficiario: maria, tema: ? }              → (El sistema buscará en O)

"¿Cuándo se lo dio?"
   { Busco: el evento de dar, momento: ? }                            → (El sistema buscará en T)

"¿Para qué se lo dio?"
   { Busco: el evento de dar, con_finalidad: ? }                      → (El sistema buscará en O)
```

Para la computadora, leer un documento y guardar los datos es exactamente el mismo proceso matemático que buscar en el archivo para responder una duda. Son las dos caras de la misma moneda. 

*(Dato curioso: Las palabras que usamos para preguntar en español descienden directamente de las reglas judiciales de Cicerón en Roma que vimos en el Capítulo 6. Los filósofos modernos lo redescubrieron hace poco, pero la mente humana ya lo traía de fábrica).*

## El efecto Matrioshka: Cuando alguien habla sobre otra cosa

Hay un nivel de dificultad que tumba a casi todos los sistemas de bases de datos: ¿Qué hacemos cuando una oración habla sobre otra oración?

> *El cliente dijo que la cámara seca estaba muy caliente.*

El verbo principal es *decir*. Y fíjate que la "cosa dicha" no es un objeto que puedas tocar (como un libro); la cosa dicha es **otra situación completa**. Nuestro sistema ni parpadea ante este reto, porque para nosotros, todas las situaciones viven como objetos iguales en el eje `O`.

Creamos el evento de "hablar" y le metemos el "reporte" por dentro, como muñecas rusas (Matrioshkas):

```text
(decir_023, instancia_de,  accion_decir)
(decir_023, agente,        cliente_ana)
(decir_023, tema,          estado_camara_001)         ← ¡El tema es otro evento!

(estado_camara_001, instancia_de,    estado_temperatura)
(estado_camara_001, sujeto,          camara_seca)
(estado_camara_001, calificacion,    muy_caliente)
(estado_camara_001, estatus_factual, reporte_de_cliente)  ← ¡Atención aquí!
```

Ese detalle final (`estatus_factual: reporte_de_cliente`) es oro puro. Le dice a la base de datos que la máquina no tiene pruebas físicas de que la cámara esté caliente; simplemente está guardando el "chisme" de que un cliente lo afirmó. 
Gracias a esto, podemos procesar frases gigantescas como *"María dijo que Juan piensa que el servidor se cayó"*, construyendo una torre de eventos sin tener que programar reglas nuevas.

## El verbo es el contrato maestro

Cerremos este capítulo fijando un concepto en piedra. Cuando metemos un verbo en nuestra base de datos, no estamos guardando una palabra de diccionario; estamos metiendo un **contrato de seguridad**.

El verbo actúa como un abogado de aduana: declara qué información es obligatoria para pasar, qué información es opcional, y de qué caja (`Q, T, L...`) tiene que venir cada dato. Si intentas meter basura, el verbo la bloquea en la puerta. Si metes datos limpios, el verbo ejecuta un proceso de ensamblaje en cinco pasos y archiva todo perfectamente.

Pero claro, para que todo este sistema de aduanas funcione, nuestra base de datos necesita un documento oficial donde estén escritos todos y cada uno de los contratos de los verbos del idioma español. Ese documento maestro se llama el **Lexicon**. 

No es un aburrido apéndice gramatical, sino **el motor traductor definitivo** que le permite a una Inteligencia Artificial hablar directamente con los discos duros de tu empresa usando lenguaje humano.