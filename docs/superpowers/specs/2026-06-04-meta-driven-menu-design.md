# Diseño — Sistema meta-driven sobre WQuestions (menú CLI)

- **Fecha:** 2026-06-04
- **Estado:** aprobado (diseño), pendiente plan de implementación
- **Ubicación del código:** `prototipo/meta/`

## 1. Propósito

Construir el primer eslabón de un sistema **meta-driven** sobre el modelo WQuestions:
una aplicación cuya estructura *y* comportamiento se describen como **hechos
WQuestions** (tripletas sobre los 7 ejes), persistidos en SQLite, e interpretados
por un **evaluador genérico**. El "hello world" es un **menú CLI** navegable:

```
Menú principal
  1. Bienvenida      → muestra un texto
  2. Configuración   → abre un submenú (Idioma / Volver)
  3. Salir           → termina
```

El objetivo de esta iteración (milestone): un **CLI meta-driven funcional** que lee
el menú desde SQLite y lo navega, donde cada opción *hace algo*. La estructura no
está hardcodeada: agregar menús/opciones/acciones de tipos conocidos = solo insertar
hechos.

## 2. Decisiones tomadas

| # | Decisión | Justificación |
|---|---|---|
| Alcance | CLI meta-driven funcional (navegable) | "hello world" honesto del ciclo datos→runtime |
| Comportamiento | **Pocas primitivas interpretadas** (verbos-K tipados + evaluador genérico) | Fiel a la teoría: una acción es un verbo (K) que se reifica en una situación (O) con roles tipados; el evaluador es el "motor externo" que el libro separa del grafo (Cap 6 D2, Cap 26). Evita el anti-patrón de "acción = string ciego" (sub-modela) y el de "meter el motor en los datos" (sobre-modela) |
| Anidamiento | **Sí**, desde v1 (Configuración abre un submenú real) | `abrir_submenu` necesita algo que abrir; la recursión como-datos es lo más potente del enfoque y cuesta solo unos hechos más |
| Arquitectura | **Reusar `prototipo/wq/` + SQLite como almacén (cargar-en-memoria)** | Dataset minúsculo; reuso máximo de la librería de 7 ejes ya testeada; SQLite guarda las tripletas; costura fina que permite promover a SQLite-consultado-directo después sin tocar el runtime |
| Ubicación | `prototipo/meta/` (junto a `wq/` y `ejemplos/`) | Cero fricción de imports (`from wq import …`, `PYTHONPATH=prototipo`, igual que los ejemplos) |
| Texto libre | **Reificado como individuo K**, referenciado por el rol `contenido` (O→K) | El modelo de 7 ejes no tiene "eje string"; mantener el texto como individuo de primera clase deja la puerta abierta a traducciones/versiones |

## 3. Arquitectura — 3 capas

1. **Datos (SQLite)** — las tripletas del menú. Única fuente de verdad.
2. **Almacén (`storage`)** — serializa/carga un `Universe` de `wq` ↔ SQLite. Aísla la BD.
3. **Evaluador (`runtime`)** — carga el universo, lee el menú actual, lo muestra,
   recibe input y **despacha según el tipo-K de la acción**. No conoce ninguna opción
   por nombre.

## 4. Estructura de archivos

```
prototipo/
  wq/                  (sin cambios — librería de 7 ejes)
  meta/                ← NUEVO
    __init__.py
    storage.py         # esquema SQLite + save(universe)/load() ↔ sqlite
    catalogo_app.py    # registra los roles del app + los verbos-K
    seed.py            # construye el menú como hechos y los persiste
    runtime.py         # evaluador: loop CLI + dispatch por tipo-K
    __main__.py        # python -m meta (seed si vacío, luego corre el menú)
    tests/
      __init__.py
      test_meta.py
```

## 5. Modelo de datos (hechos sobre los 7 ejes)

### Individuos

| id | eje | qué es |
|---|---|---|
| `menu`, `opcion` | K | tipos |
| `mostrar_texto`, `abrir_submenu`, `volver`, `salir` | K | verbos-primitiva |
| `menu_principal`, `menu_config` | O | menús (artefactos reificados) |
| `opt_bienvenida`, `opt_config`, `opt_salir`, `opt_idioma`, `opt_volver` | O | opciones |
| `acc_bienvenida`, `acc_abrir_config`, `acc_salir`, `acc_idioma`, `acc_volver` | O | acciones (situaciones reificadas) |
| `txt_bienvenida`, `txt_idioma` | K | contenido de texto (el texto vive en el `label` del individuo) |

El **label visible** de cada opción ("Bienvenida") = el `label` del propio individuo `opt_*`.

### Roles (registrados en el Catálogo)

| rol | signatura | cardinalidad | une |
|---|---|---|---|
| `instancia_de` | O→K | múltiple | individuo ↔ su tipo (ya canónico en `wq`) |
| `tiene_opcion` | O→O | múltiple | menú → opción |
| `orden` | O→N | funcional | opción → posición |
| `tiene_accion` | O→O | funcional | opción → acción |
| `destino` | O→O | funcional | acción `abrir_submenu` → menú destino |
| `contenido` | O→K | funcional | acción `mostrar_texto` → texto |

### Ejemplo de hechos

```
(menu_principal, instancia_de, menu)
(menu_principal, tiene_opcion, opt_bienvenida)
(opt_bienvenida, instancia_de, opcion)
(opt_bienvenida, orden, 1)
(opt_bienvenida, tiene_accion, acc_bienvenida)
(acc_bienvenida, instancia_de, mostrar_texto)
(acc_bienvenida, contenido, txt_bienvenida)

(opt_config, tiene_accion, acc_abrir_config)
(acc_abrir_config, instancia_de, abrir_submenu)
(acc_abrir_config, destino, menu_config)        # submenú = otro O → recursión
```

## 6. SQLite

```sql
individuos(id TEXT PRIMARY KEY, eje TEXT, label TEXT, payload TEXT)   -- payload JSON o NULL
hechos(rowid INTEGER PRIMARY KEY, sujeto TEXT, rol TEXT, valor TEXT,
       valid_from TEXT, valid_to TEXT, tx_time TEXT)                  -- temporal nullable, sin uso en v1
-- índices: hechos(sujeto), hechos(rol)
```

`storage.py`:
- `init_db(conn)` — crea tablas e índices.
- `save(universe, conn)` — vuelca individuos y hechos.
- `load(conn, catalog) → Universe` — reconstruye `Individual` y reasienta cada hecho
  con `u.assert_fact(...)`, que **revalida la signatura al cargar** (integridad gratis).

El runtime solo llama a `load()`. Promover a SQLite-directo después = reemplazar `load()`,
sin tocar el runtime.

## 7. Evaluador (`runtime.py`)

```
stack = [menu_principal]
mientras corriendo:
    actual   = stack[-1]
    opciones = facts(actual, "tiene_opcion") ordenadas por "orden"
    mostrar  título(actual.label) + opciones numeradas (por su label)
    n        = leer()              # número
    opcion   = opciones[n-1]
    accion   = one(opcion, "tiene_accion")
    verbo    = one(accion, "instancia_de")     # tipo-K
    DISPATCH[verbo.id](universe, accion, stack)
```

`DISPATCH` (1 handler por primitiva):
- `mostrar_texto` → imprime `contenido(accion).label`; sigue en el menú actual.
- `abrir_submenu` → `stack.append(destino(accion))`.
- `volver` → `stack.pop()` (si `len(stack) > 1`).
- `salir` → termina el loop.

IO inyectable: `run(universe, leer=input, escribir=print)` para testear sin teclado.
Entradas inválidas (no numérica, fuera de rango) → reimprimir el menú.

`catalogo_app.py`: parte del `Catalog` canónico de `wq` y registra los 5 roles del app
(`tiene_opcion`, `orden`, `tiene_accion`, `destino`, `contenido`). Los verbos son
individuos K; su "signatura de roles obligatorios" no se valida en v1 (el seed autora
hechos correctos).

`seed.py`: crea los individuos (con labels) y asienta los hechos vía `assert_fact`;
luego `storage.save()`. No usa el Lexicon (no hay parsing de lenguaje natural en v1).

`__main__.py`: abre `prototipo/meta/menu.db`; si está vacío → `seed`; `load`; `runtime.run`.

## 8. Testing

Corren con `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta`:

1. `test_storage_roundtrip` — save a SQLite `:memory:` → load → individuos y hechos preservados.
2. `test_seed_structure` — `menu_principal` = `[bienvenida, config, salir]` en orden 1-2-3;
   acción de `config` = `abrir_submenu → menu_config`; `menu_config` = `[idioma, volver]`.
3. `test_signatura_protege` — asentar `tiene_opcion` con valor fuera de O lanza `SignatureError`.
4. `test_navegacion` — evaluador con input scripteado `["1","2","2","3"]` (Bienvenida → entrar
   a Configuración → Volver → Salir) y salida capturada: verifica texto de bienvenida, submenú
   mostrado, retorno al principal y salida limpia.

## 9. Fuera de alcance (YAGNI por ahora)

- Escritura/edición de menús desde el runtime (v1 navega; el seed es la única escritura).
- Bitemporalidad / vigencia (columnas existen pero sin uso).
- Lexicon / parsing de lenguaje natural.
- SQLite consultado directo (queda detrás de la costura `load()`).
- Verbos más allá de las 4 primitivas; cualquier efecto nuevo = nuevo K + handler.

## 10. Nota de limpieza relacionada

El docstring de `prototipo/wq/__init__.py` todavía dice "8 ejes (Q,O,L,T,N,K,P,M)"
(quedó desactualizado tras el colapso a 7 ejes). Conviene corregirlo a 7 ejes al tocar
el prototipo, aunque es cosmético y no bloquea este trabajo.
