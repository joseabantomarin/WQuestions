# Diseño — Pantallas de entidad (form + grilla) meta-driven sobre el grafo único

- **Fecha:** 2026-06-05
- **Estado:** aprobado (diseño), pendiente plan de implementación
- **Código:** `prototipo/meta/` (motor + web)
- **Specs base:** `2026-06-04-meta-driven-menu-design.md`, `2026-06-04-meta-driven-web-ui-design.md`

## 1. Propósito

Sobre el menú meta-driven, agregar **pantallas de entidad** genéricas: una opción del
menú abre una **ventana** (título = nombre de la opción) que es un **formulario de
edición** (Registro) o una **grilla** (Consulta). Demostrado con una entidad `venta`.

Invariante (lo pidió el usuario): **solo el comportamiento se hardcodea**; los campos,
tipos, etiquetas, orden y registros **viven en los datos**. El motor no sabe qué es una
"venta"; lo lee del grafo.

Segundo principio (corrección del usuario): **un solo grafo compartido**. No hay
`venta.db` ni `compra.db`. Clientes, proveedores, productos, lugares son **individuos
compartidos** reusados por ventas, compras, etc. No se duplican como texto.

## 2. Qué se hardcodea (comportamiento) vs qué es dato

**Único código nuevo (comportamientos genéricos):**
1. **3 primitivas (verbos-K + handlers):** `abrir_formulario`, `abrir_grilla`, y la
   operación `guardar`.
2. **Mapeo de tipos** (genérico sobre el `tipo_dato` del campo, no sobre campos concretos):
   `texto`→K, `numero`→N, `fecha`→T, `referencia`→enlaza al individuo existente elegido.

**Todo lo demás es dato (tripletas):** el tipo `venta`, sus campos, etiquetas, tipos,
orden, los `rol` de cada campo, las entidades compartidas (clientes/productos) y los
registros. Agregar un campo, cambiar una etiqueta o el orden = insertar/editar hechos.

## 3. Un solo store

Se renombra `prototipo/meta/menu.db` → **`prototipo/meta/wq.db`** (el grafo único de todo).
Toca `__main__.py`, `web/__main__.py`, `web/server.py` (default), `.gitignore`. El
`menu.db` viejo se elimina (el seed re-siembra `wq.db` con el menú + esquema + ejemplos).

## 3b. Ajuste al prototipo `wq`: `instancia_de` pasa a `V→K`

Para clasificar y **enumerar** las entidades compartidas (clientes, productos), hace falta
poder decir `(ana, instancia_de, cliente)` con `ana ∈ Q`. Pero el catálogo del prototipo
fijó `instancia_de` como **O→K**, mientras el **libro** (Cap 4) lo muestra como `V→K`:
`(messi, instancia_de, jugador_de_futbol) ∈ M(Q,K)`, `(lima, …) ∈ M(L,K)`, y enuncia que
todo individuo de Q/O/L (y a veces T) debe responder "¿de qué concepto eres instancia?".
Es una **discrepancia prototipo↔libro**; la corregimos (ajuste empírico, como el libro
predica).

Cambios en `wq/` (chicos, retro-compatibles — solo *afloja* el dominio):
- `axes.py`: añadir `Axis.V` = "cualquier eje de valor" (marcador para signaturas; **no**
  es lugar de individuos: `is_value_axis(V)` es False, los individuos siguen sin poder vivir
  en V; `VALUE_AXES` no lo incluye).
- `catalog.py`: en `validate`, tratar `V` como comodín — `if sig.domain != Axis.V and
  subject.axis != sig.domain: raise` (idem rango). Cambiar la signatura de `instancia_de`
  a `domain=V, range=K`.
- Habilita además el patrón `O→V` que el libro pide para `partes` (Cap 23/minera).
- **Sync del libro:** el anexo `29_anexo_prototipo.md` (que reproduce el catálogo) y la
  prosa del Cap 4 deben reflejar `instancia_de: V→K`. Se actualiza el anexo en la
  implementación; afinar la prosa del libro queda como follow-up menor.

## 4. Modelo de datos (todo tripletas)

### 4.1 Tipo y esquema
- `venta` ∈ **K** (tipo de entidad).
- Campos = descriptores ∈ **O**, ligados con `tiene_campo` (K→O, múltiple). Cada campo:
  - **etiqueta** = el `label` del individuo (ej. "Cliente").
  - `tipo_dato` → K: `texto` | `numero` | `fecha` | `referencia`.
  - `orden` → N.
  - `rol` → K cuyo **id es el predicado** que usan los registros (ej. `cliente`).
  - si `tipo_dato = referencia`: `referencia_a` → K (el tipo apuntado, ej. `cliente`).

```
(venta, tiene_campo, campo_cliente)        ∈ M(K,O)
(campo_cliente, instancia_de, campo)
(campo_cliente, tipo_dato, referencia)     ∈ M(O,K)
(campo_cliente, referencia_a, cliente)     ∈ M(O,K)
(campo_cliente, orden, 2)
(campo_cliente, rol, cliente)
```

Esquema `venta`: `fecha` (fecha), `cliente` (referencia→cliente), `producto`
(referencia→producto), `monto` (numero).

### 4.2 Entidades compartidas
- Clientes = agentes ∈ **Q**: `(ana, instancia_de, cliente)` ∈ M(Q,K), `(beto, …)`.
- Productos ∈ **O**: `(laptop, instancia_de, producto)` ∈ M(O,K), `(mouse, …)`.
- (Clasificarlos con `instancia_de` es válido gracias al ajuste **3b** — `instancia_de`
  ahora es `V→K`.)
- Son individuos del grafo único: una venta hoy y una compra mañana referencian **los
  mismos**. `_opciones_ref(tipo)` = los individuos `instancia_de tipo`.

### 4.3 Registros
Una venta es un O `instancia_de venta`, con **un hecho por campo** (rol del campo, valor
en el eje que dicta `tipo_dato`):
```
(venta_001, instancia_de, venta)
(venta_001, fecha,    «T:2026-06-01»)   (fecha → T literal)
(venta_001, cliente,  ana)              (referencia → MISMA ana en Q)
(venta_001, producto, laptop)           (referencia → mismo laptop en O)
(venta_001, monto,    «N:120»)          (numero → N literal)
```

**Actualizar = gana el último hecho:** editar agrega un hecho nuevo `(venta_001, rol,
valor)`; el lector toma el **más reciente**. No se borra nada (historial; afín a D6).

### 4.4 Catálogo
`build_catalog()` añade roles estructurales del app: `sobre_tipo` (O→K), `tiene_campo`
(K→O múlt), `tipo_dato` (O→K), `rol` (O→K), `referencia_a` (O→K). La clasificación de
entidades usa el `instancia_de` **canónico** (ya `V→K` por el ajuste 3b). Los **roles
dinámicos de campo** (`fecha/cliente/producto/monto`) no se registran: pasan por
**política liberal**; el handler de guardado garantiza el eje correcto del valor.

## 5. Motor (`engine.py`)

**Verbos-K nuevos** en `_DISPATCH`. El `titulo` lo pone `seleccionar` = label de la opción.

- `abrir_formulario` → lee `sobre_tipo` (K) de la acción y devuelve:
  ```
  {tipo:"formulario", titulo, entidad,
   campos:[{rol, etiqueta, tipo, orden,
            opciones:[{id, label}]?   # solo si tipo=referencia: individuos del tipo
           }, ...],
   registro_id: null, valores: {}}   # blanco = alta
  ```
- `abrir_grilla` → devuelve:
  ```
  {tipo:"grilla", titulo, entidad,
   columnas:[{rol, etiqueta}, ...],
   filas:[{id, valores:{rol: "texto legible", ...}}, ...]}
  ```

**Operación `guardar(u, tipo, valores, registro_id=None)`** (única escritura):
1. `registro_id` → ese registro (edición); si no → crea O nuevo `instancia_de tipo`.
2. Por cada campo del esquema, según `tipo_dato`:
   - `referencia` → `valores[rol]` es el **id de un individuo existente**; asienta
     `(registro, rol, u.ind(id))` (lo **comparte**, no mintea).
   - `numero`→N, `fecha`→T, `texto`→K: construye el valor literal y lo asienta.
3. Devuelve el id del registro.

**Lectores genéricos:** `_campos(u, tipo)` (esquema ordenado), `_registros(u, tipo)`
(instancias), `_valor(u, reg, rol)` (último hecho, hecho legible), `_opciones_ref(u, tipo)`
(individuos `instancia_de tipo`, para los selects).

El motor no menciona "venta": recorre el esquema y las instancias del grafo.

## 6. API (`web/server.py`)

Se suman 2 endpoints (los demás iguales). El servidor delega en el motor.

| método | ruta | acción |
|---|---|---|
| `POST` | `/api/abrir_formulario` `{entidad, registro_id}` | efecto `formulario` **precargado** con los valores del registro (flujo grilla→editar) |
| `POST` | `/api/guardar` `{entidad, valores, registro_id?}` | `engine.guardar`, **persiste a `wq.db`**, → `{ok, registro_id}` |

- El form en blanco y la grilla llegan por `/api/seleccionar` (click en Registro/Consulta).
- **Persistencia:** tras `guardar`, `storage.save(universe, conn a wq.db)`. Las ventas
  creadas/editadas quedan en disco y sobreviven a reinicios.
- Builder compartido `efecto_formulario(u, tipo, titulo, registro_id=None)` lo usan el
  handler del menú (blanco) y `/api/abrir_formulario` (precargado).
- Body malformado / entidad desconocida → 400 `{error}`.

## 7. UI (`web/static/`)

Ventana modal (`#ventana`), título = label de la opción.

**Form (Registro):** un control por campo, en `orden`. El control depende de `tipo`:
- `numero`→`<input type=number>`, `fecha`→`<input type=date>`, `texto`→`<input type=text>`.
- `referencia`→`<select>` poblado con `opciones` (los individuos existentes del tipo);
  `value`=id, texto=label. Eliges uno existente.
Botones **Guardar** (→ `POST /api/guardar`) y **Cerrar**.

**Grilla (Consulta):** tabla con `columnas` (etiquetas) y `filas` (valores legibles).
**Click en fila** → `POST /api/abrir_formulario {entidad, registro_id}` → abre el form
precargado. Botón **Cerrar**.

Tras Guardar: cierra la ventana y avisa "Guardado". **Cerrar** vuelve al menú (Ventas).
La UI mapea `tipo`→control de forma genérica; no conoce los campos.

## 8. Seed (permanente)

`seed.build_universe()` incorpora, todo como dato:
- La **rama Ventas** (opción + submenú Registro/Consulta/Volver + acciones).
- Verbos-K `abrir_formulario`, `abrir_grilla`.
- El tipo `venta` + esquema (4 campos) + meta-tipo `campo` + K `texto/numero/fecha/referencia`.
- Tipos `cliente`, `producto` (K) + entidades compartidas (Ana/Beto ∈ Q; Laptop/Mouse ∈ O).
- 2–3 ventas de ejemplo que referencian esas entidades.
- Acciones: `acc_registro → abrir_formulario` + `sobre_tipo → venta`; `acc_consulta →
  abrir_grilla` + `sobre_tipo → venta`.

Resultado: Ventas **permanente** (sobrevive a `rm wq.db` → re-siembra). Las ventas creadas
por el form persisten hasta un reset.

## 9. Testing

1. **Motor (unit):** `_campos` (4 campos ordenados, con `referencia_a` donde toca),
   `_opciones_ref` (lista clientes/productos), `abrir_formulario` (campos + opciones de
   referencia), `abrir_grilla` (columnas + filas legibles), `guardar` crea (un hecho por
   campo; la referencia enlaza al MISMO individuo, verificable por id) y `guardar` con
   `registro_id` actualiza (último gana).
2. **Compartir:** crear dos ventas con el mismo cliente → ambas apuntan al **mismo** id
   en Q (no se duplica).
3. **Ajuste `wq` (instancia_de V→K):** test nuevo en `prototipo/tests/` — `instancia_de`
   ahora acepta sujeto en Q/L/etc. (`(messi∈Q, instancia_de, jugador∈K)` no lanza), pero
   sigue rechazando valor no-K. Los **21 tests de `wq` siguen verdes** (el cambio solo
   afloja el dominio).
4. **Preservación meta:** los 23 tests previos del paquete `meta` siguen verdes (tras
   renombrar la db en el código).
5. **API:** `POST /api/guardar` crea y **persiste** (reabrir `wq.db` y ver el hecho);
   `POST /api/abrir_formulario {registro_id}` precargado; body malformado → 400.
6. **Smoke visual:** Chrome headless sobre la ventana Consulta (grilla con filas) y
   Registro (form con select de cliente/producto) → capturas.

`PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta meta.tests.test_web`.

## 10. Fuera de alcance (YAGNI)

- Borrar registros (Delete); crear clientes/productos nuevos desde el form (los selects
  son de entidades existentes seeded).
- Más tipos de entidad además de `venta` (la maquinaria es genérica; el seed solo trae
  `venta`). "Compra" será una iteración futura: otra rama/efecto sobre **el mismo grafo**,
  reusando clientes/productos/lugares.
- Validación de signatura para los roles de campo (van por política liberal; el handler
  garantiza el eje).
- Inspector mostrando el esquema/registros de la entidad (sigue mostrando el menú).
- Multi-usuario / sesiones concurrentes.
