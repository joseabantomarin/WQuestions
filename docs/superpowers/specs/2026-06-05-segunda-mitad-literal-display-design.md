# Diseño — Segunda mitad: literal de texto (B) + display derivado de hechos (C)

- **Fecha:** 2026-06-05
- **Estado:** aprobado por delegación (el usuario delegó las decisiones "según la teoría / tu criterio")
- **Código:** `prototipo/meta/` (motor + seed)
- **Motivación:** fricciones #1 y #5 de `docs/fricciones-stress-test-modelo.md`

## 1. Propósito

Cerrar dos fricciones de la "segunda mitad":
- **B (fricción #1):** el texto libre no tiene eje → se reifica en K, pero hoy un literal
  de texto es indistinguible de una categoría controlada. Se formaliza la distinción.
- **C (fricción #5):** el display de una entidad referenciada se cachea en el `.label`
  inmutable y queda obsoleto al editar. Se computa de los hechos.

UI y API genéricas no cambian: solo el motor y el seed.

## 2. B — Literal de texto

**Decisión (teoría):** los 7 ejes son semánticos, no tipos primitivos; el texto no es un
eje. El texto libre se aloja como **individuo K minteado y único** (identidad propia, valor
en `label`) y se **marca** como literal con `meta={"literal": True}` — para distinguirlo de
una **categoría controlada** (K nombrada, compartida, enumerable: USD, un estado, un tipo).

**Componente:** `literal_texto(s)` en `prototipo/meta/engine.py`:
```python
def literal_texto(s):
    return Individual(id=mint_id("txt"), axis=Axis.K, label=str(s), meta={"literal": True})
```
- `guardar`, rama `texto`: usa `literal_texto(raw)` (hoy ya mintea inline; se centraliza + marca).
- `seed.build_universe`: los **valores** de `nombre` (de personas y productos) usan
  `literal_texto(...)` en vez de `_k(label)` (que dedupe por string).

**Efecto:** dos personas llamadas "Ana" tienen literales **independientes** (no comparten un
K); y el flag `literal` hace la distinción literal/categoría máquina-legible (el inspector u
otra tooling puede tratarlos distinto). No se crean hechos extra (la marca va en `meta`).

**Qué NO se toca:** las categorías controladas siguen siendo K nombradas y compartidas
(`texto`, `numero`, `referencia`, los tipos, los ejes `eje_q`/`eje_o`). El `rol` de un campo
sigue siendo un K marcador (no es un literal). Solo los **valores** de tipo `texto` se
vuelven literales marcados.

## 3. C — Display derivado de hechos

**Decisión:** lo derivado (la etiqueta visible de una entidad) se computa de los hechos, no
se guarda en la identidad. El display de una entidad referenciada se resuelve por su
`campo_etiqueta` (el valor vigente del campo nombre), con fallback al `.label`.

**Componente:** `_etiqueta(u, ind)` en `engine.py`:
```python
def _etiqueta(u, ind):
    tipo = _uno(u, ind, "instancia_de")
    if tipo is not None:
        campo_etq = _uno(u, tipo, "campo_etiqueta")
        if campo_etq is not None:
            rol = _uno(u, campo_etq, "rol")
            rol_id = rol.id if rol is not None else campo_etq.id
            val = _ultimo(u, ind, rol_id)
            if val is not None:
                return val.label
    return ind.label
```
- `_opciones_ref(u, tipo_id)`: cada opción usa `label = _etiqueta(u, individuo)` (no
  `individuo.label`).
- `_valor_display(u, reg, rol)`: devuelve `_etiqueta(u, valor)` (para referencias resuelve
  el nombre vigente; para literales N/T/K sin tipo con `campo_etiqueta`, cae al `.label`,
  igual que hoy).

**Efecto:** editar el `nombre` de una persona se refleja en los `<select>` y en las grillas
sin recrear el individuo. Cierra la fricción #5. El comportamiento visible para los datos
actuales no cambia ("Ana"/"Laptop" siguen mostrándose igual).

## 4. Testing

1. **B — literal único y marcado:** `literal_texto("Ana")` e `literal_texto("Ana")` dan
   individuos con **ids distintos**, ambos `meta["literal"] is True`. Tras `build_universe`,
   el valor de `nombre` de `ana` tiene `meta["literal"]`.
2. **B — guardar mintea literal:** `guardar` de una persona con `nombre` crea un valor K con
   `meta["literal"]` y label = el texto.
3. **C — display vigente:** crear persona "Caro"; `_opciones_ref("persona")` la lista como
   "Caro". Editar su `nombre` a "Carolina" (otro `guardar` con su `registro_id`);
   `_opciones_ref` ahora la lista como **"Carolina"** (no el label original).
4. **C — grilla derivada:** en la grilla de ventas, la columna Cliente muestra el nombre
   vigente de la persona referenciada (no su `.label` cacheado).
5. **Preservación:** todas las suites verdes (wq + meta + web); los displays actuales
   ("Ana", "Laptop") no cambian.

`PYTHONPATH=prototipo python3 -m unittest discover -s prototipo/tests -q` y
`... meta.tests.test_meta meta.tests.test_web -q`.

## 5. Fuera de alcance (YAGNI)

- **c2 — vistas como dato** (entidad `vista` con columnas/orden/filtro): feature mayor; el
  inspector ya da re-concreción. Queda como siguiente paso documentado.
- Migrar los literales ya existentes en `wq.db` (se re-siembran).
- Tratar el flag `literal` en la UI/inspector (la marca queda disponible; explotarla es
  otro paso).
- Tocar `wq/` (el helper vive en `meta`; `Individual.meta` ya existe en `wq`).
