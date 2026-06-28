# Diseño — Aplanado del modelo a tablas (`wq/vistas.py`)

- **Fecha:** 2026-06-28
- **Estado:** aprobado (diseño); pendiente de escribir el plan de implementación
- **Sub-proyecto:** 2 de 2. El sub-proyecto 1 (capítulo) ya está en producción
  (sección "De la geometría a la tabla que ya conoces" del cap. 8, Figs 8.4 y 8.5).
- **Entregable:** un módulo nuevo `prototipo/wq/vistas.py` + un seed de ejemplo
  `prototipo/ejemplos/tabla_cap8.py` + tests `prototipo/tests/test_vistas.py`,
  que producen **exactamente** las tres vistas del cap. 8.

## Contexto

El cap. 8 afirma que el grafo de coordenadas **se proyecta de vuelta** a tablas
*bajo demanda*: la tabla no es el modelo, es una de sus vistas. El capítulo ya
muestra tres figuras:

- **Fig 8.2** — la "hoja dispersa": tabla universal de hechos, columnas Q/O/L/T/N/K,
  celdas con **códigos** (ids).
- **Fig 8.4** — la proyección legible: filtra una familia de clases (K), resuelve
  los códigos a etiquetas humanas y proyecta un enlace `M` concreto (`estado`) como
  columna.
- **Fig 8.5** — la pivote: cruza **K × L** con conteos.

El criterio de aceptación del spec del capítulo
(`2026-06-28-tabla-universal-cap8-design.md`) dice: *"El prototipo deberá producir
exactamente estas tres vistas (plana / proyección / pivote) para que el capítulo y
el código no se contradigan."* Este spec implementa ese aplanado en el prototipo
Python.

## Estado actual del prototipo (lo que ya existe)

- `wq/universe.py` — `Universe` en memoria: `individuals: Dict[str,Individual]`,
  `facts: List[Fact]`, índices por sujeto/rol/valor. Métodos: `add_individual`,
  `assert_fact`, `facts_about`, `facts_with_role`, `facts_with_value`.
- `wq/individual.py` — `Individual(id, axis, label, payload, meta)`. El **id es el
  código**; el **label es la etiqueta humana**. Vive en un eje de valor.
- `wq/fact.py` — `Fact(subject, role, value, valid_from, valid_to, tx_time)`,
  bitemporal; `is_valid_at(moment)`.
- `wq/query.py` — `query(universe, Pattern(fixed, ask, type_constraint), at)`
  devuelve *bindings* (`dict` rol→Individual). Las situaciones se reifican en **O**
  con `instancia_de → K` y cada rol como hecho atómico.
- `wq/ingest.py` — `ingest_situation(u, lex, verbo, roles, sit_id=...)` reifica una
  situación en O y asienta sus roles.
- `ejemplos/municipalidad.py` — dominio municipal con `dentro_de` como jerarquía
  territorial L→L (lote → manzana → barrio → distrito → ciudad) y el lexicon de
  `solicitar/revisar/emitir/multar/...`. **Se deja intacto** (tiene 11 validaciones).
- El prototipo es hoy **Python puro, sin dependencias**, Python 3.9.

## Decisiones tomadas (en brainstorming)

1. **Dependencia:** se adopta **pandas como dependencia real** del prototipo. Las
   tres funciones devuelven `pandas.DataFrame` directamente; HTML/JSON/DataFrame
   salen nativos (`df.to_html()`, `df.to_dict(orient="records")`). Se añade
   `requirements.txt` y se documenta en el README que el prototipo deja de ser
   "cero dependencias".
2. **Datos de la pivote:** se generan **~336 trámites reales** en un seed nuevo
   (`ejemplos/tabla_cap8.py`) con la distribución exacta del libro; los conteos
   salen **computados, no hardcodeados**. `municipalidad.py` queda intacto.
3. **Arquitectura:** módulo nuevo `wq/vistas.py` con tres funciones puras sobre
   `Universe` (Enfoque A). No se infla `query.py`.
4. **Columna "Estado (M)":** se honra la Decisión 1 del spec del capítulo — la
   vista plana se queda en los 6 ejes de valor; la proyección muestra `Estado (M)`
   como **proyección de un enlace `M` concreto** (`estado`), no como 7.º eje.

## API — `wq/vistas.py`

Tres funciones puras. Todas devuelven `pandas.DataFrame`.

### `tabla_plana` — Fig 8.2 (universal, con códigos)

```python
def tabla_plana(u: Universe, subjects=None, at=None) -> pd.DataFrame
```

- Una **fila por situación reificada** (individuo de O que tiene `instancia_de`).
  Si `subjects` es `None`, son todas las situaciones del universo; si se pasa una
  lista de `Individual`, solo esas (permite mostrar una "hoja dispersa"
  cross-dominio como la Fig 8.2).
- Columnas = los seis ejes de valor en orden: `Q, O, L, T, N, K`.
- Para cada situación, cada hecho se ubica en la columna del **eje de su valor**
  (`fact.value.axis`); la columna **O** lleva el id de la propia situación.
- **Celdas = ids (códigos)**, no etiquetas (es la hoja cruda). Si un eje tiene
  varios valores (p. ej. dos hechos K: `instancia_de` + `estado`), se unen con
  `"; "`. Celdas vacías = `""` (muestra la dispersión real).
- `at` filtra hechos por vigencia (`fact.is_valid_at(at)`).

### `proyeccion` — Fig 8.4 (legible, etiquetas)

```python
def proyeccion(u: Universe, columnas, subjects=None, filtro_k=None, at=None) -> pd.DataFrame
```

- `columnas`: lista ordenada de `(cabecera, rol)`. El **rol especial `"_subject"`**
  proyecta la etiqueta de la propia situación. Cualquier otro rol proyecta el
  `label` del valor de ese hecho (resuelto a etiqueta humana; si no hay label, cae
  al id).
- `subjects`: si se pasa una lista de `Individual` (situaciones), proyecta solo
  esas, en ese orden (simétrico con `tabla_plana`). Permite armar el "reporte" de
  un puñado de trámites concretos sin un `head/tail` arbitrario. `None` = todas las
  que pasen `filtro_k`.
- `filtro_k`: un id de K o un iterable de ids; filtra las situaciones cuyo
  `instancia_de` ∈ `filtro_k`. `None` = todas. Se aplica además de `subjects`.
- `at`: resuelve los roles temporales (p. ej. `estado`) en ese instante.
- Las filas salen ordenadas por orden de inserción de la situación (determinista).
- Cabecera de columnas tal cual el libro: `"Ciudadano (Q)"`, `"Expediente (O)"`,
  `"Ubicación (L)"`, `"Fecha (T)"`, `"Costo (N)"`, `"Estado (M)"`.

### `pivote` — Fig 8.5 (conteos K × L)

```python
def pivote(u: Universe, eje_filas="instancia_de", eje_cols="lugar_de",
           orden_filas=None, orden_cols=None, filtro_k=None,
           resolver_l_a_zona=False, at=None) -> pd.DataFrame
```

- Agrupa cada situación por el valor de `eje_filas` (rol; por defecto
  `instancia_de` → la clase K) y por el valor de `eje_cols` (por defecto
  `lugar_de` → la L). Celda = **conteo** de situaciones en esa intersección.
- `resolver_l_a_zona=True`: el valor de L de cada situación se sube por la cadena
  `dentro_de` hasta encontrar una zona del conjunto de columnas (o se usa tal cual
  si ya es zona). Permite que un trámite con dirección de calle cuente en su zona.
- `orden_filas`/`orden_cols`: listas de ids para fijar el orden (etiquetas en el
  DataFrame vía `Individual.label`). Si `None`, orden de aparición.
- `filtro_k`: restringe a una familia de clases antes de contar.
- Devuelve un DataFrame indexado por las etiquetas de fila, columnas = etiquetas de
  L; valores = `int` (0 donde no hay).

## Modelado de "Ubicación" (la única sutileza)

Las zonas `zona_centro` / `zona_norte` / `zona_sur` son los individuos **L** que usa
la pivote. La dirección de calle que muestra la Fig 8.4 se modela como un **L más
fino** (`dir_juan`, etiqueta `"Jr. Trujillo 450, Centro"`) que está **`dentro_de`**
su zona — el mismo idiom territorial que ya usa `municipalidad.py`.

- La **proyección** muestra la etiqueta de calle (el `label` del valor de `lugar_de`).
- La **pivote** agrupa con `resolver_l_a_zona=True`: sube por `dentro_de` hasta la
  zona.
- Los ~336 trámites en bloque cuelgan **directo de la zona** (su L ya es la zona; se
  resuelven a sí mismos). Solo los 3 destacados llevan L a nivel de calle.

## Seed `ejemplos/tabla_cap8.py`

### Vocabulario

- **K (clases):** `licencia_construccion`, `licencia_funcionamiento`,
  `licencia_micromov`, `multa_fiscalizacion`. Estados (valores K del cable
  `estado`): `solicitado`, `en_revision`, `aprobada`.
- **L (zonas):** `zona_centro`, `zona_norte`, `zona_sur`. Tres direcciones finas
  para los destacados: `dir_juan` ("Jr. Trujillo 450, Centro") `dentro_de`
  `zona_centro`; `dir_carla` ("Av. Perú 1200, Norte") `dentro_de` `zona_norte`;
  `dir_marta` ("Jr. Lima 88, Centro") `dentro_de` `zona_centro`.
- **Q (ciudadanos):** `juan` ("Juan"), `carla` ("Carla"), `marta` ("Marta") + N
  ciudadanos genéricos `ciud_0001…` para el grueso.

### Generación (conteos computados)

Cada trámite se reifica **directamente** como un individuo de O con
`instancia_de = <clase>` y `lugar_de = <zona>` (vía `add_individual` +
`assert_fact`, **sin** pasar por los verbos del lexicon). Razón: si se usara
`ingest_situation("emitir", ...)`, el `instancia_de` quedaría en el tipo-situación
del verbo (`accion_emitir_licencia`) y la pivote agruparía por el verbo, no por la
clase del trámite. El seed valida las vistas, no el lexicon, así que el camino
directo es el correcto.

Bucles que crean esas situaciones en estas cantidades **exactas** (que deben dar la
Fig 8.5):

| Clase (K) \ Zona (L) | Centro | Norte | Sur |
|---|---|---|---|
| `licencia_construccion` | 45 | 12 | 8 |
| `licencia_funcionamiento` | 120 | 54 | 30 |
| `multa_fiscalizacion` | 15 | 42 | 10 |

Total ≈ 336 situaciones. La pivote **cuenta**; no se escribe ningún número a mano.

### Tres destacados (Fig 8.4, literal)

Tres situaciones con atributos completos (forman parte del universo; Juan y Marta
cuentan dentro de los 336 de su celda, Carla es micromovilidad — fuera de la
pivote, como en el libro):

| Ciudadano | Expediente (label de la situación) | Ubicación (L calle) | Fecha (T) | Costo (N) | Estado (M) |
|---|---|---|---|---|---|
| Juan | Licencia de funcionamiento | Jr. Trujillo 450, Centro | 22-06-2026 | S/ 450,00 | Solicitado |
| Carla | Licencia de micromovilidad | Av. Perú 1200, Norte | 23-06-2026 | S/ 300,00 | En revisión |
| Marta | Remodelación de local | Jr. Lima 88, Centro | 24-06-2026 | S/ 520,00 | Aprobada |

- `Expediente (O)` = el `label` de la situación (rol `_subject`).
- `Costo (N)` = individuo N con `payload={"value":450.0,"unit":"PEN"}`,
  label `"S/ 450,00"`.
- `Fecha (T)` = individuo T, label `"22-06-2026"`.
- `Estado (M)` = cable `estado` → categoría K, label `"Solicitado"` /
  `"En revisión"` / `"Aprobada"`.

### `main()`

Construye el universo, corre las tres vistas, las imprime, y **assert**a:

1. `pivote(...)` == los 9 números de la tabla de arriba (en su orden).
2. `proyeccion(..., subjects=[juan_t, carla_t, marta_t])` == las 3 filas destacadas
   (tuplas de etiquetas exactas de la Fig 8.4).
3. `tabla_plana(...)` sobre una muestra cross-dominio devuelve códigos (ids) y tiene
   las 6 columnas de eje.

Devuelve `True` si todo coincide (mismo patrón que `municipalidad.py::main`).

## Tests `prototipo/tests/test_vistas.py`

Estilo `unittest`, como `test_wq.py`. Sin depender de los 336:

- **Fixture mínimo** (3-4 situaciones a mano) para unitarios:
  - `tabla_plana`: nº de filas = nº de situaciones; columnas == `["Q","O","L","T","N","K"]`;
    una celda conocida lleva el id esperado; multivaluado se une con `"; "`.
  - `proyeccion`: cabeceras = las pedidas; `_subject` proyecta el label de la
    situación; un rol proyecta el label del valor; `filtro_k` recorta; `at`
    selecciona el `estado` vigente.
  - `pivote`: conteos correctos en un cruce 2×2; `resolver_l_a_zona` sube por
    `dentro_de`; celda vacía = 0.
- **Integración:** importa `ejemplos/tabla_cap8.py`, construye el universo y verifica
  los 9 conteos de la pivote y las 3 filas de la proyección (los números del libro).

## Dependencia y arranque

- Nuevo `prototipo/requirements.txt` con `pandas`.
- Nota en `prototipo/README.md`: el prototipo ahora requiere `pandas`
  (`pip install -r requirements.txt`); el núcleo `wq` sigue siendo puro salvo
  `vistas.py`.
- Paso 0 de implementación: instalar pandas (Python 3.9 → pandas 2.2.x).

## Criterios de aceptación

1. `wq/vistas.py` con `tabla_plana`, `proyeccion`, `pivote`, exportadas en
   `wq/__init__.py`.
2. `PYTHONPATH=. python3 ejemplos/tabla_cap8.py` imprime las tres vistas y sale 0
   (todos los asserts del `main` pasan): la pivote da 45/12/8 · 120/54/30 · 15/42/10
   y la proyección da las 3 filas Juan/Carla/Marta de la Fig 8.4.
3. `PYTHONPATH=. python3 -m unittest tests.test_vistas -v` pasa.
4. La suite existente `tests.test_wq` y `ejemplos/municipalidad.py` siguen pasando
   (no se rompe nada).
5. Identificadores y etiquetas consistentes con el cap. 8 y el canon municipal.

## Anti-scope

- **No** se añade un renderizador HTML propio con las clases del sitio (el libro ya
  tiene las tablas escritas a mano; `df.to_html()` basta como demostración). Se puede
  añadir un helper de paridad visual después, fuera de este spec.
- **No** se toca `municipalidad.py` ni `query.py` (salvo, si hiciera falta, un
  *import* en `__init__.py`).
- **No** se persiste a disco; el universo es en memoria, como el resto del prototipo.
- **No** se modela una 7.ª columna "verbo" en la tabla universal (Decisión 1).

## Riesgos / notas

- La proyección de `licencia_*` sobre el universo completo devuelve cientos de
  filas (hay 230 licencias). El `main` y el test de integración la usan como
  **reporte de los 3 destacados** vía `subjects=[juan_t, carla_t, marta_t]` para
  casar con la Fig 8.4 publicada, que es de suyo una muestra de 3 filas.
- Carla (micromovilidad) no aparece en la pivote por diseño: el libro publica esa
  asimetría entre la Fig 8.4 (licencias, incluye micromov) y la Fig 8.5
  (construcción/funcionamiento/multas). El prototipo reproduce el libro tal cual.
- pandas no está instalado en el entorno; el paso 0 lo instala. Si fallara en Python
  3.9, fijar `pandas<2.3` o la última 2.2.x compatible.
- Voz/estilo del seed: español neutro, sin auto-elogio de honestidad
  (ver `feedback_libro_tono_honestidad`).
