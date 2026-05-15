# Capítulo 7 — Clase: el eje de los tipos (K)

## El sustantivo que es y el adjetivo que clasifica

Cuando uno señala una taza sobre una mesa y dice "esto es una taza", está haciendo dos cosas a la vez. Por un lado, está apuntando a un objeto concreto que existe en el mundo — una taza específica, con sus rajaduras, su color, su historia de cafés. Por otro, está aplicando una **categoría**: la palabra "taza" no es ese objeto, es un nombre para un tipo del cual ese objeto es un ejemplar.

El objeto vive en O. La categoría vive en otro lado. Ese otro lado es el eje **K**.

K (de *Kind*, *Kategoria*, *Klasse* — todas convergen en la misma inicial) es el eje que aloja **tipos, categorías y conceptos abstractos**. Es donde viven *taza* y *gol* y *receta* y *infarto agudo de miocardio* y *cliente* y *modelo de lenguaje*. No los ejemplares concretos — esos están en O —, sino los nombres genéricos bajo los cuales los ejemplares se agrupan.

K es, en una primera aproximación, el eje **menos visible** del modelo en el día a día. Casi todas las consultas se hacen sobre instancias (este gol, esta receta, esta llamada al modelo). Pero K es, paradójicamente, el eje que **más trabajo hace** en sistemas reales. Es donde se enchufan las ontologías existentes — Schema.org, QUDT, CIDOC CRM, CHEBI, Biolink —, donde se definen las unidades de medida, donde viven las nomenclaturas de dominio. Si los otros ejes son los lugares donde se ubican los hechos, K es el **vocabulario común** que esos hechos comparten para no caer otra vez en la torre de Babel del capítulo 1.

Este capítulo recorre K en tres pasos: qué tipo de cosas vive ahí, por qué eso merece un eje propio (y no un atributo dentro de cada hecho), y cómo K conecta a WQuestions con el mundo de las ontologías existentes en lugar de competir con ellas.

## Qué vive en K

K aloja todo individuo cuyo modo de existencia es **categórico**, no instancial. Cuatro grandes familias:

**Tipos de objetos y eventos.** Cuando decimos *coche*, *cliente*, *receta*, *gol*, *llamada_API*, *infarto*, estamos hablando de tipos. La taza concreta está en O; el concepto *taza* está en K. La relación entre ambos es la relación canónica `instancia_de`, que va de cualquier eje hacia K:

```
(taza_007, instancia_de, taza)                 ∈ M(O, K)
(messi,    instancia_de, jugador_de_futbol)    ∈ M(Q, K)
(lima,     instancia_de, ciudad_capital)       ∈ M(L, K)
(gpt_x,    instancia_de, modelo_de_lenguaje)   ∈ M(O, K)
```

Todo individuo de V (excepto los puros valores de N y T) tiene una o más respuestas a "¿de qué es instancia?". Esa relación es lo que ata el grafo de hechos con el vocabulario categórico.

**Unidades de medida.** Como vimos en el capítulo 5, las unidades — *kilogramo*, *segundo*, *token*, *dólar*, *milisegundo*, *grado_Celsius* — son tipos, no entidades concretas. No existe "un kilogramo específico" como existe una botella específica; lo que existe es el patrón de "ser un kilogramo", que se aplica a muchas cantidades. Las unidades viven en K, y su catálogo canónico es QUDT [18].

**Estados y valores enumerativos.** Cuando un atributo solo puede tomar un valor de una lista cerrada — *casado / soltero / viudo*, *aprobado / pendiente / rechazado*, *zurdo / diestro*, *encendido / apagado*, *sano / enfermo* —, esos valores son tipos. No son números, no son textos libres: son etiquetas tomadas de un catálogo. Viven en K.

```
(paciente_042, estado_civil, casado)         ∈ P(Q, K)
(prestamo_017, estado,       aprobado)       ∈ P(O, K)
(messi,        pierna_habil, zurda)          ∈ P(Q, K)
```

**Conceptos abstractos y nomenclaturas.** Diagnósticos médicos (CIE-10, SNOMED), categorías comerciales (códigos de producto, SKUs), géneros musicales, partidos políticos, especies biológicas, lenguajes de programación, marcos legales. Cualquier nomenclatura controlada de un dominio aterriza en K.

```
(diagnostico_017, codigo_cie10, "I21.9")           ∈ P(O, K)
(producto_088,    sku,          "coca_500ml")      ∈ P(O, K)
(cancion_yesterday, genero,     pop_rock)          ∈ P(O, K)
(modelo_gpt_x,    arquitectura, transformer)       ∈ P(O, K)
```

La línea conceptual común a las cuatro familias: **lo que vive en K no es un ejemplar único, es un patrón aplicable a muchos**.

## Por qué un eje propio

Hay una objeción natural: ¿por qué no tratar las categorías como simples cadenas de texto dentro de las propiedades, sin necesidad de un eje aparte? Después de todo, "casado" podría ser el string `"casado"` y listo.

La objeción no funciona, por tres razones que se acumulan.

**Razón 1: las categorías tienen estructura interna.** *Casado* no es solo una palabra: es un concepto con propiedades. Tiene sinónimos en otros idiomas (*married*, *marié*, *verheiratet*), tiene relaciones con otras categorías (*matrimonio* es un tipo de *vínculo legal*), tiene contextos de aplicabilidad (en algunos países hay más estados civiles, como *unión civil*). Si "casado" es solo un string, esta estructura no es accesible. Si es un individuo en K, puede tener sus propios hechos:

```
(casado, sinonimo_en, en, "married")                  ∈ M(K, K)
(casado, requiere,    matrimonio_legal)               ∈ M(K, K)
(casado, opuesto_de,  soltero)                        ∈ M(K, K)
(casado, codigo_iso,  "M")                            ∈ P(K, K)
```

K, lejos de ser un saco plano de etiquetas, es una **red de conceptos**. Esta es la nota explícita del modelo: los individuos de K son ciudadanos de primera clase, con sus propios hechos.

**Razón 2: el vocabulario tiene autoridad externa.** Las categorías serias vienen, en la mayoría de los dominios, de fuentes externas: QUDT para unidades, Schema.org para tipos comerciales, SNOMED para diagnósticos, ICAO para códigos de aeropuerto, ISO 4217 para monedas. Esas fuentes asignan URIs estables a cada categoría. Tratar la categoría como string ignora la URI. Tratarla como individuo de K permite guardar la URI como atributo:

```
(qudt_milliseg, uri_canonica, "http://qudt.org/vocab/unit/MilliSEC")  ∈ P(K, K)
(snomed_infarto, uri_canonica, "http://snomed.info/id/22298006")      ∈ P(K, K)
```

Y eso permite que dos sistemas que hablan idiomas distintos se entiendan automáticamente: si ambos referencian la URI de QUDT, ambos saben que "ms" y "milisegundo" son lo mismo.

**Razón 3: la consulta sobre categorías es habitual.** Las preguntas más útiles de un sistema cruzan categorías: "todas las recetas vegetarianas que se preparen en menos de 30 minutos", "todos los modelos de lenguaje de arquitectura transformer entrenados después de 2024", "todos los pacientes con diagnóstico de la familia CIE-10 I.20 a I.25". Si las categorías son strings, esas consultas son fragiles (mayúsculas, sinónimos, ortografía). Si son individuos de K con jerarquías y atributos, las consultas se vuelven exactas y composables.

## La relación canónica: `instancia_de`

Una sola relación atraviesa K transversalmente: `instancia_de`. Es la relación más usada del modelo, porque ata cada individuo a su tipo (o sus tipos — un individuo puede ser instancia de varios).

Su signatura es la más permisiva del modelo:

```
instancia_de : V → K
```

Cualquier eje hacia K. Cualquier individuo de Q, O, L, e incluso de K mismo (un tipo puede ser instancia de un meta-tipo), puede tener una `instancia_de`.

La multiplicidad importa: un individuo puede ser instancia de varios tipos a la vez, no necesariamente jerárquicos:

```
(messi, instancia_de, jugador_de_futbol)      ∈ M(Q, K)
(messi, instancia_de, capitan_de_seleccion)    ∈ M(Q, K)
(messi, instancia_de, persona_humana)          ∈ M(Q, K)
(messi, instancia_de, ganador_balon_de_oro)    ∈ M(Q, K)
```

Estas instancias no compiten entre sí ni anulan la una a la otra. Coexisten. El sistema puede consultar por cualquiera de ellas y devolver al sujeto.

Hay otra relación canónica fundamental que vive enteramente en K: **`subtipo_de`**. Permite que K se estructure jerárquicamente cuando hace falta.

```
(jugador_de_futbol,   subtipo_de, atleta_profesional)      ∈ M(K, K)
(atleta_profesional,  subtipo_de, persona_humana)          ∈ M(K, K)
(modelo_de_lenguaje,  subtipo_de, modelo_de_aprendizaje_automatico)  ∈ M(K, K)
(modelo_transformer,  subtipo_de, modelo_de_lenguaje)      ∈ M(K, K)
```

Con `subtipo_de` y `instancia_de` definidas, el motor puede hacer inferencia básica: si Messi es instancia de jugador_de_futbol, y jugador_de_futbol es subtipo de atleta_profesional, entonces Messi es (transitivamente) atleta_profesional. Esta inferencia es lo que las ontologías llaman *closure* o cierre transitivo.

## Cómo K se conecta con las ontologías existentes

La promesa más fuerte de K es que **no obliga a reinventar nada**. Cualquier ontología existente — Schema.org, QUDT, SNOMED, CIDOC CRM, Biolink — se mapea a K como un subconjunto de categorías con sus relaciones internas. WQuestions, en K, abraza al ecosistema en lugar de competir con él.

La estrategia operativa, en tres niveles:

**Nivel 1: importar URIs canónicas.** Para cada categoría externa que se use, el sistema guarda su URI como atributo. Cuando dos sistemas distintos referencian la misma URI, el matcheo es trivial.

```
(infarto_miocardio_agudo) ∈ K
  uri_snomed   : http://snomed.info/id/22298006
  uri_icd10    : I21
  etiqueta_es  : "infarto agudo de miocardio"
  etiqueta_en  : "acute myocardial infarction"
```

**Nivel 2: mapear vocabulario de dominio.** Cada dominio puede definir aliases — *dialectos* — que apunten al canónico. Una clínica que llama "IAM" al infarto agudo registra:

```
(IAM_clinica_norte, alias_de, infarto_miocardio_agudo)  ∈ M(K, K)
```

Y todas las búsquedas por "IAM" en esa clínica encuentran al concepto canónico. Como vimos en la decisión D8, el usuario nunca toca etiquetas canónicas: usa las suyas, y el sistema las traduce.

**Nivel 3: federar conceptos.** Cuando dos ontologías describen el mismo concepto con URIs distintas, K las marca como equivalentes:

```
(snomed_infarto, equivalente_a, icd10_I21)  ∈ M(K, K)
```

Esto convierte a K, sobre el tiempo, en una **red de equivalencias** entre ontologías heterogéneas — el "puente" que las ontologías de dominio nunca construyeron por sí solas.

## K en cuatro dominios

Los cuatro dominios de referencia, vistos a través de K:

- **Receta**: tipos de plato (*entrada*, *plato_principal*, *postre*), técnicas (*saltear*, *hervir*, *hornear*), origen cultural (*sicilianos*, *yucateco*, *japonés*), dietas (*vegetariano*, *vegano*, *sin_gluten*). Schema.org/Recipe provee gran parte; las técnicas y orígenes culturales pueden bajarse de Wikidata.
- **Gol de fútbol**: tipos de gol (*de cabeza*, *de tiro libre*, *de penal*, *en contra*), partes del cuerpo (*derecha*, *izquierda*, *cabeza*), zonas de la cancha (*área grande*, *fuera_del_área*). Algunas vienen de catálogos de la FIFA; otras son vocabulario emergente del análisis deportivo.
- **Canción**: géneros (*rock*, *pop*, *bossa_nova*), tonalidades (*sol_mayor*, *re_menor*), instrumentos (*guitarra_acústica*, *piano*). MusicBrainz tiene catálogos muy completos.
- **Llamada a un LLM**: arquitecturas (*transformer*, *mamba*, *MoE*), familias (*GPT*, *Claude*, *Gemini*, *Llama*), tipos de tarea (*resumir*, *clasificar*, *traducir*, *generar_código*), modos (*sync*, *streaming*, *batch*). El vocabulario está emergiendo aún; cada laboratorio empuja el suyo. Es un caso donde K va a tener que normalizar mucho los próximos años.

## Una decisión que merece nombre: D4

K y O son los dos ejes que más fácilmente se confunden. ¿Una receta es un O o un K? ¿Un modelo de lenguaje es un O o un K? ¿Una venta es un O o un K? La respuesta no es siempre obvia y depende del enfoque.

La decisión de diseño que rige esto es D4:

> **D4 — En K viven los conceptos atemporales y categóricos; en O viven las entidades creadas, situadas o eventos concretos.**

La pregunta operativa: *¿este individuo tiene una fecha de creación, una historia, una ubicación específica?* Si sí, está en O. Si no, está en K.

- *La receta tradicional de la abuela* (un patrón replicable, sin fecha de creación específica) → K
- *La preparación de la receta del domingo pasado en mi cocina* → O (es una instancia concreta del patrón en K)
- *El modelo GPT-X-2026-05 lanzado el 14 de mayo* (tiene fecha de lanzamiento, parámetros específicos, peso entrenado) → O
- *El concepto general "modelo de lenguaje transformer"* → K

Esto produce una arquitectura recurrente en sistemas reales: una **plantilla** en K + una **instancia** en O, conectadas por `instancia_de`. La receta abstracta vive como tipo; cada vez que se prepara, se crea una situación-instancia con factor de escala (cuántas porciones, qué sustituciones, qué hora).

```
(receta_risotto_milanesa) ∈ K           // la receta abstracta
  ingrediente : arroz_arborio (porción base 200 g)
  paso        : ...

(preparacion_2026_05_14)  ∈ O           // mi cena del 14 de mayo
  instancia_de : receta_risotto_milanesa
  factor_escala : 2 (preparé para 4 en lugar de 2)
  cocinero     : juan
  cuando       : 2026-05-14T20:30:00
```

Esa dualidad — plantilla atemporal en K, ocurrencia situada en O — es uno de los patrones más usados en aplicaciones reales y aparecerá repetidamente en los capítulos de la Parte V.

## Resumen: K, el eje silencioso pero indispensable

Cerramos el recorrido de los ocho ejes. K es el último, y conviene que la imagen final que quede del modelo no sea de un esqueleto rígido con etiquetas opacas sino de una **estructura viva** donde:

- Los hechos del mundo viven como ejemplares concretos en Q, O, L, T y N.
- El vocabulario que los nombra vive en K, conectado a ontologías existentes.
- Las propiedades funcionales en P y las relaciones no funcionales en M atraviesan las dos capas — la de instancias y la de tipos — sin distinción operativa.
- Las URIs canónicas y los aliases de dominio hacen que K sea **invisible para el usuario** pero **explícito para el sistema**.

Es la combinación lo que da el efecto: el usuario habla su idioma, las máquinas se entienden por debajo gracias a K, y los hechos quedan accesibles a cualquier consumidor — humano o IA — que sepa preguntar por preguntas.

## Lo que viene

La Parte II termina con este capítulo. Hemos visto los **ocho ejes** del modelo:

- **Q** (quién) — agentes
- **O** (qué) — objetos, eventos, situaciones
- **L** (dónde) — lugares
- **T** (cuándo) — momentos
- **N** (cuánto) — magnitudes
- **P** (cuál) — propiedades funcionales
- **M** (cómo) — relaciones no funcionales
- **K** (clase) — tipos y categorías

A partir del próximo capítulo, dejamos atrás la presentación de los ejes uno por uno y pasamos a construir el modelo con ellos en conjunto. La Parte III se ocupa de **cómo funcionan juntos**: el hecho atómico como unidad mínima, el espacio multidimensional como geometría implícita, las situaciones reificadas como puntos de articulación, y las relaciones de "por qué" como el conector argumentativo que une todo. Es donde el modelo, hasta ahora desplegado en piezas, se revela como una arquitectura.

El próximo capítulo, el 8, empieza por la pieza más pequeña: el **hecho atómico**.
