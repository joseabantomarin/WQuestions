# Capítulo 1 — La torre de Babel de los datos

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

## La apuesta de este libro

Regresemos a la compra de la camiseta. Si detuviéramos a cualquier persona en la calle —sin conocimientos de bases de datos ni de código— y le pidiéramos describir ese hecho, su respuesta natural sería algo muy parecido a esto:

> "*Una clienta* (**quién**) *compró* (**qué**) *una camiseta* (**qué**) *en la tienda del centro* (**dónde**) *esta tarde* (**cuándo**) *por casi cincuenta dólares* (**cuánto**)."

Sin el menor esfuerzo, cualquier ser humano produce una descripción **estructurada, completa y combinable**. Nuestra mente no percibe el mundo como un bloque de texto ni como tablas de Excel: descompone automáticamente cualquier evento con un conjunto muy reducido de preguntas fundamentales.

Esa es la apuesta de este libro:

> **Existe un conjunto reducido y estable de preguntas primarias —siete— con capacidad descriptiva suficiente para modelar cualquier hecho factual, en cualquier dominio industrial y en cualquier idioma.** Quién, qué, dónde, cuándo, cuánto, cuál y cómo. Al diseñar las bases de datos alrededor de estas coordenadas cognitivas —en lugar de las terminologías de turno de cada industria— se neutraliza de raíz la fragmentación semántica, y la torre de Babel se desmorona desde los cimientos. Como bono, cualquier inteligencia artificial entrenada con lenguaje humano entiende esta estructura de fábrica, porque es la misma con la que aprendió a leer.

No la tomes como un acto de fe. Estas preguntas no son un invento moderno: filósofos griegos, juristas romanos, escuelas de periodismo y hasta los niños que aprenden a hablar convergen, sin coordinarse y separados por siglos, en la misma lista. A esa convergencia —la prueba de *por qué estas preguntas y no otras*— le dedicamos un capítulo entero más adelante (Capítulo 6). Pero no hace falta esperar a la demostración para empezar a construir.

Lo que sigue es la ingeniería: diseccionar, una por una, las siete coordenadas operativas sobre las que se levanta el modelo. Empecemos por las cuatro más concretas.
