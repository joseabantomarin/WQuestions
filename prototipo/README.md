# Prototipo WQuestions — informe de validación

Prototipo en Python (Python 3.9+). El núcleo `wq` no tiene dependencias; el
aplanado a tablas (`wq/vistas.py`) y el ejemplo `tabla_cap8.py` usan `pandas`. Que
implementa lo que el libro describe del modelo: los 8 ejes, los hechos
atómicos con signatura, la reificación de situaciones, el catálogo
canónico de roles, el lexicon con resolución de polisemia, D9 (vigencia
temporal), las cuatro relaciones del "por qué" y un motor de consulta
por proyección sobre roles.

Objetivo: **validar la arquitectura con código real**, no construir
producción.

## Cómo correr

```bash
cd /Users/joseabanto/WQuestions/prototipo

# Suite de tests unitarios (21 tests)
PYTHONPATH=. python3 -m unittest tests.test_wq -v

# Demo extremo a extremo del dominio spa (10 validaciones)
PYTHONPATH=. python3 ejemplos/spa.py

# Validación de fricciones en los 8 dominios previos (17 comprobaciones)
PYTHONPATH=. python3 ejemplos/dominios_previos.py

# Instalar la dependencia del aplanado a tablas
python3 -m pip install -r requirements.txt

# Las tres vistas del cap. 8 (plana / proyección / pivote) sobre ~336 trámites
PYTHONPATH=. python3 ejemplos/tabla_cap8.py
```

## Estructura

```
wq/
  axes.py       Los 8 ejes (Q, O, L, T, N, K, P, M) como enum.
  individual.py Individuo (vive en un eje de valor) + helpers (category, quantity, time_point).
  fact.py       Hecho atómico (sujeto, rol, valor) + vigencia D9.
  universe.py   Almacén en memoria con índices por sujeto/rol/valor.
  catalog.py    D7 — 38 roles canónicos con signatura tipada + validación.
  lexicon.py    Entradas, polisemia (patrón más específico primero), nominalización, dialectos.
  ingest.py     verbo + roles → situación reificada + hechos atómicos.
  query.py      Patrones WH como proyecciones sobre roles, con filtro temporal `at`.

ejemplos/
  spa.py            Dominio spa completo (3 clientes, 16 sesiones, plan, fidelidad, D9).
  dominios_previos.py Valida fricciones en aeropuerto, ventas, taxi, clínica,
                      música, contrato, química, fútbol.

tests/
  test_wq.py    21 tests unitarios cubriendo ejes, signaturas, lexicon,
                modales, queries, D9, spa end-to-end.
```

## Resultados de validación

| Suite                              | Pasa | Total |
| ---------------------------------- | ---- | ----- |
| Tests unitarios (`tests/test_wq.py`)  | 21   | 21    |
| Spa end-to-end (`ejemplos/spa.py`) | 10   | 10    |
| 8 dominios previos (`ejemplos/dominios_previos.py`) | 17 | 17 |

Capacidades validadas:

- **Validación de signatura**: el catálogo rechaza un hecho con valor en eje
  equivocado (`(situ, agente, ciudad_a)` → `SignatureError`).
- **Polisemia por especificidad**: `tomar [sesion]` → `servicio_spa`,
  `tomar [el_pelo]` → `accion_bromear`, `tomar` solo → `accion_tomar`.
  Igual para `dar [la_mano]` vs `dar [conferencia]` vs `dar` genérico.
- **Nominalización**: `contratación` (forma nominal) resuelve a la
  misma entrada que `contratar` (verbo).
- **Modal como decorador**: `Juan quiere viajar` produce UNA situación
  con `modalidad: volitiva` y `estatus_factual: intencionado`, no dos.
- **D9 vigencia temporal**: la residencia de Marta/Carlos cambiada en 2026
  se consulta correctamente "en 2018" → ciudad_a, "en 2027" → ciudad_b,
  con la misma estructura de query sólo cambiando el parámetro `at`.
- **Cuatro relaciones del por qué**: `causado_por`, `motivado_por`,
  `con_finalidad`, `justificado_por` operan como tripletas regulares O → O.
- **WH-queries**: `¿quién dio el libro a María?` se traduce a un `Pattern`
  con un `Var` y devuelve el agente.
- **Estado derivado**: contar las sesiones de Ana para evaluar la regla
  "7 visitas → 1 gratis" funciona como agregación sobre el grafo.
- **Política liberal de roles**: roles no canónicos (`producto`, `insumo`,
  `tripulante`, `asistencia`, `frecuencia`) se aceptan sin validación,
  habilitando dialectos de dominio sin tocar el catálogo.

## Fricciones reales encontradas mientras codificaba

Estas son fricciones que el prototipo expuso al construir el spa y los
demás dominios — no estaban todas en el libro. Cuatro de cinco son
**ajustes de uso, no del modelo**; la quinta es una fricción real ya
documentada.

### F1 — `tema` espera O, pero a veces lo contratado es una categoría K

**Síntoma**: `Carlos contrata plan_mensual` con `plan_mensual` como K
(`category("plan_gym_mensual")`) → `SignatureError` en `tema: O → O`.

**Causa**: ambigüedad entre **categorías de servicio** (K, atemporales)
y **ofertas reificadas del negocio** (O, instancias concretas que el
negocio comercializa).

**Solución aplicada**: reificar la oferta como O con `instancia_de:
tipo_oferta_servicio`. El plan que Carlos contrata es entonces un O,
no un K. Es más correcto semánticamente (la oferta del Spa Oasis es
una entidad concreta del negocio) y evita el patch al catálogo.

**Implicación para el libro**: vale la pena explicitar en Parte V que
las ofertas comerciales se reifican como O, no como K. Es sutil.

### F2 — `(persona, lugar_de, ciudad)` no es modelable directamente

**Síntoma**: intenté escribir `(carlos, lugar_de, ciudad_a)` para
"Carlos vive en ciudad_a" → `SignatureError` (lugar_de espera sujeto O).

**Causa**: lugar_de es propiedad de **situaciones**, no de personas.
Una persona que vive en una ciudad participa de una **residencia**
(situación reificada en O) que tiene lugar_de.

**Solución aplicada**: reificar `residencia_001 ∈ O` con `agente: carlos`
y `lugar_de: ciudad_a`. Esto es lo que el cap 10 ya describía con la
residencia de Marta. El prototipo me obligó a aplicar la convención.

**Implicación**: D5 + D9 + reificación de situaciones de estado producen
un modelo más rico que las relaciones planas Q-L. Esto debería quedar
nítido en algún ejemplo de la Parte V (residencia de un cliente del
spa a través del tiempo).

### F3 — Consultas de conteo necesitan `ask` vacío

**Síntoma**: para contar sesiones de Ana no quiero proyectar ningún
rol; solo contar matches. Mi `Pattern` exigía al menos una `Var`.

**Solución aplicada**: permitir `ask={}` y devolver bindings con sólo
`_subject`. El llamador hace `len(...)` o usa la helper `count(...)`.

**Implicación**: API de consulta más limpia. Documentado.

### F4 — Fricción documentada en química #2 (paciente: O → Q) — CONFIRMADA

El prototipo confirma la fricción documentada: `paciente` declarado como
`O → Q` rechaza el valor `CH4_qty` (en N). El patch propuesto (relajar `paciente` a `O → V`) sigue siendo válido. Mientras
no se aplique, el dominio químico se modela con roles de dominio
(`insumo`, `reactivo`, `producto_reaccion`) que la política liberal admite.

### F5 — Fricción documentada en música #1 (obra como K) — CONFIRMADA

`tema: O → O` rechaza una obra musical en K. Solución de dominio
(`obra_interpretada: O → K`) funciona sin parche al catálogo. El libro
podría considerar si vale la pena canonizar `obra_interpretada` como
patrón típico de "ejecución de algo categorial".

## Observaciones de diseño

1. **La política liberal vale oro.** Permitir que roles no declarados
   pasen sin validación habilitó que los 8 dominios se modelaran sin
   patches del catálogo. Sin ella, cada dominio nuevo exigiría editar
   `catalog.py`. Con ella, el catálogo es una *base* y los dominios la
   extienden.

2. **La reificación es asimétrica respecto a costo cognitivo.** Las
   situaciones que no se reifican generan código más corto pero
   bloquean D9. Cuando descubrí en el spa que quería consultar
   "¿dónde vivía Carlos en 2022?" tuve que volver atrás y reificar
   la residencia. Vale la pena reificar generosamente desde el inicio
   si hay sospecha de evolución temporal.

3. **El evaluador externo es una necesidad, no una hipótesis.** Las
   reglas "7 visitas → 1 gratis", "rescisión por impago", "marcador como
   suma de goles" son todas formas del mismo patrón. El prototipo las
   modela todas como datos (regla reificada en O), pero **no las dispara
   solo**. Una implementación productiva necesitaría una capa de
   evaluación encima del grafo.

4. **El tipado de los ejes paga por sí mismo.** La validación de
   signaturas detectó dos errores reales (F1 y F2) que de otro modo
   habrían pasado desapercibidos hasta una consulta mal armada. Sin
   `SignatureError` el modelo se llena rápidamente de hechos
   sintácticamente válidos pero semánticamente sin sentido.

5. **184 hechos atómicos cubren un día de operación de un spa chico.**
   Tres clientes, 16 sesiones, un plan mensual, una cadena causal y dos
   residencias temporales: 184 hechos, 111 individuos, 7 verbos en el
   lexicon. Esto es comparable en densidad a lo que un schema relacional
   ad-hoc requeriría — y el grafo es consultable uniformemente.

## Lo que no se implementó (deliberadamente)

- **Persistencia**: el universo vive en memoria. Una capa SQLite/Kùzu
  es trabajo siguiente y no afecta la validación arquitectónica.
- **Inferencia automática**: las reglas se almacenan declarativamente
  pero no se disparan. Cf. observación #3.
- **Parser de español**: el lexicon usa entradas pre-resueltas
  (verbo + roles ya identificados). En producción el LLM/parser hace
  ese trabajo y le entrega al motor las situaciones estructuradas.
- **Bitemporalidad completa**: tenemos valid time (D9) y transaction
  time (en `Fact.tx_time`) pero no consultas tipo "¿qué sabíamos en
  T0?". Cf. decisión pendiente #4 del WQuestions.md.
- **UUID v7**: usamos ids cortos monotónicos para legibilidad. Trivial
  de reemplazar.
