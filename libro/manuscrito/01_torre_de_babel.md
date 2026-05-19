# Capítulo 1 — La torre de Babel de las ontologías

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

## ¿Por qué nos cuesta tanto evitarlo?

Si el problema de los silos de datos lleva décadas costando miles de millones de dólares en integraciones fallidas, la pregunta obligada es: ¿por qué los ingenieros no lo han resuelto aún?

La realidad es que la industria sí lo ha intentado, y con herramientas brillantes. Históricamente, el esfuerzo por unificar los datos se ha canalizado a través de cuatro grandes estrategias. Entender por qué fracasaron en crear un idioma verdaderamente universal es clave para nuestro modelo:

**El primer camino: Las ontologías de dominio.** 
La estrategia aquí fue agrupar a los mayores expertos de una industria y pedirles que escribieran un diccionario perfecto y definitivo para su sector. Así nacieron estándares magníficos como CIDOC CRM `[4]` para los museos, el Biolink Model `[5]` para la genética, IFC `[19]` para la arquitectura y XBRL `[7]` para las finanzas. 
¿Por qué fallan? Porque resuelven la comunicación interna, pero construyen muros hacia el exterior. Una ontología diseñada para clasificar pinturas del Renacimiento no tiene el vocabulario para describir la estructura química de los pigmentos que la componen. Cuando dos ciencias se cruzan, las ontologías de dominio se vuelven lenguajes extranjeros entre sí.

**El segundo camino: Los estándares de intercambio.** 
En lugar de obligar a todos a organizar sus bases de datos de la misma manera, este enfoque propuso crear un "formato de envío" estándar. Es decir, cada hospital o banco guarda sus datos como quiera internamente, pero cuando necesiten enviarse un mensaje, deben traducirlo temporalmente a un formato común, como HL7 FHIR en salud `[6]`, EDI en comercio `[20]` o ISO 20022 en la banca `[21]`.
¿Por qué fallan? Porque funcionan como un traductor automático que se usa solo para el transporte. Una vez que el sistema receptor recibe el paquete de datos, debe desarmarlo y traducirlo de nuevo a su complejo esquema interno para poder buscar o analizar la información. No hay unificación real, solo un servicio de mensajería estandarizado.

**El tercer camino: Los grafos abiertos.** 
Tecnologías como RDF `[8]`, OWL `[22]` y los *knowledge graphs* propusieron una idea revolucionaria: destruir las tablas rígidas y representar toda la información mundial como frases simples de tres partes (*sujeto - relación - objeto*). Por ejemplo: "Ana - trabaja_en - Empresa X". La idea era tener una pizarra infinita donde cualquiera pudiera conectar cualquier dato.
¿Por qué fallan? Porque al dar libertad absoluta, la torre de Babel simplemente se mudó de lugar. En una pizarra libre, un programador de España usa la relación `empleado_de`, uno de EE.UU. usa `worksFor`, y otro usa `colabora_con`. Al final del día, la máquina no sabe que los tres hablan de lo mismo, obligando a los ingenieros a imponer, nuevamente, un diccionario estricto por encima de la pizarra.

**El cuarto camino: La canonicalización post-hoc.** 
*Canonicalizar* significa tomar muchas formas distintas de decir algo (como "Bs. As.", "BUE" y "Buenos Aires") y forzarlas hacia un único valor oficial. "Post-hoc" significa que este proceso se hace *después* de que el caos ya ocurrió. Plataformas como OpenIE `[23]` o los sistemas de limpieza de datos intentan leer millones de registros desordenados y unificarlos a la fuerza mediante algoritmos de inteligencia artificial.
¿Por qué fallan? Porque limpiar datos a posteriori funciona cuando cruzas tres o cuatro bases de datos. Cuando intentas aplicar modelos probabilísticos para reconciliar la información de cincuenta sistemas corporativos distintos, el esfuerzo computacional y el margen de error se vuelven inmanejables.

![Los cuatro caminos previos para resolver la torre de Babel y la dimensión que cada uno deja sin resolver.](../diagrams/png/03_cuatro_intentos_previos.png)

Cada uno de estos caminos fue un triunfo técnico en su área, pero ninguno atacó la enfermedad de fondo; solo aliviaron los síntomas.

## La causa de todo el problema

La raíz estructural de esta torre de Babel —y el punto de partida de este libro— es que en todos los intentos anteriores **hemos permitido que cada sector invente su propia forma de entender la realidad desde cero**. 

La ingeniería médica no hereda ninguna estructura de la contabilidad comercial; el comercio no comparte bases con el derecho penal; y la educación diseña bases de datos que no se hablan con el urbanismo. Cada industria construye su pirámide desde la base utilizando planos distintos, y luego nos sorprendemos cuando resulta carísimo contratar programadores para tender puentes colgantes entre las cimas de esas pirámides.

¿Qué pasaría si la solución a este caos fuera anterior y mucho más simple que cualquier diseño de base de datos? ¿Qué pasaría si, mucho antes de que existieran los hospitales, los bancos o el comercio internacional, la humanidad ya hubiera desarrollado un esquema cognitivo universal que nadie puede evitar utilizar?

La hipótesis de este libro es que esa estructura maestra ya existe, y está codificada en la forma en que hablamos y pensamos todos los días.

## La pista que estaba a la vista

Regresemos al ejemplo de la compra de la camiseta. Si detuviéramos a cualquier persona en la calle —sin conocimientos de bases de datos, ontologías o código SQL— y le pidiéramos que nos describa ese hecho, su respuesta natural sería algo muy parecido a esto:

> "*Una clienta* (**quién**) *compró* (**qué**) *una camiseta* (**qué**) *en la tienda del centro* (**dónde**) *esta tarde* (**cuándo**) *por casi cincuenta dólares* (**cuánto**)."

Cualquier ser humano es capaz de producir una descripción **estructurada, completa y combinable** sin el menor esfuerzo. Esto ocurre porque nuestra mente no percibe el mundo como un bloque de texto desordenado ni como tablas de Excel; nuestro cerebro descompone automáticamente cualquier evento de la realidad utilizando un conjunto muy reducido de preguntas fundamentales.

Que todos pensemos así no es una casualidad evolutiva. A lo largo de la historia, cuatro grandes áreas del conocimiento humano, trabajando de forma independiente y separadas por siglos, llegaron exactamente a la misma conclusión estructural:

1.  **Aristóteles (Siglo IV a. C.):** En su texto *Ética a Nicómaco*, el filósofo griego analizó la moralidad de las acciones humanas `[1]`. Para determinar si un acto fue voluntario o un accidente, Aristóteles dedujo que era matemáticamente imposible entender el contexto sin aislar a la persona (quién), el acto (qué), el instrumento (con qué) y la motivación (por qué).
2.  **Los juristas romanos (Siglo I):** Al sentar las bases del derecho, formalizaron las llamadas *circumstantiae* (las circunstancias del delito): *quis, quid, ubi, quando, cur, quomodo* (quién, qué, dónde, cuándo, por qué y cómo) `[2]`. Sin responder a este esqueleto, ninguna argumentación legal era válida.
3.  **El periodismo norteamericano (Finales del Siglo XIX):** En las primeras escuelas de comunicación se estandarizó la regla de las **5W1H** (*who, what, where, when, why, how*) `[3]`. Se comprobó que, si una noticia omitía una sola de estas dimensiones en su primer párrafo, el lector humano sentía intuitivamente que la historia estaba incompleta.
4.  **La lingüística formal (Mediados del Siglo XX):** Los científicos del lenguaje descubrieron que esta estructura no depende de la cultura. Al estudiar cientos de idiomas, categorizaron estos espacios mentales bajo el concepto de **roles temáticos** `[24]`. Comprobaron que, sin importar si hablas quechua, mandarín o inglés, tu cerebro distribuye automáticamente a los actores de una oración en casilleros fijos: el agente (quién), la locación (dónde), la temporalidad (cuándo).

La filosofía, el derecho, el periodismo y la neurociencia lingüística descubrieron el mismo mecanismo cognitivo. Esa convergencia histórica es la pista arquitectónica más valiosa que tenemos.

## La apuesta arquitectónica

Si este vector de preguntas es la forma estable y universal en la que la mente procesa los hechos, el paso lógico más inteligente que podemos dar en la ingeniería de software es utilizar este mismo esquema como la estructura central de nuestras bases de datos.

La propuesta fundacional de este libro se resume en este principio:

> **Existe un conjunto reducido y estable de preguntas primarias —aproximadamente ocho— que posee la capacidad descriptiva suficiente para modelar y organizar cualquier hecho factual, en cualquier dominio industrial y en cualquier idioma. Al diseñar los esquemas de bases de datos alrededor de estas coordenadas cognitivas, en lugar de utilizar terminologías especializadas, se neutraliza de raíz la fragmentación semántica de los datos.**

La validación ya está hecha —los ocho dominios del prototipo que presentaremos lo demuestran—, y a partir de este punto, la ingeniería de sistemas habilita una optimización estructural en dos frentes masivos. 

Primero, conectar sistemas informáticos dejará de ser una pesadilla artesanal. Hoy en día, cada vez que dos empresas necesitan cruzar información, hay que programar "puentes" manuales a medida para traducir los datos de un lado al otro. Con este modelo, eso se acaba. Al apoyarnos todos en este mismo esqueleto de preguntas, las integraciones dejan de ser proyectos complejos y se vuelven conexiones directas, casi como usar un adaptador universal.

Segundo —y esto es quizá lo más potente—, las inteligencias artificiales actuales van a poder entender la información de cualquier empresa a la primera. Piénsalo de este modo: los modelos como ChatGPT aprendieron a razonar leyendo textos humanos, y nuestro lenguaje natural ya viene ordenado instintivamente por *quién*, *qué*, *dónde* y *cuándo*. Si estructuramos los datos de un negocio utilizando exactamente esa misma lógica, la IA los va a poder leer y analizar de forma natural. De un plumazo, eliminamos la necesidad de gastar fortunas o meses de trabajo intentando "traducirle" a la máquina cómo funcionan los archivos internos de la compañía.

En los capítulos siguientes iremos viendo los antecedentes y esfuerzos que se hicieron antes de llegar a demostrar que el modelo definitivamente funciona.
