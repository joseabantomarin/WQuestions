# Modelos bitemporales — Snodgrass y descendencia

Documento de referencia sobre la tradición bitemporal en bases de datos y grafos de conocimiento. Es el refinamiento natural de **D9** (validez temporal): donde D9 captura *valid time*, los modelos bitemporales agregan una segunda dimensión, *transaction time*, que captura *cuándo se afirmó* un hecho (no solo cuándo es cierto).

## Datos bibliográficos

- **Fundacional**: Snodgrass, R. (2000) — *Developing Time-Oriented Database Applications in SQL*. Morgan Kaufmann.
- **Survey**: Snodgrass, R. T. & Ahn, I. (1986) — *Temporal Databases*.
- **Estándar**: SQL:2011 incorpora la distinción valid/transaction time como estándar ISO/IEC 9075.
- **Extensión a RDF**: *Time Travel with the BiTemporal RDF Model* (MDPI 2025).
- **Extensión a property graphs**: *Bitemporal Property Graphs: Dealing with Both Valid and Transaction Time* (Springer/ADBIS 2024).
- **Variante probabilística**: *Towards Probabilistic Bitemporal Knowledge Graphs* (ACM 2018).
- **Introducción práctica**: Martin Fowler — *Bitemporal History*. https://martinfowler.com/articles/bitemporal-history.html

## Motivación declarada

Una base de datos tradicional almacena "lo que es cierto ahora". Un modelo con *valid time* almacena "lo que fue cierto cuándo en el mundo". Un modelo bitemporal **completo** almacena además "lo que el sistema sabía/afirmaba cuándo".

La diferencia importa cuando:
- Se corrigen errores históricos (un hecho registrado mal en 2024 se descubre en 2026).
- Hay obligaciones legales de retención y auditoría.
- Se necesita responder "¿qué sabíamos en marzo cuando tomamos esa decisión?".
- Se modelan retractaciones, actualizaciones de información, descubrimientos posteriores.

Ejemplo clásico:

> En 2010, el sistema afirma que Juan vive en Chile desde 2008.
> En 2026, se descubre que en realidad se mudó a Chile en 2007.
> El hecho histórico cambió, pero el sistema necesita registrar **ambos**: lo que sabía en 2010 (vivía en Chile desde 2008) y lo que sabe ahora (vivía en Chile desde 2007).

## Núcleo formal

Cada hecho `f` tiene cuatro coordenadas temporales (no dos):

```
valid_from         — cuándo el hecho es cierto en el mundo (inicio)
valid_to           — cuándo deja de ser cierto en el mundo (fin)
transaction_from   — cuándo el sistema afirmó este hecho
transaction_to     — cuándo el sistema retractó/superseded este hecho
```

Un hecho retractado **no se borra**: se cierra su `transaction_to` y se crea un nuevo hecho con el contenido corregido. Esto permite reconstruir "lo que el sistema sabía en cualquier momento" sin pérdida de información.

## Características clave

- **Inmutabilidad total**: nada se borra; las correcciones son nuevos hechos.
- **Time travel**: se puede consultar el estado del sistema en cualquier momento del pasado.
- **Auditoría completa**: trazabilidad legal para cumplimiento normativo.
- **Soporte para retractación**: distinguir "no era cierto" de "no lo sabíamos".
- **Compatibilidad SQL:2011**: PERIOD FOR VALID_TIME y PERIOD FOR SYSTEM_TIME son parte del estándar.

## Aplicaciones

- Sistemas financieros (banca, contabilidad) — auditoría regulatoria.
- Sistemas de historia clínica — corrección de diagnósticos sin perder historia.
- Sistemas legales — versiones de contratos, modificaciones.
- Knowledge graphs académicos — versionado de afirmaciones científicas.
- Sistemas de inmigración / identidad — corrección de datos personales con trazabilidad.

## Posicionamiento frente a WQuestions

| Aspecto | Modelos bitemporales | WQuestions actual |
|---|---|---|
| Valid time | `valid_from`/`valid_to` por hecho | D9: `inicio`/`fin` en situaciones reificadas |
| Transaction time | `transaction_from`/`transaction_to` por hecho | **No tiene** |
| Inmutabilidad | Total, axiomática | Convención (inmutabilidad), respetada |
| Retractación | Nativa | Vía `cancela`/`modifica` (no temporal-aware) |
| Time travel | Soportado por diseño | No directamente |
| Implementación | SQL:2011, BiTRDF, Property Graphs bitemporales | Pendiente |

## Convergencias importantes

- **Inmutabilidad como principio**: las convenciones de WQuestions ("hechos inmutables, cambios = nuevas situaciones") ya están alineadas con la filosofía bitemporal.

- **Valid time = D9**: lo que D9 cubre con `inicio`/`fin` es exactamente *valid time* en la tradición bitemporal. No hay conflicto, solo nomenclatura distinta.

- **Reificación de hechos cambiables**: bitemporal databases usan tablas con períodos; WQuestions usa situaciones reificadas con `inicio`/`fin`. Soluciones isomórficas al mismo problema.

## Divergencias importantes

- **Transaction time ausente en WQuestions**: hoy no podemos responder "¿qué sabíamos en marzo?". Para casos de auditoría legal, esto es deficiencia real.

- **Granularidad**: bitemporal database aplica las dos dimensiones a CADA hecho. WQuestions las aplica a *situaciones* (no a hechos atómicos). Esto puede ser limitación: si un hecho atómico aislado (ej. `dni` de Juan) se corrige, ¿necesitamos reificarlo como situación solo para auditarlo?

- **Madurez de implementación**: bitemporal databases tienen 30+ años de investigación, dos generaciones de optimizaciones, soporte de estándares. WQuestions todavía es modelo conceptual.

## Qué tomar prestado

- **El concepto de transaction time** como dimensión separada de valid time. Es la corrección obvia y útil a D9.

- **El patrón "no borrar, retractar con timestamp"** para correcciones. Coherente con nuestra convención de inmutabilidad pero más preciso.

- **Las primitivas SQL:2011** (PERIOD, FOR VALID_TIME, FOR SYSTEM_TIME) como nomenclatura cuando WQuestions necesite especificar implementación. Estándar reconocido.

- **El cálculo de Allen** (relaciones temporales: meets, overlaps, contains, before, after, equals) como vocabulario canónico para predicados temporales sobre situaciones.

- **De BiTRDF y Bitemporal Property Graphs**: los patrones de implementación cuando WQuestions se construya sobre stores tipo grafo.

## Qué NO tomar prestado

- **El compromiso con tablas y SQL**: WQuestions es agnóstico de stack. Bitemporal SQL es un patrón válido pero no obligatorio.

- **La granularidad por-tupla**: WQuestions opera sobre situaciones reificadas. Aplicar bitemporalidad a cada triple individual sería ruido sin beneficio para la mayoría de casos.

## Recomendación para WQuestions

Agregar una **decisión pendiente** sobre bitemporalidad completa:

> ¿Incorporar transaction time (cuándo se afirmó un hecho) como dimensión paralela a valid time (D9)? Necesario para auditoría legal, retractación trazable, y consultas "qué sabíamos cuándo". Posible patch: agregar `asercion_inicio`/`asercion_fin` a las situaciones reificadas, o reificar la afirmación misma como un O-individuo enlazado por `afirma`.

No promover a decisión inmediata; primero confirmar que los casos de uso lo justifican (probablemente sí en derecho y salud).

## Conclusión

La tradición bitemporal es el **complemento natural** de D9. WQuestions ya capturó la mitad fácil (valid time vía `inicio`/`fin`); la otra mitad (transaction time) está pendiente y bien resuelta en la literatura. Cuando WQuestions necesite auditoría legal real, esta línea provee 30 años de soluciones probadas listas para adoptar.

Para WQuestions:

1. **Validación filosófica de inmutabilidad**: la tradición bitemporal lleva 40 años probando que es la mejor base para sistemas serios.
2. **Roadmap claro de extensión**: cómo y cuándo agregar transaction time.
3. **Vocabulario y herramientas**: Snodgrass y SQL:2011 dan nomenclatura estable.
4. **Camino de implementación**: BiTRDF y Bitemporal Property Graphs son los stacks recomendados.
