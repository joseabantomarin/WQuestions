# Someter el modelo a carga reflexiva: fricciones y conclusiones

> Qué aprendimos al construir, **sobre el propio modelo WQuestions**, una aplicación que
> describe su propia tooling: el menú, los formularios, los tipos de dato, las relaciones
> y las entidades — todo como hechos `(sujeto, rol, valor)`. El modelo deja de hablar de
> un dominio externo y empieza a hablar **de sí mismo**. Este documento registra, sin
> rodeos, dónde rozó y dónde aguantó.

- **Fecha:** 2026-06-05
- **Artefactos:** `prototipo/meta/` (motor + web), specs/planes en `docs/superpowers/`,
  notas de implementación en `docs/superpowers/notes/2026-06-05-meta-driven-situaciones-implementacion.md`.
- **Capítulos relacionados:** Cap 4 (clase, `instancia_de`), Cap 6 y 26 (grafo vs.
  evaluador externo), D5 (agencia contextual), D6 (bitemporalidad), D8 (catálogo).

---

## La prueba reina

La pregunta que ordena todo lo demás: **¿cuánto cuesta agregar estructura?** Si la tesis
("estructura y comportamiento son datos") es real, agregar un campo a una entidad debería
costar *insertar hechos*, no *escribir código*.

Lo medimos en vivo, con el sistema corriendo: agregar el campo **"Documento"** a la entidad
`venta`.

```
(campo_venta_documento, instancia_de, campo)        ∈ M(O,K)
(venta, tiene_campo, campo_venta_documento)         ∈ M(K,O)
(campo_venta_documento, tipo_dato, texto)           ∈ M(O,K)
(campo_venta_documento, orden, 5)                   ∈ M(O,N)
(campo_venta_documento, rol, documento)             ∈ M(O,K)
```

**Cinco tripletas. 1.9 ms. Cero líneas** de motor, API o UI. Al recargar, el formulario de
Ventas dibujó el campo, la grilla le agregó la columna y `guardar` lo persiste — porque
`abrir_formulario`, `abrir_grilla` y `guardar` **leen el esquema del grafo**, no lo conocen.

Ese número —cinco hechos, ningún código— es el resultado central. Todo lo que sigue es la
letra chica: qué hizo posible ese número, qué se dobló para lograrlo, y qué quedó expuesto.

---

## Fricciones (las tensiones y límites reales)

### 1. El texto libre no tiene eje — es el punto ciego del modelo
Los nombres ("Ana"), las etiquetas, el contenido de "Bienvenida": todo texto arbitrario
terminó **reificado como individuo K** (con la cadena en el `label`). N y T son hogares
legítimos para números y fechas; el texto, en cambio, se mete *a presión* en K. El modelo
trata de **individuos y relaciones**, no de literales — y cuando el dato *es* un literal de
texto, queda en una zona gris entre "individuo K" y "atributo (`label`)". No es un bug; es
una elección (los siete ejes son semánticos, no tipos primitivos). Pero la carga la dejó a
la vista: **el texto libre es la materia que el modelo no sabe dónde poner.**

### 2. La garantía del catálogo tipado se evapora justo donde dejamos definir campos
Los roles estructurales (`tiene_campo`, `sobre_tipo`, `eje_instancia`…) viven en el
catálogo y se validan por signatura. Pero los **roles dinámicos de cada campo** (`cliente`,
`monto`, `documento`, `nombre_producto`…) no están: pasan por **política liberal**, sin
validación. El tipado fuerte protege el núcleo y *confía* en la extensión; el motor
reimpone el eje al escribir, a mano. Conclusión incómoda: **el catálogo mismo quiere ser
meta-driven** — que el esquema, al declarar un campo, registre su signatura. No lo hicimos
(YAGNI), pero la frontera quedó señalada: hoy corre entre "núcleo cerrado y tipado" y
"extensión abierta y liberal"; podría correrse hacia "el dato define sus propios tipos".

### 3. La tasa de reflexividad: para hablar de un predicado como dato, hay que volverlo K
WQ separa con nitidez **M** (predicados) de **K** (categorías). Pero al **meta-modelar**
—describir los predicados *como datos*— el nombre del predicado debe existir como
individuo, y lo alojamos en K. Resultado: el mismo individuo `documento` es a la vez
nombre-de-rol y marcador; `texto` es tipo-de-dato y, en otros campos, predicado; `producto`
fue tipo y predicado. **La frontera M/K se vuelve porosa en el nivel meta.** Funciona por
idempotencia de identificadores, pero es exactamente el punto donde un lector humano pierde
pie: deja de estar claro si una palabra nombra una cosa, una categoría o una relación.

### 4. Hasta el eje de un individuo tuvo que volverse dato (`eje_instancia`)
`guardar` no podía saber si lo nuevo es una persona (Q), un producto (O) o una compra (O).
El **eje** —la clasificación más fundamental e "intrínseca" de WQ— hubo que **declararlo el
tipo, como dato** (`(persona, eje_instancia, «K:Q»)`). Es profundo: los siete ejes son el
sustrato fijo, pero *en cuál* cae cada cosa nueva es conocimiento de esquema, no del motor.
El meta-app empujó incluso la asignación de eje hacia los datos.

### 5. Inmutabilidad de los individuos vs. edición de datos
La mutación de datos se resolvió con **"gana el último hecho"** (agregar un hecho nuevo,
leer el más reciente): elegante y **alineado con D6** (bitemporal; historial gratis). Pero
el `label` cacheado sobre el individuo *inmutable* no pudo seguir a una edición del nombre.
Lección limpia: en WQ **mutar es asentar hechos nuevos, no cambiar individuos** — perfecto.
El roce aparece solo donde *cacheamos un valor derivado* (la etiqueta) sobre la identidad.
Lo derivado debe computarse de los hechos, no guardarse en el individuo.

### 6. El vértigo del humano es un hallazgo, no un defecto del lector
Cuando *todo* —menú, formularios, tipos, relaciones— es `(sujeto, rol, valor)`, el humano
pierde el andamiaje de "tablas, formularios y tipos con nombre" que normalmente carga el
significado. El modelo es lo bastante potente para ser **reflexivo**, y la reflexividad
cobra peaje cognitivo. El antídoto ya está construido: el **inspector** ("lo que ves =
datos") re-concreta la abstracción mostrando las tripletas detrás de cada pantalla.
Conclusión fuerte: **un sistema totalmente meta-driven necesita una capa de
re-concreción** (vistas, inspector, proyecciones con nombre) *precisamente porque* es tan
abstracto. Es, también, la razón de ser del libro: el modelo necesita prosa y ejemplos para
ser agarrable.

---

## Conclusiones (lo que el modelo aguantó y validó)

### A. `instancia_de` es `V→K`, no `O→K` — clasificar es universal
La carga forzó la generalización que **el propio libro ya afirmaba** (Cap 4: `messi∈Q`,
`lima∈L`). Clasificar ("¿de qué concepto eres instancia?") aplica a cualquier eje de valor,
no solo a O. El prototipo estaba *detrás* de su propia teoría; la fricción terminó
**corrigiendo el modelo hacia el libro**, no al revés. Introdujimos `V` (comodín de eje de
valor) en las signaturas — el mismo `V` que el libro pedía para generalizar `partes` a
`O→V`.

### B. El "comportamiento como datos" se sostuvo
El **evaluador externo** que los Cap 6 y 26 anuncian como pieza pendiente — lo
construimos: un despachador genérico por tipo-verbo (K). Agregar **Compras entero** costó
~cero código de motor (dos lecturas nuevas: `eje_instancia`, `campo_etiqueta`) y datos.
La tesis central **sobrevivió** la carga máxima.

### C. El grafo compartido (D5) es el verdadero pago
Al tratar "cliente" y "proveedor" como **roles contextuales** —no como tipos— una persona
vive una sola vez y se reusa entre venta y compra, sin duplicar. El anti-Babel no es
aspiracional: **cae solo** en cuanto dejas de modelar el rol como tipo. Verificado de punta
a punta: una persona registrada en una pantalla aparece, sin nada extra, como proveedora en
otra.

### D. Mutar-como-hechos-nuevos confirma D6
"Gana el último hecho" da edición *con historial* sin borrar nada. La bitemporalidad no fue
un adorno teórico: fue la forma natural de implementar el "update" de un CRUD.

### E. La línea núcleo-cerrado / extensión-abierta es correcta
Tipado fuerte donde es estructural; liberal donde es instancia. El modelo pone bien la
frontera; la fricción #2 solo dice *hacia dónde* podría moverse (que el esquema registre
sus propias signaturas).

---

## En una frase

El modelo aguantó la carga máxima —describirse a sí mismo—, de paso **se auto-corrigió**
(`instancia_de: V→K`) y **confirmó su tesis** (estructura y comportamiento = datos; grafo
compartido). Las fricciones reales no son agujeros del modelo, sino **tres fronteras** que
el experimento iluminó: el **texto libre** (sin eje propio), el **catálogo** (que quiere ser
dato él también) y el **humano** (que necesita re-concreción para no ahogarse en la
reflexividad). La prueba reina —cinco hechos, ningún código— es la medida de que la primera
mitad de la tesis está saldada; las tres fronteras son la agenda de la segunda mitad.

---

## Qué ilumina esto para los pendientes (Cap 26)

1. **El catálogo como dato.** Permitir que un campo, al definirse, registre su signatura —
   cerrando la fricción #2 sin perder el tipado.
2. **Un tratamiento de primera clase para el texto.** Decidir si el texto libre merece su
   propia consideración o si la reificación en K es la respuesta definitiva (fricción #1).
3. **Display derivado de hechos, no cacheado en el individuo** (fricción #5).
4. **La capa de re-concreción como parte del modelo, no del accidente de UI** (fricción #6):
   vistas y proyecciones con nombre como ciudadanos del grafo.

---

## Actualización — la agenda, ejecutada (misma sesión)

Tras escribir este documento, **saldamos tres de las cuatro fronteras**, cada una sin tocar
la librería núcleo `wq` y validada con tests + demo end-to-end:

- **#2 — El catálogo como dato → HECHO.** `registrar_firmas_de_esquema` deriva la signatura
  de cada campo desde sus propios datos (dominio = `eje_instancia` del tipo dueño; rango =
  `tipo_dato`/`referencia_a`) y la registra en el catálogo, solo si el rol no es ya canónico.
  Escribir en un campo dinámico ahora se valida como un rol canónico, y una violación se
  responde **400**, no 500. El tipado dejó de vivir en Python.
  *Spec:* `docs/superpowers/specs/2026-06-05-catalogo-como-dato-design.md`.

- **#1 — El texto libre → HECHO (decisión + obra).** Decisión, fiel a la teoría (los 7 ejes
  son semánticos, no tipos primitivos): el texto no es un eje; el texto libre se aloja como
  **literal K minteado y único** (`literal_texto`), marcado `meta.literal`, **distinto de una
  categoría controlada** (K nombrada y compartida). Dos personas llamadas "Ana" ya no comparten
  un K. La distinción literal/categoría es ahora máquina-legible.

- **#5 — Display derivado de hechos → HECHO.** La etiqueta visible de una entidad referenciada
  se computa de los hechos vía `campo_etiqueta` (`_etiqueta`), no del `.label` cacheado en el
  individuo inmutable. Editar el nombre de una persona se refleja en los `<select>` y grillas.
  Lo derivado se computa de los hechos, no se guarda en la identidad.
  *Spec (#1 y #5):* `docs/superpowers/specs/2026-06-05-segunda-mitad-literal-display-design.md`.

**Lo que queda:**
- **#6 — Vistas como dato (c2):** *pendiente, por criterio.* Es la pieza mayor de la
  re-concreción (una entidad `vista` con columnas/orden/filtro como ciudadana del grafo). Por
  ahora el **inspector** ya re-concreta lo suficiente; se difiere como siguiente paso.
- **#3 (reflexividad: M↔K poroso al meta-modelar) y #4 (el eje de instancia como dato):** no
  son bugs a cerrar sino **rasgos del modelo bajo carga reflexiva** — se documentan como tales,
  no como deuda.

En síntesis: de las tres fronteras de "la segunda mitad", **el catálogo y el texto quedaron
saldados**; del humano, resuelto el display obsoleto (#5) y disponible el inspector, con las
vistas-como-dato como el siguiente escalón.
