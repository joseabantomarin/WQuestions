# Diseño — Maestros (persona, producto) + Compras sobre el grafo único

- **Fecha:** 2026-06-05
- **Estado:** aprobado (diseño), pendiente plan
- **Código:** `prototipo/meta/` (motor + seed) — UI/API sin cambios
- **Spec base:** `2026-06-05-entidad-form-grilla-design.md`

## 1. Propósito

Demostrar que, con la maquinaria meta-driven de pantallas de entidad ya construida,
agregar **entidades maestras** (persona, producto) y una **segunda transacción** (compra)
es **casi solo datos**: dos generalizaciones chicas del motor + tripletas en el seed. Todo
sobre el **mismo grafo** — personas y productos se comparten entre ventas y compras.

## 2. Principio (se mantiene)

Solo el comportamiento se hardcodea; el esquema, los tipos, los registros y ahora también
**el eje de instancia y la etiqueta visible** viven en datos. La UI y la API no cambian:
son genéricas y las entidades nuevas funcionan solas.

## 3. Modelo

- `persona` ∈ **Q** — entidad maestra. "Cliente" y "proveedor" son **roles contextuales**
  (el nombre del campo en venta/compra), no tipos (D5, agencia contextual). La misma
  persona puede ser cliente de una venta y proveedora de una compra.
- `producto` ∈ **O** — maestra; ahora **registrable** con esquema.
- `compra` ∈ **O** — espeja a `venta`.

Esquemas (campos como datos):
| entidad | campos |
|---|---|
| `persona` | `nombre` (texto) |
| `producto` | `nombre` (texto), `precio` (numero) |
| `compra` | `fecha` (fecha), `proveedor` (referencia→persona), `producto` (referencia→producto), `monto` (numero) |
| `venta` (migración) | `cliente` pasa de `referencia_a cliente` a **`referencia_a persona`** |

Migración de datos en el seed: Ana/Beto se re-siembran `instancia_de persona` (mismos
individuos Q); Laptop/Mouse `instancia_de producto` con su `nombre` (y `precio`). El tipo K
`cliente` deja de usarse como tipo de entidad (los registros de venta siguen usando el
**rol** `cliente`, que apunta ahora a una `persona`).

## 4. Las dos generalizaciones del motor (`engine.py`)

Hoy `guardar` hardcodea `axis=Axis.O` y un `label` genérico. Pasan a leerse de datos.

### 4.1 Eje de instancia — `eje_instancia`
El tipo declara el eje de sus instancias:
```
(persona,  eje_instancia, «K:Q»)
(producto, eje_instancia, «K:O»)     # opcional; ausencia → default O
```
`guardar`: `ax = _uno(u, tipo, "eje_instancia"); axis = Axis(ax.label) if ax else Axis.O`.
Se siembran 2 individuos K con label de la letra del eje: `eje_q` ("Q"), `eje_o` ("O").

### 4.2 Etiqueta visible — `campo_etiqueta`
El tipo designa el campo cuyo valor es la etiqueta del individuo (la que ven los `<select>`
y la grilla, vía `.label`):
```
(persona,  campo_etiqueta, campo_persona_nombre)
(producto, campo_etiqueta, campo_producto_nombre)
```
`guardar` arma el individuo nuevo con `label = valores[rol_del_campo_etiqueta]` (ej.
"Ana"); si el tipo no lo declara, usa el genérico `f"{tipo} nuevo"`.

### 4.3 `guardar` (revisado)
```python
def guardar(u, tipo_id, valores, registro_id=None):
    tipo = u.ind(tipo_id)
    campos = _campos(u, tipo)
    if registro_id:
        reg = u.ind(registro_id)
    else:
        ax = _uno(u, tipo, "eje_instancia")
        axis = Axis(ax.label) if ax is not None else Axis.O
        etq = _uno(u, tipo, "campo_etiqueta")
        label = f"{tipo_id} nuevo"
        if etq is not None:
            rol_etq = (_uno(u, etq, "rol") or etq).id
            label = str(valores.get(rol_etq, label))
        reg = Individual(id=mint_id(tipo_id), axis=axis, label=label)
        u.assert_fact(reg, "instancia_de", tipo)
    for c in campos:
        ... (igual que hoy: referencia enlaza individuo; numero/fecha/texto literales)
    return reg.id
```

### 4.4 Catálogo
`build_catalog()` añade `eje_instancia` (K→K) y `campo_etiqueta` (K→O).

## 5. UI y API — sin cambios

La ventana modal (form/grilla), los `<select>` de referencia, `abrir_formulario`/
`abrir_grilla`/`efecto_formulario`/`efecto_grilla` y los endpoints `/api/seleccionar`,
`/api/abrir_formulario`, `/api/guardar` ya son genéricos. Las entidades y menús nuevos
funcionan sin tocar `web/`. El campo `texto` usa `input type=text` (ya soportado). Los
submenús anidados (Maestros → Personas/Productos) los soporta el `stack` del motor sin
cambios.

## 6. Menús (seed, todo dato)

```
Menú principal
├ Bienvenida
├ Configuración
├ Ventas      → Registro / Consulta / Volver
├ Compras     → Registro / Consulta / Volver        (acc: abrir_formulario/grilla, sobre_tipo=compra)
├ Maestros    → Personas / Productos / Volver
│   ├ Personas → Registro / Consulta / Volver        (sobre_tipo=persona)
│   └ Productos→ Registro / Consulta / Volver        (sobre_tipo=producto)
└ Salir
```
Órdenes: Ventas 2.5, Compras 2.6, Maestros 2.7 (entre Configuración y Salir), o enteros
re-secuenciados — a criterio del plan, sin tocar el motor.

## 7. Seed permanente

`seed.build_universe()` incorpora: tipos `persona`/`compra` + producto registrable; sus
esquemas (campos con etiqueta/tipo/orden/rol; `referencia_a`); `eje_instancia` y
`campo_etiqueta` por tipo; entidades maestras (personas Ana/Beto en Q con `nombre`;
productos Laptop/Mouse en O con `nombre`+`precio`); 1–2 compras de ejemplo; las ramas de
menú Compras y Maestros. Migra `venta.cliente` → `referencia_a persona`.

## 8. Testing

1. **Motor:** `guardar` en `persona` crea individuo **Q** (eje_instancia) con `label` = el
   `nombre` (campo_etiqueta); `guardar` en `producto` con `precio`; `guardar` en `compra`
   referenciando persona+producto existentes.
2. **Compartir:** una persona usada como `cliente` en una venta y `proveedor` en una compra
   → ambas apuntan al **mismo** id.
3. **Selects:** `_opciones_ref("persona")` = las personas; `venta.cliente` y
   `compra.proveedor` tienen `referencia_a = persona`.
4. **Migración:** actualizar los tests previos que asumían `referencia_a == "cliente"` →
   `"persona"`, y `_opciones_ref("cliente")` → `_opciones_ref("persona")`.
5. **Preservación:** resto de las suites verde (wq + meta + web).
6. **Smoke visual:** Chrome headless sobre Maestros→Personas (grilla) y Compras (form con
   select de proveedor=persona) — capturas.

Corre con `PYTHONPATH=prototipo python3 -m unittest discover -s prototipo/tests -q` y
`... meta.tests.test_meta meta.tests.test_web -q`.

## 9. Fuera de alcance (YAGNI)

- Refrescar el `.label` al **editar** el nombre de una persona/producto (el `Individual` es
  inmutable; la grilla sí refleja el cambio por el hecho, el `<select>` mantiene el label
  original hasta recrear). Follow-up: resolver el display vía `campo_etiqueta` en lugar de
  `.label`.
- Borrar registros; validar el `precio`/inputs (sigue el nit conocido de `guardar` → 500
  ante input inválido, no endurecido aquí).
- Tipos de entidad más allá de persona/producto/venta/compra.
- Clasificar personas como cliente/proveedor (son roles contextuales, no clasificaciones).
