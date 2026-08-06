# Los tres casos de cambio — destilación al manuscrito

**Fecha:** 2026-08-05
**Alcance:** dos secciones nuevas en `libro/manuscrito2/` (caps. 11 y 29). Solo prosa y marcado; ningún cambio en el prototipo, el MCP ni el motor.

## El problema

Un identificador deja de ser el que vale por tres motivos distintos, y desde fuera los tres se ven igual:

1. **El mundo cambió.** María se mudó, el precio subió, el dueño vendió. El valor viejo *fue* verdad.
2. **Lo anotamos mal.** Un tecleo, el cliente equivocado. El valor viejo *nunca* fue verdad.
3. **Son la misma cosa con dos nombres.** La persona está en ficha bajo su DNI y bajo su RUC. Ninguno de los dos es un error.

El almacén no puede distinguirlos: solo ve tripletas. La distinción vive en quien anota.

Elegir mal no produce un fallo. Produce una respuesta plausible y equivocada — que es la forma cara del error.

## Qué es nuevo respecto de lo ya escrito

El capítulo 11 ya cubre el caso 3 con solvencia: tres vías de resolución, el modelo canónico con alias colgando, `owl:sameAs` como precedente, y hasta el consejo operativo *"no intentes renumerar sus identificadores: déjalos como están y tiende los `mismo_que`"* ([11-identidad.html:417-420](../../../libro/manuscrito2/11-identidad.html)).

Lo que **no** está es el contraste. `mismo_que` se explica en aislamiento, nunca frente a los otros dos motivos por los que un identificador cambia. El consejo de "no renumeres" queda como recomendación suelta en vez de consecuencia de un principio. Un lector que entiende el capítulo entero sigue pudiendo elegir la herramienta equivocada, porque el capítulo nunca le enseñó que hay una elección que hacer.

## La tesis

El capítulo cierra con su propia imagen: *"Un identificador es un papelito que dice dónde mirar; la identidad es lo que encuentras al mirar."* Los tres casos son tres cosas distintas que le pasan a ese papelito:

| Caso | Qué le pasó al papelito | Sobre qué se está afirmando |
|---|---|---|
| El mundo cambió | cambió lo que dice | **el mundo** |
| Lo anotamos mal | se escribió mal | **la anotación** |
| Son la misma cosa | hay dos papelitos para una persona | **el referente** |

El filo: los tres casos **no se distinguen por lo que pasó afuera, sino por sobre qué objeto se está afirmando algo**. Por eso el grafo no puede decidirlo. Ve tripletas, no intenciones.

Los tres modos de fallo, que la sección debe hacer concretos:

- Corregir lo que era **misma cosa** borra una verdad. El hecho ocurrió bajo `contribuyente_77_3389`; corregido, la pregunta por el identificador bajo el que realmente ocurrió deja de encontrarlo, y un total que debía sumar los dos suma uno.
- Corregir lo que era **cambio del mundo** pierde el pasado. La dirección vieja fue verdad; el envío que llegó allí el año pasado queda sin explicación.
- Poner **vigencia** a lo que fue un tecleo certifica una equivocación como habiendo sido cierta durante un periodo: deja escrito que María se apellidó "Gonzalez" entre marzo y julio.

Los tres modos se cuentan sobre María, no sobre ejemplos importados de otros capítulos (nada de precios ni de ventas): el capítulo ya tiene su reparto y el lector lo tiene cargado.

## Cambio 1 · Capítulo 11 (núcleo)

**Archivo:** `libro/manuscrito2/11-identidad.html`
**Ubicación:** `<h2>` nuevo entre la línea 366 (cierre de "El modelo: una persona canónica con identidades colgando", tras la `nota-margen` de "Dirección del cable") y la 368 ("No es una decisión numerada").

Es el punto exacto donde el lector acaba de ver tres alias colgando de un nodo canónico y piensa *"¿y por qué no arreglo los ids y ya?"*.

**Título propuesto:** "Tres cosas que le pasan a un identificador".

**Estructura (~550 palabras):**

1. **Apertura** que formula la pregunta del lector ("¿por qué no corregir los ids y terminar?") y responde que corregir es una de tres cosas distintas, y solo una de ellas es correcta aquí.
2. **Los tres casos sobre María Gonzales**, reusando el reparto que el capítulo ya tiene:
   - se mudó → el mundo cambió;
   - le tecleamos el apellido como "Gonzalez" → lo anotamos mal;
   - `contribuyente_77_3389` resulta ser ella → son la misma cosa.
3. **Rejilla comparativa** `rejilla-3` con tres `tarjeta`, una por caso. Cada tarjeta responde las mismas tres preguntas, en el mismo orden: *¿el valor viejo fue verdad?* · *¿qué se escribe?* · *¿qué pasa si preguntas después por el valor viejo?*
4. **El giro conceptual**: los tres se distinguen por el objeto de la afirmación (mundo / anotación / referente), no por lo ocurrido. Aquí se ata a la imagen del papelito.
5. **`caja--alerta`** con el modo de fallo silencioso: elegir mal no rompe nada, responde mal. Los tres modos listados arriba, comprimidos.

**Enganches:** la vigencia se enlaza a [`09-situaciones.html`](../../../libro/manuscrito2/09-situaciones.html) referenciando **D6** en prosa o `nota-margen` — no se re-explica ni se abre una `caja--decision` (D6 se enuncia en el cap. 9). La sección cierra apuntando a que "No es una decisión numerada" (la sección siguiente) sigue valiendo: esto tampoco añade maquinaria.

**Efecto secundario buscado:** la sección "En la práctica" del final (línea 415 y siguientes) deja de ser un consejo suelto y pasa a leerse como corolario. No hace falta reescribirla.

## Cambio 2 · Capítulo 29 (eco)

**Archivo:** `libro/manuscrito2/29-prueba-reflexiva.html`
**Ubicación:** `<h2>` nuevo tras el cierre de "Las fricciones nuevas: dos cerradas, una abierta" (después de la línea 479, antes de "Honradez intelectual" en la 481).

**Por qué ahí y no dentro:** las tres fricciones de esa sección salieron del prototipo reflexivo. Esta salió de otra presión, distinta y posterior — un LLM operando el MCP contra la migración de yaku. Meterla dentro obligaría a renumerar a "tres cerradas" y mezclaría dos experimentos bajo un mismo encabezado. Como sección aparte funciona además como **segundo testigo independiente**, que prueba más que un cuarto ítem de la misma lista.

**Título propuesto:** en la línea de "La interfaz, por detrás de su propia teoría".

**Estructura (~280 palabras):**

1. Una segunda presión, con otro método: no el prototipo describiéndose a sí mismo, sino un modelo de lenguaje operando el grafo a través de su interfaz, sobre datos de un sistema real en producción.
2. Lo que pasó: la interfaz sabía ofrecer dos puertas (corregir, vigencia) y el mundo tenía tres casos. Obligado a elegir entre dos, el modelo eligió plausible y mal.
3. **El paralelo, que es el pago:** con `instancia_de` el prototipo estaba detrás de su propia teoría. Aquí `mismo_que` llevaba escrito desde el capítulo 11 — la teoría estaba completa. Lo que estaba detrás era la interfaz, que no sabía decirlo. Misma forma de hallazgo, capa distinta.
4. Remisión a [`11-identidad.html`](../../../libro/manuscrito2/11-identidad.html) para la distinción, sin repetirla.

**No se toca** el encabezado "dos cerradas, una abierta" ni el conteo de fricciones existente.

## Restricciones de estilo

De `libro/manuscrito2/GUIA-DE-ESTILO.md`:

- Tuteo neutro. Nada de voseo.
- No inventar `Dn`. D6 (vigencia) se **referencia**, no se enuncia; se define en el cap. 9. Esta sección no introduce ninguna D nueva, igual que la resolución de identidad tampoco lo hacía.
- Identificadores canónicos del repertorio: `persona_maria_g`, `cliente_1042`, `paciente_maria_g`, `contribuyente_77_3389`.
- Componentes: `rejilla-3` con `tarjeta`, `caja caja--alerta`, `nota-margen`, `bloque-codigo` con `data-lang="triple"` si hace falta una tripleta.

De las convenciones de tono ya acordadas para el libro:

- **No auto-declarar honestidad.** El hallazgo se muestra, no se anuncia como acto de transparencia. Los límites se presentan como hoja de ruta, no como confesión.
- **Registro medio:** llano pero con voz. Glosar la jerga, no eliminarla.
- **La raya (—) solo para ritmo o énfasis.** Paréntesis para lo secundario, dos puntos para introducir.

## Lo que este cambio NO hace

- No nombra las operaciones concretas del MCP (`valid_from`, `correct`, `at=`, `history=`, `identidades`, `fixed=`). El capítulo 11 es conceptual y hoy no menciona ninguna API; se queda así.
- No añade ninguna decisión numerada.
- No modifica `indice.html` ni `index.html`: el índice lateral de cada capítulo lo construye `assets/interacciones.js` por scrollspy, así que los `<h2>` nuevos aparecen solos.
- No toca `mcp-server/`, `INSTRUCTIONS` ni los tests. Eso ya está hecho y verificado en `d789003`.

## Verificación

1. Los dos archivos siguen siendo HTML bien formado (etiquetas balanceadas en las secciones nuevas).
2. `python3 libro/generar_pdf_html.py` corre sin error y las secciones nuevas salen en el PDF.
3. Lectura de las dos secciones en el navegador: la `rejilla-3` no desborda, la `caja--alerta` se ve, los enlaces a `09-situaciones.html` y `11-identidad.html` resuelven.
4. Repaso de tono contra las tres restricciones de arriba, en concreto: ninguna frase que anuncie honestidad, y las rayas clasificadas por función.
