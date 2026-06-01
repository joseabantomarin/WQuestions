# Capítulo 1 — La torre de Babel y la pista que estaba a la vista

## Una sala de emergencias a las dos de la mañana

Para entender la magnitud del problema arquitectónico que enfrentamos hoy en la industria de los datos, no necesitamos mirar un servidor corporativo; basta con mirar una sala de emergencias a las dos de la mañana. 

Un médico de guardia recibe a una paciente de cuarenta y dos años que ingresa con un dolor torácico agudo. Está consciente, pero experimenta sudoración fría y dificultad para respirar. En esos minutos críticos, el médico necesita acceder a tres piezas de información para tomar una decisión de vida o muerte: qué medicación de uso diario consume, si tiene alergias documentadas y si existe un historial reciente de episodios similares. Sin embargo, al introducir el nombre de la paciente en el sistema del hospital, la pantalla solo devuelve una ficha de tres líneas indicando que fue atendida por una bronquitis hace cuatro años.

La información vital que el médico busca no es un misterio; de hecho, está perfectamente documentada. Esta paciente tiene una endocrinóloga privada que gestiona su historial desde hace siete años; fue evaluada por un cardiólogo en otra ciudad hace unos meses; y ya pasó por una emergencia similar donde le realizaron un electrocardiograma completo. Los datos existen, están almacenados en discos duros, y ninguna de estas clínicas tiene la intención de ocultarlos. 

El problema es puramente estructural: los datos están atrapados en esquemas incompatibles. 

La endocrinóloga utiliza un software que guarda el diagnóstico bajo la variable `diagnostico_principal`. El sistema del cardiólogo, desarrollado por otra empresa, lo registra como `dx_p`. Cuando miramos los medicamentos, la primera clínica utiliza una estructura plana llamada `medicacion_actual` separando `nombre`, `dosis` y `frecuencia`. La segunda clínica, en cambio, diseñó una base de datos relacional con una tabla de `prescripciones` que requiere un identificador numérico (`farmaco_id`), los miligramos por toma (`mg_por_toma`) y las tomas diarias (`tomas_dia`).

Si eres ingeniero de software o analista de datos, sabes que conectar estas dos bases de datos no es ciencia ficción. Es posible, pero es un trabajo artesanal, costoso y sumamente frágil. Tienes que programar un puente de código (un *middleware*), mapear manualmente qué columna equivale a qué columna, y escribir excepciones para cada formato de fecha o número. Y lo peor de esta solución parche es su caducidad: el día en que la clínica actualice su sistema y cambie un solo nombre en su base de datos, tu puente de código colapsará silenciosamente. 

Multiplica este pequeño esfuerzo técnico por miles de hospitales, decenas de proveedores de software y décadas de historiales clínicos. La integración de datos deja de ser un reto técnico y se revela como un problema de diseño a nivel mundial. La información existe, pero matemáticamente no podemos razonar con ella.

## El mismo hecho, cuatro idiomas distintos

Para visualizar exactamente qué ocurre dentro de las bases de datos cuando ocurre un evento, analicemos algo mucho más cotidiano: *el instante exacto en que una persona compra una camiseta en una tienda física*. 

Es un único hecho en la realidad. Sin embargo, si nos asomamos a los servidores de la empresa que vende la camiseta, descubriremos que sus distintos departamentos registran ese mismo segundo en el tiempo utilizando cuatro lenguajes radicalmente distintos:

En el sistema del **punto de venta (la caja registradora)**, la prioridad es registrar la transacción comercial y los actores involucrados. Por eso, el hecho se guarda como una fila en una base de datos relacional:

```sql
INSERT INTO ventas
  (id, cliente_id, producto_id, monto, fecha, vendedor_id)
VALUES (74921, 1042, 88, 49.90, '2026-05-14', 17);
```

Para el sistema de **contabilidad**, la identidad del vendedor o el cliente es irrelevante. Su objetivo es mantener el equilibrio financiero de la empresa mediante el método de partida doble. Ese mismo evento se descompone así:

```text
asiento: 2026-05-14
  debe:  cuentas_por_cobrar       49.90
  haber: ventas_brutas            42.29
  haber: impuesto_al_consumo       7.61
```

Si saltamos al departamento de **marketing**, su obsesión es el comportamiento del usuario y el origen de la compra para medir el éxito de sus campañas. Ellos estructuran la información como un evento de rastreo:

```text
evento: compra_completada
id_usuario: u_1042
sku_producto: sku-88
ingresos: 49.90
canal: tienda_física
id_sesión: s_abcdef
```

Finalmente, para el sistema de **inventario o almacén**, lo único que importa es la logística: un objeto físico acaba de abandonar las instalaciones. El evento se reduce a un simple movimiento de existencias:

```text
movimiento: salida
producto: 88
cantidad: 1
almacen: tienda_central
ref: vta-74921
```

Observa la desconexión. Tenemos cuatro departamentos operando con cuatro estructuras diferentes. Cada esquema es perfecto y coherente para el equipo que lo diseñó. El problema surge cuando la dirección de la empresa pide un análisis global. Si le entregamos estas cuatro piezas de código a una computadora, el sistema no tiene ninguna forma obvia de saber que todas están hablando del mismo suceso. El sistema contable no sabe quién vendió la camisa; marketing no sabe de qué almacén salió; y la caja registradora no sabe cómo separar los impuestos. Cada software capturó solo la "sombra" del evento que le interesaba y la guardó en su dialecto privado.

![El mismo hecho del mundo registrado en cuatro vocabularios incompatibles, uno por cada sistema que lo procesa.](../diagrams/png/02_mismo_hecho_cuatro_sistemas.png)

A esta fragmentación masiva es a lo que en este libro llamaremos **la torre de Babel de las ontologías**. En la ciencia de datos, la palabra *ontología* no es un concepto filosófico inalcanzable; es simplemente el catálogo oficial de conceptos que un sistema reconoce (como "cliente", "factura" o "producto") y las reglas lógicas que dictan cómo se conectan entre sí. El gran error de la industria tecnológica ha sido permitir que cada departamento, empresa y sector científico construya su propia ontología cerrada, aislándose sistemáticamente del resto del mundo.

## La causa de todo el problema

La raíz estructural de esta torre de Babel —y el punto de partida de este libro— es que **hemos permitido que cada sector invente su propia forma de entender la realidad desde cero**. 

La ingeniería médica no hereda ninguna estructura de la contabilidad comercial; el comercio no comparte bases con el derecho penal; y la educación diseña bases de datos que no se hablan con el urbanismo. Cada industria construye su pirámide desde la base utilizando planos distintos, y luego nos sorprendemos cuando resulta carísimo contratar programadores para tender puentes colgantes entre las cimas de esas pirámides.

¿Qué pasaría si la solución a este caos fuera anterior y mucho más simple que cualquier diseño de base de datos? ¿Qué pasaría si, mucho antes de que existieran los hospitales, los bancos o el comercio internacional, la humanidad ya hubiera desarrollado un esquema cognitivo universal que nadie puede evitar utilizar?

La hipótesis de este libro es que esa estructura maestra ya existe, y está codificada en la forma en que hablamos y pensamos todos los días.

## La pista que estaba a la vista

Regresemos al ejemplo de la compra de la camiseta. Si detuviéramos a cualquier persona en la calle —sin conocimientos de bases de datos, ontologías o código SQL— y le pidiéramos que nos describa ese hecho, su respuesta natural sería algo muy parecido a esto:

> "*Una clienta* (**quién**) *compró* (**qué**) *una camiseta* (**qué**) *en la tienda del centro* (**dónde**) *esta tarde* (**cuándo**) *por casi cincuenta dólares* (**cuánto**)."

Cualquier ser humano es capaz de producir una descripción **estructurada, completa y combinable** sin el menor esfuerzo. Esto ocurre porque nuestra mente no percibe el mundo como un bloque de texto desordenado ni como tablas de Excel; nuestro cerebro descompone automáticamente cualquier evento de la realidad utilizando un conjunto muy reducido de preguntas fundamentales.

Que todos pensemos así no es una casualidad. A lo largo de la historia, cuatro grandes áreas del conocimiento humano —el periodismo, el derecho, la filosofía y la lingüística—, trabajando de forma independiente y separadas por siglos, llegaron exactamente a la misma conclusión estructural. Vale la pena recorrer esa convergencia con calma, porque es la pista arquitectónica más valiosa que tenemos.

## Un aula de 1917

Imagina por un momento que estás en un aula de periodismo de cualquier universidad norteamericana, alrededor del año 1917. El profesor entra, toma una tiza y escribe seis letras mayúsculas en la pizarra: *W, W, W, W, W, H*. Debajo de cada una, anota su significado en inglés: *who, what, where, when, why, how* (quién, qué, dónde, cuándo, por qué y cómo). La consigna para los alumnos es simple pero estricta: para aprobar el ejercicio de esa noche, deben leer un recorte de periódico y subrayar, con colores distintos, las respuestas exactas a esas seis preguntas. Si el texto omite una sola de ellas, la noticia se descarta por estar incompleta.

Este ejercicio no era una ocurrencia pasajera del profesor. El manual *Newspaper Writing and Editing*, publicado apenas cuatro años antes por Willard Bleyer `[3]`, había formalizado esto como la regla de oro de la profesión: cualquier noticia bien construida debía responder a estas seis interrogantes, idealmente en su primer párrafo. Esta regla metodológica, bautizada mundialmente como las **5W1H**, sobrevivió intacta a todo el siglo XX, superó la transición hacia el periodismo digital y se sigue enseñando hoy como el estándar básico en las escuelas de comunicación de todo el planeta.

Lo verdaderamente interesante de esta anécdota no es preguntarnos por qué a Bleyer se le ocurrió la regla, sino por qué funcionó con tanta eficacia. Cuando un académico inventa una regla por capricho, la industria suele olvidarla en la siguiente generación. Pero cuando una norma sobrevive más de cien años en un entorno tan cambiante, es porque ha logrado capturar una verdad estructural profunda. 
Las 5W1H no sobrevivieron por ser un "invento" brillante de los periodistas; sobrevivieron porque fueron el redescubrimiento moderno de un patrón cognitivo que aparece una y otra vez a lo largo de la historia de la humanidad.

## Veinte siglos antes de Bleyer

Bleyer probablemente no era un erudito en historia antigua, pero la matriz analítica que acababa de plasmar en su manual ya llevaba más de dos mil años circulando. Si rastreamos esta idea hacia el pasado, nos topamos de frente con la retórica de la antigua Roma, y específicamente con Cicerón.

A mediados del siglo I antes de Cristo, Cicerón redactó un tratado fundamental para enseñar a hablar en público y argumentar en los tribunales, llamado *De inventione* `[2]`. En este texto, rescatando conceptos de un filósofo griego llamado Hermágoras, propuso que cualquier análisis serio sobre los actos de una persona debía estructurarse alrededor de siete *circumstantiae* (circunstancias):

> *quis, quid, ubi, quibus auxiliis, cur, quomodo, quando.*
> Quién, qué, dónde, con qué medios, por qué, cómo, cuándo.

Para Cicerón, esta lista no era un recurso retórico para sonar elegante. Era una herramienta de ingeniería legal. Si un abogado pretendía defender a un acusado argumentando que actuó por necesidad, o buscaba incriminarlo demostrando malicia, tenía la obligación de reconstruir la historia paso a paso utilizando esas siete dimensiones. Si el abogado olvidaba responder a una sola de esas preguntas, su argumento presentaba una falla estructural por donde la contraparte podía destruir su caso.

Un siglo más tarde, otro romano llamado Quintiliano perfeccionó esta metodología en su obra *Institutio Oratoria* `[25]`. A partir de ahí, la fórmula viajó intacta a través del tiempo hasta llegar a la Edad Media. En su monumental *Suma Teológica*, Tomás de Aquino retomó exactamente estas mismas circunstancias, esta vez para evaluar si una acción humana era moralmente buena o mala `[26]`. 

La línea de transmisión histórica es innegable: los juristas romanos le pasaron el esquema a los teólogos medievales, estos se lo entregaron a los pensadores modernos y, para finales del siglo XIX, la misma lista reapareció (ya despojada de sus citas en latín) como un manual de uso práctico para las redacciones de noticias en Norteamérica.

Visto en retrospectiva, resulta casi cómico que Bleyer creyera estar patentando la rueda periodística cuando solo la estaba desenterrando. Sin embargo, la lección que nos importa sacar de aquí es estrictamente arquitectónica. Si la misma lista exacta de preguntas reemerge de forma natural en entornos tan dispares como un tribunal romano, una iglesia medieval y un periódico moderno, se debe a que existe una fuerza de gravedad que obliga a esa lista a regresar. Y esa fuerza no es la tradición cultural —las tradiciones se diluyen o se olvidan—; la lista vuelve a aparecer porque es la única solución lógica a un problema de procesamiento de información universal: ¿cómo hacemos para describir un evento de la realidad sin dejar puntos ciegos?

## Aristóteles, todavía más atrás

Y la historia no comienza con Cicerón. Trescientos años antes de que los romanos sistematizaran el derecho, el filósofo griego Aristóteles ya había ejecutado este mismo ejercicio analítico, aunque utilizando otro vocabulario.

En su célebre tratado *Ética a Nicómaco* `[1]`, Aristóteles se enfrentó al problema de cómo diferenciar una acción realizada a propósito de una ocurrida por accidente. Para resolverlo, trazó un inventario de las variables que una persona debe conocer al momento de actuar para que la sociedad pueda considerarla plenamente responsable. Traducido a un lenguaje contemporáneo, el planteamiento de Aristóteles sostenía lo siguiente:

> Para determinar si alguien actuó en completa ignorancia, debemos verificar si desconocía: (a) quién es él mismo, (b) qué es lo que está haciendo, (c) a quién o sobre qué está recayendo la acción, (d) con qué instrumento lo hace, (e) por qué lo hace, o (f) cómo lo hace (por ejemplo, si aplicó fuerza moderada o violencia extrema).

Si observamos el desglose, la estructura es idéntica a la que venimos rastreando: identifica al agente, la acción, el paciente, el instrumento, el motivo y el modo. Es cierto que falta la variable temporal ("¿cuándo?"), pero su ausencia en este párrafo específico es totalmente lógica: a la hora de juzgar si alguien es moralmente responsable de haber golpeado a otro, el momento exacto en el reloj es un dato casi siempre irrelevante. No obstante, el "cuándo" reaparece con fuerza en otros textos de Aristóteles cuando teoriza sobre el tiempo y el cambio físico.

En resumen, la filosofía clásica ya estaba atravesada por una intuición metodológica brillante: para lograr comprender cualquier fenómeno del mundo real, es imperativo desensamblarlo en sus dimensiones naturales. Y esas dimensiones, sin falta, terminan mapeándose sobre nuestras preguntas básicas.

## El testimonio de la gramática

Hasta este punto de la argumentación, podría parecer que estamos frente a un sesgo cultural, una simple herencia del pensamiento occidental europeo. Sin embargo, la evidencia empírica más contundente de que este esquema es universal proviene de una disciplina estrictamente técnica: la lingüística comparada.

Si analizamos cualquier idioma vivo del planeta —sea quechua, chino mandarín, swahili, euskera, árabe o español— y observamos la mecánica que utilizan sus hablantes para interrogar la realidad, encontraremos invariablemente el mismo conjunto compacto de palabras: quién, qué, dónde, cuándo, cómo, por qué, cuál y cuánto. Cada lengua tiene, por supuesto, sus propias rarezas gramaticales. Algunas poseen pronombres distintos para decir "quién" en singular o en plural; otras utilizan partículas específicas para diferenciar entre "dónde estoy" y "hacia dónde voy". Pero, a nivel semántico, el núcleo de preguntas base es asombrosamente idéntico en toda la especie humana.

A mediados del siglo XX, la investigadora Anna Wierzbicka lideró un proyecto monumental buscando identificar conceptos que significaran exactamente lo mismo en todas las culturas humanas. El resultado fue la formulación del **Metalenguaje Semántico Natural** `[28]`. En su catálogo final de conceptos universales aparecieron, sin la menor sorpresa, términos como: alguien (quién), algo (qué), dónde, cuándo y por qué. Wierzbicka no incluyó estas palabras por conveniencia teórica; se ganaron su lugar en la lista tras superar pruebas de traducción exhaustivas en decenas de lenguas pertenecientes a comunidades aisladas que jamás tuvieron contacto con Occidente.

Casi en paralelo, la comunidad de la lingüística formal le otorgó a este fenómeno un nombre técnico que todavía se utiliza en ciencias de la computación: **roles temáticos** `[24]`. En 1968, Charles Fillmore postuló que la mente humana, al procesar cualquier verbo, asigna automáticamente "roles" específicos a las entidades que lo rodean. Estos roles son fijos: existe un *agente* (quién), un *tema* o paciente (qué), una *locación* (dónde), una *temporalidad* (cuándo), un *instrumento* (con qué) y un *beneficiario* (para quién). Dependiendo de la escuela lingüística, el modelo puede contar con ocho o doce roles, pero el chasis estructural coincide milimétricamente con el análisis que Aristóteles hizo veintitrés siglos atrás.

Contamos, entonces, con cuatro disciplinas distintas operando bajo cuatro nomenclaturas diferentes. Aristóteles hablaba de las *circunstancias del acto*; Cicerón las bautizó como *circumstantiae*; las escuelas de periodismo las empaquetaron como las *5W1H*; y la lingüística formal las catalogó como *roles temáticos*. Pero al tabularlas y compararlas, la conclusión es ineludible: todos descubrieron exactamente la misma estructura base de la información.

![Línea de tiempo de las cuatro tradiciones independientes que convergen, sin coordinarse, en el mismo conjunto reducido de preguntas.](../diagrams/png/04_convergencia_tradiciones.png)

## El niño que pregunta

Nos queda una última pieza de evidencia, y resulta ser la más profunda a nivel biológico. Este inventario de preguntas no solo reside en tratados de filosofía o en la estructura de idiomas milenarios; se manifiesta de forma espontánea durante el desarrollo cognitivo temprano de cualquier niño, y lo hace en un orden de aparición increíblemente estricto sin importar su país de nacimiento.

En 1973, el investigador Roger Brown llevó a cabo un estudio longitudinal clásico `[27]` sobre la adquisición de la lengua materna. Documentó un patrón fascinante que posteriormente fue replicado y confirmado en niños hispanohablantes, franceses, japoneses y hebreos: los infantes no asimilan todas las preguntas al mismo tiempo. Su cerebro las desbloquea siguiendo una secuencia inalterable:

1.  La primera herramienta en aparecer es el **qué** ("¿Qué es eso?"). Es el mecanismo de escaneo más básico para construir vocabulario e identificar el entorno material.
2.  Le sigue el **dónde** ("¿Dónde está mamá?"). Emerge cuando el niño adquiere la noción de permanencia, entendiendo que los objetos existen aunque desaparezcan de su campo visual.
3.  A continuación se activa el **quién** ("¿Quién hizo esto?"). Es el momento en que el cerebro logra distinguir entre un objeto pasivo y un agente capaz de ejercer fuerza y voluntad.
4.  El **cuándo** tarda mucho más en llegar (generalmente cerca de los tres años de edad). Esto obedece a que el cerebro primero necesita madurar la abstracción mental necesaria para diferenciar el pasado del presente y proyectar un futuro.
5.  El **por qué** aparece casi a la par, desatando la conocida "etapa de los porqués", donde el niño busca entender la causalidad mecánica de las cosas.
6.  Finalmente, el **cómo** suele ser la última métrica en consolidarse. Es una interrogante altamente compleja, ya que exige que el individuo sea capaz de conceptualizar un proceso secuencial completo, en lugar de un simple hecho aislado.

![Las preguntas-W aparecen en los niños en un orden estable a través de los idiomas, lo cual sugiere que el orden refleja complejidad cognitiva del concepto, no del idioma.](../diagrams/png/05_adquisicion_infantil.png)

La belleza arquitectónica de este hallazgo radica en que la secuencia de aprendizaje no está dictada por las normas culturales ni por la dificultad gramatical de cada idioma. Este orden inalterable nos demuestra que las dimensiones factuales poseen distintos niveles de exigencia computacional para el cerebro. Identificar un objeto tangible ("¿qué es eso?") requiere menos carga cognitiva que ubicar una acción en un continuo espacio-temporal ("¿cuándo ocurrió?"). 

Si los seres humanos, independientemente de su origen, despliegan estas interrogantes en el mismo orden secuencial, la conclusión tecnológica es contundente: estas preguntas no son una convención inventada por la sociedad. Son el firmware de fábrica; el mecanismo primario de procesamiento de datos con el que nuestra mente logra darle sentido a la entropía de la realidad.

## Las preguntas como invariantes cognitivos

Con este panorama empírico sobre la mesa, ya estamos en condiciones de formular explícitamente la tesis que actuará como columna vertebral del resto de este libro:

> **Las preguntas fundamentales (quién, qué, dónde, cuándo, cómo...) no son un capricho cultural ni un artefacto inventado por una disciplina académica. Constituyen "invariantes cognitivos": las dimensiones estructurales universales mediante las cuales el cerebro humano desensambla y almacena la realidad. Operaban con total precisión mucho antes de la invención del derecho, la estadística, las bases de datos relacionales, o de que un niño sea siquiera capaz de estructurar una oración fluida.**

Aunque esta sea una afirmación audaz, la validación empírica sostiene sus pilares:

   **¿Aparecen sistemáticamente en el análisis humano?** Sí. Filósofos griegos, juristas romanos, periodistas americanos y lingüistas modernos convergieron en el mismo vector dimensional sin haber cruzado información metodológica.
   **¿Son independientes del idioma?** Sí. Los pronombres interrogativos fungen como una clase léxica universal, manteniendo su núcleo semántico en lenguas sin ninguna relación etimológica.
   **¿Emergen de forma innata?** Sí. Su aparición en el desarrollo infantil sigue un cronograma rígido, transversal a todas las culturas y lenguajes.
   **¿Preceden a la especialización científica?** Sí. Ningún niño puede ser instruido en taxonomías biológicas o principios de física si antes no domina la operatoria básica de la pregunta "¿qué?".

Nos enfrentamos a cuatro predicciones estructurales, y las cuatro ofrecen confirmaciones sólidas. Si bien las ciencias cognitivas continúan debatiendo detalles granulares de estos procesos, el volumen de evidencia apunta unívocamente hacia un mismo centro de gravedad.

## El cimiento de diseño más robusto

Llegados a este punto, un arquitecto de software pragmático podría preguntarse: *"Todo este recorrido antropológico y filosófico es fascinante, pero ¿de qué me sirve a mí si mi único objetivo es diseñar una base de datos escalable o programar el backend de un agente de Inteligencia Artificial?"*

La utilidad es inmensa y estrictamente **arquitectónica**. Si acabamos de demostrar con evidencia histórica y biológica que estas preguntas *son* la estructura nativa mediante la cual la mente procesa y clasifica la información, entonces tenemos frente a nosotros **el cimiento de diseño más robusto posible para edificar cualquier sistema informático**.

Elegir este cimiento cognitivo es infinitamente más seguro que anclar un sistema a los vocabularios de turno de cada industria, porque la jerga corporativa muta año tras año. Es más estable que apostar por los "estándares" de diseño de bases de datos, porque las metodologías tecnológicas se vuelven obsoletas cada década. Resulta ser más perdurable, incluso, que las propias lenguas maternas, ya que, aunque el euskera y el español suenen incomprensibles entre sí, la matemática subyacente de sus preguntas es la misma.

Al estructurar nuestros ecosistemas de datos utilizando este vector cognitivo como base matemática, estamos cimentando nuestra infraestructura sobre el patrón de diseño más antiguo y depurado que poseemos como especie. Y la ventaja operativa de tomar esta decisión en el contexto actual es insuperable: cualquier Inteligencia Artificial moderna —entrenada devorando millones de textos redactados por cerebros humanos— va a asimilar este sistema de datos de forma nativa e inmediata. No hará falta invertir meses en enseñarle a la red neuronal cómo navegar las intrincadas tablas de tu base de datos corporativa; la IA ya comprenderá la topología de la información porque estará organizada bajo la misma lógica inmutable con la que aprendió a leer.
