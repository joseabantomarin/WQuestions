# Diseño — El catálogo como dato (firmas derivadas del esquema)

- **Fecha:** 2026-06-05
- **Estado:** aprobado por delegación (el usuario delegó el diseño "ajustándote a la teoría"); pendiente su revisión del spec escrito
- **Código:** `prototipo/meta/` (catálogo + motor + web)
- **Specs base:** `2026-06-05-entidad-form-grilla-design.md`, `2026-06-05-maestros-compras-design.md`
- **Motivación:** fricción #2 de `docs/fricciones-stress-test-modelo.md`

## 1. Propósito

Hoy los roles **dinámicos de cada campo** (`documento`, `precio`, `proveedor`, `fecha`…)
no están en el catálogo: pasan por **política liberal** (sin validar signatura). Esta
iteración hace que la **firma de cada campo se derive de sus propios datos** y se registre
en el catálogo, de modo que escribir en un campo dinámico se valide igual que un rol
canónico. Y surfacing limpio: una violación se responde **400**, no 500.

Es la última pieza de "estructura" que se vuelve dato: **el tipado deja de vivir en
Python**. Cierra la fricción #2 y completa, del lado de la estructura, la tesis "todo es
dato".

## 2. Teoría

El catálogo (D8) es la garantía de signatura tipada del modelo. Aquí pasa a **alimentarse
del esquema** (que ya es dato): la línea "núcleo cerrado y tipado / extensión abierta y
liberal" se corre hacia "**el dato define sus propios tipos**". El núcleo canónico se
mantiene intacto y con prioridad (se confía en él); la extensión deja de ser liberal y pasa
a ser tipada-por-datos. Surfacing como 400 es fiel al propósito de D8: el catálogo
**rechaza** hechos malformados, y un rechazo debe ser **legible**, no un crash.

## 3. Derivación de la firma (por campo)

Por cada individuo `instancia_de campo`:
- **rol** = el valor de su `rol` (id del K; ej. `documento`).
- **dominio** = el `eje_instancia` del **tipo dueño** (el `T` tal que `(T, tiene_campo,
  campo)`), leyendo `Axis(eje_instancia.label)`; default `Axis.O` si el tipo no lo declara.
- **rango** = de `tipo_dato`:
  - `texto`→K, `numero`→N, `fecha`→T.
  - `referencia`→ `Axis(eje_instancia(referencia_a).label)`, default O.
- **functional** = `True` (semántico: un valor actual por campo). El modelo **no impone**
  cardinalidad (`assert_fact` solo valida ejes), así que "gana el último hecho" (varios
  hechos por campo) sigue intacto.

**Registro:** solo si `catalog.get(rol)` es `None`. Si el rol ya existe (canónico:
`cliente`, `monto`, `nombre`, o ya derivado en esta pasada), **se omite** — se confía en el
núcleo y se evitan conflictos (dos campos con el mismo rol → gana el primero/canónico).

Resultado en el seed actual: se registran `documento` (O→K), `fecha` (O→T), `producto`
(O→O), `proveedor` (O→Q), `precio` (O→N), `nombre_producto` (O→K). Se omiten los canónicos
`cliente` (O→Q), `monto` (O→N), `nombre` (Q→K).

## 4. Componente y momento

- **`registrar_firmas_de_esquema(u)`** en `prototipo/meta/catalogo_app.py`: autónomo (lee
  hechos vía `u.facts_about`/`u.facts_with_value`); si no existe el meta-tipo `campo` en el
  universo (universos mínimos de test), retorna sin hacer nada.
- **Momento (post-pass):** se llama al **final de `build_universe()`** y **tras
  `storage.load(...)` en `abrir_universo()`**. Los datos ya sembrados/cargados **se
  confían** (no se re-validan); la validación aplica a **escrituras futuras** (el `guardar`
  del formulario). Esto evita problemas de orden de carga (campos y registros interleaved).

## 5. Surfacing de errores (validación → 400)

- `engine.guardar` deja **propagar** las excepciones naturales:
  - `SignatureError` (valor en eje equivocado, ahora que el campo está tipado),
  - `ValueError` (`float(raw)` de un `numero` no numérico; `time_point(raw)` de una fecha
    inválida),
  - `KeyError` (`u.ind(raw)` de una referencia a un id inexistente).
- Los endpoints **`/api/guardar`** y **`/api/abrir_formulario`** capturan
  `(SignatureError, ValueError, KeyError)` y responden **`400 {"error": <mensaje>}`** en vez
  de 500. `server.py` importa `SignatureError` de `wq`.
- El frontend ya muestra un aviso ante fallo de `fetch`/respuesta no-ok (manejo existente);
  no requiere cambios. (Opcional menor: mostrar el `error` del body; fuera de alcance.)

## 6. Testing

1. **Derivación:** tras `build_universe()`, `u.catalog.get("documento")` es `O→K`,
   `get("precio")` es `O→N`, `get("proveedor")` es `O→Q`; `get("cliente")` sigue siendo el
   **canónico** O→Q (no se sobrescribió).
2. **Validación activa:** asentar un valor de campo en el eje equivocado (ej. `(venta_x,
   documento, <individuo N>)`) lanza `SignatureError`.
3. **Surfacing 400:** `POST /api/guardar` con `monto="abc"` → 400; con una referencia a un
   id inexistente → 400 (no 500). Body malformado sigue → 400.
4. **Universo mínimo:** `registrar_firmas_de_esquema` sobre un universo sin `campo` no
   rompe.
5. **Campo agregado en vivo:** un campo insertado como datos (p. ej. `documento`) queda
   **tipado** tras recargar (su firma se deriva en el post-pass).
6. **Preservación:** todas las suites verdes (wq + meta + web). Los datos sembrados no se
   re-validan, así que la migración no rompe nada.

Corre con `PYTHONPATH=prototipo python3 -m unittest discover -s prototipo/tests -q` y
`... meta.tests.test_meta meta.tests.test_web -q`.

## 7. Fuera de alcance (YAGNI)

- Imponer la cardinalidad `functional` (el modelo no lo hace; "último gana" lo necesita).
- Re-validar o migrar los datos ya sembrados/cargados.
- Permitir declarar la firma de un campo explícitamente (se deriva; declararla a mano sería
  redundante con `tipo_dato`/`referencia_a`).
- Mostrar el texto del `error` 400 en la UI (el aviso genérico existente basta).
- Tocar `wq/` (la derivación vive en la capa `meta`; el catálogo canónico no cambia).
