# Capítulo 6 — Cómo: los predicados (M)

## El universo está completo, pero las cosas siguen sueltas

Hagamos un balance de lo que hemos construido hasta ahora en los capítulos anteriores. Nuestro modelo ya cuenta con seis "cajas" gigantes (los ejes de valor) donde podemos alojar cualquier elemento del mundo: 

   **Q** guarda a las personas y agentes que actúan.
   **O** guarda los objetos físicos y los eventos.
   **L** guarda los lugares.
   **T** guarda las fechas y los momentos.
   **N** guarda los números y las magnitudes.
   **K** guarda los conceptos abstractos y las categorías.

Seis ejes, seis tipos distintos de individuos. En teoría, cualquier cosa que exista o pase en el universo puede encontrar un lugar en alguna de estas cajas.

Pero si nos quedáramos solamente con esto, nuestro sistema sería inútil. Imagina que tienes una base de datos donde *"Marta"* vive en `Q`, *"Buenos Aires"* vive en `L`, *"1984"* vive en `T`, el número *"45"* vive en `N` y el concepto *"persona"* vive en `K`. Tienes las piezas del rompecabezas, pero... ¿cómo sabe la computadora que esas piezas están conectadas? ¿Cómo le explicamos a la máquina que *Marta vive en Buenos Aires*, que *nació en 1984*, que *tiene 45 años* y que *es una persona*? 

Los seis ejes que ya vimos son perfectos para alojar individuos aislados, pero no sirven para guardar los **enlaces**. Nos faltan los "cables" lógicos que le dicen a la máquina qué tiene que ver cada cosa con cada cosa.

Esos enlaces son los protagonistas de este capítulo. En el mundo de la lógica y la programación se les conoce como *predicados*. Y en nuestro modelo todos viven en un único eje estructural: **M** (de *Modos*), el eje que responde a la pregunta **¿cómo?** —cómo se conecta cada cosa con cada cosa.

Con este último eje cerramos oficialmente el inventario de las siete coordenadas. Pero antes de darlo por sentado, este capítulo nos obliga a hacernos una pregunta técnica fascinante: en el fondo de una base de datos, *¿qué diferencia real hay entre una propiedad y una relación?* La respuesta —que ambas son el mismo tipo de cable, y que lo único que las separa es su cardinalidad— se convertirá en nuestra decisión de diseño **D2**, y nos ahorrará miles de horas de programación innecesaria.

## Una pregunta que parece de sentido común

Arranquemos con un ejemplo para calentar motores. Imagina que tenemos estos cinco datos sueltos sobre un paciente y sobre un modelo de Inteligencia Artificial:

```text
1. Al paciente_042 le corresponde la edad de 42.
2. Al paciente_042 le corresponde la fecha_nacimiento de 1984-03-17.
3. El paciente_042 vive_en Buenos Aires.
4. El modelo_gpt_4 tiene parámetros por 175.000.000.000.
5. El modelo_gpt_4 fue entrenado_con el corpus de texto C4.
```

Si le pedimos a un programador junior que divida estos cinco enlaces en "propiedades" (atributos propios de la cosa) y "relaciones" (vínculos con otra cosa externa), lo haría sin dudar: 
Diría que la *edad*, la *fecha de nacimiento* y la cantidad de *parámetros* son claramente **propiedades** del sujeto. Por otro lado, argumentaría que *vive en* y *entrenado con* son **relaciones**, porque conectan al sujeto con otra entidad separada. 

Esta intuición suena muy lógica: *propiedad = un atributo interno*; *relación = un puente hacia afuera*.

Sin embargo, esa lógica se rompe apenas la sometemos a un poco de presión arquitectónica:

*   Decimos que *el paciente vive en Buenos Aires* es una relación externa. Pero ¿no podríamos diseñar la tabla diciendo que el paciente tiene un campo interno llamado `ciudad_residencia` que equivale a Buenos Aires? Bajo esa óptica, se vuelve una propiedad.
*   Decimos que *el modelo tiene 175 mil millones de parámetros* es una propiedad interna. Pero, matemáticamente, podríamos leerlo como que el modelo "está conectado o se relaciona" con el número gigante 175.000.000.000 en el eje N. Bajo esa óptica, se vuelve una relación externa.
*   Decimos que *la fecha de nacimiento* es una propiedad. Pero el valor "1984" es un individuo con derechos propios que vive en el eje T. El paciente, en realidad, se está relacionando con un punto en el tiempo.

Si analizamos estos cinco enlaces con frialdad informática, descubrimos una verdad incómoda: **la diferencia entre propiedad y relación no existe en la realidad material**. Es solo una diferencia gramatical sobre cómo los humanos redactamos las oraciones. A veces usamos verbos posesivos ("tiene 42 años") y a veces verbos de lugar ("vive en Buenos Aires"). 

Pero para el disco duro de la computadora que guarda el dato, la estructura técnica es idénticamente la misma: hay un sujeto de partida, un cable conector y un objeto de destino.

Esa observación técnica es el punto de partida de nuestra regla D2. Pero antes de formalizarla, miremos cómo es esa "estructura técnica idéntica" que comparten todos los cables.

## La anatomía del cable: la signatura tipada

Todo enlace dentro de nuestro modelo —no importa si lo llamas propiedad o relación— obedece matemáticamente a una misma forma de tres partes:

> **hecho = (sujeto, predicado, objeto)**

Pero el modelo esconde un truco de seguridad brutal: cada enlace o cable (el predicado) no es un texto ciego; viene de fábrica con una **signatura**. Esta signatura es como la etiqueta de un enchufe que le indica a la computadora de qué eje tiene que venir obligatoriamente el sujeto, y a qué eje debe ir a conectarse el objeto. 

Si lo vemos como funciones matemáticas, los cinco enlaces anteriores tienen estas etiquetas de seguridad:

```text
edad             : va desde Q hacia N (De Personas a Números)
fecha_nacimiento : va desde Q hacia T (De Personas a Fechas)
vive_en          : va desde Q hacia L (De Personas a Lugares)
parametros       : va desde O hacia N (De Objetos a Números)
entrenado_con    : va desde O hacia O (De Objetos a otros Objetos)
```

La signatura es la magia que convierte un montón de datos desordenados en una estructura **predecible y validable**. Si un programador comete un error de código e intenta guardar esto: `(paciente_042, edad, "color rojo")`, el sistema lo bloquea automáticamente. ¿Por qué? Porque la signatura del cable `edad` advierte que el destino tiene que estar en la caja `N` (los números), y "color rojo" es un texto. 

Esta capacidad de bloquear errores absurdos desde el momento en que se ingresan los datos es la ventaja comercial más grande de este modelo. Es lo que separa a la arquitectura sólida de WQuestions del caos que generan los grafos libres (como RDF), donde cualquiera puede conectar a un paciente con un color usando el verbo "edad" sin que el sistema detecte la falla.

## La verdadera diferencia: ¿funcional o múltiple?

Visto que la forma del cable es siempre la misma (`sujeto - cable - objeto`), ¿existe alguna razón técnica para distinguir entre "propiedades" y "relaciones"? Sí, y la diferencia es estrictamente matemática. Se trata de la **cardinalidad**.

Vuelve a mirar nuestras cinco signaturas. Cuatro de ellas se comportan como lo que en matemáticas llamamos **funciones cerradas**: dado un sujeto específico, el cable solo puede conducir a *un único* destino posible en ese instante. Un paciente solo puede tener *una* edad matemática hoy; solo puede tener *una* fecha de nacimiento y solo tiene *una* ciudad donde reside principalmente. Un modelo de IA tiene *un solo* conteo exacto de parámetros. 

El quinto cable —`entrenado_con`— rompe esa regla. Un modelo de IA puede haber sido entrenado usando el corpus C4, la Wikipedia y libros de dominio público al mismo tiempo. Es decir, un mismo sujeto puede disparar varios cables hacia múltiples objetos simultáneos, y todos son correctos.

Esta es la única y verdadera diferencia estructural en la base de datos entre lo que solemos llamar "propiedades" y "relaciones":

*   Los cables **funcionales** (los que solo admiten *un destino único* por sujeto) son los que solemos llamar **propiedades**.
*   Los cables **no funcionales** (los que permiten que el sujeto apunte a *múltiples destinos* a la vez) son los que solemos llamar **relaciones**.

Pero ambos son el mismo tipo de cable y viven en el mismo eje (**M**, *cómo*). La cardinalidad no es un eje aparte: es un **atributo de cada cable**, declarado en su signatura. Y lo único que ese atributo le indica a la base de datos es **cómo comportarse cuando el dato se actualice**.
Si el cable es funcional (único) y llega información nueva, el sistema **borra y reemplaza** lo anterior. Si el paciente cumple años, borramos el 42 y ponemos un 43; no acumulamos edades. 
En cambio, si el cable es múltiple y llega información nueva, el sistema simplemente la **agrega a la lista**. Si el modelo de IA es entrenado con una biblioteca nueva, ese texto se suma al historial de entrenamiento sin borrar a la Wikipedia.

Esa diferencia de cardinalidad es lo único que distingue una propiedad de una relación. Pero, y aquí viene el alivio para el programador: **el motor de búsquedas del sistema no hace diferencias**. Si tú le preguntas a la base de datos *"¿Qué edad tiene el paciente 042?"* o *"¿Con qué fue entrenado el modelo X?"*, la máquina ejecuta exactamente el mismo código de búsqueda. Solo que en el primer caso te devuelve una sola respuesta, y en el segundo te devuelve una lista.

![Cardinalidad de los cables: misma forma sujeto-predicado-objeto. Un cable funcional reemplaza el valor anterior; uno múltiple se acumula con los previos.](../diagrams/png/12_p_vs_m_cardinalidad.png)

## La regla de diseño D2: La unificación matemática

Esta revelación nos lleva a establecer de manera formal una de las decisiones de diseño más elegantes del modelo:

> **D2 — Las propiedades y las relaciones se unifican bajo el mismo concepto: son simplemente cables (predicados) del eje *cómo* (M) con etiquetas de seguridad (signaturas tipadas). La única diferencia entre ellas es la cardinalidad —si aceptan uno o varios destinos simultáneos—, y esa cardinalidad es un atributo de la signatura de cada cable, no un eje aparte. Le indica a la base de datos cuándo debe "borrar y reemplazar" (cable funcional) y cuándo debe "acumular" (cable múltiple) nueva información.**

Entender la regla D2 significa comprender que el enorme abismo técnico que se nos enseña en la universidad —donde nos obligan a tratar a los atributos internos como "columnas en una tabla" y a los vínculos externos como "tablas conectadas o JOINs"— es, en realidad, **una ilusión pedagógica**. Es una complicación innecesaria de la programación tradicional. A nivel matemático, todo es simplemente un sujeto, un cable tipado y un destino. Y esa simplicidad es la gasolina que hace que este modelo vuele.

## ¿Qué gana una empresa unificando esto?

Adoptar la regla D2 tiene cuatro beneficios gigantescos y directos en entornos de producción:

1.  **Un motor de búsqueda unificado:** El sistema ya no necesita tener un "lenguaje para consultar datos internos" y otro "lenguaje para consultar cruces de tablas". El código se reduce a una sola instrucción maestra: *"dado este sujeto y este cable, devuélveme el destino"*. Le decimos adiós a los enredados *SELECT* y *JOIN* del SQL tradicional.
2.  **Facilita el trabajo de la IA (JSON universal):** Cuando un agente de Inteligencia Artificial (LLM) solicita datos a través de *function calling*, el sistema le devuelve todo empaquetado en exactamente la misma estructura limpia y predecible. La IA no gasta tokens tratando de averiguar si la edad viene en un formato y el listado de amistades viene en otro. La uniformidad abarata la integración corporativa.
3.  **Extensibilidad a prueba de balas:** Si mañana la empresa quiere registrar un dato nuevo sobre sus clientes, los programadores no tienen que reunirse a debatir si crear una columna nueva en la tabla o construir una tabla intermedia entera. Simplemente añaden el nuevo "cable" al diccionario, deciden si la respuesta es única o múltiple, y el motor de la base de datos ya sabe qué hacer.
4.  **Habilitan el procesamiento del lenguaje natural:** En capítulos posteriores comprobaremos que cada verbo que usamos los humanos (como "vender", "comer", "firmar") exige ciertos roles. Cuando le decimos al sistema: *"María le vendió un libro a Juan"*, la máquina registra al vendedor, al comprador y a la mercancía usando esta estructura uniforme. Al no hacer diferencias entre propiedades y relaciones, el sistema lee frases humanas como si leyera código de máquina.

## Tres dominios bajo el microscopio

Para terminar de consolidar este concepto, veamos cómo se reparten los cables funcionales y múltiples cuando los aplicamos al diseño de tres mundos totalmente distintos. 

### 1. El mundo de la gastronomía: Una receta
```text
Cables funcionales (respuesta única):
  tiempo_preparacion : va de O hacia N  (15 minutos)
  tiempo_coccion     : va de O hacia N  (45 minutos)
  porciones          : va de O hacia N  (4)
  dificultad         : va de O hacia K  (intermedia)

Cables múltiples (acumulan):
  ingrediente        : va de O hacia K  (varios ingredientes por receta)
  paso               : va de O hacia O  (muchos pasos en la preparación)
  utensilio          : va de O hacia K  (varios utensilios a ensuciar)
```
La lógica se cumple: lo que el sentido común considera "atributos estáticos" del plato es funcional (un solo valor); lo que son "piezas que se suman" es múltiple.

### 2. El mundo del software: Una llamada a la Inteligencia Artificial
```text
Cables funcionales (respuesta única):
  tokens_entrada     : va de O hacia N  (4500)
  latencia_ms        : va de O hacia N  (2300)
  costo_usd          : va de O hacia N  (0.018)
  modelo_usado       : va de O hacia K  (gpt-4-turbo)

Cables múltiples (acumulan):
  fuente_documento   : va de O hacia O  (la IA pudo consultar 5 PDFs distintos)
```
Mismo patrón de fondo: el consumo exacto en dinero es uno solo (funcional), pero los documentos analizados durante la consulta pueden ser docenas (múltiple).

### 3. El mundo del deporte: Un partido de fútbol
```text
Cables funcionales (respuesta única):
  resultado_final    : va de O hacia K  (victoria_local, empate)
  asistencia         : va de O hacia N  (52.000)

Cables múltiples (acumulan):
  partes_jugando     : va de O hacia Q  (son siempre 2 equipos, es múltiple)
  gol_anotado        : va de O hacia O  (puede haber varios goles)
  tarjeta_amarilla   : va de O hacia O  (puede haber docenas)
```

Aquí la distinción requiere una mirada afilada. El cable `partes_jugando` (los dos equipos) engaña: podrías pensar que es **funcional** porque el número de equipos en un partido *siempre* es exactamente dos, un número fijo. Sin embargo, es **múltiple**. ¿Por qué? Porque la regla no trata sobre si el número es fijo o infinito, la regla dicta que un cable funcional solo admite **una única respuesta posible**. Al haber dos respuestas legítimas para el mismo partido (el equipo A y el equipo B), matemáticamente es un cable múltiple. 

## Cierre de la Parte II: El tablero está listo

Con la formalización del eje *cómo*, hemos terminado de construir todo el andamiaje del modelo. El inventario de las siete coordenadas maestras está oficialmente cerrado y listo para operar:

*   **Q  (Quién)**    — Las personas y agentes.
*   **O  (Qué)**      — Los objetos físicos, eventos y situaciones.
*   **L  (Dónde)**    — Las locaciones.
*   **T  (Cuándo)**   — El flujo del tiempo.
*   **N  (Cuánto)**   — Los números y magnitudes matemáticas.
*   **K  (Cuál)**     — Los conceptos abstractos y las categorías (tipos, unidades, estados, vocabularios).
*   **M  (Cómo)**     — Los cables o predicados que conectan los ejes de valor (funcionales o múltiples).

Seis cajas gigantes para guardar "cosas", entrelazadas por una red de cables estructurales (el eje *cómo*, M). Cualquier fenómeno, suceso, registro bancario o reporte médico que ocurra en el mundo cabe, sin distorsiones, dentro de esta matriz de siete ejes. Cumplimos con la promesa inicial del libro: hemos demostrado que el universo de los datos puede ser mapeado usando únicamente las preguntas fundamentales del cerebro humano.

![Los siete ejes de WQuestions: seis ejes de valor (Q, O, L, T, N, K) alrededor del universo V, conectados por el eje estructural de predicados (M, cómo).](../diagrams/png/01_ocho_ejes.png)

El diagrama bautiza con una letra al conjunto de esas seis cajas: **V**, *el universo de valores*. No es un séptimo eje ni una caja nueva: es, simplemente, **la unión de los seis ejes de valor** (Q, O, L, T, N, K) tomados juntos — todo lo que puede ser *valor* de un hecho, frente a M, que son los cables y no los valores. Lo nombramos desde ya porque más adelante hará falta: cuando una relación no se ate a un eje concreto sino que admita *cualquiera* de los seis, diremos que su dominio o su rango es V (lo veremos al definir las signaturas, en el Capítulo 11).

Pero tener el plano del motor en la mano no es lo mismo que encenderlo. Hasta aquí, hemos visto los ejes por separado, como piezas sueltas de un reloj. Lo que le da valor industrial a este modelo es observar **cómo interactúan todos juntos** a la vez para estructurar escenarios del mundo real de altísima complejidad. Ahí dejamos atrás la etapa de inventario y entramos en la etapa operativa: el diseño en movimiento.