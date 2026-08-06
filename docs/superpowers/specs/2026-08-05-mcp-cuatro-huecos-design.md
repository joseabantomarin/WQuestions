# Los cinco huecos del MCP: que el servidor responda sin ayuda externa

> Diseño para cerrar las cinco carencias del servidor `wquestions-mcp` que
> quedaron expuestas al consultar un universo real de 3 M de hechos (la
> migración de yaku). Hoy el MCP no sabe encontrar una entidad por su nombre,
> responde con identificadores opacos, no sabe preguntar por un período, no
> agrega, y no puede escribir un atributo sobre una entidad. Las cinco se
> descubrieron usándolo, no leyéndolo.

- **Fecha:** 2026-08-05
- **Alcance:** `mcp-server/wquestions_mcp/session.py` y `server.py`;
  `prototipo/wq/query.py`. El motor (`Universe`, `Fact`, `ingest`) no se toca.
- **Relacionado:** Cap 26 (pendientes), D8 (catálogo invisible),
  `2026-08-01-derivacion-dimensional-design.md`.

---

## Por qué

El universo yaku migrado tiene 3.012.634 hechos y responde consultas en
milisegundos. Pero **ninguna pregunta de negocio se pudo contestar entera por el
MCP**. En cada caso hubo que salir del protocolo y recorrer el universo con
Python:

| pregunta real | qué faltó |
|---|---|
| "los consumos de **Jose Abanto**" | no hay forma de llegar a `cli_26696215` desde el nombre |
| "dame los consumos de este cliente" | devolvió `pro_850`, `n_000032`: ilegible |
| "solo este año" | `ask` fija valores exactos, no períodos |
| "qué producto tiene las ventas récord" | habría que traer 243.147 filas |
| (al migrar) "el nombre de la persona" | no hay forma de escribir `(juan, nombre, …)` |

El quinto es la causa raíz del segundo, y es el más interesante: el catálogo
declara `nombre` como `Q→K` —el nombre pertenece a la persona— pero
`assert_situation` siempre mintea un sujeto en O y `correct()` rechaza sujetos
que no sean O. El modelo pide algo que su propia interfaz no sabe expresar.

El primero es el más embarazoso: **todas** las consultas de esta sesión
arrancaron de un id que ya se conocía por tener el SQL delante. Un cliente que
solo tenga el MCP no puede dar el primer paso. Diseñar que los nombres salgan
(hueco 2) sin poder entrar por ellos deja la puerta tapiada por dentro.

## Qué NO entra (YAGNI)

- Pipeline de agregación completo (varias claves, `HAVING`, paginación).
- Índice invertido por palabras, ranking por relevancia o corrección de erratas.
  `find` hace subcadena normalizada y nada más.
- Snapshot del universo para acelerar el replay. Es un problema real y medido,
  pero es otra pieza.
- Arreglar el bug de escritura parcial no registrada en el log. Va aparte.

---

## 1. `assert_fact` — escribir una tripleta sobre cualquier entidad

**Herramienta nueva.**

```
assert_fact(subject, role, value, valid_from=None, valid_to=None)
  -> {ok, fact: {subject, role, value}}
```

- `subject` es el id de una entidad **existente**, de cualquier eje de valor.
  Si no existe, error (no se mintea en silencio).
- `value` acepta lo mismo que hoy `assert_situation`: un id existente o una
  especificación inline `{id, axis, label}` / `{id, axis:'N', value, unit}`.
- Se valida contra el catálogo. `(juan, nombre, lit)` pasa por ser `Q→K`;
  `(juan, momento, t)` se rechaza porque `momento` es `O→T`.
- Se registra en el log como op `assert_fact` y se añade al despacho de
  `_replay`.

Además, **`correct()` deja de exigir sujeto en O**. Corregir el nombre de una
persona es tan legítimo como corregir un rol de una situación, y el almacén es
append-only en ambos casos.

**Por qué no rompe nada:** el almacén ya es tripletas binarias. Esto no añade una
forma nueva de dato, solo expone una escritura que el motor siempre soportó
(`Universe.assert_fact`) y que el MCP tapaba tras la reificación obligatoria.

## 1bis. `find` — encontrar una entidad por su nombre

**Herramienta nueva.** Es la puerta de entrada: sin ella nada de lo demás se
puede usar sin conocer los identificadores de antemano.

```
find(texto, eje=None, limite=20)
  -> {count, results: [{id, axis, label}], truncated: bool}
```

- Coincidencia por **subcadena normalizada**: sin distinguir mayúsculas ni
  acentos (`"azañero"` encuentra `ROMERO AZAÑERO, MARCELA`). Es lo mínimo que
  hace falta en español y no requiere tokenizar.
- `eje` filtra a un eje de valor (`"Q"` para buscar solo personas).
- El nombre de cada entidad sale de la **misma resolución que `labels`**: hecho
  con rol `nombre` primero, `individual.label` después. Una sola definición de
  "cómo se llama esto" para leer y para buscar.
- `limite` por defecto 20, con `truncated` para avisar de que hay más. Buscar
  `"a"` en yaku daría cientos de miles de coincidencias; devolverlas sería
  peor que no responder.

**Rendimiento — medido sobre las 539.075 entidades de yaku:**

| estrategia | tiempo |
|---|---|
| escaneo lineal normalizando en cada consulta | 920–1.180 ms |
| índice de etiquetas normalizadas | **13,5 ms** |

El escaneo ingenuo no sirve. Se construye un índice `etiqueta_normalizada →
[ids]` **la primera vez que se llama a `find`**, no al arrancar: cuesta 2,6 s y
unas decenas de MB, y un universo que nunca busca no debe pagarlos. El índice se
invalida al escribir (`add_entity`, `assert_fact`, `correct`, `reset`).

## 2. `labels` — nombres en la respuesta de `ask`

`ask` gana una clave `labels` al mismo nivel que `results`: un **diccionario
único** `id → nombre`, no una anotación por fila. En una consulta de 381 filas
con 105 productos distintos, son 105 entradas en vez de 381 pares repetidos.

```json
{
  "count": 381,
  "results": [
    {"_subject": "accion_vender_132175", "tema": "pro_850",
     "momento": "t_2023-07-16", "por_cuanto": "n_000032"}
  ],
  "labels": {
    "pro_850": "SAUNA PLUS",
    "t_2023-07-16": "2023-07-16",
    "n_000032": {"value": 25.0, "unit": "PEN"}
  }
}
```

**Cómo se resuelve el nombre de una entidad**, en este orden:

1. un hecho con rol `nombre` sobre ella — el que ahora se puede escribir con
   `assert_fact`; se usa la etiqueta de su valor;
2. si no lo hay, `individual.label`;
3. si el label es igual al id (nodos de situación, entidades stub), **se omite**
   de `labels`. Un id que no aporta nada no gasta tokens.

Las magnitudes N se resuelven a `{"value", "unit"}` desde su payload, con la
unidad traducida a su propia etiqueta.

Se resuelven todos los ids que aparecen en `results`, sujetos incluidos.
Parámetro `labels: bool = True` para apagarlo cuando el llamador solo va a
encadenar identificadores.

**Esto cierra el círculo con el hueco 4:** el nombre se escribe como hecho y
`ask` lo devuelve. Deja de vivir en un `label` inalcanzable.

## 3. Rangos en `fixed`

Un valor de `fixed` puede ser, en vez de un id, un objeto de comparación:

```
fixed={"momento":    {"desde": "2026-01-01", "hasta": "2026-12-31"}}
fixed={"por_cuanto": {"desde": 100}}
```

`desde` es inclusivo, `hasta` es inclusivo. Cualquiera de los dos puede faltar.

- **Eje T:** compara por el `datetime` del payload si lo hay; si no, por la
  cadena del label, que en ISO-8601 ordena correctamente. Las entidades T de
  yaku están en este segundo caso (`label="2026-05-12"`, payload `None`).
- **Eje N:** el extremo se escribe de dos formas, y la diferencia es explícita:
  - `{"desde": 100}` — número pelado: compara contra el valor del payload **sin
    mirar la unidad**. Vale cuando el rol tiene una sola unidad en todo el
    universo, que es el caso de `por_cuanto` en yaku.
  - `{"desde": {"value": 100, "unit": "pen"}}` — con unidad: convierte ambos
    lados a unidad base antes de comparar, y **descarta** las magnitudes de
    dimensión distinta en vez de compararlas mal.
- Otros ejes: error explícito. Un rango sobre Q o K no significa nada.

**Ancla:** el punto 1 de `query()` sigue eligiendo el rol fijo *más selectivo*
entre los de valor exacto, y el rango se aplica como filtro en el punto 2. Solo
cuando el rango es la única condición se recorre `facts_with_role(rol)`.

## 4. `agrupar_por` / `medir` — agregación

```
ask(type="accion_vender",
    agrupar_por="tema",
    medir={"veces": "count", "importe": {"sum": "importe"}},
    orden="-importe", limite=10)
```

- `agrupar_por`: un nombre de rol. Si se omite y hay `medir`, se calcula un
  total general (una sola fila, sin clave de grupo).
- `medir`: `{nombre_salida: medida}`, donde la medida es `"count"` o
  `{"sum"|"min"|"max"|"avg": rol}`.
- `orden`: `"campo"` o `"-campo"` (descendente). Por defecto, el orden de
  aparición.
- `limite`: entero. Sin límite por defecto — pero como agrupar reduce a decenas
  de filas, el riesgo de volcado desaparece.
- La respuesta trae `results` con las filas agregadas y su `labels` como
  siempre.

**Las sumas comprueban la unidad.** `sum` sobre magnitudes de unidades no
conmensurables devuelve error, no un número. Es la regla del eje N aplicada a la
consulta: sumar soles con unidades sueltas produce un hecho numéricamente
correcto y dimensionalmente falso, que es peor que no calcular. El resultado de
una suma es `{"value", "unit"}`, no un número pelado.

`agrupar_por` y `ask` (la lista de roles a proyectar) son excluyentes: o
proyectas filas o agregas grupos.

## 5. Habilitante: derivar `importe` en cada línea

Sin esto, la agregación da totales equivocados en yaku: `sum(por_cuanto)` suma
**precios unitarios**, y el importe real de una línea es `PRECIO × CANTIDAD`.

La decisión tomada es no meter aritmética en el lenguaje de consulta, sino
**derivar el hecho** con el motor que ya existe (`wq/derivacion.py`), que es
donde el modelo puso ese trabajo. La regla vive en el grafo:

```
(regla_importe_linea, instancia_de,   regla_de_derivacion)
(regla_importe_linea, expresion,      "por_cuanto * cantidad")
(regla_importe_linea, unidad_destino, K:pen)
```

y la migración escribe en cada línea `(linea, importe, N)`.

**Requisito dimensional, verificado:** una unidad sin física declarada se reduce
a **unidad base**, así que `pen × unidad` da la dimensión compuesta `pen·unidad`
y `convertir_a("pen")` falla. Hay que declarar la unidad de conteo como
**adimensional** (`declarar_unidad(u, "unidad", factor=1.0)`); entonces
`25 PEN × 3 = 75 PEN`. Medido antes de escribir esto. Semánticamente es lo
correcto: contar no tiene dimensión.

**Se escribe el hecho sobre la propia línea**, no con `derivar()`, que mintea un
nodo aparte con dos cables de procedencia. Para 243.147 líneas eso serían 243 k
entidades y 729 k hechos diciendo todos lo mismo. La regla queda declarada una
vez en el grafo, que es donde importa que esté; la procedencia por línea no
aporta información nueva cuando la regla es única y universal.

Coste: +243.147 hechos y unos pocos miles de magnitudes (van internadas).

---

## Arquitectura

Todo el comportamiento nuevo vive en `session.py`, que es donde está hoy y donde
se prueba sin MCP. `server.py` solo gana la declaración de `assert_fact` y los
parámetros nuevos de `ask`. En `query.py` se toca únicamente el punto 1 (ancla)
para admitir rangos.

Tres piezas independientes y testeables por separado:

| pieza | dónde | qué hace | depende de |
|---|---|---|---|
| resolución de nombres | `session.py` | id → nombre, una sola definición | `Universe.individuals`, hechos con rol `nombre` |
| índice de búsqueda | `session.py` | nombre normalizado → ids, perezoso | resolución de nombres |
| comparación de rangos | `query.py` | filtra candidatas por T/N | payload/label del individuo |
| agregación | `session.py` | agrupa filas y mide | `Magnitud` para las unidades |

La **resolución de nombres es una sola función** que sirve a `labels` y a `find`:
si algún día el nombre pasa a salir de otro sitio, cambia en un lugar y los dos
lo heredan. El índice de búsqueda se apoya en ella y no sabe de consultas; la
agregación no sabe de nombres (se aplica después, sobre los ids que quedaron).

## Compatibilidad

Todo lo nuevo es aditivo. Una llamada existente a `ask` devuelve exactamente lo
mismo **más** la clave `labels`. Los 128 tests actuales deben seguir pasando sin
tocarlos; si alguno compara la respuesta completa de `ask`, se ajusta ese test y
se anota por qué.

## Pruebas

- `assert_fact`: sujeto de cada eje; sujeto inexistente; violación de signatura;
  que sobreviva al replay; `correct` sobre una entidad Q.
- `find`: subcadena; insensible a mayúsculas y a acentos; filtro por eje; tope y
  bandera `truncated`; que el índice se invalide tras escribir (buscar, añadir
  una entidad, volver a buscar y encontrarla); que un universo que nunca llama a
  `find` no construya el índice.
- `labels`: prioridad hecho-`nombre` > label > omitido; magnitud con unidad;
  `labels=false`; que un id repetido en 300 filas aparezca una sola vez.
- rangos: T con payload y sin payload; N; extremo abierto; eje inválido; que el
  ancla siga eligiendo el rol exacto más selectivo cuando lo hay.
- agregación: `count`, `sum`, `min`, `max`, `avg`; unidades no conmensurables →
  error; `orden` y `limite`; total general sin `agrupar_por`.
- extremo a extremo sobre yaku: las cuatro preguntas de la tabla de arriba,
  contrastadas contra el SQL de origen.

## Riesgos

- **Coste en tokens de `labels`.** Mitigado por el diccionario único y por omitir
  los ids sin nombre propio. Conviene medirlo sobre una consulta real antes de
  darlo por bueno.
- **Rango como única condición** recorre todos los hechos de ese rol. Aceptable
  hoy (yaku: ~1 M de hechos por rol en el peor caso, ~100 ms), pero es el punto
  que se degradará primero.
- **La derivación de `importe` es específica de yaku**, no del estándar. Debe
  quedar en el script de migración, no en el motor.
- **El índice de `find` se invalida entero al escribir.** Con escrituras
  frecuentes intercaladas con búsquedas, se reconstruiría una y otra vez a 2,6 s
  la vez. Aceptable en el uso previsto (cargar y consultar), pero si aparece un
  patrón escribe-busca-escribe hay que pasar a actualización incremental.
