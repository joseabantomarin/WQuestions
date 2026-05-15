# Capítulo 13 — El lexicon: diccionario que es compilador

## El problema de la mano

Tomemos dos oraciones del español que comparten cinco letras y, en apariencia, comparten verbo:

> *Pedro le dio un regalo a María.*
>
> *Pedro le dio la mano a su jefe.*

Si aplicamos al pie de la letra lo que el capítulo anterior estableció — el verbo nombra el tipo de situación, los constituyentes llenan los roles — las dos oraciones generarían situaciones del mismo tipo: `accion_dar`. El primero da un regalo; el segundo da una mano. Para el motor, parecería el mismo verbo con distinto tema.

Pero claramente no es así. En la primera oración hay una **transferencia de posesión**: María ahora tiene el regalo. En la segunda oración no hay transferencia de nada: el jefe no sale del encuentro con la mano de Pedro en el bolsillo. *Dar la mano* es una expresión idiomática que en español significa **saludar formalmente**. La situación que describe pertenece a una categoría completamente distinta — no a `accion_dar`, sino a `accion_saludar`.

Y *dar* tiene más. *Pedro dio una conferencia el martes* tampoco transfiere nada; significa que Pedro **realizó** una conferencia, una situación del tipo `evento_exposicion`. *El reloj dio las tres* es una metáfora del sonar, situación `accion_sonar`. *Le dio asco la noticia* es una experiencia sensorial, `experiencia_asco`. Un mismo verbo, cinco tipos de situación distintos.

Este fenómeno — un verbo cuyo significado depende del complemento que lo acompaña — se llama **polisemia léxica**, y es la regla, no la excepción. El sistema **necesita resolver** qué tipo de situación está realmente describiendo antes de aplicar el procedimiento del capítulo 12, porque la signatura del verbo es distinta para cada caso. `dar(agente, tema, beneficiario)` no tiene la misma firma que `dar_la_mano(agente, paciente)` ni que `dar_conferencia(agente, tema, audiencia)`.

Lo que el modelo necesita, entonces, es un **diccionario** que mapee no verbos sueltos, sino **unidades léxicas** — verbo + complemento patrón — a sus tipos de situación correspondientes. Ese diccionario es el **lexicon**.

## El lexicon es la pieza más visible del proyecto

Antes de bajar al detalle conviene fijar la importancia arquitectónica del lexicon. El capítulo 12 mostró que el modelo tiene un catálogo canónico de roles (D7): `agente`, `tema`, `beneficiario`, `lugar_de`, `momento`, etcétera. Una decisión de diseño correlativa — la decisión número 8, **D8** — establece algo fundamental: **el catálogo canónico es invisible para el usuario final**. El usuario nunca debe escribir "agente" ni "beneficiario" para que el sistema funcione; debe poder hablar en su idioma habitual ("vendedor", "comprador", "cliente", "el que paga") y el sistema traducir.

Quien hace esa traducción es el lexicon. D7 establece **qué hay debajo**; el lexicon establece **cómo se accede desde arriba**. Sin lexicon, el modelo es una librería interna excelentemente diseñada pero inutilizable; con lexicon, se vuelve una interfaz que cualquier humano puede usar — y, cada vez más relevante, cualquier modelo de lenguaje puede consultar.

Por eso D8 es estrictamente más fuerte que una decisión de cómoda usabilidad: garantiza que la arquitectura interna del modelo pueda evolucionar — agregar roles, refinar signaturas, cambiar identificadores — sin romper la experiencia de los usuarios, porque la única cara que el usuario ve es el lexicon. Ese es el contrato: el lexicon es estable hacia afuera; lo de adentro puede moverse.

![La arquitectura en capas del lexicon (D8): el usuario habla con su vocabulario natural; el lexicon traduce a los roles canónicos del catálogo D7; el almacenamiento opera con identificadores internos. Cada capa puede cambiar sin afectar a las demás.](../diagrams/png/23_lexicon_capas.png)

## Anatomía de una entrada

Una entrada del lexicon tiene un formato fijo que conviene mirar de cerca. Tomemos el caso de `vender`, que vamos a ver completo y luego desglosar:

```yaml
verbo: vender
  tipo_situacion: accion_vender
  roles:
    agente:
      canónico:  agente
      aliases:   ["vendedor", "el que vende", "quien vende"]
    tema:
      canónico:  tema
      aliases:   ["producto", "lo vendido", "ítem", "mercancía"]
    beneficiario:
      canónico:  beneficiario
      aliases:   ["comprador", "cliente", "el que compra"]
    por_cuanto:
      canónico:  por_cuanto
      aliases:   ["precio", "monto", "costo"]
  obligatorios: [agente, tema, beneficiario, por_cuanto]
  opcionales:   [momento, lugar_de, moneda, instrumento]
  ejemplo:      "María le vendió el libro a Juan por 20 dólares"
```

Las piezas son seis y todas tienen un trabajo claro.

**`verbo`** — la unidad léxica que dispara esta entrada. Puede ser una palabra (`vender`) o un patrón verbo + complemento (`dar [la mano]`, `dar [conferencia | clase]`). Los corchetes denotan los complementos que activan esta lectura específica.

**`tipo_situacion`** — el identificador en K al que la situación reificada quedará anclada. Es el nombre que `instancia_de` tomará como valor. Estable, interno, en general no expuesto al usuario.

**`roles`** — la lista de roles que la situación admite, cada uno con dos campos: el nombre canónico (vive en D7) y la lista de **aliases naturales** que el usuario podría usar al hablar. *"El vendedor le dio una factura al cliente"* y *"el agente proveyó un comprobante al beneficiario"* deben producir exactamente la misma situación; el lexicon hace ese trabajo de unificación.

**`obligatorios`** y **`opcionales`** — los dos listados que dicen qué roles deben aparecer para que la situación sea válida y cuáles son extras admisibles. Como vimos en el capítulo 12, esto convierte cada entrada en una signatura tipada chequeable.

**`ejemplo`** — una oración natural que muestra la entrada en uso. No es decorativa: es lo que el motor de prueba (o el modelo de lenguaje que aprende del lexicon) utiliza para verificar que la entrada efectivamente reconoce el patrón.

Una entrada del lexicon es, vista así, **una declaración de función con su documentación adjunta**. Y aquí es donde la analogía deja de ser pedagógica para volverse técnica.

## El lexicon como function schema

Los modelos de lenguaje de la generación 2024-2026 — GPT, Claude, Gemini y sus equivalentes — han convergido en un paradigma de integración con sistemas externos llamado *function calling* o *tool use* [22]. El patrón es siempre el mismo: el sistema le presenta al modelo un catálogo de funciones disponibles, cada una con su schema JSON que declara nombre, descripción, parámetros y tipos. El modelo, cuando el usuario pide algo que requiere acción, genera una invocación estructurada: el nombre de la función y los argumentos con sus tipos correctos. Un evaluador externo recibe la invocación y la ejecuta.

Lo notable es que el formato esperado por function calling es **estructuralmente idéntico** al formato de una entrada del lexicon. Tomemos la entrada de `vender` arriba y traduzcámosla a un schema de función:

```json
{
  "name": "vender",
  "description": "Registrar una venta: transferencia de un bien con compensación monetaria",
  "parameters": {
    "type": "object",
    "properties": {
      "agente":       {"type": "Q", "description": "vendedor, el que vende"},
      "tema":         {"type": "O", "description": "producto, ítem, mercancía"},
      "beneficiario": {"type": "Q", "description": "comprador, cliente"},
      "por_cuanto":   {"type": "N", "description": "precio, monto, costo"},
      "momento":      {"type": "T", "description": "cuándo ocurrió"},
      "lugar_de":     {"type": "L", "description": "dónde ocurrió"}
    },
    "required": ["agente", "tema", "beneficiario", "por_cuanto"]
  }
}
```

Las correspondencias son una a una: `tipo_situacion` → `name`; los `aliases` se convierten en `description` para que el modelo sepa cómo lo llamaría el usuario; los tipos de eje (`Q`, `O`, `T`, `N`, `L`) se vuelven tipos del schema; `obligatorios` → `required`. **El lexicon, leído así, es un catálogo de funciones que un LLM puede invocar.**

Esto importa más de lo que parece. Cuando un usuario escribe *"Ana se inscribió ayer en el plan mensual del sauna"* a un asistente conversacional respaldado por WQuestions, el modelo no necesita inventar cómo estructurar esa información: el lexicon le dice exactamente qué función llamar (`inscribirse` o `contratar`), qué roles llenar (`agente`, `tema`, `momento`) y qué tipos esperar en cada uno. La generación de la situación reificada es lo que produce la función. Y como el lexicon vive separado del motor de almacenamiento, agregar dominios nuevos es agregar entradas al lexicon — no escribir parsers ad-hoc.

Esta convergencia no es accidente. El paradigma de function calling redescubrió la misma intuición que la lingüística formal venía explotando desde Fillmore y Davidson: **un verbo es una función con argumentos tipados** [12, 24]. Lo que cambió en 2024 fue que los modelos se volvieron lo suficientemente buenos como para poder *llamar* esas funciones con fluidez. El lexicon de WQuestions queda exactamente sobre esa línea de convergencia.

## Polisemia: una entrada por sentido

Volvamos al *dar* del comienzo. ¿Cómo lo trata el lexicon?

La respuesta es directa: **una entrada por cada sentido**. El lexicon no intenta que una única declaración de `dar` cubra todos los usos. En su lugar, lista varias unidades léxicas, cada una con su patrón de complemento que dispara la lectura específica:

```
dar
  tipo_situacion: accion_dar
  obligatorios:   [agente, tema, beneficiario]
  notas:          dar canónico = transferir posesión
  ejemplo:        "Pedro le dio un regalo a María"

dar [la_mano]
  tipo_situacion: accion_saludar
  obligatorios:   [agente, paciente]
  notas:          colocación idiomática; tipo es saludar, no dar
  ejemplo:        "Pedro le dio la mano a su jefe"

dar [conferencia | clase | charla]
  tipo_situacion: evento_exposicion
  obligatorios:   [agente, tema]
  opcionales:     [audiencia, lugar_de, momento, duracion]
  notas:          light verb; dar = realizar
  ejemplo:        "Pedro dio una conferencia el martes"

dar [las_horas]
  tipo_situacion: accion_sonar
  obligatorios:   [agente, tema]
  notas:          metáfora del reloj; sujeto = el reloj
  ejemplo:        "El reloj dio las tres"

dar [asco | pena | miedo]
  tipo_situacion: experiencia_sensorial
  obligatorios:   [tema, experimentador]
  opcionales:     [momento]
  notas:          dar invertido: el tema causa la experiencia
  ejemplo:        "La noticia le dio asco"
```

El procedimiento de resolución es mecánico: el parser intenta hacer *match* del verbo con cada patrón disponible, **del más específico al más general**. Si la oración contiene *dar la mano*, el patrón `dar [la_mano]` coincide y se activa la entrada de saludo; si la oración contiene *dar un regalo*, ningún patrón específico coincide y se aplica la entrada genérica de `dar`. La regla del más específico al más general es la misma que cualquier compilador moderno usa para resolver sobrecarga de funciones.

![Resolución de polisemia: el verbo "dar" se desambigua por su patrón de complemento. Cuatro unidades léxicas distintas apuntan a cuatro tipos de situación distintos en K. El parser elige el patrón más específico que coincida.](../diagrams/png/24_polisemia_resolucion.png)

Lo importante es que la polisemia **no se trata como un problema lingüístico a resolver heurísticamente**; se trata como un caso normal de sobrecarga, declarado en el lexicon. Cada sentido tiene su signatura propia, su lista de obligatorios, su tipo en K. La complejidad no desaparece, pero se traslada al lugar donde corresponde: el diccionario, donde el lingüista del dominio (o el modelador, o el LLM) puede registrar nuevas lecturas sin tocar el motor.

## Dialectos de dominio

Hay otra capa de aliases que vale la pena explicar. Hasta ahora vimos aliases por *rol* — el rol `agente` puede llamarse "vendedor" en una venta, "médico" en una consulta, "piloto" en un viaje. Pero hay aliases que aplican **transversalmente a todos los verbos** de un dominio determinado. Un sistema de ventas en cierto país llama "RUC" al identificador fiscal y "razón social" al nombre del cliente, sea cual sea el verbo. Un sistema clínico habla de "DNI del paciente" y "diagnóstico" en lugar de "identificador" y "estado_evaluado". Un sauna habla de "cliente", "sesión", "plan mensual" y "promoción" todo el tiempo.

El lexicon admite **dialectos de dominio**: paquetes de aliases que se activan cuando el contexto operativo lo indica. Su declaración es liviana:

```yaml
dominio: sauna_oasis
  aliases_de_dominio:
    cliente:           agente
    sesion:            servicio_sauna
    plan_mensual:      contrato_servicio
    sesion_gratuita:   beneficio_fidelidad
    promo:             aplicacion_de_promocion
    redimir:           verbo_usar_beneficio
    cubierto_por:      cubierto_por
```

Con este dialecto cargado, un usuario del sauna puede escribir *"el cliente redimió su sesión gratuita el sábado"* y el sistema entender — sin ambigüedad — que `cliente` mapea a `agente`, `redimió` mapea al verbo `usar_beneficio`, y `sesión gratuita` mapea a una instancia de `beneficio_fidelidad`. Sin el dialecto, el sistema requeriría que el usuario escribiera las palabras canónicas, lo cual derrotaría D8.

Un dialecto de dominio no introduce nuevos verbos ni nuevos roles; introduce **traducciones del vocabulario habitual del dominio al vocabulario canónico**. Es la pieza que hace que el mismo motor sirva sin modificación para sauna, hospital, aeropuerto, contrato legal y juego de fútbol — porque cada uno trae su dialecto y el resto del sistema no se entera.

## Precedentes industriales: FrameNet, VerbNet, PropBank

El lexicon no nació en el vacío. La lingüística computacional pasó las últimas tres décadas construyendo recursos masivos con la misma intuición central. Vale la pena mencionarlos brevemente, porque cualquier implementación seria del lexicon va a apoyarse en ellos.

**FrameNet** [14], iniciado por Charles Fillmore en Berkeley en los años noventa, codifica el inglés (y por extensión otros idiomas) en términos de *frames semánticos*: escenarios conceptuales con un conjunto de roles típicos. El frame *Commerce_buy* de FrameNet tiene los roles `Buyer`, `Seller`, `Goods`, `Money`, `Means_of_payment`, casi uno a uno con la entrada de `vender` del lexicon. Sus más de 1.200 frames, anotados sobre corpus reales, son una fuente directa para poblar el catálogo de tipos en K.

**VerbNet** [15], desarrollado por Karin Kipper Schuler en UPenn, clasifica verbos del inglés en clases que comparten sintaxis y semántica. Las clases de VerbNet — `give-13.1`, `transfer-mesg-37.1.1`, `meet-36.3` — funcionan como una primera aproximación a la familia de tipos en K, con la ventaja de venir con predicados lógicos explícitos que se pueden traducir al modelo.

**PropBank**, de Martha Palmer, prioriza la anotación masiva sobre corpus reales con roles minimalistas (`Arg0`–`Arg5`). Es menos rico semánticamente, pero su volumen y su uso en entrenamiento de modelos de procesamiento lingüístico lo hacen una referencia obligada al construir lexicones de gran escala.

WQuestions no pretende reemplazar a ninguno de ellos. Se posiciona, más bien, como una capa de **agregación** que puede consumir sus aportes: la signatura de cada entrada del lexicon puede derivarse de FrameNet, los tipos en K pueden alinearse con clases de VerbNet, los corpus de PropBank pueden alimentar el entrenamiento de parsers que llenan el lexicon automáticamente. La integración exacta es trabajo futuro; lo importante por ahora es que el camino no es de cero.

## Lo que se gana con el lexicon

Conviene cerrar enumerando lo que aparece cuando el lexicon está presente y desaparece cuando no.

**Con lexicon, el sistema entiende dialectos.** Un usuario del sauna habla de "cliente" y "sesión"; un usuario del hospital habla de "paciente" y "consulta"; un usuario del aeropuerto habla de "pasajero" y "vuelo". Los tres pueden ingresar información al mismo motor sin saber que internamente todo se llama `agente` y `situacion`. Sin lexicon, los tres tienen que aprender el vocabulario interno o el sistema necesita un parser ad-hoc por dominio.

**Con lexicon, los modelos de lenguaje pueden invocar el sistema.** Como vimos, una entrada del lexicon es estructuralmente un function schema. Un LLM con acceso al lexicon puede traducir lenguaje natural a invocaciones estructuradas sin entrenamiento adicional sobre el modelo. Sin lexicon, integrar un LLM exige escribir prompts complejos que enseñen al modelo el catálogo canónico cada vez.

**Con lexicon, la polisemia es declarativa.** *Dar la mano* y *dar un regalo* son entradas separadas en el diccionario; el parser elige por patrón. Sin lexicon, la desambiguación queda repartida en reglas dispersas en el código.

**Con lexicon, el modelo es extensible sin tocar el motor.** Un dominio nuevo se incorpora agregando entradas y un dialecto. El motor de almacenamiento, el espacio multidimensional, la maquinaria de consulta — todo eso queda intacto. Sin lexicon, cada dominio nuevo requiere modificaciones en varios lados.

Por estas cuatro razones, decir que el lexicon es *el más importante de los artefactos del proyecto* no es exageración. La elegancia conceptual del modelo (los ocho ejes, los roles canónicos, las situaciones reificadas) vive en el catálogo D7. Pero su **usabilidad real** vive en el lexicon — y la usabilidad es la diferencia entre una propuesta interesante y una infraestructura adoptable. El próximo capítulo se ocupa de los tres casos lingüísticos que ponen al lexicon (y al modelo) bajo presión: nominalizaciones, modales e idiomas. Veremos qué hace bien, qué hace con esfuerzo y dónde están las grietas reales.
