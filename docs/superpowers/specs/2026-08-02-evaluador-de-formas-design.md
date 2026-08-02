# El evaluador de formas — segunda rebanada del Frente 1

Diseño validado · 2026-08-02

## Qué resuelve

El Frente 1 tiene dos mitades pendientes: el disparo condicional con agregados
y la validación. Esta entrega cierra la segunda. Hoy el modelo comprueba que
un hecho encaje en la signatura del rol (el eje del sujeto y el del valor) y no
comprueba nada sobre el valor mismo: una disponibilidad del 140 % se guarda con
la misma docilidad que una del 94 %.

## La medición, que decidió el diseño

Medido sobre el prototipo, en tres escalas, antes de escribir una línea.

**Escribir con validación cuesta lo mismo que escribir sin ella.**

| | 1.000 hechos | 10.000 | 100.000 |
|---|---|---|---|
| Línea base | 3,1 ms | 33,4 ms | 545 ms |
| Comprobando formas | 3,3 ms | 34,5 ms | 536 ms |
| Sobrecoste | +8,8 % | +3,3 % | −1,8 % |

Con cincuenta formas en el catálogo en vez de dos: +11,9 %, +1,3 %, −0,6 %. El
sobrecoste se pierde en el ruido porque las formas se indexan por rol, así que
cada escritura consulta cero o una.

**El barrido a demanda, sobre 100.000 hechos:**

| Clase | Coste |
|---|---|
| Rango sobre un valor | 13,3 ms |
| Cardinalidad (por sujeto) | 5,6 ms |
| Unicidad (por rol) | 4,8 ms |
| Relacional (cruza dos roles) | 9,2 ms |

Las cuatro son lineales: el índice por rol las convierte en una pasada más un
conjunto hash. Un turno de modelo de lenguaje ronda los 2.000 ms, así que el
barrido completo es el 0,66 % de lo que el usuario ya está esperando.

**No medido, y de otra clase:** las formas que exigen recorrer caminos («que no
haya ciclos en `causado_por`»). Quedan fuera de esta entrega.

Conclusión: el rendimiento no decide nada. Decide la semántica.

## La decisión semántica

Bloquear la escritura contradiría el mundo abierto, que es lo que permite
modelar cualquier dominio sin un comité que apruebe cada concepto. Pero callar
hasta que alguien pregunte desperdicia una comprobación que es gratis.

La salida es la tercera: **comprobar al escribir, no rechazar nada y registrar
la violación como un hecho más**. La violación entra al grafo con su sujeto, su
forma, su momento y su vigencia. Se consulta como cualquier cosa, se cuenta, y
se cierra cuando el hecho que la causaba se corrige, con el mismo patrón de
estados que el capítulo 23 usa para los punchitems.

Una violación no es una excepción que interrumpe: es un hecho sobre un hecho.

## Las formas, como datos

Igual que la regla de derivación, la forma es una entidad del grafo:

```
(forma_disponibilidad, instancia_de,  forma_de_validacion)
(forma_disponibilidad, rol_objetivo,  "disponibilidad")
(forma_disponibilidad, tipo_forma,    rango)
(forma_disponibilidad, minimo,        0 K:Porcentaje)
(forma_disponibilidad, maximo,        100 K:Porcentaje)
```

Cuatro tipos, los que se midieron:

| Tipo | Qué comprueba |
|---|---|
| `rango` | El valor de un rol cae entre un mínimo y un máximo, respetando unidades |
| `cardinalidad` | Un sujeto tiene el rol entre N y M veces |
| `requiere` | Si un sujeto tiene el rol A, debe tener también el rol B |
| `unicidad` | El valor de un rol no se repite entre sujetos |

`rango` compara con el álgebra dimensional, así que un mínimo en gramos y un
valor en toneladas se comparan bien, y un mínimo en segundos contra un valor en
gramos falla como error de forma, no como violación.

## La violación, como hecho

```
(violacion_0001, instancia_de,     violacion_de_forma)
(violacion_0001, sobre,            sim_prod_jul_junio)
(violacion_0001, justificado_por,  forma_disponibilidad)
(violacion_0001, detalle,          "140.0 fuera de [0, 100]")
(violacion_0001, estado,           abierta)          valid_from = t0
(violacion_0001, estado,           resuelta)         valid_from = t1
```

El cierre no borra: añade un estado nuevo con su vigencia, y la violación queda
en el grafo con su historia. Preguntar por las violaciones abiertas hoy es
`ask(estado, at=hoy)`.

## API

```python
declarar_forma(u, "forma_disponibilidad", tipo="rango",
               rol="disponibilidad", minimo=..., maximo=...)

u.validate()                 # barrido; abre y cierra violaciones
u.validate(registrar=False)  # solo informa, no escribe
```

El gancho al escribir es **opcional** (`Universe(validar_al_escribir=True)`).
No se activa por defecto: cambiar la conducta de `assert_fact` para todo el
mundo por una función nueva sería imponer una decisión que cada dominio debe
tomar. La recursión se corta con una guarda: los hechos que el propio evaluador
escribe no se validan.

## Alcance

**Entra:** `wq/formas.py` con los cuatro tipos, `u.validate()`, el gancho
opcional, tests, y una demostración en el ejemplo del banco.

**No entra:** formas de camino o transitivas; el disparo condicional con
agregados (la otra mitad del Frente 1); la herramienta MCP.

## Capítulos

| Capítulo | Qué cambia |
|---|---|
| 5 · Los predicados | Sección nueva: la forma junto a la signatura. La signatura dice qué enchufe encaja; la forma, qué voltaje es aceptable |
| 19 · El banco | Demostración donde una restricción violada tiene consecuencias reales |
| 28 · Simulación | Recupera el escenario del 140 %, ahora en positivo: se guarda y queda registrado |
| 31 · Qué falta | Cierra la mitad de validación del Frente 1 |

## Verificación

Tests por tipo de forma, más: la violación se registra sin rechazar el hecho,
se cierra al corregirse, el evaluador no se valida a sí mismo, y una forma con
unidades incomparables falla como error y no como violación.
