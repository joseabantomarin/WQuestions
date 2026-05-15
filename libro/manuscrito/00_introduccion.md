# Introducción

## La pregunta que todos los niños saben hacer

Hay seis palabras que cualquier niño de cinco años usa con maestría: **quién, qué, dónde, cuándo, cómo, por qué**. Las usa antes de saber qué es un sustantivo o un verbo. Las usa cuando todavía confunde el ayer con el mañana, cuando todavía no entiende que hay países al otro lado del mar, cuando los números mayores a diez le suenan a magia. Las usa para entender el mundo porque son, casi literalmente, los andamios con los que el mundo se vuelve entendible.

Cuando ese niño crezca y se convierta en periodista, le enseñarán que toda noticia debe responder esas mismas seis preguntas, más una séptima — *cuánto* — que la formalidad adulta añadió para distinguir lo importante de lo trivial. En la escuela de periodismo de 1917 ya se enseñaba como "los 5W y 1H" [3]. Antes, los romanos del primer siglo se preguntaban *quis, quid, ubi, quando, cur, quomodo* [2]; antes, Aristóteles las usaba para evaluar la responsabilidad moral de las acciones humanas [1]. Las preguntas son más viejas que la lógica formal, más viejas que la escritura — son la forma en que la mente humana se ha relacionado con el mundo desde que tenemos memoria.

Este libro propone una idea sencilla pero con consecuencias profundas: **esas mismas preguntas pueden ser la arquitectura de toda información del mundo**, y reconocerlas como tal cambia radicalmente cómo construimos sistemas de inteligencia artificial.

## El problema concreto

Vamos a un caso real. María vive en una gran ciudad. Hace dos años se atendió en una clínica privada por dolores de cabeza. El año pasado, en un viaje al interior del país, una caída la llevó a un hospital regional, donde le recetaron analgésicos. Este mes está embarazada y quiere atenderse en una nueva clínica.

La nueva clínica necesita saber qué medicamentos toma María, qué alergias tiene, qué diagnósticos previos relevantes existen. La información está, pero está dispersa en tres sistemas que no se hablan. Cada uno tiene su esquema, sus nombres de columnas, su forma de codificar la información. Si la nueva clínica quiere ver la historia completa, alguien tiene que escribir un integrador. Y otro. Y otro. Y cuando el hospital regional cambie su sistema, todo se rompe.

María no es una abstracción. Es la realidad cotidiana de cualquier sistema de salud, de cualquier sistema bancario, de cualquier cadena de suministro, de cualquier organización que tenga que combinar información que vino de fuentes distintas.

El problema no es nuevo. Lleva décadas intentándose resolver. Se han probado **ontologías de dominio** (cada profesión define exhaustivamente su vocabulario, como CIDOC CRM para patrimonio cultural [4] o Biolink para biomedicina [5]), **estándares de intercambio** (HL7 FHIR en salud [6], XBRL en finanzas [7]), **enfoques de grafo abierto** (RDF [8], knowledge graphs), y **canonicalización post-hoc** (técnicas para reconciliar vocabularios después del hecho).

Cada enfoque resuelve parte del problema. Ninguno lo cierra completamente. La razón, sospecha este libro, es que todos atacan el síntoma — la diversidad de vocabularios — sin atacar la causa: que cada dominio se permite *inventar* su vocabulario en lugar de heredar uno común.

¿Y si hubiera un vocabulario común, anterior a cualquier dominio, suficientemente universal para que todos los dominios sean dialectos de él?

## Las preguntas como invariantes

Aquí está la apuesta del libro. Las preguntas-W — quién, qué, dónde, cuándo, cuánto, cuál, cómo, y una octava que llamaremos "clase" (qué tipo de cosa) — no son convenciones culturales. Son **invariantes cognitivos**: aparecen en todos los idiomas indoeuropeos, en todas las tradiciones de organización del conocimiento, en todas las etapas del desarrollo lingüístico infantil. Aristóteles las llamó las "circunstancias" del acto [1]. La gramática las llama "argumentos del verbo". El periodismo las llama 5W1H [3]. La lingüística formal moderna las llama "roles temáticos" [24].

Cuatro tradiciones distintas, mismo descubrimiento.

Si las preguntas son tan estables, tan universales, tan profundamente ligadas a cómo hablamos, ¿no sería razonable usarlas como esqueleto de cualquier sistema que pretenda almacenar y consultar información del mundo? ¿No sería razonable que la pregunta "¿quién?" tenga una única respuesta canónica en todo sistema — un eje donde viven los agentes — en lugar de inventar `vendedor`, `cliente`, `usuario`, `paciente`, `actor`, `perpetrador` en cada nuevo proyecto?

La apuesta es: sí. Y si funciona, las consecuencias son grandes.

## Lo que este libro hace

El libro construye, paso a paso, una arquitectura llamada **WQuestions** que toma las preguntas como ejes literales de un espacio multidimensional donde se ubican los hechos del mundo. Construye el modelo desde su intuición fundacional, lo formaliza con rigor matemático, lo refina contra siete dominios distintos (transporte aéreo, comercio minorista, servicios on-demand, historia clínica, composición musical, contratos legales, reacciones químicas, partidos deportivos), y lo conecta con doce tradiciones académicas e industriales relevantes.

Pero hace algo más, también: muestra que **el momento es 2026**. La explosión de los modelos de lenguaje grandes, el paradigma de *function calling* y la maduración de los *agentic workflows* han creado un contexto donde un esquema universal explícito ya no es una curiosidad académica. Es infraestructura necesaria.

Si los agentes de IA van a comunicarse con sistemas del mundo real — leer datos, registrar hechos, consultar información — necesitan una manera estructurada de hacerlo. Function calling ya provee la mecánica (JSON, schemas, tipos). Lo que falta es el **vocabulario semántico común** sobre el cual operar. Cada API expone hoy su propio JSON Schema; el agente tiene que aprender cada uno. Si todos los APIs hablaran preguntas, el agente las aprendería una sola vez.

WQuestions propone que las preguntas sean ese vocabulario.

## Para quién es este libro

Lo escribí pensando en tres lectores simultáneos. Si me sale bien, los tres encuentran lo suyo en cada capítulo.

**El lector con interés general** en cómo la IA se relaciona con el conocimiento humano encontrará en este libro una invitación a pensar más finamente lo que damos por sentado. Las preguntas son tan obvias que no las miramos. Pero cuando uno se detiene en ellas, descubre que organizar el mundo *así* en vez de *asá* tiene consecuencias enormes — para cómo aprendemos, cómo enseñamos, cómo razonamos, cómo construimos máquinas que también lo hagan.

**El profesional técnico** — arquitecto de información, ingeniero de datos, desarrollador de IA — encontrará una arquitectura concreta, validada, formalizada, con doce comparaciones rigurosas contra precedentes industriales y siete casos de aplicación detallados. Hay decisiones de diseño numeradas, convenciones explícitas, un lexicon ejemplar. Hay un camino claro de implementación.

**El investigador o académico** — en lingüística computacional, representación del conocimiento, semántica formal — encontrará un aporte teórico verificable. Cada decisión se contrasta contra la literatura existente: Barwise & Perry [11], Davidson [12], Gärdenfors [13], Yang & Hu [9], Mahmood [10], CIDOC CRM [4], FrameNet [14], VerbNet [15], Universal Schema [16], Biolink Model [5], Snodgrass [17], QUDT [18]. No hay reinvención silenciosa; cada préstamo se cita, cada diferencia se justifica.

El texto está **estratificado**: cada capítulo abre con narrativa accesible y profundiza con rigor formal en sus segundas mitades. Si solo te interesa la idea general, lee el primer tercio de cada capítulo. Si quieres la formalización, lee los apéndices técnicos. Si quieres construir, lee los capítulos de aplicación.

## El recorrido

El libro tiene seis partes.

**Parte I (capítulos 1–3) — Por qué las preguntas.** Establece el problema, traza la historia de las preguntas como invariantes, y revisa los intentos previos. Termina motivando por qué hace falta algo distinto.

**Parte II (capítulos 4–7) — Las ocho coordenadas.** Presenta uno por uno los ejes del modelo: quién, qué, dónde, cuándo, cuánto, cuál, cómo, clase. Cada uno con sus particularidades, sus trampas, sus convenciones.

**Parte III (capítulos 8–11) — Cómo funcionan juntas.** Construye el modelo a partir de los ejes: el hecho atómico como unidad, el espacio multidimensional como geometría, las situaciones reificadas como puntos, y las relaciones de "por qué" como conectores.

**Parte IV (capítulos 12–14) — Del lenguaje a los hechos.** Conecta el modelo con el lenguaje humano: el verbo como signatura, el lexicon como diccionario operativo, los casos lingüísticos difíciles (nominalización, modales, idiomas).

**Parte V (capítulos 15–18) — En la práctica.** Modela cinco dominios en detalle: ventas, taxis, historia clínica, y los cuatro casos de validación (música, química, fútbol, contratos). Es donde el lector profesional encontrará material directamente aplicable.

**Parte VI (capítulos 19–21 y conclusión) — Implicaciones y futuro.** Conecta WQuestions con LLMs y function calling, explora aplicaciones futuras, identifica lo que falta implementar, y cierra circularmente con la pregunta del comienzo: ¿qué significa, finalmente, que las preguntas sean coordenadas?

## Una nota sobre el método

Este libro es resultado de un proceso particular: una conversación sostenida entre un autor humano y un asistente de IA, donde la arquitectura de WQuestions se desarrolló iterativamente, dominio por dominio, fricción por fricción. Cada decisión de diseño se tomó porque algún caso real la forzó. Ninguna se inventó "por completitud teórica".

Eso debería ser, paradójicamente, una de las garantías más fuertes del libro: la arquitectura no se diseñó sobre papel y se aplicó a casos forzados; se descubrió viendo cómo siete dominios distintos pedían la misma cosa con palabras distintas.

El proceso mismo ilustra la tesis: una IA suficientemente capaz, en diálogo con un humano motivado, puede explorar el espacio conceptual de un problema con una velocidad y rigor que ningún equipo humano podría replicar. WQuestions es, en parte, el producto. En parte, la demostración. En parte, el llamado: tenemos que aprender a usar estas herramientas para pensar mejor, no solo para hablar más fluido.

Empezamos por la torre de Babel.
