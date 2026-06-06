# Capítulo 26 — La prueba reflexiva: el modelo descrito con el modelo

## La carga que faltaba

A lo largo del libro sometimos WQuestions a presiones de distinto tipo. La presión lingüística del Capítulo 13, donde el lenguaje aprieta con nominalizaciones, modales e idiomas. La presión de ocho dominios disímiles —del spa a la minera— que confirmaron que un mismo catálogo se sostiene en territorios que no se parecen en nada. La presión de un sistema en producción, en el yaku del Capítulo 22. Y la de cuatro dominios deliberadamente incómodos en el 23, elegidos para que crujieran.

Falta una presión más, y es la más exigente de todas: pedirle al modelo que **se describa a sí mismo**. No modelar un dominio externo con WQuestions, sino construir una herramienta —un programa con menús, formularios, pantallas, tipos de dato y reglas de comportamiento— cuya **estructura, cuyos tipos y cuya conducta sean, ellos mismos, hechos WQuestions**. Si la tesis del libro es cierta —que las preguntas son la base universal de la información—, entonces la propia maquinaria que manipula información debería poder expresarse en esas preguntas. Este capítulo cuenta qué pasó cuando lo intentamos. No venimos a presumir de una varita mágica; venimos, como en el Capítulo 13, con honradez intelectual: a mostrar qué aguantó, qué se dobló para aguantarlo y qué quedó al descubierto.

## Una aplicación hecha de preguntas

Construimos, sobre el prototipo, una pequeña aplicación de gestión: un menú navegable, formularios para dar de alta y editar registros, grillas para consultarlos, y entidades de negocio —personas, productos, ventas, compras— con sus campos. Lo decisivo no es la aplicación; es **de qué está hecha**. Cada opción del menú, cada campo de cada formulario, cada tipo de dato, cada relación entre entidades y cada acción que el programa ejecuta es una tripleta `(sujeto, rol, valor)` en un único grafo.

El menú es un objeto reificado que `tiene_opcion` a otros objetos; cada opción `tiene_accion` una acción; cada acción es `instancia_de` un verbo —`mostrar_texto`, `abrir_formulario`, `abrir_grilla`, `guardar`— que un evaluador genérico interpreta. El esquema de una entidad es dato: la entidad `tiene_campo` a descriptores que declaran su etiqueta, su `tipo_dato` y su `orden`. Un registro es un individuo `instancia_de` su tipo, con un hecho por campo. No hay, en ningún lado, una tabla `venta` con columnas fijas ni una clase `Formulario` con atributos cableados. Hay hechos, y un motor que los lee.

La consecuencia se ve en la pantalla del propio programa: al lado de cada vista, un **inspector** muestra las tripletas que la sostienen. *Lo que ves es, literalmente, lo que hay en el grafo.* La interfaz no es una capa que traduce una base de datos a botones; es una proyección directa de los hechos.

## La prueba reina

La medida de si la tesis se sostiene cabe en una sola operación: **¿cuánto cuesta agregar estructura?** Si estructura y comportamiento son de verdad datos, agregar un campo nuevo a una entidad debería costar *insertar hechos*, no *escribir código*.

Lo medimos en vivo, con el sistema corriendo, agregando el campo "Documento" a la entidad `venta`:

```text
(campo_venta_documento, instancia_de, campo)        ∈ M(O,K)
(venta, tiene_campo, campo_venta_documento)         ∈ M(K,O)
(campo_venta_documento, tipo_dato, texto)           ∈ M(O,K)
(campo_venta_documento, orden, 5)                   ∈ M(O,N)
(campo_venta_documento, rol, documento)             ∈ M(O,K)
```

Cinco tripletas. Ninguna línea de código en el motor, en el servidor ni en la interfaz. Al recargar, el formulario dibujó el campo, la grilla le sumó la columna y el guardado lo persistió — porque las tres operaciones leen el esquema del grafo en vez de conocerlo de antemano. Ese número —cinco hechos, cero código— es el resultado central del experimento, y la confirmación más limpia de la primera mitad de la tesis: **la estructura es dato**.

## Lo que la carga confirmó

Más allá del número, el experimento puso a prueba tres ideas que el libro defendió en abstracto, y las tres aguantaron en concreto.

**El comportamiento como datos.** Seis veces a lo largo del libro apareció la figura del *evaluador externo*: el motor que recorre el grafo y ejecuta lo que los hechos prescriben, separado del grafo que solo almacena. Aquí ese evaluador dejó de ser una promesa y pasó a ser código que corre: un despachador genérico que, dado un verbo (un tipo K), ejecuta la conducta asociada. Agregar una transacción entera nueva —"compras", hermana de "ventas"— costó esencialmente datos, no motor. El comportamiento vive en el grafo y se interpreta desde afuera, tal como el modelo prometía.

**El grafo compartido.** El Capítulo 1 abrió con la torre de Babel: cada sistema con su esquema, incapaz de hablar con el de al lado. El antídoto del libro es un único piso de hechos donde las entidades se reúsan. Lo comprobamos modelando "cliente" y "proveedor" no como tipos distintos sino como **roles contextuales** —el nombre del campo en la venta o en la compra (D5, agencia contextual)—. La misma persona es cliente de una venta y proveedora de una compra sin duplicarse: un solo individuo, dos papeles según el contexto. El anti-Babel no fue una aspiración; cayó solo en cuanto dejamos de modelar el rol como tipo.

**La vigencia.** La edición de un dato se implementó sin borrar nada: editar un valor es asentar un hecho nuevo y leer el más reciente. Es bitemporalidad en miniatura (D6) —historial gratis, ninguna sobreescritura destructiva—, y resultó ser la forma *natural* de implementar el "update" de un CRUD, no un agregado teórico.

## La auto-corrección: `instancia_de` pasa a `V→K`

El experimento no solo validó: forzó una corrección del prototipo, y vale contarla porque es el método del libro operando sobre sí mismo. Para clasificar a una persona —decir "Ana es un cliente"— hace falta el hecho `(ana, instancia_de, cliente)`. Pero `ana` vive en el eje **Q** (es un agente), y el prototipo había restringido `instancia_de` a sujetos del eje O. La carga reveló la contradicción: este mismo libro, en el Capítulo 4, ya escribía `(messi, instancia_de, jugador_de_futbol) ∈ M(Q, K)` y `(lima, instancia_de, ciudad_capital) ∈ M(L, K)`. El prototipo estaba *detrás* de su propia teoría.

La corrección fue generalizar `instancia_de` a `V→K` —donde **V** es un comodín que significa "cualquier eje de valor"—. Clasificar es una operación universal: todo individuo de Q, O, L o T puede responder "¿de qué concepto soy instancia?". Y ese comodín `V` no resuelve solo este caso: es exactamente el mecanismo que el Capítulo 28 reclama para relajar otras signaturas demasiado estrechas (`paciente`, `partes`) de `O→Q` a `O→V`. La fricción, sometida a carga, no abrió un agujero en el modelo: lo empujó a alinearse con lo que ya afirmaba.

## Las fricciones nuevas: dos cerradas, una abierta

La presión reflexiva destapó tres fronteras que los ocho dominios no habían tocado. Dos las cerramos en el mismo experimento; la tercera quedó señalada como trabajo.

**El texto libre.** Los siete ejes son semánticos, no tipos primitivos: no hay un eje "string". Un nombre como "Ana", el contenido de un mensaje, el número de un documento —texto arbitrario— no tienen casa propia. Decisión, fiel a la teoría: el texto libre se aloja como un **literal en K, minteado y único**, con su valor en la etiqueta y una marca que lo distingue de una **categoría controlada** (un vocabulario cerrado como las unidades monetarias o los estados, que sí son K nombradas y compartidas). Así, dos personas llamadas "Ana" no terminan compartiendo un mismo individuo, y el modelo sabe distinguir un literal de una categoría.

**El catálogo como dato.** El catálogo D8 tipa con fuerza el núcleo canónico, pero los campos que el usuario define como datos pasaban sin validar, bajo política liberal. La carga lo expuso: el tipado del esquema vivía a medias en el código. La cerramos haciendo que **cada campo derive su signatura de sus propios datos** —dominio del eje de la entidad, rango de su `tipo_dato`— y la registre en el catálogo. Escribir en un campo dinámico ahora se valida como un rol canónico; el tipado dejó de vivir en Python y pasó a vivir en el grafo.

**El humano.** Queda en pie la tercera frontera, y no es del modelo sino del lector. Cuando *todo* es `(sujeto, rol, valor)`, se pierde el andamiaje de tablas y formularios con nombre que normalmente carga el significado. El poder de la abstracción reflexiva tiene un peaje cognitivo. El inspector —"lo que ves = datos"— re-concreta lo suficiente para no ahogarse, pero la pieza que falta es hacer de las **vistas y proyecciones con nombre** ciudadanas del grafo: datos, no accidente de interfaz. Es trabajo pendiente, y aparece como tal en el capítulo siguiente.

## Honradez intelectual

Conviene nombrar el vértigo, porque es un hallazgo y no un defecto del lector. Un modelo capaz de describirse a sí mismo es, por construcción, mareante: en el límite, no hay "tablas" ni "pantallas", solo preguntas sobre preguntas. Pero ese mareo no invalida la propuesta —la confirma—, y al mismo tiempo explica por qué un modelo así necesita prosa, ejemplos y una capa de re-concreción para ser usable por personas. Es, en el fondo, la razón de ser de este libro: el grafo es operable; el texto es lo que lo vuelve comprensible.

Que el modelo pueda describir su propia herramienta es la evidencia más fuerte que el prototipo produjo. Más que ocho dominios distintos, es el modelo hablando de sí mismo sin salirse de sus siete ejes, corrigiéndose cuando una signatura quedó corta y absorbiendo como datos lo que un sistema convencional cablearía en código. La primera mitad de la tesis —estructura y comportamiento son datos— está saldada, y medida en un número. Lo que sigue es la otra mitad: el inventario honesto de lo que todavía falta para que esto deje de ser un prototipo y se vuelva infraestructura. A eso dedicamos el próximo capítulo.
