# QUDT — Quantities, Units, Dimensions and Types

Documento de referencia sobre **QUDT**, la ontología canónica de cantidades, unidades, dimensiones y tipos para representación semántica de mediciones. Es el donante natural para la convención de WQuestions sobre **mediciones con unidad reificadas**.

## Datos bibliográficos

- **Sitio oficial**: https://qudt.org
- **Organización**: QUDT.org Inc., 501(c)(3) nonprofit.
- **Repositorio público**: https://github.com/qudt/qudt-public-repo
- **Versión actual**: QUDT 2.1.
- **Implementación**: OWL 2 + RDF/Turtle.
- **Base normativa**: BIPM International System of Units (SI), ISO Standards on Units and Quantities, NIST Guide for the use of SI.
- **Adopción**: NASA, NIST, Linked Data community, BioOntology BioPortal, Circular Economy Ontology Network, varios proyectos científicos.
- **Trabajo reciente**: *Using a units ontology to annotate pre-existing metadata* (Nature Scientific Data 2025).

## Motivación declarada

Las cantidades, las unidades, las dimensiones físicas y los tipos de datos son el núcleo de toda investigación científica y de ingeniería. Sin un vocabulario estándar:

- Cada sistema reinventa "kilogramo" y obligamos a integradores a hacer matching ad-hoc.
- Las conversiones de unidad son fuente constante de errores (Mars Climate Orbiter, anyone).
- No hay forma estándar de afirmar "esto es 5 ± 0.2 m" con incertidumbre.
- Los dominios mezclan unidades del mismo tipo (cm y pulgadas) sin sistema de conversión común.

QUDT provee una **ontología OWL completa** que estandariza estos conceptos para uso interoperable.

## Núcleo del framework

Cuatro conceptos primarios:

### QuantityKind

Una **propiedad observable medible**. Ejemplos:
- `Length`, `Mass`, `Time`, `Force`, `Energy`, `Power`, `ElectricCharge`.
- `Temperature`, `Pressure`, `Velocity`, `Acceleration`.
- `MolarMass`, `MagneticFlux`, `Frequency`.

Es una categoría abstracta de lo que se mide.

### Unit

Una **cantidad específica usada como escala**. Ejemplos:
- `Meter` (para `Length`).
- `Kilogram` (para `Mass`).
- `Second` (para `Time`).
- `Joule` (para `Energy`).
- `PEN`, `USD`, `EUR` (para `Currency`, si lo incluyera).

Cada unit pertenece a uno o más QuantityKinds y tiene factores de conversión a unidades base.

### Dimension

El **vector de exponentes** sobre dimensiones fundamentales. Por ejemplo, fuerza tiene dimensión `MLT^-2` (masa × longitud × tiempo⁻²). Permite verificar consistencia dimensional automáticamente.

### Scale

La **estructura matemática** del valor: ratio scale, interval scale, ordinal scale, nominal scale. Importante para saber qué operaciones son válidas (sumar centígrados es válido en intervalo, no en absoluto).

### Quantity Value

El **valor medido** con su unidad:

```turtle
:medicion_pres_sistolica
  rdf:type qudt:QuantityValue ;
  qudt:value 145.0 ;
  qudt:unit unit:MilliM_HG ;
  qudt:quantityKind quantitykind:BloodPressure ;
  qudt:standardUncertainty 5.0 .
```

## Características clave

- **Cobertura extensa**: cientos de QuantityKinds, miles de Units.
- **Verificación dimensional**: el sistema sabe que `Energy = Mass × Velocity²`.
- **Conversión automática**: 1 km = 1000 m, 1 pulgada = 2.54 cm.
- **Compatible con SI**: respeta el sistema internacional pero soporta sistemas alternativos (imperial, CGS, atómico).
- **Identificadores URI**: cada unit/quantityKind tiene un URI estable.
- **Multilingüe**: nombres de unidades en varios idiomas.
- **Estándar OWL**: integra con cualquier knowledge graph RDF/OWL.

## Aplicaciones

- **Bioinformática**: anotación de mediciones experimentales.
- **Ingeniería aeroespacial**: NASA usa QUDT internamente.
- **Ciencia abierta**: anotación de datasets para FAIR data.
- **Industria 4.0**: sensores IoT con metadatos QUDT.
- **Sistemas de salud**: signos vitales con unidades estándar.

## Posicionamiento frente a WQuestions

| Aspecto | QUDT | WQuestions actual |
|---|---|---|
| Alcance | Cantidades, unidades, dimensiones | Modelo general de información |
| Estructura | OWL/RDF, ontología completa | 8 ejes + catálogo de roles |
| Mediciones | QuantityValue (núcleo) | Convención de reificación |
| Catálogo | Cientos de QuantityKinds, miles de Units | Sin catálogo de mediciones propio |
| Conversiones | Automáticas, integradas | No definidas |
| Verificación dimensional | Soportada | No soportada |
| Incertidumbre | `qudt:standardUncertainty` | Mencionada en convención |

## Convergencias importantes

- **Reificación de la medición**: QUDT reifica cada medición como `QuantityValue` con propiedades. Esto es **exactamente** lo que propuso nuestra convención de mediciones reificadas. No es coincidencia: cualquier sistema serio termina ahí.

- **Distinción QuantityKind vs Unit**: QUDT separa "lo medido" (BloodPressure como categoría) de "la escala de medición" (mmHg como unidad). Esto refina nuestra convención: en WQuestions, el `tipo` y la `unidad` de una medición eran ambos K; QUDT confirma que son dos roles distintos en K.

- **OWL como vehículo**: QUDT vive en OWL, que es la tecnología compatible con la mayoría de stacks RDF que WQuestions podría usar.

## Divergencias importantes

- **Alcance**: QUDT es solo mediciones; WQuestions es información general. Son complementarios, no competidores.

- **Compromiso con OWL**: QUDT requiere stack semantic-web. WQuestions es agnóstico.

- **Profundidad**: QUDT tiene maquinaria dimensional rica que WQuestions no necesita ni quiere reinventar.

## Qué tomar prestado

- **TODO el vocabulario**: en vez de inventar `kilogramo`, `mmHg`, `kJ_mol` en nuestro K, usar los URIs de QUDT directamente. Esto da interoperabilidad inmediata.

- **La distinción QuantityKind / Unit / QuantityValue**: refinar nuestra convención de mediciones reificadas para incluir `tipo` (QuantityKind) y `unidad` (Unit) como roles separados, no fusionados.

- **El patrón de incertidumbre**: `standardUncertainty`, `relativeStandardUncertainty`, `confidenceInterval` son roles que WQuestions debería adoptar cuando reifique mediciones.

- **Las conversiones**: si WQuestions implementa motor de inferencia, las conversiones QUDT son reglas de derivación canónicas.

- **El compromiso con SI / ISO / NIST**: alineación con estándares internacionales — credibilidad inmediata.

## Qué NO tomar prestado

- **La complejidad OWL**: WQuestions no debe heredar el peso completo de OWL para soportar QUDT. Basta con que los URIs de QUDT vivan en K como individuos opacos; la maquinaria dimensional se delega al motor que use QUDT (cuando lo necesite).

- **El sesgo científico-ingenieril**: QUDT cubre bien mediciones físicas, no tan bien dimensiones sociales/legales (precios, plazos, calificaciones subjetivas). WQuestions debe complementar con sus propias K-categories para esos casos.

## Recomendación para WQuestions

**Agregar convención**: cuando se reifique una medición física/cuantitativa de naturaleza estándar, **usar URIs de QUDT** para las unidades y QuantityKinds en K, en lugar de strings ad-hoc.

```
ANTES (ad-hoc):
  (medicion_pres, valor,  145)
  (medicion_pres, unidad, "mmHg")
  (medicion_pres, tipo,   "presion_sistolica")

DESPUÉS (con QUDT):
  (medicion_pres, valor,        145)
  (medicion_pres, unidad,       qudt-unit:MilliM_HG)            // → K (URI QUDT)
  (medicion_pres, tipo,         qudt-qk:BloodPressureSystolic)  // → K (URI QUDT)
  (medicion_pres, incertidumbre, 5)
```

Esto es D8 aplicado a unidades: QUDT vive abajo (capa de canónico de mediciones); el usuario habla "presión 145 mmHg" en la capa superior.

## Conclusión

QUDT es la **infraestructura terminológica estándar** para mediciones cuantitativas, y se integra perfectamente con WQuestions vía D8 (canónico interno) y la convención de mediciones reificadas. Adoptar QUDT como vocabulario K para unidades es **ganancia neta**: 0 costo conceptual, máximo beneficio en interoperabilidad y credibilidad.

Para WQuestions:

1. **Vocabulario donante completo** para K-mediciones: cientos de QuantityKinds, miles de Units listos.
2. **Validación del patrón reificación**: el ecosistema científico ya converge a la misma solución.
3. **Puente a sistemas científicos**: cualquier dataset anotado con QUDT puede integrarse a WQuestions sin retraducción.
4. **Resistencia a errores**: verificación dimensional automática cuando exista capa de inferencia.
