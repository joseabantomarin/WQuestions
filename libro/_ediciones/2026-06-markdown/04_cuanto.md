# Capítulo 4 — Cuánto: el eje cuantitativo y sus trampas

## Una sonda que se estrelló y una IA que se desconcertó

En septiembre de 1999, la sonda espacial *Mars Climate Orbiter* de la NASA completó un viaje de nueve meses hacia Marte. Se preparó para la maniobra final de inserción orbital, encendió sus motores... y se desintegró por completo en la atmósfera marciana. La pérdida instantánea fue de 327 millones de dólares. 

Cuando los ingenieros revisaron qué había salido mal, encontraron una de las fallas más absurdas en la historia de la exploración espacial: el software de la empresa constructora enviaba la fuerza de los propulsores medida en **libras-fuerza por segundo**, pero el software de navegación de la NASA recibía esos números creyendo que eran **newtons por segundo**. Esa pequeña discrepancia —un error de factor de 4.45— se fue acumulando en silencio durante meses. Para cuando la nave llegó a Marte, su trayectoria era tan baja que la atmósfera la hizo pedazos. 

Nadie había hecho mal el cálculo matemático. Ningún código estaba roto. El problema fue que el número viajó "desnudo", sin su unidad de medida pegada a él.

Saltemos veinticinco años hacia el futuro. En agosto de 2024, un equipo de ingenieros en una startup tecnológica sufrió una versión en miniatura de esta misma historia. Estaban construyendo un asistente de Inteligencia Artificial para analizar documentos legales inmensos. Eligieron el modelo más potente del mercado porque presumía de una capacidad enorme: *"128.000 de ventana de contexto"*. El primer usuario subió un contrato de 200 páginas, pero la IA empezó a comportarse de forma errática: cortaba las respuestas a la mitad, inventaba artículos de ley y alucinaba datos. 

Cuando el equipo revisó los registros, entendieron el error: la capacidad de 128.000 era de **tokens** (fragmentos de palabras), no de **caracteres**. Un contrato en español de 200 páginas consume fácilmente 200.000 tokens. La Inteligencia Artificial, sencillamente, estaba borrando todo lo que no cabía en su memoria, y nadie en el equipo sabía hacer la conversión entre páginas, caracteres y tokens.

Estas dos historias no tratan realmente sobre matemáticas. Tratan sobre el mismo error de diseño fundamental: **un número sin su unidad de medida no es información; es ruido disfrazado de dígitos**.

Este capítulo se adentra en el eje encargado de alojar los números —al que llamaremos el eje **N**— y en la trampa mortal que esconde: fingir que un número se basta a sí mismo. Modelar correctamente la dependencia entre el número y su unidad es lo que diferencia a una base de datos profesional de una hoja de cálculo a punto de colapsar.

## Por qué N exige tener su propio eje

Es una pregunta totalmente válida: ¿para qué crearle un eje exclusivo a los números? ¿No podríamos simplemente guardar los números dentro de la caja de los objetos (O), junto con las botellas, los contratos y los goles?

La respuesta es no, y el motivo queda claro apenas intentas forzar esa idea. Una botella es un individuo físico: tiene identidad propia, existe a lo largo del tiempo y puede aparecer en diferentes eventos. Lo mismo ocurre con un gol. Pero el número "87" no es una cosa física; es un **valor**. No existe un "87" guardado en un cajón del universo al que podamos hacer referencia. 

Lo que sí existe son millones de hechos en el mundo que utilizan el valor 87 para describir algo: el minuto 87 del gol de Messi, el 87% de precisión de un algoritmo, o los 87 tokens descartados por una IA. Cada vez que usamos ese número, su aparición es totalmente independiente de las demás. 

Esta diferencia filosófica tiene un impacto brutal en la arquitectura de software. En los ejes que ya vimos (Q, O, L y K), cada elemento necesita una **identidad propia e inconfundible**. Un sistema informático serio le asigna a cada persona, ciudad o concepto un código interno único (un UUID) para no perderlo de vista. 

El eje **N** no necesita eso. Para un número, su valor *es* su identidad. Cuando un servidor anota que "la IA respondió en 340 milisegundos", el sistema no necesita inventarle un código secreto al número 340; el dato puro y crudo es suficiente. (Lo mismo ocurre con las fechas en el eje T: las fechas se comparan por su valor matemático, no por un código interno). 

La regla es simple: **Q, O, L y K son ejes de entidades físicas o conceptuales; N y T son ejes de valor puro.**

## Las unidades de medida nunca son neutrales

Volvamos a la sonda marciana y al caos con los tokens de la IA. Ambas anécdotas demuestran una regla de oro en la ingeniería de datos: **todo número extraído del mundo real trae una unidad implícita**, y confundir esa unidad es una de las formas más caras de destruir un proyecto.

La conclusión arquitectónica no admite excepciones: **un valor en el eje N nunca debe viajar solo**. Tiene que estar siempre escoltado por su unidad de medida. Y aquí es donde los ejes comienzan a trabajar en equipo. Como aprendimos en el capítulo anterior, las unidades (como *kilogramo*, *segundo*, *dólar* o *token*) no son objetos físicos; son categorías abstractas. Por lo tanto, esas unidades viven cómodamente en el eje **K**. 

Nuestro trabajo al diseñar la base de datos es asegurar que cada vez que se registre un número, se tienda un "cable" que lo conecte con su unidad correspondiente en K. 

En la notación formal del modelo se vería así:

```text
(gol_messi_87,  minuto,           87)           ∈ M(O, N)
(gol_messi_87,  unidad_minuto,    minuto)       ∈ M(O, K)

(respuesta_017, latencia,         340)          ∈ M(O, N)
(respuesta_017, unidad_latencia,  milisegundo)  ∈ M(O, K)
```

A primera vista, esto podría parecer un exceso de burocracia. ¿Acaso no es obvio que el minuto de un partido se mide en minutos? Sí, es obvio hoy. Pero deja de serlo el día en que un proveedor de estadísticas decide enviar los datos del partido en segundos en lugar de minutos, y tu sistema se rompe por no saber en qué unidad estaba hablando la otra máquina.

Cuando sabemos que un dato va a sufrir conversiones frecuentes, la estrategia de diseño más limpia es **reificar la medición**. Esto significa elevar la simple medida al estatus de un evento formal en el eje O, dándole sus propias propiedades. 

En código se vería así:

```text
(latencia_resp_017) ∈ O
  cantidad   : 340               → Va al eje N
  unidad     : milisegundo       → Va al eje K
  contexto   : llamada_API_017   → Va al eje O
```

Hacer esto es lo que separa a un sistema amateur que escupe un "340" sin contexto, de un sistema profesional que te dice exactamente: *"Esto es 340 ms, medidos sobre la llamada número 017 al modelo GPT-4, tal día y a tal hora"*. El primero es solo un número flotando en el vacío; el segundo es inteligencia accionable.

![Dos formas de modelar una medición: la versión simple guarda el valor y la unidad como propiedades del sujeto; la versión reificada eleva la medición misma a entidad en O, con cantidad, unidad, contexto, instrumento y momento como sus propiedades.](../diagrams/png/11_medicion_reificada.png)

## El catálogo oficial: QUDT y las nuevas unidades de la IA

Una duda común al llegar a este punto es: *¿Tengo que sentarme a escribir un diccionario con todas las unidades del mundo para mi sistema?* La respuesta es un rotundo no. Este es uno de los pocos problemas que la industria mundial ya solucionó de forma definitiva. 

Existe una ontología pública llamada **QUDT** (*Quantities, Units, Dimensions and Types*) `[18]` que cataloga miles de unidades reconocidas, sus dimensiones físicas, sus fórmulas de conversión exactas y sus enlaces oficiales (URIs). Si necesitas milisegundos, usas el código `qudt:MilliSEC`; si es un archivo de computadora, usas `qudt:Byte`; si es dinero, `qudt:USD`. Cuando el sistema de WQuestions adopta una unidad, lo hace enlazándose directamente a este catálogo oficial. 

Sin embargo, hay industrias tan nuevas que QUDT todavía no tiene palabras para describirlas. El ecosistema de la Inteligencia Artificial es el mejor ejemplo. ¿Con qué unidad se mide la "calidad" de un texto generado por ChatGPT? ¿Qué unidad le ponemos a la "similitud" entre dos conceptos para una IA? Algunas de estas medidas ni siquiera tienen nombre oficial todavía, y otras dependen enteramente de pruebas de laboratorio (*benchmarks*).

Nuestra regla de diseño para estos casos es sencilla:
1.  Si la unidad existe en el catálogo QUDT, se usa QUDT.
2.  Si es un concepto inventado ayer, el desarrollador define una unidad nueva en el eje K, la describe, y si es posible, le programa una fórmula para convertirla a una unidad conocida.

Para el mundo de la IA, el eje K tendría que alojar unidades como estas:

```text
K:token                   — La unidad básica con la que la IA lee el texto.
K:parametro_modelo        — Unidad para medir el "cerebro" de la IA (ej: 7B, 70B).
K:precision_clasificador  — La tasa de acierto, medida entre 0 y 1.
K:USD_por_millon_tokens   — La unidad con la que OpenAI o Google te cobran la factura.
```

Esa última es sumamente interesante: es una "unidad compuesta" que mezcla dinero y capacidad de procesamiento. Los sistemas maduros permiten armar estas unidades híbridas y guardarlas en el eje K sin que la arquitectura tiemble.

## Conversiones y sumas: El fin de las matemáticas ciegas

Una vez que cada número de tu base de datos tiene su unidad explícitamente pegada a él, operaciones que antes eran peligrosísimas se vuelven seguras y automáticas.

**La conversión:** Imagina que tienes un panel de control que recibe la latencia de cuatro servidores distintos. Uno te manda el dato en milisegundos, dos en microsegundos y otro en segundos. Si tu sistema tiene las unidades mapeadas en K, la base de datos se encarga de convertir todo a una misma unidad antes de sumar. La regla matemática vive centralizada en K, y el programador no tiene que escribir traductores a mano.

**La agregación:** Si le pides a un sistema mal diseñado que saque el promedio de "340 ms, 1200 μs y 0.7 s", la máquina va a sumar los números desnudos (340 + 1200 + 0.7) y dividirlos, entregándote un dato ridículo y totalmente falso. Con nuestro modelo, la máquina sabe que no puede mezclar peras con manzanas y homogeneiza los datos antes de operar. (Aunque parezca increíble, este error de suma ciega ocurre todos los días en paneles de análisis de datos corporativos).

**La inflación y el tiempo:** Los 100 dólares que costaba algo en 2020 no valen lo mismo que 100 dólares en 2026. Si estás modelando un contrato indexado por inflación, registrar "100 dólares" no es suficiente. Ese número tiene que llevar pegada la unidad (USD) y la **fecha exacta de denominación**. El valor del dinero es una propiedad que cambia con el tiempo, y nuestro modelo está diseñado para gestionar esto a través de la bitemporalidad (un concepto que abordaremos más adelante).

## Rangos y porcentajes: Lidiando con la incertidumbre

En el mundo real, los números casi nunca son exactos. Cuando lees un estudio sobre un modelo de lenguaje, te dicen que su nivel de acierto es *"78.3% ± 2.1%"*. Cuando un servidor mide su latencia, no te da un número fijo, te da una campana de Gauss con promedios y percentiles.

Nuestro eje N está preparado para recibir la respuesta a "¿cuánto?" en tres formatos distintos:

1.  **Valor puntual:** Un número fijo y simple (ej: `340 ms`).
2.  **Rango:** Un intervalo con piso y techo (ej: `[300 ms, 400 ms]`).
3.  **Distribución:** Aquí la cosa se pone profesional. La distribución estadística se reifica; es decir, se convierte en una entidad dentro del eje O, y se le añaden propiedades como la media, la varianza y el tipo de curva. 

Esto último es vital al trabajar con IA. Si le haces la misma pregunta dos veces a un modelo como GPT-4, te dará dos respuestas distintas. La "calidad" de la IA no es un número clavado en piedra; es una distribución de probabilidades. Cuando un estudio dice que un modelo tiene un *78.3%* de eficacia, te está dando el promedio de 14.000 pruebas distintas. Modelar bien los datos significa que nuestro sistema sepa que ese 78.3% no es una métrica plana, sino la punta del iceberg de un evento estadístico complejo.

## Los cuatro ejemplos pasan por el eje N

Veamos cómo se comporta el eje N cruzando nuestros escenarios habituales, sumándole el ecosistema de la Inteligencia Artificial:

   **La Receta:** *200 gramos de harina, 30 minutos a 180 °C, rinde para 4 porciones.* Tenemos tres números atados a tres unidades distintas (`gramo`, `minuto`, `°C`), más un número solitario que indica cantidad (4 porciones).
   **El Gol de fútbol:** *Minuto 87, remate desde 22 metros, velocidad del balón a 105 km/h.* Tres números, tres unidades físicas. (Nota: el "87" requiere contexto explícito en el sistema para saber si se cuenta desde el inicio del partido o desde el descanso).
   **La Canción:** *BPM 128, duración de 3 minutos y 24 segundos.* (Ojo aquí: si decimos que la canción está en "Sol Mayor", eso no va a N, porque una nota musical no es un número matemático, es una categoría que pertenece al eje K). 
   **La Noticia política:** *Un decreto entra en vigor en 30 días, mueve un presupuesto de 50 millones de dólares y afecta a 3 ministerios.* Tres números, tres unidades, siendo una de ellas altamente sensible a la inflación temporal.
   **La llamada a una IA:** *Entrada de 4.500 tokens, salida de 1.200 tokens, latencia de 2.3 segundos, costo de 0.018 dólares y precisión de 78.3% ± 2.1%.* Seis números, seis unidades, y dos de ellos incluyen márgenes de incertidumbre.

La verdadera magia ocurre cuando un usuario hace una consulta que cruza todos estos mundos. Por ejemplo: *"¿Cuántos dólares y tokens me cuesta pedirle a una IA que analice un decreto gubernamental de 30 páginas sobre importación de comida?"* 

Es una pregunta perfectamente lógica para un negocio moderno. Mezcla unidades de páginas, tokens, dólares y tiempo. Y todas estas variables exigen que el sistema sepa exactamente qué unidad acompaña a cada número y cómo se convierten matemáticamente entre sí. Sin esa capa de inteligencia estructural, cualquier respuesta que dé la base de datos es una simple adivinanza disfrazada de cálculo.

## Resumen del eje N

Antes de saltar al siguiente concepto, consolidemos lo que hemos construido con el eje cuantitativo:

1.  **N es un eje de valor puro.** A diferencia de los objetos, los números son su propia identidad y no necesitan un código interno (UUID) para existir en la base de datos.
2.  **La desnudez numérica está prohibida.** Todo número ingresa al sistema con una unidad de medida pegada a él. Esa unidad siempre habita en el catálogo del eje K.
3.  **La medición como evento.** Si la unidad de medida no es obvia, o si los datos sufrirán conversiones matemáticas, la medición se reifica: pasa a ser un evento formal en el eje O.
4.  **Estándares mundiales.** Utilizamos el catálogo oficial **QUDT** para no inventar unidades básicas. Para conceptos emergentes (como los tokens o la precisión de un LLM), creamos unidades personalizadas en K.
5.  **Tolerancia estadística.** El eje soporta la incertidumbre modelando rangos o distribuciones estadísticas completas, no solo promedios planos.

## Trampa de programación: el número que viaja desnudo

El error clásico, el que aparece en producción y cuesta dinero real: guardar `100` en una columna `monto` y dar por hecho que "ya se sabe" que son dólares. Un día el sistema integra un proveedor que factura en yenes, otro operario carga `100` pensando en soles, y la suma `100 + 100` arroja `200` de una moneda que no existe. Es la misma falla que, a otra escala, le costó a la NASA el Mars Climate Orbiter en 1999: un módulo entregaba libras-fuerza y el otro leía newtons. El número, solo, **miente por omisión**.

La regla del eje N lo previene de raíz: una magnitud nunca se almacena como un escalar pelado, sino como el par **valor + unidad**, y la unidad vive en K con su URI canónica (QUDT). El motor que intente sumar `100 USD` con `100 JPY` se detiene en seco, igual que se negaría a sumar peras con tornillos. La cantidad deja de ser un número y pasa a ser un **hecho completo y autoexplicativo**.

## El inventario de cajas está completo

Con el pilar N instalado, nuestro universo de catalogación está formalmente completo. Ya contamos con los cuatro pilares del mundo físico (quién, qué, dónde, cuándo), tenemos el zócalo intelectual para las categorías (K) y acabamos de asegurar el terreno para las magnitudes matemáticas (N). En resumen, **ya tenemos los cajones listos para alojar cualquier tipo de valor existente.**

Lo que nos falta no son más cajones. Lo que nos falta ahora son los **cables** que conecten todos estos valores entre sí. Necesitamos etiquetas que le expliquen a la máquina *cómo* un agente interactúa con un objeto. 

Esos cables lógicos viven en un eje adicional: el eje **M** (*cómo*), el de los predicados o conectores que le dan vida al modelo. Y la diferencia entre "tener una propiedad" y "estar relacionado con algo" es, a nivel informático, muchísimo más delgada de lo que dicta nuestro sentido común: es solo cuestión de cardinalidad.