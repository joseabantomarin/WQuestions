# Capítulo 3 — Lo que ya intentamos: 5W1H, web semántica y ontologías de dominio

## Tres puertas, ninguna cerrada

Si organizar toda la información del mundo a través de preguntas básicas (quién, qué, dónde, cuándo) es algo tan natural y lógico como vimos en el capítulo anterior, la duda surge casi de inmediato: ¿por qué a nadie en la industria del software se le ocurrió hacerlo antes?

La realidad es que sí se intentó. Históricamente, diferentes grupos de investigadores y programadores abordaron este inmenso problema desde ángulos muy distintos, abriendo lo que podríamos llamar "tres puertas" tecnológicas. En este capítulo vamos a asomarnos a esas tres puertas para entender qué cosas brillantes lograron y, sobre todo, por qué ninguna terminó de solucionar el problema de fondo. Entender dónde y por qué fallaron es el único camino seguro para no diseñar un sistema que vuelva a tropezar con las mismas piedras.

Para no enredarnos en teorías abstractas de computación, vamos a poner a prueba cada una de estas tecnologías usando escenarios cotidianos a los que volveremos a lo largo del libro: la preparación de una receta de cocina, el relato de un gol de fútbol, los datos de una canción y la cobertura de una noticia política. Son mundos totalmente dispares, con jergas que no tienen nada que ver entre sí. Una arquitectura de datos que se llame a sí misma "universal" tiene que ser capaz de estructurar estos cuatro ejemplos sin obligarnos a forzar o deformar la información. 

Veamos cómo le fue a la industria intentándolo.

## La primera puerta: el 5W1H como metodología de extracción

Como ya sabemos, la regla de las 5W1H (las seis preguntas periodísticas) nació en las redacciones de prensa. Sin embargo, a finales del siglo XX, algunos investigadores informáticos empezaron a ver esta regla con otros ojos: la vieron como una **herramienta para extraer datos automáticamente**. 

La lógica era muy atractiva. Pensaron: *"Si una noticia bien escrita siempre contiene las respuestas a estas seis preguntas, ¿no podríamos programar un software que lea el texto, extraiga esas variables por su cuenta y construya una base de datos ordenada sin intervención humana?"*

Investigadores como Yang y Hu `[9]` desarrollaron sistemas que hacían exactamente esto. Leían una nota de prensa y devolvían las seis respuestas acomodadas en casilleros. En una línea muy similar, Mahmood `[10]` formalizó esto pidiéndole a un algoritmo que etiquetara cada frase de la noticia para saber qué rol jugaba en la historia.

Para entenderlo, imaginemos que el sistema lee el siguiente texto:

> *El ministro de Salud anunció ayer en conferencia de prensa una nueva campaña de vacunación contra el sarampión para reducir los brotes detectados en zonas rurales del norte del país.*

El programa procesa las palabras y devuelve este esquema:

```text
quién:   el ministro de Salud
qué:     anunció una nueva campaña de vacunación contra el sarampión
cuándo:  ayer
dónde:   en conferencia de prensa
por qué: para reducir los brotes detectados en zonas rurales del norte
cómo:    (no especificado)
```

A primera vista, el resultado es fantástico. Hemos pasado de un párrafo de texto plano a un resumen estructurado. Pero el problema, y es un problema gravísimo en la ingeniería de sistemas, estalla apenas intentamos **almacenar esto de forma útil** para luego **cruzarlo con otras bases de datos**.

Para una computadora, guardar la frase "el ministro de Salud" en la caja del *quién* no significa que la máquina entienda que se trata de un ser humano o de un cargo público; para el sistema, es simplemente una cadena de texto, un conjunto de letras. Si en la noticia de la semana siguiente el texto dice "el titular de la cartera de salud", el programa lo guardará como un texto nuevo. Al no existir una capa de inteligencia semántica por encima, el sistema no tiene forma de saber que ambas frases hablan de la misma persona. Si le pides a esta base de datos: *"muéstrame todas las acciones del ministro de este año"*, la consulta fracasa, porque la máquina no sabe cómo agrupar esos textos sueltos.

Y cuando intentamos cruzar dominios diferentes, el sistema revela sus mayores carencias. Pasémosle a este mismo algoritmo la narración de un evento deportivo:

> *Messi marcó el gol del empate en el minuto 87 con un remate de zurda desde fuera del área, tras una pared con su compañero.*

```text
quién:   Messi
qué:     marcó el gol del empate
cuándo:  el minuto 87
dónde:   fuera del área
por qué: (implícito: empatar el partido)
cómo:    con un remate de zurda tras una pared
```

El programa hizo su trabajo de extracción, sí. Pero observemos el resultado desde la perspectiva de la base de datos: el campo "qué" del ministro (un anuncio de vacunación) y el campo "qué" de Messi (un gol) son procesados exactamente como lo mismo: texto plano. El sistema es completamente ciego a la naturaleza de los eventos. Estructurar un gol requiere casilleros para registrar con qué pierna se pateó o quién dio la asistencia; estructurar un anuncio público requiere casilleros para la audiencia o el canal de transmisión. 

En resumen, usar el modelo 5W1H como un simple **diccionario de roles** funciona de maravilla para asegurarnos de no olvidar información clave. Pero como arquitectura tecnológica le faltan dos motores fundamentales: una **estructura de tipos** (para que la base de datos sepa diferenciar si un texto representa a un lugar, a un evento o a una persona física) y un **vocabulario oficial o canónico** (para estandarizar cómo llamamos a las cosas y no confundirnos con sinónimos). 

Esa fue la primera puerta: una intuición correcta que se quedó a un paso de consolidarse en algo útil.

## La segunda puerta: la web semántica

Años más tarde, en 2001, Tim Berners-Lee (nada menos que el creador de la World Wide Web) propuso una visión profundamente ambiciosa a la que llamó la **Web Semántica** `[31]`. Su objetivo era transformar internet. Quería que las páginas web no solo mostraran texto para que lo leyeran los humanos, sino que incluyeran descripciones de datos invisibles y estructuradas, diseñadas para que las computadoras pudieran leerlas, procesarlas y conectarlas por sí solas. La pieza maestra para lograr esta visión era un formato tecnológico llamado **RDF** `[8]`.

La idea detrás de RDF es de una elegancia matemática impecable: toda la información del universo puede descomponerse en unidades atómicas de tres partes, llamadas **tripletas** (*sujeto — predicado — objeto*). Es como reducir todo el conocimiento a oraciones muy simples:
*   El hecho "Messi marcó un gol" se expresa como `(Messi, marcó, un_gol)`. 
*   El detalle "El gol ocurrió en el minuto 87" se convierte en `(un_gol, ocurrió_en, minuto_87)`. 
*   La autoría "La canción fue compuesta por McCartney" se anota como `(la_cancion, compuesta_por, McCartney)`. 

La promesa arquitectónica era inmensa. Si toda la información mundial se estructuraba usando estas mismas tripletas, cualquier base de datos podría conectarse con otra sin importar en qué país o empresa se originó. Bajo esta promesa nacieron proyectos titánicos como **Wikidata** `[32]` y **DBpedia** `[33]`, que hoy en día almacenan miles de millones de estas tripletas extraídas de Wikipedia y alimentan las respuestas automáticas de los buscadores.

Sin embargo, aquí es donde la brillantez académica choca de frente con el caos de la realidad industrial. RDF resolvió magníficamente la sintaxis (el "cómo" se estructuran y envían los datos), pero dejó una libertad total respecto a la semántica (el "qué" palabras usar). 

Al no haber un diccionario central que limite las opciones, un programador en una empresa puede registrar la tripleta `(McCartney, compuso, "Yesterday")`, mientras que otro desarrollador en una empresa rival podría registrar `(McCartney, autor_de, "Yesterday")` o `(McCartney, escribió_la_canción, "Yesterday")`. A nivel técnico, las tres tripletas están perfectamente escritas; pero a nivel de integración, son incompatibles. Si un analista intenta escribir código para buscar "todas las canciones de McCartney" en todo internet, su programa tendría que conocer de memoria, y traducir en tiempo real, todas las variaciones posibles de ese verbo que a la gente se le haya ocurrido inventar. 

Para intentar frenar este descontrol, la comunidad tecnológica desarrolló herramientas adicionales (como el estándar OWL `[22]`) buscando obligar a la gente a usar los mismos predicados. Pero al hacer esto, terminaron cayendo exactamente en la misma trampa de la tercera puerta que veremos a continuación: la necesidad casi imposible de imponer un diccionario único para todos. 

La intuición de separar la información en unidades mínimas de tres partes fue un acierto técnico indiscutible, pero al carecer de restricciones sobre qué palabras usar, la diversidad de lenguajes simplemente se escondió en otra capa del sistema.

## La tercera puerta: las ontologías de dominio

Ante el caos de la libertad total, el tercer enfoque optó por el extremo opuesto: la especialización exhaustiva y el control estricto. La premisa fue la siguiente: *si el problema es que cada quien inventa sus propios términos, reunamos a los mejores expertos de cada industria, encerrémoslos en una sala, y que no salgan hasta diseñar un vocabulario oficial, riguroso y formalizado para su sector*. Una vez publicado ese diccionario oficial, todas las empresas de esa industria estarían obligadas a usarlo.

Así nacieron las llamadas "ontologías de dominio", y muchas de ellas son obras de arte de la ingeniería. **CIDOC CRM** `[4]` lleva décadas modelando hasta el último detalle de cómo los museos deben clasificar el patrimonio histórico. El **Biolink Model** `[5]` integra complejas bases de datos de biomedicina y genética. **HL7 FHIR** `[6]` es la ley mundial indiscutible para mover historias clínicas electrónicas entre hospitales. Y, a un nivel más comercial y masivo, existe **Schema.org** `[30]`, un monumental acuerdo entre Google, Microsoft y Yahoo para estandarizar cómo las páginas web deben describir su contenido.

Tomemos Schema.org como caso de estudio para ver sus virtudes y sus límites. Dentro de su enorme diccionario, tienen una categoría oficial llamada `Recipe` (Receta). Esta entidad define con precisión quirúrgica qué información necesita un buscador como Google para entender una preparación culinaria. Te ofrece casilleros exactos para los ingredientes (`recipeIngredient`), para la lista ordenada de pasos a seguir (`recipeInstructions`), e incluso para los tiempos de cocción (`cookTime`). Si tú gestionas un portal gastronómico, implementar `Recipe` en tu código soluciona tu vida; Google te entenderá a la perfección.

El problema asoma la cabeza apenas intentas modelar un escenario que se salga un milímetro de ese molde estricto. Supongamos que publicas un libro digital interactivo de historia gastronómica. Quieres que cada receta esté ligada al contexto político de su país de origen en esa época, y a la biografía detallada del chef que la creó. 

Los datos de la comida encajan perfecto en `Recipe`. Pero la biografía del chef requiere usar otra entidad oficial llamada `Person` (Persona); el contexto histórico requiere la entidad `Event` (Evento); y la geografía requiere `Place` (Lugar). Y aquí viene el golpe crítico: Schema.org no provee un mecanismo claro y estandarizado para vincular profundamente estas distintas ramas entre sí. Como las entidades fueron creadas como bloques aislados, la tarea de integrarlas recae, una vez más, en el esfuerzo manual del programador, que tiene que atar los cables con código personalizado.

Y si intentamos saltar a una disciplina científica, la fragmentación es absoluta. Para hablar de fórmulas químicas no basta con Schema.org; existen diccionarios ultraespecíficos como CHEBI o ChEMBL. Si un proyecto de investigación requiere cruzar la composición química de un nuevo fármaco (ontología química) con el historial de un paciente bajo el estándar hospitalario FHIR (ontología médica), hay que invertir meses y muchísimo presupuesto en construir, desde cero, un puente informático entre ambos mundos.

Las ontologías de dominio acertaron plenamente al exigir definiciones precisas para cada industria. Su debilidad estructural —y la razón por la que no unificaron los datos mundiales— es que **se construyeron sin un piso compartido**. Al desarrollarse de forma aislada, cada grupo de expertos tuvo que modelar desde cero conceptos que son universales. Por eso, para definir algo tan básico como a "una persona", los museos usan la etiqueta `E21_Person`, la genética usa `biolink:Agent`, la web comercial usa `Person` y las clínicas usan `Patient`. En la vida real, todos hablan de un ser humano físico; pero tecnológicamente, han creado cuatro entidades incompatibles que las computadoras no saben mezclar.

![Las tres puertas previas comparadas en qué resuelve cada una y qué deja sin resolver. Ninguna terminó de cerrar el problema porque cada una atacó un síntoma distinto y dejó el otro intacto.](../diagrams/png/06_tres_puertas.png)

## Cuatro dominios, tres puertas: El balance

Para aterrizar todo este análisis, veamos en una tabla cómo se comportan estas tres grandes metodologías cuando las obligamos a procesar nuestros cuatro ejemplos iniciales.

|                         | 1. El modelo 5W1H (El enfoque heurístico)                                                  | 2. RDF / Web Semántica (El enfoque de libre conexión)                                                             | 3. Ontología de Dominio (El diccionario estricto)                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **La Receta**           | Insuficiente: no entiende medidas exactas, listas ordenadas de pasos ni tiempos de horno.  | Factible, siempre que los programadores no usen verbos distintos para describir "mezclar" o "hervir".             | Schema.org/Recipe la modela a la perfección, pero dificulta cruzarla con datos históricos o geográficos.          |
| **El Gol de fútbol**    | Muy útil para leer la noticia deportiva, pero inútil para armar estadísticas del partido.  | Posible vía Wikidata, aunque los términos para describir una jugada varían drásticamente entre bases.             | Existe la etiqueta `SportsEvent`, pero no llega al detalle técnico de con qué pierna se ejecutó el remate.        |
| **La Canción**          | Sirve para procesar una noticia *sobre* la canción, no para modelar la obra musical en sí. | Bases gigantes como MusicBrainz lo soportan bien, pero sus vocabularios chocan de frente con otras fuentes.       | Existen modelos robustos en la industria musical, pero operan como burbujas cerradas difíciles de integrar.       |
| **La Noticia política** | Excelente. Es el dominio exacto para el que este modelo fue concebido.                     | Funcional, pero la falta de acuerdo sobre cómo nombrar verbos como "promulgar" o "debatir" arruina las búsquedas. | Schema.org/NewsArticle estructura perfectamente el "contenedor" de la noticia, pero no entiende qué dice adentro. |

Si analizamos la tabla, la conclusión es dura: ningún enfoque ofrece una solución transversal perfecta. Cada tecnología brilla en su especialidad, pero se rompe cuando le pedimos versatilidad. Y lo que es más crítico para la era del Big Data: si intentamos generar una consulta compleja que mezcle dos columnas (por ejemplo, buscar *"qué canciones de protesta han sido objeto de debate en noticias políticas recientes"*), las tres opciones colapsan y exigen que un ingeniero construya la integración a mano.

## Lo que nos faltó: construir un piso, no un techo

Si nos alejamos un paso y observamos el panorama histórico de estos tres grandes intentos, el patrón de sus fallas se vuelve bastante evidente:

   El **5W1H** identificó correctamente las dimensiones naturales de la realidad, pero olvidó construir una arquitectura de software formal para procesarlas.
   El **RDF (Web Semántica)** desarrolló una forma brillante y matemática de conectar datos, pero pecó de exceso de libertad al no imponer un vocabulario mínimo como base.
   Las **Ontologías de Dominio** crearon vocabularios de altísima calidad técnica, pero cometieron el error de aislarse, olvidando apoyarse en una capa fundamental que fuera común a todas las industrias.

Lo que hace falta hoy en la ingeniería de datos, entonces, no es publicar otro diccionario técnico adicional —ya existen miles que nadie usa—, ni tampoco inventar un nuevo formato de conexión de cables. Lo que verdaderamente necesitamos es **un piso compartido que se sitúe por debajo de todos esos vocabularios**. Necesitamos un estándar fundacional que sea lo suficientemente sutil para no interferir con la terminología avanzada que usan los médicos o los arquitectos, pero que sea lo suficientemente firme como para que la información fluya entre ellos sin necesidad de traductores informáticos.

Ese piso es justamente lo que el modelo periodístico de las 5W1H rozó a nivel intuitivo. Como demostramos en el capítulo anterior, las preguntas cognitivas (quién, qué, dónde, cuándo) son el sistema operativo universal con el que la mente humana procesa la realidad. Si tomamos esas preguntas, las matematizamos y las convertimos en **los ejes estructurales fijos de un sistema de datos**, obtenemos precisamente esa base común.

La mecánica es directa y transparente: si una receta tiene un chef, ese individuo se registra en la coordenada del **quién**. Si el gol de Messi ocurre en el minuto 87, ese instante de tiempo va al eje del **cuándo**. Si una canción se ejecuta en una tonalidad particular, ese atributo se clasifica en el **cómo**. Y si un anuncio político se realiza dentro de las instalaciones de un ministerio, ese edificio se mapea en la caja del **dónde**. 

Al adoptar este enfoque, el esfuerzo que se le exige a cualquier empresa o industria es mínimo: solo deben comprometerse a acomodar sus términos técnicos dentro de estas coordenadas preestablecidas. A cambio de aceptar ese orden, el beneficio a nivel de sistema es gigantesco: la información de cualquier dominio del planeta pasa a ser auditable y consultable mediante un único lenguaje estructural, unificando la torre de Babel desde los cimientos.

## Lo que viene

Con este análisis histórico concluimos la Parte I del libro. Hasta ahora hemos repasado el **por qué** estamos inmersos en este problema: analizamos el altísimo costo corporativo que genera la fragmentación de datos (capítulo 1), descubrimos que las preguntas básicas son el modelo natural de procesamiento del cerebro humano (capítulo 2), y revisamos por qué los grandes esfuerzos tecnológicos previos se acercaron a la solución, pero no lograron cerrarla del todo (capítulo 3).

A partir de este punto, abandonamos el terreno del análisis histórico y pasamos a la ingeniería pura y dura. En los próximos capítulos, vamos a diseccionar una por una nuestras ocho coordenadas operativas: **quién, qué, dónde, cuándo, cuánto, cuál, cómo y clase**. Revisaremos las particularidades de cada eje, revelaremos las trampas lógicas más comunes en su diseño informático y las someteremos a una prueba de fuego contra nuestros cuatro escenarios (la receta, el gol, la canción y la noticia) para garantizar que la arquitectura no se rompa.

Empezaremos por analizar el primer eje de todos. Uno que a simple vista parece el más trivial, pero que, cuando se lleva a código, esconde la mayor cantidad de sutilezas de todo el modelo: la pregunta **¿quién?**.