# Capítulo 29  
## El software como grafo

Imagine una pantalla dividida en dos partes.

A la izquierda, una aplicación convencional: un menú, formularios y una grilla de datos.  
A la derecha, una lista de tripletas que crece constantemente.

Esa lista no describe lo que ocurre en la aplicación.  
Esa lista es la aplicación.

---

## Todo es tripleta

Cada elemento visible existe porque está definido en el grafo.

Un menú no es un componente programado.  
Es un conjunto de relaciones.

Cada opción de menú está asociada a una acción.  
Cada acción corresponde a un verbo que el sistema puede interpretar.

De la misma forma:

- Una entidad tiene campos  
- Un campo tiene un tipo  
- Un campo tiene un orden  
- Un campo tiene una etiqueta  

Nada de esto está fuera del grafo.  
La estructura completa del sistema está expresada como tripletas.

---

## Interpretar en lugar de programar

No hay lógica escrita para cada caso particular.

Existe un motor que interpreta las tripletas.

Las acciones se representan como verbos:

- abrir_grilla  
- guardar  
- mostrar_texto  

El motor reconoce estos verbos y ejecuta el comportamiento correspondiente.

El sistema no se construye programando cada pantalla.  
El sistema se define a partir de relaciones.

---

## La interfaz emerge del grafo

La interfaz no se diseña manualmente.

Cuando una entidad tiene campos definidos con su tipo y orden, el sistema genera:

- formularios  
- grillas  
- estructuras de captura  

La interfaz es una consecuencia directa del grafo.

---

## Agregar un campo

Se agrega el campo “Documento” a la entidad “venta”.

Solo se definen algunas tripletas:

- el campo existe  
- pertenece a la entidad  
- tiene un tipo  
- tiene un orden  
- cumple un rol  

No se modifica código.

El resultado aparece inmediatamente:

- el formulario incluye el nuevo campo  
- la grilla muestra la nueva columna  
- el sistema permite almacenarlo  

Todo ocurre a partir del grafo.

---

## La estructura es dato

La organización del sistema forma parte del dato.

No solo se almacenan valores, sino también:

- cómo se estructuran  
- cómo se relacionan  
- cómo se presentan  

La separación entre datos y lógica deja de ser rígida.

---

## El comodín V

Las consultas sobre el grafo no requieren conocer de antemano todos los valores.

Se puede utilizar un comodín, representado como **V**, para indicar una variable.

Este comodín permite expresar consultas donde uno o más elementos son desconocidos.

Por ejemplo, en una tripleta:

- sujeto – relación – V  

V representa el valor que se desea obtener.

El sistema resuelve la consulta buscando en el grafo las tripletas que satisfacen esa condición.

El resultado es el conjunto de valores que pueden ocupar ese lugar.

De esta forma, las consultas no son procedimientos, sino patrones que se buscan dentro del grafo.

---

## Consulta sobre el grafo

Se formula una pregunta utilizando las relaciones definidas.

El sistema evalúa la consulta directamente sobre el grafo.  
La respuesta se obtiene a partir de las coincidencias encontradas.

No hay lógica adicional fuera de este mecanismo.

---

## La interfaz, por detrás de su propia teoría

La interfaz misma puede analizarse utilizando el mismo modelo que la define.

Los elementos que la componen —menús, campos, acciones— están representados en el grafo.

Esto permite consultar la interfaz como si fuera cualquier otro conjunto de datos.

La propia estructura que genera la interfaz puede ser recorrida, inspeccionada y utilizada.

La interfaz no es un elemento externo al sistema.  
Forma parte del mismo conjunto de relaciones.

---

## Cierre

El sistema queda definido completamente por el grafo.

La estructura y el comportamiento se expresan como datos.  
Los cambios consisten en agregar o modificar tripletas.

El grafo no describe el sistema.  
El grafo es el sistema.