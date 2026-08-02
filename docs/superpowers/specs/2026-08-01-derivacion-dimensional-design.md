# Derivación dimensional — primera rebanada del Frente 1

Diseño validado · 2026-08-01

## Qué problema resuelve

El capítulo 28 declara un límite: «el grafo no calcula». El Frente 1 del capítulo 31
lo confirma y estima el motor de inferencia completo en tres a seis meses. Esta es
la rebanada más pequeña que produce un hecho derivado y auditable, y que toda
inferencia posterior necesitará por debajo.

El zócalo ya existe. `prototipo/ejemplos/minera.py:238` declara
`(produccion_oro, calculado_de, extraccion)` y escribe el 685,8 a mano dos líneas
más arriba. Esta entrega llena ese zócalo.

## Por qué es aritmética dimensional, no evaluación de fórmulas

Las magnitudes de WQuestions llevan unidad obligatoria (regla del eje N, cap. 4).
Un motor que multiplique sin mirar unidades produce hechos numéricamente
correctos y dimensionalmente falsos, que es peor que no calcular: es el accidente
de las turbinas con el que abre el capítulo 4.

Hoy nada del prototipo sabe que toneladas × (gramos/tonelada) da gramos.

## Estado de partida

- El MCP guarda bien las magnitudes: `payload = {"value": …, "unit": <id de K>}`,
  y rechaza una N sin unidad existente en K.
- Los ejemplos del prototipo van sueltos: el helper `n()` de `minera.py` mete la
  unidad como cadena libre (`"toneladas"`) y además cuelga un rol `unidad`
  redundante de la situación. Se alinean con la forma del MCP.
- Las unidades en K son categorías opacas, sin dimensión ni factor.
- Verificado: una entidad de K puede ser sujeto de hechos bajo la política
  liberal, sin tocar el catálogo.

## Las tres capas

### Capa 1 · La unidad deja de ser opaca

Sigue el JSON que el capítulo 4 ya publica para `K:USD` (`ancla_qudt`,
`dimension`, `convertir_a`), expresado como tripletas:

```
(K:ToneladaMetrica,   ancla_qudt,    "qudt:unit/TONNE")
(K:ToneladaMetrica,   unidad_base,   K:Gramo)
(K:ToneladaMetrica,   factor_a_base, 1e6)

(K:GramoPorTonelada,  numerador,     K:Gramo)
(K:GramoPorTonelada,  denominador,   K:ToneladaMetrica)
```

La tabla de conversiones vive en el grafo, no en el código. Un dominio puede
añadir `K:token` o `K:USD_por_millon_tokens` sin tocar Python, que es lo que el
capítulo 4 exige para las unidades que QUDT todavía no cataloga.

### Capa 2 · El álgebra — `wq/magnitud.py`

Sin dependencias externas. `pint` queda descartado a propósito: el prototipo no
tiene dependencias y una biblioteca movería el conocimiento de las unidades
fuera del grafo.

Una unidad se reduce a exponentes sobre unidades base más un factor:

| Unidad | Exponentes | Factor |
|---|---|---|
| `K:Gramo` | `{gramo: 1}` | 1 |
| `K:ToneladaMetrica` | `{gramo: 1}` | 1e6 |
| `K:OnzaTroy` | `{gramo: 1}` | 31,1034768 |
| `K:GramoPorTonelada` | `{}` (adimensional) | 1e−6 |

Operaciones: producto y cociente combinan exponentes; suma y resta los exigen
idénticos y fallan si no; `convertir_a` exige exponentes iguales al destino.

### Capa 3 · La regla de derivación

La regla es una entidad, como el `regla_desgaste_camion` del capítulo 28:

```
(regla_oro_fino, instancia_de,    regla_de_derivacion)
(regla_oro_fino, expresion,       "monto * ley_mineral")
(regla_oro_fino, unidad_destino,  K:OnzaTroy)
(regla_oro_fino, aplica_a,        accion_extraer_mineral)
```

La expresión es una cadena de nombres de rol separados por `*` o `/`, evaluada de
izquierda a derecha. Sin paréntesis y sin constantes: si hace falta un factor,
se declara como magnitud y se referencia por su rol.

API, siguiendo la forma que el capítulo 31 anuncia:

```python
u.derive(regla, sobre=extraccion, destino_id="prod_oro_extr_001")
```

Escribe el resultado con su procedencia:

```
(prod_oro_extr_001, monto,           685.7 K:OnzaTroy)
(prod_oro_extr_001, calculado_de,    extr_001)
(prod_oro_extr_001, justificado_por, regla_oro_fino)
```

## Consecuencia sobre el libro

Con el factor exacto de QUDT la cuenta da **685,7 onzas**; el libro publica
**685,8**, que sale de redondear la onza troy a 31,1. Se corrigen las dos
menciones (cap. 23 y cap. 28) y se regenera el PDF. El libro se apoya en QUDT
explícitamente y presume de factores exactos, así que publicar un número nacido
de redondear la constante contradice su propio argumento.

## Alcance

**Entra:** las tres capas con tests; el `produccion_oro` de la minera pasa a
derivarse de verdad; corrección del 685,8 en los dos capítulos.

**No entra:** condiciones ni reglas con antecedente. «Siete sesiones cumplidas,
la octava gratis» necesita conteo y disparo condicional, y eso es el Frente 1
propiamente dicho. Tampoco entra la herramienta MCP: se expone cuando la API
esté asentada.

## Verificación

- Tests del álgebra: producto, cociente, suma coherente, suma incoherente que
  debe fallar, conversión, unidad compuesta, unidad desconocida.
- Test de la derivación: el oro de la minera calculado da 685,7 y lleva sus dos
  cables de procedencia.
- Las 18 validaciones de minera y los 34 tests existentes siguen pasando.
