# Anexo — Código del prototipo en Python

Este anexo recopila, en un solo lugar y por capítulo, **todos los fragmentos de código Python** que aparecen en la Parte V del libro (capítulos 14 al 19). El propósito es doble:

1. **Ser una referencia rápida para quien quiera implementar.** El lector que vaya a programar contra el prototipo no necesita ir saltando entre capítulos; aquí tiene el código consolidado, con suficiente contexto para entender cada bloque sin volver al texto.
2. **Servir como vista panorámica del estilo del modelo.** Mirar todo el código de la Parte V en una pasada permite ver patrones que el flujo capítulo-a-capítulo diluye: la uniformidad de la API, la economía de llamadas, la consistencia del catálogo.

Las APIs principales que aparecen a lo largo del anexo son cuatro:

- **`ingest_situation(u, lex, verbo, roles=…, complements=…, …)`** — crea una situación reificada en el universo `u`, resuelve el verbo en el lexicon `lex`, asienta los hechos atómicos correspondientes.
- **`u.assert_fact(sujeto, rol, valor, valid_from=…, valid_to=…)`** — agrega un hecho atómico directo al universo, con bitemporalidad opcional (D6).
- **`query(u, Pattern(fixed=…, ask=…, type_constraint=…), at=…)`** — consulta el grafo por un patrón de hechos. `at` proyecta la consulta a un momento de tiempo de validez.
- **`count(u, Pattern(…))`** — variante de `query` que solo devuelve la cardinalidad.

El prototipo completo vive en `prototipo/wq/` del repositorio. Lo que sigue son los fragmentos publicados en el libro, en orden de aparición.

---

## §15 — Spa comercial

### §15.1 — Crear una sesión articuladora

Ingesta de la sesión de Ana en la cámara de vapor 1 (situación reificada con cliente, lugar, ventana temporal y estatus factual). El parámetro `complements=["sesion"]` dispara la resolución de polisemia del verbo *tomar*: sin él, el sistema no sabría si "tomar" significa "tomar una sesión" o "tomar el pelo".

```python
sit = ingest_situation(u, lex, "tomar",
    roles={
        "cliente":  ana,
        "lugar_de": camara_vapor_1,
        "inicio":   t_inicio,
        "fin":      t_fin,
    },
    complements=["sesion"],          # dispara polisemia
    extra={"estatus_factual": finalizada},
    sit_id="sesion_ana_07",
)
```

### §15.2 — Registro de polisemia en el lexicon

Tres entradas del lexicon para el mismo verbo *tomar*. Cada una con su propio `pattern` (el complemento que la dispara) y su propio `situation_type`. El parser elige del más específico al más general.

```python
lex.register(LexiconEntry(
    verb="tomar",
    situation_type="servicio_spa",
    obligatory=["cliente", "lugar_de"],
    pattern=("sesion",),                  # dispara cuando el complemento es "sesion"
))

lex.register(LexiconEntry(
    verb="tomar",
    situation_type="accion_bromear",
    obligatory=["agente", "paciente"],
    pattern=("el_pelo",),                 # locución idiomática
))

lex.register(LexiconEntry(
    verb="tomar",
    situation_type="accion_tomar",
    obligatory=["agente", "tema"],
    notes="genérico — recibir/asir",
))
```

### §15.3 — Dialecto de dominio del spa

El dialecto activa los aliases del negocio del spa: cliente, sesión, plan mensual, sesión gratuita. El usuario habla en este vocabulario y el sistema traduce a los roles canónicos sin que se entere.

```python
lex.register_domain_dialect("spa_oasis", {
    "cliente":         "agente",
    "sesion":          "servicio_spa",
    "plan_mensual":    "contrato_servicio",
    "sesion_gratuita": "beneficio_fidelidad",
})
```

### §15.4 — Consulta: ¿cuántas sesiones lleva Ana este mes?

Patrón con sujeto fijo (Ana) y constraint de tipo (`servicio_spa`). El resultado es el conteo directo.

```python
n = count(u, Pattern(
    fixed={"cliente": ana, "estatus_factual": finalizada},
    type_constraint=u.ind("servicio_spa"),
))
# n == 8
```

### §15.5 — Consulta: ¿Ana califica para el beneficio?

Una decisión de negocio (regla "siete sesiones → una gratis") expresada como código Python que consume el resultado de la consulta anterior.

```python
qualifies = n >= 7
# True
```

### §15.6 — Consulta bitemporal: ¿dónde vivía Carlos en 2022?

Demostración de D6 (vigencia temporal): la misma consulta sobre el mismo individuo retorna respuestas distintas según el `at=` que se le pasa. Carlos vivió en ciudad_a hasta 2025 y luego se mudó a ciudad_b.

```python
res_2022 = query(u, Pattern(
    fixed={"agente": carlos},
    ask={"lugar_de": Var()},
    type_constraint=u.ind("residencia"),
), at=datetime(2022, 6, 1, tzinfo=timezone.utc))
# res_2022[0]["lugar_de"].id == "ciudad_a"

res_2027 = query(u, ..., at=datetime(2027, 6, 1, tzinfo=timezone.utc))
# res_2027[0]["lugar_de"].id == "ciudad_b"
```

---

## §16 — Servicio on-demand (app de taxi)

### §16.1 — Asignación con software como agente (D5)

El `agente` del verbo *asignar* es el app — no Valeria, no Luis. Cuatro participantes con roles distintos: app (agente, Q), solicitud previa (tema, O), conductor (beneficiario, Q), vehículo (instrumento, O). D5 en su forma más interesante.

```python
asig = ingest_situation(u, lex, "asignar", roles={
    "agente":       app,            # ¡APP COMO Q!
    "tema":         sol,            # asigna la solicitud previa
    "beneficiario": luis,           # al conductor disponible
    "instrumento":  vehiculo,       # con su vehículo
    "momento":      at(1),
}, sit_id="asig_001")
```

### §16.2 — Recuperar la cadena de un viaje

El viaje completo es una entidad superior que contiene las seis situaciones del recorrido (solicitar, asignar, aceptar, recoger, trasladar, completar) más la tarifa. Consultar `parte_de` con valor `viaje_001` devuelve toda la cadena.

```python
partes = [f.subject for f in u.facts_with_role("parte_de")
          if f.value.id == "viaje_001"]
# devuelve las 6 situaciones + la tarifa
```

### §16.3 — Surge pricing: causalidad emergente

El estado de alta demanda se reifica como una situación con su momento y lugar; la tarifa elevada queda explicada por `causado_por` apuntando a ese estado. Recuperar la explicación es un salto del grafo.

```python
estado_demanda = u.add_individual(Individual(
    id="alta_demanda_2026_05_16_14_30", axis=Axis.O,
    label="alta demanda 16/5 14:30"))
u.assert_fact(estado_demanda, "instancia_de", alta_demanda)
u.assert_fact(estado_demanda, "lugar_de", plaza)
u.assert_fact(estado_demanda, "momento", at(0))

tarifa = u.add_individual(Individual(id="tarifa_viaje_001", axis=Axis.O))
u.assert_fact(tarifa, "instancia_de", category("tarifa"))
u.assert_fact(tarifa, "monto", n_25_usd)
u.assert_fact(tarifa, "causado_por", estado_demanda)
```

### §16.4 — Cancelación como hecho nuevo (nunca borramos)

La convención del modelo es no borrar ni sobreescribir. Una cancelación es una situación nueva que `cancela` la previa y le pone `estatus_factual: cancelado`. El historial queda intacto.

```python
canc = ingest_situation(u, lex, "cancelar", roles={
    "agente":   valeria,
    "tema":     viaje2,
    "momento":  at(62),
}, sit_id="canc_001")
u.assert_fact(canc, "cancela", viaje2)
u.assert_fact(viaje2, "estatus_factual", cancelado)
```

### §16.5 — Consulta: ¿adónde llevó Luis a Valeria?

Patrón con agente y paciente fijos y `destino` como variable a resolver. Constraint de tipo `accion_trasladar`.

```python
r = query(u, Pattern(
    fixed={"agente": luis, "paciente": valeria},
    ask={"destino": Var()},
    type_constraint=u.ind("accion_trasladar"),
))
# r[0]["destino"].id == "aeropuerto"
```

### §16.6 — Consulta: ¿cuántos viajes completó Luis hoy?

Conteo con dos restricciones: agente y estatus factual. Filtra viajes en estado `completado`.

```python
n = count(u, Pattern(
    fixed={"agente": luis, "estatus_factual": completado},
    type_constraint=u.ind("viaje"),
))
```

### §16.7 — Recuperar la causa de una tarifa

Iteración manual sobre los hechos de la tarifa para encontrar el `causado_por`. Permite explicar al usuario por qué un viaje específico costó lo que costó.

```python
explicaciones = u.facts_about(tarifa_viaje_001)
causa = [f for f in explicaciones if f.role == "causado_por"]
# causa[0].value.id == "alta_demanda_2026_05_16_14_30"
```

---

## §17 — Historia clínica

### §17.1 — Roles de dominio que apuntan a K

En clínica, "el medicamento prescrito" no es un objeto físico individual (O) sino una categoría farmacológica (K). El catálogo canónico declara `tema: O → O`, así que el dominio agrega su propio rol `medicamento_prescrito: O → K` mediante la política liberal del catálogo. Lo mismo con `medida_de`.

```python
# El medicamento prescrito es una categoría (K), no un objeto.
u.assert_fact(pres, "medicamento_prescrito", enalapril)

# La variable medida es una categoría también.
u.assert_fact(medicion, "medida_de", presion_arterial)
```

### §17.2 — Rediagnóstico con vigencia temporal (D6)

Un diagnóstico se reemplaza por otro vía bitemporalidad. El primer diagnóstico es válido entre `t_consulta` y `t_redx`; el segundo, desde `t_redx` en adelante (sin `valid_to`). La relación `rectifica` deja la trazabilidad del cambio.

```python
# Diagnóstico original (vigente hasta el rediagnóstico)
u.assert_fact(diag, "diagnosticado_como", hta_g1,
              valid_from=t_consulta, valid_to=t_redx)

# Rediagnóstico (vigente desde T1, abierto al futuro)
u.assert_fact(diag2, "diagnosticado_como", hta_g2,
              valid_from=t_redx)
u.assert_fact(diag2, "rectifica", diag)
```

### §17.3 — Prescripción con motivo, finalidad y verificación normativa

Tres relaciones del "por qué" (D7) sobre la misma situación: `motivado_por` apunta al diagnóstico, `con_finalidad` al objetivo terapéutico, `verificado_contra` a la regla farmacológica que confirma que la prescripción no contradice una contraindicación. Las tres coexisten sin pisarse.

```python
pres = ingest_situation(u, lex, "prescribir", roles={
    "agente":                dra_torres,
    "paciente":              maria_g,
    "medicamento_prescrito": enalapril,
    "frecuencia":            cada_manana,
    "duracion":              indefinida,
    "momento":               at(0),
})

u.assert_fact(pres, "motivado_por",   diag)        # por qué se prescribió
u.assert_fact(pres, "con_finalidad",  objetivo)    # para qué se prescribió
u.assert_fact(pres, "verificado_contra", regla_contraindicacion)
```

---

## §18 — Banco regional

### §18.1 — Recuperar las dos contrapartidas contables de una transferencia

La transferencia operativa y los dos asientos contables (débito y crédito) son tres situaciones distintas ligadas por `parte_de`. Recuperar los asientos es un filtro adicional sobre la etiqueta.

```python
asientos = [f.subject for f in u.facts_with_role("parte_de")
            if f.value.id == "transferencia_001"
            and f.subject.label.startswith("asiento_")]
# devuelve [asiento_debito_001, asiento_credito_001]
```

---

## §19 — Cuatro dominios incómodos

### §19.1 — Marcador de fútbol como estado derivado

El marcador "Argentina 1 - Perú 0" no es un hecho que alguien asienta; emerge de contar los goles registrados por cada equipo. La consulta es un conteo doble con composición de strings final.

```python
n_goles_arg = count(u, Pattern(
    fixed={"equipo": argentina},
    type_constraint=u.ind("evento_gol"),
))
n_goles_per = count(u, Pattern(
    fixed={"equipo": peru},
    type_constraint=u.ind("evento_gol"),
))
marcador = f"{n_goles_arg} - {n_goles_per}"
```

---

## §20 — WQuestions y los modelos de lenguaje

### §20.1 — Ingesta médica generada por un LLM

Un LLM procesa una nota clínica en lenguaje natural y produce cinco invocaciones `ingest_situation`, una por verbo identificado en el texto. La extracción es directa porque el lexicon clínico ya expone las signaturas como function schemas.

```python
ingest_situation("consultar", roles={
    "agente": dra_torres, "paciente": maria_g,
    "momento": fecha_nota, "motivo": cefalea,
})
ingest_situation("medir", roles={
    "agente": dra_torres, "paciente": maria_g,
    "medida_de": presion_arterial,
    "monto": "145/92", "unidad": mmHg,
})
ingest_situation("diagnosticar", roles={
    "agente": dra_torres, "paciente": maria_g,
    "diagnosticado_como": hta_g1,
})
ingest_situation("prescribir", roles={
    "agente": dra_torres, "paciente": maria_g,
    "medicamento_prescrito": enalapril,
    "frecuencia": cada_manana,
})
ingest_situation("controlar", roles={
    "paciente": maria_g, "agente": dra_torres,
    "momento": fecha_nota_plus_30,
    "estatus_factual": previsto,
})
```

### §20.2 — Consulta cross-dominio con LLM

El LLM cruza dos dominios distintos (política y retail) emitiendo dos consultas paralelas. Cada una tiene su propio `type_constraint`; el LLM las combina y produce la respuesta narrativa al usuario.

```python
noticias = query(Pattern(
    fixed={"tema_categorico": impuesto_consumo},
    type_constraint="noticia_politica",
    ask={"agente": Var(), "momento": Var(), "contenido": Var()},
))

ventas = query(Pattern(
    fixed={"sector": retail},
    type_constraint="agregado_ventas_trimestral",
    ask={"momento": Var(), "monto": Var()},
))
```

---

## Patrones que emergen al verlo todo junto

Si se revisan los 20 fragmentos en serie, se observan cinco regularidades que valen la pena nombrar:

1. **La API es realmente pequeña.** `ingest_situation`, `assert_fact`, `query`, `count`. Con esos cuatro verbos se modelan ocho dominios completos. No hay 200 funciones que aprender; hay cuatro.

2. **Las llamadas son densas pero uniformes.** Una llamada típica tiene entre 5 y 10 líneas. El patrón visual es siempre el mismo: nombre del verbo, diccionario de roles, opcionales al final. Una vez que el lector reconoce el patrón, el código se lee como prosa.

3. **El verbo se elige primero, los roles después.** Esto no es coincidencia: refleja la signatura tipada del verbo (capítulo 11). Primero el contrato, después los argumentos.

4. **La política liberal del catálogo se ejerce constantemente.** `medicamento_prescrito`, `medida_de`, `diagnosticado_como`, `equipo`, `tema_categorico`, `sector`, `frecuencia`, `duracion` — todos son roles de dominio que ningún capítulo declara explícitamente y, sin embargo, el sistema los acepta. El motor solo valida los roles canónicos; el resto pasa.

5. **La bitemporalidad y la inmutabilidad son la regla.** Casi todos los fragmentos importantes asientan con `valid_from`/`valid_to`, marcan `estatus_factual`, o `rectifican` sin borrar. El modelo no tiene una operación "update": tiene "asentar un hecho nuevo que reemplaza al previo conservando el historial".

Estas cinco regularidades, juntas, son lo que hace que el código del prototipo sea tan corto (apenas 2.250 líneas en total) a pesar de modelar dominios tan distintos como un spa, un banco regional, una historia clínica y un partido de fútbol. El motor no crece con cada dominio nuevo; el lexicon y los datos sí.
