# Capítulo 19 — Una universidad: timelines largos y grafos de dependencia

## Por qué la universidad es un dominio distinto

El ERP nos mostró cómo el modelo absorbe la integración cross-módulo de una empresa. La universidad pone sobre la mesa un tipo de complejidad muy distinta: **los tiempos son largos y las cosas dependen unas de otras**. Una carrera universitaria dura cinco años. Un estudiante atraviesa decenas de cursos, cada uno con sus prerequisitos, en una secuencia que es parcialmente libre y parcialmente forzada. Las personas cambian de rol a lo largo de su vida académica: ayer eran estudiantes, hoy son ayudantes de cátedra, mañana son docentes, pasado son investigadores principales. Las calificaciones se asignan, se reclaman, se rectifican — y el historial completo dura **toda la vida del egresado**.

Cualquier sistema universitario serio tiene que poder responder cosas como:

- *¿Qué calificación recibió Ana en Matemática I antes de su reclamo? ¿Y después de la rectificación?*
- *¿Qué cursos puede tomar Luis ahora, dado lo que ya aprobó?*
- *¿En qué cursos estuvo inscripto Pablo en el segundo semestre de 2024?*
- *¿Quiénes fueron los miembros del jurado de la tesis de María?*
- *¿Qué docente dictó Estructuras de Datos entre 2020 y 2026?*

Cada una de estas preguntas es trivial **siempre que el modelo se diseñe pensando en bitemporalidad, en grafos de dependencia y en personas que cargan múltiples roles**. En arquitecturas tradicionales — un sistema de matrícula con tablas relacionales —, cada una requiere agregar una tabla histórica o forzar consultas con `OUTER JOIN`s creativos. En WQuestions, **cada una es una consulta de uno o dos saltos sobre el grafo**.

Este capítulo modela seis escenarios del mundo académico, cada uno estresando una dimensión distinta del modelo.

## La arquitectura conceptual del dominio académico

Antes de meternos en los casos, el mapeo a las siete coordenadas:

- **Personas** (estudiantes, docentes, autoridades, miembros de jurado, la universidad misma como persona jurídica) viven en **Q**. Una sola persona puede aparecer en muchos roles distintos — D5 a pleno.
- **Carreras, semestres, cursos, inscripciones, evaluaciones, tesis, defensas, graduaciones** viven en **O**. Cada uno con identidad, momento de creación y trazabilidad.
- **Facultades, aulas, auditorios, campus** viven en **L** (forman jerarquías como cualquier organización territorial).
- **Fechas de inicio y fin de semestre, momentos de inscripción, fechas de defensa** viven en **T**.
- **Créditos, calificaciones numéricas, horas-semestre, montos de pago** viven en **N** con su unidad.
- **Tipos de carrera, estados de inscripción, modalidades de evaluación, niveles cualitativos (excelente/aprobado/desaprobado)** viven en **K**.

Las decisiones que más se ejercitan acá son: **D4** (la evaluación, la inscripción, la defensa son situaciones reificadas con sus participantes y momentos), **D5** (María es a la vez estudiante, asistente docente y tesista — el modelo no obliga a duplicar al individuo), **D6** (calificaciones, inscripciones y estados cambian en el tiempo y se preservan), **D7** (la rectificación está `motivado_por` el reclamo y `rectifica` la evaluación original; la graduación está `justificado_por` la defensa).

## Caso 1 — La estructura académica jerárquica

La organización académica forma una jerarquía limpia que el modelo absorbe con `parte_de`:

```
carrera_ing_sistemas
└── primer_anio_is
    ├── semestre_2026_i
    │   ├── curso_mate1
    │   └── curso_intro_prog
    └── semestre_2026_ii
        ├── curso_mate2
        └── curso_estr_datos
```

Cada nivel es una entidad en O. Cada uno **es parte de** el nivel superior:

```python
u.assert_fact(primer_anio, "parte_de", carrera_is)
u.assert_fact(sem_2026_i, "parte_de", primer_anio)
u.assert_fact(mate1, "parte_de", sem_2026_i)
```

Tres tripletas y la jerarquía completa de la carrera. Cuando un estudiante pregunta *"¿qué cursos hay en mi semestre actual?"*, la consulta es: encuentra todas las entidades en O cuya `parte_de` sea el semestre del estudiante. Un único salto.

Cada curso, además de ser parte de un semestre, lleva sus propios atributos: créditos (en N), docente (`agente` apuntando a Q), aula (`lugar_de` apuntando a L). Y por supuesto un nombre, un código, un syllabus. Todo el inventario académico vive con la misma forma.

## Caso 2 — Prerequisitos como grafo dirigido acíclico (DAG)

El segundo gran patrón del mundo académico es **la malla curricular**: el conjunto de reglas que dicta qué cursos son requisito de qué otros. Es un DAG por naturaleza — sin ciclos, con muchas dependencias cruzadas.

En sistemas tradicionales, esto se modela con una tabla `curso_prereq(curso_id, prereq_id)` y consultas recursivas con `WITH RECURSIVE`. En WQuestions, **cada prerequisito es una tripleta**:

```python
u.assert_fact(mate2,             "requiere_prerequisito", mate1)
u.assert_fact(estructuras_datos, "requiere_prerequisito", intro_prog)
u.assert_fact(algoritmos,        "requiere_prerequisito", mate2)
u.assert_fact(algoritmos,        "requiere_prerequisito", estructuras_datos)
```

Algoritmos Avanzados requiere **dos** prerequisitos simultáneos — uno de cada línea (matemática + programación). El modelo lo absorbe sin problema porque `requiere_prerequisito` es un rol multi-valor (M, no funcional).

![DAG de prerequisitos académicos: cada curso es un individuo en O; cada arista es una tripleta `requiere_prerequisito`. Algoritmos Avanzados depende simultáneamente de Matemática II y Estructuras de Datos, una dependencia que el modelo expresa con dos hechos atómicos independientes. La consulta *"¿puedo inscribirme a Algoritmos?"* es un recorrido sobre el grafo de aprobados del estudiante.](../diagrams/png/46_universidad_dag_prereqs.png)

La consulta crítica del modelo — *"¿qué cursos puede tomar Luis este semestre?"* — se vuelve un recorrido directo sobre el grafo: para cada curso del semestre actual, verifica que **todos** sus prerequisitos tengan, en el historial de Luis, una situación de evaluación con `estatus_factual = aprobado`. Si falta uno, el curso queda excluido. No hay tabla intermedia, no hay JOIN, no hay procedimiento almacenado. **Un recorrido y un filtro.**

## Caso 3 — Inscripciones con vigencia (D6)

Ana se inscribe en Matemática I el 10 de marzo. Luis también, dos días después. Pero Luis abandona el curso a mediados de abril. ¿Cómo modelar esto sin perder información?

La trampa clásica es usar una columna `estado` en la tabla de matrículas y *actualizarla* cuando alguien abandona. El problema: si en julio alguien pregunta *"¿quiénes estaban inscriptos el 1 de abril?"*, no hay forma de responder fielmente — la actualización borró el estado anterior.

En WQuestions, los dos estados **conviven** en el grafo, separados por vigencia:

```python
u.assert_fact(insc_luis, "estado", vigente,
              valid_from=t_inscripcion, valid_to=t_cancelacion)
u.assert_fact(insc_luis, "estado", cancelada,
              valid_from=t_cancelacion)
```

La pregunta *"¿estaba Luis inscripto el 1 de abril?"* es directa: una consulta con `at=2026-04-01` filtra por vigencia y devuelve `vigente`. La misma consulta con `at=2026-05-01` devuelve `cancelada`. Sin esfuerzo extra, sin tabla histórica auxiliar. La inscripción nunca se borra; cambia de estado y el historial queda.

## Caso 4 — Una persona, varios roles a lo largo del tiempo

Una verdad incómoda del mundo académico: las personas no son solo *una cosa*. María es estudiante de cuarto año Y, al mismo tiempo, jefa de práctica del curso de Introducción a la Programación. En unos años será docente titular; en otros, directora de tesis; en otros, decana. **Es la misma persona** — un solo individuo en Q —, pero ocupa roles distintos en situaciones distintas.

En sistemas tradicionales esto es notoriamente difícil. Una tabla `estudiantes` y otra `docentes` con `foreign keys` cruzadas. Y cuando un estudiante se vuelve docente, alguien tiene que sincronizar — o el sistema se confunde.

En WQuestions el problema **no existe**. María es `est_maria`, un individuo en Q. Aparece como agente en una inscripción (rol *estudiante*), como agente en una asignación TA (rol *jefe de práctica*), como agente en una tesis (rol *tesista*), como agente en una defensa (rol *defendiente*). Cada rol vive en su situación. El sistema no distingue entre "tipos de personas"; distingue entre tipos de situaciones.

```python
# María como estudiante
ingest_situation("inscribir", roles={"agente": maria, "tema": estructuras_datos})

# María como jefa de práctica
u.assert_fact(asignacion_ta, "agente", maria)
u.assert_fact(asignacion_ta, "rol_funcional",
              category("jefe_de_practica"))

# María como tesista
ingest_situation("defender_tesis", roles={"agente": maria, "tema": tesis})
```

Cuando el sistema pregunta *"¿qué actividades hizo María este año?"*, la consulta es una sola: buscá todas las situaciones donde María sea `agente` y proyectá su `instancia_de`. La respuesta sale del grafo de forma natural — y abarca lo académico, lo docente y lo investigativo en una sola lista.

## Caso 5 — La cadena calificación → reclamo → rectificación

Acá viene el caso emblemático del audit trail académico. Ana rinde su examen final de Matemática I el 15 de julio. La Dra. López corrige y le pone 12 puntos. Ana revisa el examen, no está de acuerdo con la corrección de una pregunta, presenta un reclamo formal el 20 de julio. La docente revisa, le da la razón, y el 25 de julio rectifica la nota a 14 puntos.

En sistemas tradicionales, la nota se **sobreescribe**. El historial — si existe — vive en una tabla auxiliar que la mayoría de las facultades no consulta nunca. Cuando años después alguien quiere reconstruir el incidente — un decano que revisa una queja, un comité de calidad académica que audita —, el rastro está borroso.

En WQuestions, las tres situaciones **conviven** en el grafo:

1. La **evaluación inicial** es una situación reificada con su agente (la docente), su paciente (la estudiante), su `puntaje` y su `momento`.
2. El **reclamo** es otra situación, agente=Ana, `tema`=evaluación, `motivado_por`=motivo específico.
3. La **rectificación** es una tercera situación, agente=docente, `tema`=evaluación, `motivado_por`=reclamo, `rectifica`=evaluación.

```python
rectificacion = ingest_situation("rectificar_nota", roles={
    "agente": dra_lopez,
    "tema": evaluacion,
    "puntaje": nota_14,
    "motivado_por": reclamo,
})
u.assert_fact(rectificacion, "rectifica", evaluacion)
```

Y la calificación vigente cambia con bitemporalidad (D6): la nota era 12 entre el 15 y el 25 de julio; desde el 25 es 14.

```python
u.assert_fact(evaluacion, "puntaje_vigente", nota_12,
              valid_from=t_eval, valid_to=t_rect)
u.assert_fact(evaluacion, "puntaje_vigente", nota_14,
              valid_from=t_rect)
```

Las dos versiones existen en el grafo. La consulta `at=2026-07-18` devuelve 12; `at=2026-07-30` devuelve 14. El reclamo está en el grafo, sigue siendo consultable años después, y la cadena causal está explícita: la rectificación está `motivado_por` el reclamo, y `rectifica` la evaluación original. Si dentro de cinco años alguien revisa el caso de Ana, el grafo le entrega la historia completa sin gimnasia.

## Caso 6 — Defensa de tesis con director y jurado

El último escenario es la defensa de tesis de María. Una tesis es una situación de larga duración (un año, en su caso) con múltiples participantes:

- La **tesista** (María, agente principal)
- El **director de tesis** (Dra. Díaz, rol específico del dominio)
- Tres **miembros del jurado** (Decano García como presidente, Dra. López como vocal, Dr. Morales como secretario)

En sistemas tradicionales, esto exige una tabla `tesis_participantes` con un `tipo` discriminador. En WQuestions, **cada rol es una tripleta separada**:

```python
u.assert_fact(tesis, "agente", maria)
u.assert_fact(tesis, "director_tesis", dra_diaz)
u.assert_fact(defensa, "jurado_presidente", decano)
u.assert_fact(defensa, "jurado_vocal", dra_lopez)
u.assert_fact(defensa, "jurado_secretario", dr_morales)
```

`director_tesis`, `jurado_presidente`, `jurado_vocal`, `jurado_secretario` son roles de dominio académico. Ninguno está en el catálogo D8 — la política liberal los acepta sin protestar, y mientras el dominio universitario los use consistentemente, el modelo opera con ellos como si fueran canónicos.

La graduación final es una situación con `justificado_por` apuntando a la defensa: María se graduó **porque** defendió exitosamente su tesis. El grafo deja la cadena causal explícita.

## Resultado del prototipo

El ejemplo Python que acompaña el capítulo ([`prototipo/ejemplos/universidad.py`](https://github.com/joseabantomarin/WQuestions/blob/main/prototipo/ejemplos/universidad.py)) materializa los seis casos con 80 individuos en 6 ejes y 102 hechos atómicos. Las once validaciones pasan:

```
✓  Jerarquía académica: curso → semestre → año → carrera
✓  DAG de prerequisitos: algoritmos requiere mate2 + estructuras_datos
✓  Múltiples roles de una persona: María es estudiante Y TA Y tesista
✓  D6: inscripción de Luis vigente el 30-Mar, cancelada el 30-Abr
✓  Calificación bitemporal: nota=12 el 18-Jul, nota=14 el 30-Jul
✓  D7: rectificación motivada_por reclamo y rectifica evaluación original
✓  Defensa de tesis: 3 miembros de jurado con roles distintos
✓  Graduación justificada_por la defensa exitosa
✓  WH: ¿quién dicta Matemática I?
✓  WH bitemporal: ¿quiénes seguían inscriptos en Mate I el 1-Mayo?
✓  Política liberal: jurado_presidente / jurado_vocal / jurado_secretario aceptados sin declarar

Resultado: 11/11 validaciones pasadas.
```

## Qué quedó probado en este capítulo

El sistema universitario es probablemente el dominio donde el **timeline largo** y los **grafos de dependencia** se vuelven el problema central, no un detalle accesorio. El modelo absorbe ambas cosas con su maquinaria estándar: la bitemporalidad (D6) deja todas las inscripciones, calificaciones y estados con su historial intacto durante toda la vida académica del egresado. El catálogo D8 con su política liberal admite roles tan específicos como `jurado_secretario`, `director_tesis` o `requiere_prerequisito` sin que el motor tenga que cambiar nada. Una persona puede ser estudiante, docente y tesista a la vez — el grafo no distingue tipos de personas, distingue tipos de situaciones (D5).

Y, otra vez, **el motor no creció ni una línea** para absorber el dominio. Lo único que creció fue el lexicon — siete verbos (`inscribir`, `dictar`, `evaluar`, `reclamar`, `rectificar_nota`, `graduar`, `defender_tesis`) con sus signaturas, más un dialecto de dominio que mapea "estudiante", "docente", "tesista", "director_tesis" a sus roles canónicos.
