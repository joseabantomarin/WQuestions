# Lexicon — diccionario de verbos canónicos para WQuestions

Este documento contiene un catálogo **ejemplar (no exhaustivo)** de verbos y unidades léxicas del español, cada uno mapeado a un tipo de situación en `K` con sus roles obligatorios y opcionales del catálogo canónico (D7).

El lexicon es un artefacto **vivo y extensible**. Esta versión cubre verbos frecuentes en los dominios ya modelados (aeropuerto, ventas, taxi, clínica, música, contrato, química, fútbol) y algunos universales (movimiento, comunicación, posesión, percepción).

## El lexicon como pieza central (D8)

Por **D8 (invisibilidad del catálogo canónico)**, el lexicon es la pieza central de usabilidad de WQuestions. D7 da el vocabulario interno; el lexicon es la **capa de traducción** entre el lenguaje del usuario (lenguaje natural, vocabulario de dominio) y los roles canónicos almacenados.

Cada entrada del lexicon, además de su tipo de situación y signatura, lista **aliases naturales por rol**: cómo el usuario llamaría a ese rol al hablar o al llenar un formulario.

## Formato de cada entrada

**Formato corto** (suficiente para la mayoría):

```
[unidad_léxica]                       ← el verbo o verbo+complemento patrón
  tipo_situacion: nombre_en_K
  obligatorios:   [rol1, rol2, ...]   ← roles que la situación debe tener
  opcionales:     [rol3, rol4, ...]   ← roles que pueden aparecer
  notas:          comentarios breves
  ejemplo:        "oración natural"
```

**Formato expandido con aliases** (para verbos centrales del lexicon):

```yaml
verbo: vender
  tipo_situacion: accion_vender
  roles:
    agente:
      canónico:  agente
      aliases:   ["vendedor", "el que vende", "quien vende"]
    tema:
      canónico:  tema
      aliases:   ["producto", "lo vendido", "item", "mercancía"]
    beneficiario:
      canónico:  beneficiario
      aliases:   ["comprador", "cliente", "el que compra"]
    por_cuanto:
      canónico:  por_cuanto
      aliases:   ["precio", "monto", "costo"]
  obligatorios: [agente, tema, beneficiario, por_cuanto]
  opcionales:   [momento, lugar_de, moneda, instrumento]
  ejemplo:      "María le vendió el libro a Juan por 20 soles"
```

Para los dominios reales, las entradas críticas usan el formato expandido; las menos centrales pueden usar el corto.

## Dialectos de dominio

Adicionalmente, cada dominio puede declarar sus propios aliases que aplican a *todos* los verbos de ese contexto. Forma sugerida:

```yaml
dominio: ventas_peruanas
  aliases_de_dominio:
    razon_social:    nombre
    ruc:             identificador_fiscal
    serie_correlativo: numero_documento
    fecha_emision:   momento
```

Esto permite que un usuario en el dominio de ventas peruanas hable de "RUC" y "razón social" sin pensar en `identificador_fiscal` ni `nombre`.

Para verbos polisémicos, hay **una entrada por unidad léxica** (verbo + complemento patrón), no por verbo aislado.

---

## 1. Acciones de transferencia

```
dar
  tipo_situacion: accion_dar
  obligatorios:   [agente, tema, beneficiario]
  opcionales:     [momento, lugar_de, instrumento, con_finalidad]
  notas:          dar canónico = transferir posesión
  ejemplo:        "Pedro le dio un regalo a María"

dar [la_mano]
  tipo_situacion: accion_saludar
  obligatorios:   [agente, paciente]
  opcionales:     [momento, lugar_de, modo]
  notas:          colocación idiomática; tipo es saludar, no dar
  ejemplo:        "Pedro le dio la mano a su jefe"

dar [conferencia | clase | charla]
  tipo_situacion: evento_exposicion
  obligatorios:   [agente, tema]
  opcionales:     [momento, lugar_de, audiencia, duracion]
  notas:          light verb; dar = realizar
  ejemplo:        "Pedro dio una conferencia el martes"

recibir
  tipo_situacion: accion_dar              # inversa de dar (misma situación, otra perspectiva)
  obligatorios:   [beneficiario, tema]
  opcionales:     [agente, momento, lugar_de]
  notas:          en voz activa pero perspectiva del receptor

vender
  tipo_situacion: accion_vender
  obligatorios:   [agente, tema, beneficiario, por_cuanto]
  opcionales:     [momento, lugar_de, moneda, instrumento]
  ejemplo:        "María le vendió el libro a Juan por 20 soles"

comprar
  tipo_situacion: accion_vender           # misma situación, perspectiva inversa
  obligatorios:   [agente, tema, por_cuanto]   # agente aquí = beneficiario semántico
  opcionales:     [proveedor, momento, lugar_de]

pagar
  tipo_situacion: accion_pagar
  obligatorios:   [agente, por_cuanto, beneficiario]
  opcionales:     [moneda, instrumento, sobre_situacion, momento]
  ejemplo:        "Juan pagó 18.50 con tarjeta"

prestar
  tipo_situacion: accion_prestar
  obligatorios:   [agente, tema, beneficiario]
  opcionales:     [momento, fecha_devolucion, lugar_de]
```

## 2. Movimiento

```
ir
  tipo_situacion: accion_ir
  obligatorios:   [agente, destino]
  opcionales:     [origen, via, momento, instrumento, acompañantes]
  ejemplo:        "El tren va de Lima a Cusco"

venir
  tipo_situacion: accion_venir
  obligatorios:   [agente, destino]       # destino = lugar del hablante
  opcionales:     [origen, via, momento, instrumento]

llegar
  tipo_situacion: accion_llegar
  obligatorios:   [agente, destino]
  opcionales:     [origen, momento, instrumento]
  ejemplo:        "El avión llegó a Lima a las 12"

salir
  tipo_situacion: accion_salir
  obligatorios:   [agente, origen]
  opcionales:     [destino, momento, instrumento]

pasar [por]
  tipo_situacion: accion_pasar
  obligatorios:   [agente, via]
  opcionales:     [origen, destino, momento]

viajar
  tipo_situacion: accion_viajar
  obligatorios:   [agente, destino]
  opcionales:     [origen, via, momento, instrumento, acompañantes, con_finalidad]
  ejemplo:        "Juan viajó a Cusco con su familia"
```

## 3. Estado y existencia

```
ser
  tipo_situacion: estado_ser
  obligatorios:   [tema, atributo]
  opcionales:     [momento]
  notas:          predicación nominal o adjetival permanente
  ejemplo:        "Juan es médico"

estar
  tipo_situacion: estado_estar
  obligatorios:   [tema]
  opcionales:     [lugar_de, atributo, momento]
  notas:          predicación locativa o de estado transitorio
  ejemplo:        "La caja está sobre la mesa"

existir
  tipo_situacion: estado_existencia
  obligatorios:   [tema]
  opcionales:     [lugar_de, momento]

haber [hay X]
  tipo_situacion: estado_existencia
  obligatorios:   [tema]
  opcionales:     [lugar_de, momento]
  notas:          impersonal; sin agente

durar
  tipo_situacion: estado_duracion
  obligatorios:   [tema, duracion]
  opcionales:     [inicio, fin]
```

## 4. Experiencia y percepción

```
ver
  tipo_situacion: accion_ver
  obligatorios:   [experimentador, tema]
  opcionales:     [momento, lugar_de]

oír | escuchar
  tipo_situacion: accion_oir
  obligatorios:   [experimentador, tema]
  opcionales:     [momento, lugar_de]

amar | querer [a Q]
  tipo_situacion: estado_amar
  obligatorios:   [experimentador, tema]
  opcionales:     [intensidad, momento]
  notas:          "querer a alguien" = amar; distinto de querer modal

recordar
  tipo_situacion: accion_recordar
  obligatorios:   [experimentador, tema]
  opcionales:     [momento]

soñar [con]
  tipo_situacion: accion_soñar
  obligatorios:   [experimentador, tema]
  opcionales:     [momento]
```

## 5. Comunicación

```
decir
  tipo_situacion: accion_decir
  obligatorios:   [agente, tema]
  opcionales:     [beneficiario, momento, lugar_de]
  notas:          tema suele ser otra situación (cláusula subordinada)
  ejemplo:        "Juan dijo que María vendría"

preguntar
  tipo_situacion: accion_preguntar
  obligatorios:   [agente, tema]
  opcionales:     [beneficiario, momento]

prometer
  tipo_situacion: accion_prometer
  obligatorios:   [agente, tema, beneficiario]
  opcionales:     [momento]
  notas:          tema = situación futura

llamar [a Q]
  tipo_situacion: accion_llamar
  obligatorios:   [agente, paciente]
  opcionales:     [momento, instrumento, lugar_de]
```

## 6. Sucesos naturales

```
llover
  tipo_situacion: suceso_lluvia
  obligatorios:   [momento, lugar_de]
  opcionales:     [intensidad, duracion]
  notas:          sin agente

amanecer | anochecer
  tipo_situacion: suceso_cambio_dia
  obligatorios:   [momento, lugar_de]

ocurrir | suceder | pasar
  tipo_situacion: meta_suceso
  obligatorios:   [tema]                  # tema = otra situación
  opcionales:     [momento, lugar_de]
  notas:          tematiza la ocurrencia de cualquier situación
```

## 7. Modales (no son situaciones; modifican otras)

Los modales no introducen una situación independiente. Se modelan como **propiedades modales** sobre la situación principal:

```
querer [+ INF]
  modificador: modalidad = volitiva
  efecto:      la situación modificada no es factual (todavía / quizá nunca)
  ejemplo:     "Juan quiere viajar a Cusco"
  modelado:    (viajar_001, modalidad, volitiva)
               (viajar_001, hecho_actual, falso)

deber [+ INF]
  modificador: modalidad = deontica
  efecto:      obligación o expectativa
  ejemplo:     "Juan debe pagar la deuda"

poder [+ INF]
  modificador: modalidad = alética (capacidad) o epistémica (probabilidad)
  notas:       desambiguar por contexto
  ejemplo:     "Juan puede correr 10 km" → alética
               "Puede llover" → epistémica

soler [+ INF]
  modificador: aspecto = habitual

tener_que [+ INF]
  modificador: modalidad = deontica
```

## 8. Verbos copulativos y de cambio

```
volverse | convertirse_en | hacerse
  tipo_situacion: accion_transformacion
  obligatorios:   [tema, estado_final]
  opcionales:     [agente, estado_inicial, momento]
  ejemplo:        "El agua se convirtió en hielo"

romper
  tipo_situacion: accion_romper
  obligatorios:   [paciente]
  opcionales:     [agente, instrumento, momento]
  notas:          agente opcional permite "se rompió el vaso" sin culpable
```

## 9. Acciones varias

```
escribir
  tipo_situacion: accion_escribir
  obligatorios:   [agente, tema]
  opcionales:     [beneficiario, instrumento, momento, lugar_de, sobre_tema]

leer
  tipo_situacion: accion_leer
  obligatorios:   [agente, tema]
  opcionales:     [momento, lugar_de]

correr
  tipo_situacion: accion_correr
  obligatorios:   [agente]
  opcionales:     [lugar_de, momento, distancia, duracion, con_finalidad]
  ejemplo:        "Juan corre en el parque por las mañanas"

dormir
  tipo_situacion: estado_dormir
  obligatorios:   [tema]
  opcionales:     [lugar_de, momento, duracion]

cancelar
  tipo_situacion: accion_cancelar
  obligatorios:   [agente, tema]            # tema = situación cancelada
  opcionales:     [causado_por, momento]
```

## 10. Verbos del dominio taxi (ejemplares específicos)

```
solicitar [viaje]
  tipo_situacion: solicitud_viaje
  obligatorios:   [agente, origen, destino]
  opcionales:     [con_finalidad, momento, instrumento]

emparejar
  tipo_situacion: evento_emparejamiento
  obligatorios:   [agente, sobre_solicitud, asigna_agente, asigna_instrumento]
  opcionales:     [momento, motivado_por, duracion_estimada, precio_estimado]
```

---

## Convenciones y reglas

### 1. Polisemia → unidades léxicas

Cuando un verbo tiene sentidos distintos según colocación, se registra **una entrada por sentido**. El parser de ingesta debe detectar la colocación.

```
dar             → accion_dar (transferir)
dar [la_mano]   → accion_saludar
dar [conferencia | clase | charla] → evento_exposicion
```

### 2. Pares activa/pasiva → mismo tipo

`vender` y `comprar`, `dar` y `recibir`, son la misma situación vista desde perspectivas distintas. Comparten `tipo_situacion`; cambia qué rol llena el sujeto.

### 3. Verbos sin agente

Verbos como `llover`, `existir`, `haber`, `durar` no toman agente. Su signatura simplemente omite el rol; la situación queda válida sin agente.

### 4. Verbos cuyo tema es otra situación

`decir`, `prometer`, `creer`, `ver` (en sentido de "presenciar"), `ocurrir` toman como `tema` o `paciente` otra situación. Esto da composicionalidad: cláusulas subordinadas modeladas como hechos anidados.

### 5. Modales: no son situaciones

`querer + INF`, `deber + INF`, `poder + INF` modifican otra situación. Se modelan como propiedad `modalidad` sobre la situación principal, no como un verbo aparte.

### 6. Aspecto y tiempo: propiedades de la situación

```
(situacion, tiempo,    pasado | presente | futuro)
(situacion, aspecto,   perfectivo | imperfectivo | progresivo | habitual)
(situacion, voz,       activa | pasiva)
(situacion, polaridad, afirmativa | negativa)
```

## Estado del catálogo

- **Cobertura actual**: ~50 unidades léxicas, sesgadas a verbos comunes y a los dominios ya modelados.
- **Cobertura objetivo eventual**: los ~2000 verbos más frecuentes del español, idealmente alineados con FrameNet/VerbNet (ver [related/framenet-verbnet.md](related/framenet-verbnet.md)).
- **Política de promoción**: una unidad léxica entra al catálogo cuando aparece en más de un dominio modelado o cuando responde a un patrón comunicativo universal.

## Cómo extender

Para agregar un verbo:

1. Identificar la unidad léxica (verbo solo o verbo + complemento patrón).
2. Determinar el tipo de situación en `K` (reusar si existe; crear si nuevo).
3. Listar roles obligatorios (los que aparecen casi siempre).
4. Listar roles opcionales (los que pueden aparecer).
5. Anotar un ejemplo de uso.
6. Si el verbo cambia el inventario de tipos en `K`, anotar.
