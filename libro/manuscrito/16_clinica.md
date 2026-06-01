# Capítulo 16 — Un dominio nuevo: La historia clínica

## El cambio de marcha

Los dos dominios que vimos antes (el Spa y el Taxi) tenían algo en común que suele pasar desapercibido: eran negocios puramente **transaccionales**. Sus situaciones eran eventos fugaces. La sesión de spa de Ana empieza, termina, se cobra y el mundo sigue girando. El viaje de Valeria ocurre, se paga y listo. Modelar uno de estos negocios es solo cuestión de aprender a usar nuestras herramientas; modelar el otro es repetir la misma fórmula cambiando las palabras del Lexicon.

Pero el mundo de la medicina no funciona así. Una consulta médica es un evento, sí, pero lo verdaderamente importante no es cuánto duró la cita, sino **el contenido denso que se produjo allí adentro**: un diagnóstico, una receta de pastillas, una alerta de alergia, la programación de un control futuro. 

A un médico no le importa el evento de la consulta; al médico le importan los "objetos de información" que nacieron en ella. Le importa el diagnóstico de hipertensión que seguirá vigente un año después; la pastilla que se debe ajustar mes a mes; la regla universal que prohíbe mezclar dos fármacos. Aquí, la riqueza de los datos no está en la línea de tiempo, sino en el peso intelectual de cada decisión.

Esto somete a nuestra arquitectura a una presión titánica. Ya no basta con encadenar eventos. Necesitamos que nuestro sistema sepa **de qué habla cada evento**, con una estructura tan perfecta que una Inteligencia Artificial pueda leer el expediente de un paciente y deducir si una pastilla lo va a matar. Y todo esto tiene que funcionar a lo largo de décadas, porque los diagnósticos mutan, las medicinas cambian y los protocolos se actualizan. 

Este capítulo modela una consulta típica: la Dra. Torres atiende a María Gonzales por un dolor de cabeza crónico. Veremos cómo nuestro modelo absorbe esta avalancha científica. Y, siendo honestos, te mostraré el primer bache real con el que me topé al programar este prototipo: cuando la intuición humana choca contra la rigidez de las matemáticas.

## La consulta como la "Carpeta Maestra"

Igual que en el caso del Taxi creamos un `viaje_001` gigante que abrazaba todos los pequeños pasos, la consulta médica funciona como una gran carpeta articuladora. Una revisión típica produce cinco documentos internos:

1.  **El síntoma:** Lo que dice el paciente. *"Me duele la cabeza hace tres días."*
2.  **La medición:** Los números crudos que saca el doctor. *"Presión en 145/92."*
3.  **El diagnóstico:** La conclusión clínica. *"Tiene Hipertensión de grado 1."*
4.  **La prescripción:** El ataque químico. *"Tome Enalapril de 10 mg."*
5.  **El control:** El plan a futuro. *"Nos vemos en 30 días."*

En nuestro modelo, estas cinco cosas no son campos de texto; son **cinco situaciones reificadas independientes** que cuelgan de la consulta principal usando nuestro viejo y confiable cable `parte_de`.

```text
(consulta_001) ∈ O
  instancia_de    : consulta_medica
  agente          : dra_torres
  paciente        : maria_g
  lugar_de        : consultorio_03
  motivo          : cefalea_persistente

(sintoma_001    ∈ O,  parte_de,  consulta_001)
(medicion_001   ∈ O,  parte_de,  consulta_001)
(diag_hta_001   ∈ O,  parte_de,  consulta_001)
(prescrip_001   ∈ O,  parte_de,  consulta_001)
(control_001    ∈ O,  parte_de,  consulta_001)
```

La arquitectura se mantiene inalterable: una entidad gigante que contiene un racimo de sub-situaciones. Pero el interior de cada una de estas sub-situaciones es lo que vuelve fascinante a la medicina.

![La consulta médica con sus cinco sub-situaciones colgando: síntoma, medición, diagnóstico, prescripción, control futuro. Cada una con su propia estructura semántica.](../diagrams/png/31_consulta_clinica.png)

## Un choque frontal con las matemáticas: Cuando la Caja O se queda corta

Aquí apareció mi primera fricción seria al programar. Piénsalo como humano: cuando el médico mide la presión arterial de María, tu instinto te dice que escribas que el evento tiene como `tema` a la "presión arterial". 
Y cuando el doctor receta Enalapril, tu instinto te dice que el `tema` de la receta es el "Enalapril".

Pero espera. **"Presión arterial" y "Enalapril" no son objetos físicos con identidad propia**. No puedes guardar a la "Presión arterial universal" en un cajón. Son **categorías** teóricas. La cajita de pastillas que María compra en la farmacia sí es un objeto físico (caja `O`), pero el concepto científico de la droga *Enalapril de 10mg* es una idea (caja `K`).

Nuestro catálogo estricto D8 dictamina que el cable `tema` solo puede conectar la caja `O` con la caja `O`. Si yo intento conectar la caja `O` con la caja `K` usando el cable `tema`, el sistema entra en pánico y me lanza un error matemático (`SignatureError`). El modelo me regañó por intentar mezclar conceptos físicos con conceptos teóricos.

¿La solución? Crear "Cables de Dominio" (roles propios) específicos para la medicina, diseñados para apuntar hacia la caja `K`:

```python
# Mal: Usar "tema" para la medicina
# Bien: Crear un cable especial

u.assert_fact(prescripcion, "medicamento_prescrito", enalapril)  ← Este cable va de O a K
u.assert_fact(medicion,     "medida_evaluada", presion_arterial) ← Este también
```

Esto me dejó dos lecciones valiosas:
1.  El catálogo de 38 cables universales sirve para casi todo, pero cada industria altamente técnica (como la medicina o la química) te obligará a crear un puñado de cables exclusivos para sus conceptos abstractos.
2.  El error no era del modelo; el error era de mi mente humana, que mezcla objetos y conceptos todo el tiempo. La rigidez de las matemáticas me salvó de crear un desastre semántico que habría confundido a una IA en el futuro.

## Diseccionando el Diagnóstico: Dudas, Causas y Tiempo

Un diagnóstico médico es una joya de la información. Combina tres dimensiones complejísimas que nuestro modelo resuelve con elegancia:

**1. El nivel de duda (Modalidad Epistémica):**
Un diagnóstico casi nunca es una verdad absoluta tallada en piedra; es lo que el médico *cree* en ese instante. Para reflejar esa incertidumbre clínica, decoramos la situación con `modalidad: epistemica` y jugamos con su `estatus_factual` (puede ser *confirmado*, *sospechoso* o *descartado*).

```text
(diag_hta_001, modalidad,       epistemica)
(diag_hta_001, estatus_factual, confirmado)
```

**2. La evidencia (Causalidad):**
Un diagnóstico no nace de la magia; nace de los números. Si el doctor dice "Hipertensión", es porque vio el número de la "medición de presión". Esta conexión de causa y efecto la guardamos usando nuestro amado cable `motivado_por`:

```text
(diag_hta_001, motivado_por, medicion_pa_001)
```
Ahora la medición no es un simple número flotando; es la **evidencia** del diagnóstico. Si un auditor médico o una IA revisan el expediente, la máquina puede justificar el diagnóstico instantáneamente leyendo este cable.

**3. El viaje en el tiempo (Vigencia D6):**
Esta es la regla que separa el software de juguete del software hospitalario real. Los diagnósticos caducan y cambian. 
Supongamos que en mayo de 2026 María fue diagnosticada con Hipertensión Grado 1. Un año después, en enero de 2027, el médico le dice que empeoró y ahora tiene Grado 2. Si reescribes el diagnóstico viejo y pones el nuevo, acabas de cometer un crimen de negligencia médica al borrar la historia de la paciente.

La Regla D6 (Vigencia temporal) entra a salvarnos la vida. Guardamos **ambos** diagnósticos, cada uno con sus fechas de inicio y fin:

```python
# El Diagnóstico viejo (caducó cuando el doctor emitió el nuevo)
u.assert_fact(diag1, "diagnostico_asignado", hta_grado_1,
              valid_from=mayo_2026, valid_to=enero_2027)

# El Diagnóstico nuevo (vigente hasta el día de hoy)
u.assert_fact(diag2, "diagnostico_asignado", hta_grado_2,
              valid_from=enero_2027)

# Y conectamos ambos para que no queden dudas
u.assert_fact(diag2, "rectifica", diag1)
```

Si hay una demanda por negligencia y el juez pregunta: *"¿Qué sabía el hospital sobre esta paciente en agosto de 2026?"*, la base de datos devuelve exactamente la "verdad clínica" que existía en esa fecha (Grado 1), ignorando el futuro. Esta capacidad forense viene incluida de fábrica en nuestra arquitectura.

![D6 sobre un diagnóstico: HTA grado 1 vigente hasta enero 2027, reemplazado por HTA grado 2 desde entonces. La relación `rectifica` conecta ambos. Una consulta `at=` devuelve el correcto según el momento.](../diagrams/png/32_d9_diagnostico.png)

## Prescripción Médica: La tormenta de los "Por qués"

Cuando un médico te receta una pastilla, se activan simultáneamente varias de las fuerzas causales que vimos en el Capítulo 10. Mira cómo se acumulan en nuestro sistema:

```python
pres = ingest_situation(u, lex, "prescribir", roles={
    "agente":                dra_torres,
    "paciente":              maria_g,
    "medicamento_prescrito": enalapril,
    "frecuencia":            cada_manana,
    "duracion":              indefinida,
})

u.assert_fact(pres, "motivado_por",      diag_hta_001)           ← Por qué me recetan esto
u.assert_fact(pres, "con_finalidad",     bajar_presion_obj)      ← Para qué me recetan esto
u.assert_fact(pres, "verificado_contra", regla_embarazo_alerta)  ← Ley médica de seguridad
```

Tres respuestas profundas a tres preguntas distintas. El médico no te receta por gusto; lo hace *motivado* por tu enfermedad. Lo hace *con la finalidad* de alcanzar un resultado a futuro (bajar tu presión). Y lo hace amparado por un manual de farmacología que *verifica* que la pastilla no te matará. 

Y hablemos un segundo de esa última regla de farmacología. Un manual que dice *"Prohibido dar Enalapril a embarazadas"* no es un pedazo de código escondido por un programador; la guardamos como un evento reificado más en el eje `O`, como si fuera una ley de tránsito:

```text
(ley_enalapril_embarazo) ∈ O
  instancia_de:           contraindicacion_medica
  medicamento_implicado:  enalapril           
  condicion:              estado_embarazo     
  orden_oficial:          evitar_medicamento  
```

Con esto, nuestra base de datos se vuelve inteligente. Cuando la doctora presiona "recetar", un script de código externo simplemente escanea la base de datos, lee esta regla universal, se da cuenta de que la paciente está embarazada y bloquea el botón lanzando una alerta roja. 

## Balance Médico: Misión Cumplida

El modelo WQuestions devoró el reto del mundo médico sin sudar. Observa lo que validamos con código ejecutable:

1.  La "Carpeta Maestra" de la consulta abrazó cinco sub-situaciones con la relación `parte_de` sin tener que fabricar bases de datos paralelas.
2.  La receta médica se enlazó a la evidencia clínica (`motivado_por`).
3.  El control médico de la próxima semana se guardó como `estatus_factual: previsto`. El sistema sabe que es un plan, no una realidad.
4.  La regla del tiempo **D6** nos permitió guardar dos diagnósticos contrarios sin perder el rastro histórico forense de la paciente.
5.  Todo este enmarañado monstruo científico ocupó apenas **62 hechos atómicos**. Un volumen de datos ridiculamente pequeño si lo comparamos con la burocracia de un servidor SQL tradicional.

## Una lección de diseño: El arte de saber qué reificar

Quiero regalarte una pepita de oro metodológica que extraje al programar este hospital. 

A la hora de diseñar, ¿cómo decides qué evento merece convertirse en una entidad importante (Reificarse en `O`) y qué cosa solo debe ser un número triste en la caja `N`?
La regla es simple y brutal: **Si crees que en el futuro alguien va a hacer una pregunta o una afirmación sobre ese dato, entonces reifícalo.**

*   *¿Reificamos el "Síntoma de dolor"?* Sí, porque mañana el médico querrá saber cuándo empezó y qué tan fuerte es. Lo volvemos entidad (`O`).
*   *¿Reificamos la "medición de presión"?* Sí, porque mañana querremos conectarla como evidencia de una enfermedad. Entidad (`O`).
*   *¿Reificamos el dato "tomar cada mañana"?* No. Es un valor final. A nadie le importa interrogar al concepto "cada mañana". Eso se queda como una etiqueta inerte en `K`.
*   *¿Reificamos la "Regla de prohibición para embarazadas"?* Sí, porque tiene fecha de vigencia, condición y autor. Entidad (`O`).

El costo en el servidor de convertir algo en entidad es de unos cuantos bytes. El costo corporativo de no hacerlo y luego descubrir que un juez te exige el historial de ese dato... te costará millones en refactorización de software.