# Capítulo 5 — Clase: el zócalo categórico (K)

## Lo que los pilares dejan sin decir

Volvamos un momento al final del capítulo anterior. Habíamos descripto los cuatro pilares — Q, O, L, T — y los habíamos visto trabajar juntos en la oración *"Marta le regaló un libro a su sobrino ayer en su casa."* La descripción cerró bien: cada palabra encontró su pilar.

Pero si miramos esa misma oración con un poco más de exigencia, descubrimos algo que los cuatro pilares **no nos dejan decir**.

Marta es una persona. Su sobrino también. Cuando preguntamos *"¿quién?"*, los dos son respuestas válidas — los dos viven en Q. Bien. Pero un sistema que quiere razonar sobre ellos necesita saber algo más: *que ambos son personas*. Necesita reconocer que `marta` y `sobrino_de_marta` comparten algo: pertenecen a la misma **categoría**.

El libro, por su parte, vive en O — es un objeto. Pero "libro" no es libro_007 en particular; "libro" es **el tipo** de cosas a las que ese objeto pertenece. El sistema tiene que ser capaz de distinguir entre el ejemplar concreto (este libro, con sus rajaduras y dedicatorias) y la categoría a la que pertenece (libro como tipo de objeto).

Los pilares son el inventario de individuos del mundo: este libro, esta persona, este lugar, este momento. Lo que falta es el inventario de **lo que esos individuos son**. Y eso vive en otro eje: **K**, el eje de las clases.

## Qué es K, exactamente

K (de *Kind*, *Klasse*, *Kategoria* — la inicial converge en todas las lenguas que importan) es el eje que aloja **tipos, categorías y conceptos abstractos**. Es donde viven *libro*, *persona*, *gol*, *receta*, *modelo de lenguaje*, *infarto agudo de miocardio*, *cliente*, *kilogramo*, *dólar*, *transformer*, *receta vegetariana*.

K es el **segundo zócalo** del modelo. Los pilares Q, O, L y T son el zócalo de lo concreto: cosas que existen en el mundo, con identidad propia y, en muchos casos, ubicación física. K es el zócalo de lo categórico: nombres genéricos bajo los cuales esos ejemplares se agrupan.

La distinción es sutil pero potente. Un *cocinero* concreto vive en Q (es Juan, con su DNI, su edad, su trayectoria). El concepto *cocinero* — la profesión, el rol, la categoría — vive en K. Una *llamada al modelo GPT* específica vive en O (tiene su ID, sus tokens, su latencia). El concepto *llamada a un modelo de lenguaje* vive en K. La ciudad concreta donde sucedió algo vive en L. La categoría *ciudad capital* vive en K.

Esta dualidad — instancias en los pilares, categorías en K — es lo que permite que un sistema **razone con generalidad**: que pueda decir "todos los pacientes con hipertensión" sin tener que enumerar cada paciente por nombre.

## Cuatro familias dentro de K

K no es un saco plano de etiquetas. Aloja al menos cuatro tipos distintos de entidades categóricas, y vale la pena distinguirlas.

**Tipos de objetos y eventos.** Cuando decimos *coche*, *cliente*, *gol*, *receta*, *llamada_API*, *infarto*, estamos hablando de tipos. La taza concreta está en O; el tipo *taza* está en K. La relación que ata los pilares con K se llama `instancia_de`:

```
(taza_007,    instancia_de, taza)                      ∈ M(O, K)
(messi,       instancia_de, jugador_de_futbol)         ∈ M(Q, K)
(lima,        instancia_de, ciudad_capital)            ∈ M(L, K)
(gpt_x,       instancia_de, modelo_de_lenguaje)        ∈ M(O, K)
```

Cualquier individuo de Q, O, L (y T, en algunos casos) puede tener una o más respuestas a "¿de qué es instancia?". Esa relación es lo que ata el grafo de hechos con el vocabulario categórico.

**Unidades de medida.** Las unidades — *kilogramo*, *segundo*, *token*, *dólar*, *milisegundo*, *grado_Celsius* — son categorías, no entidades concretas. No existe "un kilogramo específico" como existe una botella específica; lo que existe es el patrón de "ser un kilogramo", que se aplica a muchas cantidades. Las unidades viven en K, y su catálogo canónico universal es **QUDT** [18] (*Quantities, Units, Dimensions and Types Ontology*), que cataloga miles de unidades con sus dimensiones físicas, sus conversiones, y sus URIs estables. Veremos esto con más detalle cuando trabajemos el eje N en el próximo capítulo.

**Estados y valores enumerativos.** Cuando un atributo solo puede tomar un valor de una lista cerrada — *casado / soltero / viudo*, *aprobado / pendiente / rechazado*, *zurdo / diestro*, *encendido / apagado*, *real / planeado / cancelado* —, esos valores son categorías. No son números, no son textos libres: son etiquetas tomadas de un catálogo. Viven en K.

```
(paciente_042, estado_civil, casado)               ∈ P(Q, K)
(prestamo_017, estado,       aprobado)             ∈ P(O, K)
(llamada_042,  modo,         streaming)            ∈ P(O, K)
```

**Conceptos abstractos y nomenclaturas.** Diagnósticos médicos (CIE-10, SNOMED), categorías comerciales (códigos de producto, SKUs), géneros musicales, partidos políticos, especies biológicas, lenguajes de programación, arquitecturas de modelos de IA. Cualquier nomenclatura controlada de un dominio aterriza en K.

```
(diagnostico_017, codigo_cie10, "I21.9")           ∈ P(O, K)
(producto_088,    sku,          "coca_500ml")      ∈ P(O, K)
(cancion_yesterday, genero,     pop_rock)          ∈ P(O, K)
(modelo_gpt_x,    arquitectura, transformer)       ∈ P(O, K)
```

La línea común a las cuatro familias: **lo que vive en K no es un ejemplar único, es un patrón aplicable a muchos**.

## Por qué K necesita un eje propio

Una objeción razonable: ¿por qué no tratar las categorías como simples cadenas de texto dentro de las propiedades? *"casado"* podría ser el string `"casado"` y listo. ¿Hace falta otro eje?

La objeción no se sostiene, por tres razones que se acumulan.

**Razón 1: las categorías tienen estructura interna.** *Casado* no es solo una palabra. Es un concepto con propiedades. Tiene sinónimos en otros idiomas (*married*, *marié*, *verheiratet*). Tiene relaciones con otras categorías (*matrimonio* es un tipo de *vínculo legal*). Tiene contextos de aplicabilidad (en algunos países hay más estados civiles, como *unión civil*). Si "casado" es un string, esta estructura no es accesible. Si es un individuo en K, puede tener sus propios hechos:

```
(casado, sinonimo_en_ingles, "married")            ∈ M(K, K)
(casado, requiere,           matrimonio_legal)     ∈ M(K, K)
(casado, opuesto_de,         soltero)              ∈ M(K, K)
(casado, codigo_iso,         "M")                  ∈ P(K, K)
```

K, lejos de ser un saco plano, es una **red de conceptos**. Los individuos de K son ciudadanos de primera clase del modelo, con sus propios hechos. Esta propiedad va a ser decisiva cuando lleguemos a discutir cómo WQuestions se enchufa con las ontologías existentes.

![K como red de conceptos: las relaciones `subtipo_de` arman la jerarquía categórica e `instancia_de` ata cada individuo concreto a sus tipos. El motor puede inferir transitivamente.](../diagrams/png/09_k_red_conceptos.png)

**Razón 2: el vocabulario serio tiene autoridad externa.** Las categorías que se usan en sistemas profesionales no se inventan: vienen de fuentes externas con URIs estables. **QUDT** [18] da las unidades; **Schema.org** [30] da los tipos comerciales y web; **SNOMED** da los diagnósticos médicos; **ICAO** da los códigos de aeropuerto; **ISO 4217** da las monedas. Tratar la categoría como string ignora la URI. Tratarla como individuo de K permite guardar la URI como atributo:

```
(qudt_milliseg,  uri_canonica, "http://qudt.org/vocab/unit/MilliSEC")  ∈ P(K, K)
(snomed_infarto, uri_canonica, "http://snomed.info/id/22298006")        ∈ P(K, K)
```

Y eso permite que dos sistemas que hablan dialectos distintos se entiendan automáticamente: si ambos referencian la URI canónica, ambos saben que "ms" y "milisegundo" son la misma unidad.

**Razón 3: las consultas sobre categorías son habituales.** Las preguntas más útiles de un sistema cruzan categorías: *"todas las recetas vegetarianas que se preparen en menos de 30 minutos"*, *"todos los modelos de lenguaje de arquitectura transformer entrenados después de 2024"*, *"todos los pacientes con diagnóstico de la familia CIE-10 I.20 a I.25"*. Si las categorías son strings, esas consultas son frágiles (mayúsculas, sinónimos, ortografía). Si son individuos de K con jerarquías y atributos, las consultas se vuelven exactas y composables.

## Dos relaciones canónicas: `instancia_de` y `subtipo_de`

Dos relaciones atraviesan K de forma estructural y conviene tenerlas presentes desde ya.

**`instancia_de`** es la relación más usada del modelo. Ata cada individuo de los pilares a su tipo o tipos (un individuo puede ser instancia de varios a la vez):

```
(messi, instancia_de, jugador_de_futbol)        ∈ M(Q, K)
(messi, instancia_de, capitan_de_seleccion)     ∈ M(Q, K)
(messi, instancia_de, persona_humana)           ∈ M(Q, K)
(messi, instancia_de, ganador_balon_de_oro)     ∈ M(Q, K)
```

Las cuatro instancias no compiten ni se anulan. Coexisten. El sistema puede consultar por cualquiera y devolver al sujeto.

**`subtipo_de`** es la relación que estructura jerárquicamente al propio K. Permite construir taxonomías sin salir del eje:

```
(jugador_de_futbol,   subtipo_de, atleta_profesional)               ∈ M(K, K)
(atleta_profesional,  subtipo_de, persona_humana)                   ∈ M(K, K)
(modelo_de_lenguaje,  subtipo_de, modelo_de_aprendizaje_automatico) ∈ M(K, K)
(modelo_transformer,  subtipo_de, modelo_de_lenguaje)               ∈ M(K, K)
```

Con `instancia_de` y `subtipo_de` declaradas, el motor puede hacer **inferencia transitiva básica**: si Messi es instancia de jugador_de_futbol, y jugador_de_futbol es subtipo de atleta_profesional, entonces Messi es (transitivamente) atleta_profesional. Esto es lo que las ontologías llaman *closure* o cierre transitivo, y es la mecánica más simple — y más útil — del razonamiento sobre categorías.

## K como zócalo para las ontologías existentes

La promesa más fuerte de K es que **no obliga a reinventar nada**. Las ontologías serias que ya existen — Schema.org, QUDT, SNOMED, CIDOC CRM, Biolink — se mapean a K como subconjuntos de categorías con sus relaciones internas. WQuestions no compite con ellas: **las abraza**.

La estrategia, en tres niveles:

**Nivel 1: importar URIs canónicas.** Para cada categoría externa que se use, el sistema guarda su URI como atributo:

```
(infarto_miocardio_agudo) ∈ K
  uri_snomed   : http://snomed.info/id/22298006
  uri_icd10    : I21
  etiqueta_es  : "infarto agudo de miocardio"
  etiqueta_en  : "acute myocardial infarction"
```

Cuando dos sistemas distintos referencian la misma URI, el matcheo es automático. No hace falta un mapeo ad-hoc por par de sistemas.

**Nivel 2: mapear vocabulario de dominio.** Cada dominio puede definir aliases — *dialectos* — que apunten al canónico. Una clínica que llama "IAM" al infarto agudo registra:

```
(IAM_clinica_norte, alias_de, infarto_miocardio_agudo)   ∈ M(K, K)
```

Y todas las búsquedas por "IAM" en esa clínica encuentran al concepto canónico. Vale la pena adelantarlo: este principio se va a formalizar como una decisión de diseño completa (D8) cuando lleguemos a la parte sobre el lexicon — la idea es que **el usuario nunca toca etiquetas canónicas**, usa las suyas y el sistema traduce. K es la pieza que hace esto posible.

**Nivel 3: federar conceptos equivalentes.** Cuando dos ontologías describen el mismo concepto con URIs distintas, K las marca como equivalentes:

```
(snomed_infarto, equivalente_a, icd10_I21)               ∈ M(K, K)
```

Sobre el tiempo, K se convierte en una **red de equivalencias** entre ontologías heterogéneas — el "puente" que las ontologías de dominio nunca construyeron por sí solas.

## Cinco dominios, cinco vistas de K

K se vuelve concreto cuando se ve aplicado a dominios distintos. Los cuatro habituales más el caso de IA:

- **Receta**: tipos de plato (*entrada*, *plato_principal*, *postre*), técnicas (*saltear*, *hervir*, *hornear*), origen cultural (*siciliano*, *yucateco*, *japonés*), dietas (*vegetariano*, *vegano*, *sin_gluten*). Schema.org/Recipe provee buena parte; las técnicas y orígenes culturales pueden bajarse de Wikidata [32].

- **Gol de fútbol**: tipos de gol (*de cabeza*, *de tiro libre*, *de penal*, *en contra*), partes del cuerpo (*derecha*, *izquierda*, *cabeza*), zonas de la cancha (*área grande*, *fuera_del_área*). Algunas vienen de catálogos de la FIFA; otras son vocabulario emergente del análisis deportivo.

- **Canción**: géneros (*rock*, *pop*, *bossa_nova*), tonalidades (*sol_mayor*, *re_menor*), instrumentos (*guitarra_acústica*, *piano*). MusicBrainz tiene catálogos muy completos accesibles vía API.

- **Noticia política**: instituciones (*ministerio*, *partido_político*, *congreso*), tipos de acto administrativo (*decreto*, *ley*, *resolución*), niveles de gobierno (*nacional*, *regional*, *municipal*).

- **Llamada a un modelo de lenguaje**: arquitecturas (*transformer*, *mamba*, *mixture_of_experts*), familias (*GPT*, *Claude*, *Gemini*, *Llama*), tipos de tarea (*resumir*, *clasificar*, *traducir*, *generar_código*), modos (*síncrono*, *streaming*, *batch*). Es un caso especialmente interesante porque el vocabulario está emergiendo aún: cada laboratorio empuja el suyo, y K es el lugar donde — eventualmente — esas convenciones convergerán.

## D4: la plantilla y la instancia

Hay una decisión de diseño que rige la frontera entre K y los pilares (sobre todo entre K y O), y que vale la pena hacer explícita.

> **D4 — En K viven los conceptos atemporales y categóricos; en O (y los demás pilares) viven las entidades creadas, situadas, instanciadas.**

La pregunta operativa: *¿este individuo tiene una fecha de creación, una historia, una ubicación específica?* Si sí, está en O (o el pilar correspondiente). Si no, está en K.

- *La receta tradicional del risotto a la milanesa* (un patrón replicable, sin fecha de creación específica) → K
- *La preparación del risotto del domingo pasado en mi cocina* → O (es una instancia concreta del patrón en K)
- *El modelo GPT-X-2026-05 lanzado el 14 de mayo* (tiene fecha de lanzamiento, parámetros específicos, peso entrenado) → O
- *El concepto general "modelo de lenguaje transformer"* → K

Esto produce una arquitectura recurrente: una **plantilla en K** + una **instancia en O**, conectadas por `instancia_de`. La receta abstracta vive como tipo; cada vez que se prepara, se crea una situación-instancia con factor de escala (cuántas porciones, qué sustituciones, qué hora).

```
(receta_risotto_milanesa) ∈ K           // la receta abstracta
  ingrediente_base : arroz_arborio (porción base 200 g)
  paso             : ...

(preparacion_2026_05_14)  ∈ O           // mi cena del 14 de mayo
  instancia_de  : receta_risotto_milanesa
  factor_escala : 2 (preparé para 4 en lugar de 2)
  cocinero      : juan
  cuando        : 2026-05-14T20:30:00
```

Esa dualidad — plantilla atemporal en K, ocurrencia situada en O — es uno de los patrones de modelado más usados en aplicaciones reales y aparecerá repetidamente en los capítulos de la Parte V.

![D4 en acción: la receta abstracta vive como tipo en K; la preparación concreta del 14 de mayo vive como instancia en O, con factor de escala, fecha, lugar y cocinero específicos.](../diagrams/png/10_plantilla_instancia.png)

## Resumen del capítulo

K es el segundo zócalo del modelo, complementario a los pilares concretos (Q, O, L, T):

- Aloja **tipos, unidades, estados enumerativos y nomenclaturas**.
- Tiene **estructura interna**: sus individuos pueden tener sus propios hechos.
- Aterriza las **ontologías existentes** sin reinventarlas — Schema.org, QUDT, SNOMED, CIDOC CRM, Biolink.
- Habilita inferencia transitiva básica vía `instancia_de` y `subtipo_de`.
- Marca la frontera D4 entre **plantilla atemporal** y **instancia situada**.

Con K presentado, el universo de individuos del modelo está prácticamente completo. Q, O, L, T y K son los cinco ejes que alojan **a los individuos del mundo y sus categorías**. Falta uno más en este registro: **N**, el eje de las magnitudes y los números.

## Lo que viene

El próximo capítulo retoma una pregunta que ya rozamos en el capítulo 4 cuando vimos la oración extendida sobre el regalo de Marta — *un libro de cuentos que costó treinta dólares*. La pregunta es: ¿cómo modelar bien la cantidad? Y la respuesta, lejos de ser una trivialidad sobre números, va a obligarnos a usar K de forma central: **todo número viene con una unidad, y las unidades viven en K**.

Es exactamente por esa razón que K tenía que presentarse antes que N.
