# Guía de registro — la prosa del libro

> Documento **interno**, no forma parte del libro. Complementa a [`GUIA-DE-ESTILO.md`](GUIA-DE-ESTILO.md), que define el canon de **estructura** (componentes, ejemplos, decisiones Dn, mapa de capítulos). Esta guía define el canon de **voz**: cómo se escriben las frases.
>
> Se destiló del capítulo 29 (`29-prueba-reflexiva.html`), que es el capítulo de referencia. Ante la duda, abre ese archivo y compara.

---

## 1. El principio

El libro se escribía en registro académico: párrafos largos, frases con subordinadas encadenadas, jerga sin glosar. Se entendía, pero solo si ya sabías del tema.

El registro nuevo tiene una prueba: **un lector que nunca oyó hablar de grafos ni de bases de datos debe poder seguir la prosa de principio a fin.** Que no entienda cada detalle está bien. Que se pierda, no.

Esto no se consigue quitando contenido. Se consigue partiendo las ideas y glosando los términos. El capítulo 29 conserva sus dos figuras, sus cinco bloques de código, sus tripletas y sus seis cajas. Lo que cambió fue cómo se dice.

---

## 2. Las cifras

Medidas sobre el manuscrito (prosa del `<div class="contenido">`, excluyendo figuras, código y notas al margen):

| | Resto del libro | Capítulo 29 | Objetivo |
|---|---|---|---|
| Palabras por párrafo (media) | 52,8 | **19,9** | ≤ 25 |
| Párrafo más largo | 79–178 | **49** | ≤ 60 |
| Palabras por frase (media) | 18,3 | **12,0** | ≤ 14 |

No son cuotas que haya que cumplir con la calculadora. Son el síntoma: si un capítulo mide 50 palabras por párrafo, tiene ideas apelotonadas. El script de §11 da el número en un segundo.

---

## 3. Un párrafo, una idea

Regla dura. Si un párrafo dice dos cosas, son dos párrafos.

**Antes** (76 palabras, cuatro ideas):

> Imagina una pantalla partida en dos. A la izquierda, una aplicación de gestión cualquiera: un menú lateral, un formulario de venta con sus campos, una grilla con los últimos registros. Nada que un programador no haya construido cien veces. A la derecha, en un panel angosto, una lista que crece a cada clic. Ese panel no describe la aplicación: *es* la aplicación.

**Después** (cinco párrafos):

> Imagina una pantalla partida en dos.
>
> A la izquierda, una aplicación de gestión como cualquier otra: un menú lateral, un formulario de venta, una grilla con los últimos registros. Nada que un programador no haya construido cien veces.
>
> A la derecha, una lista que crece a cada clic. Cada línea afirma una cosa mínima: «la venta tiene un campo llamado monto». Y debajo otra, y otra.
>
> Esa lista no describe la aplicación de la izquierda.
>
> Esa lista *es* la aplicación.

Un párrafo de una línea no es un error de maquetación. Es el énfasis del libro.

---

## 4. El remate va solo

Las frases que cargan el peso de una sección van en su propio párrafo, sin nada delante ni detrás que las diluya.

- «El sistema nos detuvo.»
- «La estructura es dato.»
- «Cinco hechos, cero líneas.»
- «Falta una prueba, y es la más incómoda.»
- «El grafo no describe el sistema. El grafo *es* el sistema.»

Enterrar el remate al final de un párrafo de sesenta palabras lo desperdicia.

---

## 5. La jerga se glosa, no se quita

El término técnico se queda. Lo que cambia es que llega **después** de la idea, no antes.

Patrón: *primero en castellano, luego el nombre propio.*

**Antes:**

> El menú es un objeto reificado que `tiene_opcion` a otros objetos; cada opción `tiene_accion` una acción; cada acción es `instancia_de` un verbo (`mostrar_texto`, `abrir_formulario`…) que un evaluador genérico interpreta.

**Después:**

> Un menú no es una pieza programada. Es un puñado de relaciones. Cada opción del menú lleva una acción, y cada acción dice de qué tipo es: mostrar un texto, abrir un formulario, abrir una grilla, guardar. El motor conoce esos verbos y sabe qué hacer con cada uno.
>
> Escrito con los nombres que usa el prototipo, el menú se ve así:
>
> ```
> (menu_principal, tiene_opcion, opcion_ventas)
> (opcion_ventas,  tiene_accion, abrir_grilla_venta)
> ```

La prosa explica. El bloque de código nombra. Nadie pierde nada.

---

## 6. Las cuatro capas

El libro sigue siendo estratificado. La simplificación **solo afecta a la prosa corrida**. Estas cuatro capas conservan su registro técnico y no se tocan:

| Capa | Registro | Ejemplo |
|---|---|---|
| Bloques de código y sus etiquetas | Canónico, sin glosa | `tripletas · el campo declara su propia signatura` |
| Pies de figura | Técnico, denso | «Cada uno de los siete ejes es una `instancia_de` el concepto «eje»…» |
| Notas al margen `caja--precedente` / etiqueta «Referencia» | Académico, con citas | «La bitemporalidad se enuncia formalmente en el capítulo 9» |
| Cajas de definición | Preciso, pero en frases cortas | La caja del comodín V |

Un lector neófito puede saltarse las cuatro y seguir entendiendo el capítulo. Un lector técnico las lee y encuentra el rigor. Esa es la estratificación de `GUIA-DE-ESTILO.md` §1, intacta.

---

## 7. Sustituciones

Salidas reales del capítulo 29. Sirven de patrón, no de diccionario cerrado.

| Jerga | En prosa |
|---|---|
| un despachador genérico que delega en el manejador del verbo | un repartidor que recibe una acción, mira de qué tipo es y se la pasa a quien sabe ejecutarla |
| bitemporalidad en miniatura | el historial sale gratis, y ningún dato nuevo pisa al viejo |
| el clásico «update» de cualquier CRUD | lo que en cualquier programa se llama «editar» |
| un literal en K, minteado y único | un nodo que se acuña en el momento y no se comparte con nadie |
| cada campo deriva su signatura (dominio, rango) | cada campo dice por sí mismo qué se le puede escribir |
| el tipado dejó de vivir en Python | las reglas de validación dejaron de vivir en el código |
| la abstracción reflexiva tiene un peaje cognitivo | toda esa potencia se paga con esfuerzo mental |
| un modelo de lenguaje operando la interfaz | una IA habló con el grafo por su cuenta |
| vistas y proyecciones con nombre | vistas con nombre |
| la signatura `V→K` | la regla `V→K` dice: a la izquierda puede ir algo de cualquier eje de valor; a la derecha, una clase |
| entidades semánticas, no tipos primitivos | los siete ejes responden a preguntas, no a tipos de programación |
| el catálogo canónico tipa con fuerza | el catálogo del modelo vigila con rigor sus propios roles |
| re-concreta lo suficiente | devuelve algo de suelo firme |

**Términos que se quedan siempre**, porque son el vocabulario del libro: eje, hecho, tripleta, grafo, lexicon, rol, clase, situación, vigencia, los nombres de las decisiones `Dn` y los siete ejes (Q, O, L, T, N, K, M).

---

## 8. Listas

Cuando la prosa enumera tres cosas o más con la misma forma, es una lista.

**Antes:**

> El esquema de una entidad también es dato: la entidad `tiene_campo` a descriptores que declaran su etiqueta, su `tipo_dato` y su `orden`.

**Después:**

> Con la forma de las entidades pasa lo mismo:
>
> - una entidad tiene campos
> - un campo tiene una etiqueta
> - un campo tiene un tipo
> - un campo tiene un orden

Sin `class`: en `.contenido`, el `<ul>` desnudo ya lleva sus viñetas de color. Ítems cortos, sin punto final, en minúscula.

---

## 9. Lo que se quita

**Los resúmenes de capítulos anteriores.** El lector viene de leerlos. Un recordatorio de dos párrafos se reduce a una línea o desaparece.

- Antes: dos párrafos repasando el lenguaje, los ocho dominios, el yaku y los cuatro casos de estrés, con cuatro enlaces.
- Después: «Hasta aquí, el libro ha apretado a WQuestions siempre desde fuera: el lenguaje, ocho dominios industriales, un sistema real en producción, cuatro casos elegidos para que crujiera.»

Los enlaces a otros capítulos se conservan donde el lector los necesita, no en un repaso.

**Las dos columnas.** `<div class="columnas">` parte la prosa en un cuerpo más chico y estrecho, lo que empuja justo en contra de lo que busca esta guía. Los párrafos van a una sola columna. La regla CSS sigue viva en `estilo.css:495` porque la usan 30 capítulos; se quita el envoltorio en cada capítulo al reescribirlo.

Esto **no** afecta a `rejilla-2` ni a `rejilla-3`: ahí las columnas son la comparación misma (las tarjetas «antes / después» de una figura, el par literal-vs-categoría de una caja), no prosa partida.

**Las declaraciones de honradez.** Sin «venimos con honradez a mostrar», sin «seamos sinceros». Los límites se muestran contándolos, no anunciándolos. Ver la memoria del proyecto sobre el tono.

---

## 10. Trampas de marcado

**`.nodo` fuera de `.triple`.** El CSS solo estiliza `.triple .nodo` (`estilo.css:387`). Suelto en un párrafo, el `<small>O</small>` del componente se dibuja crudo y pegado a la palabra: «ventaO». Dentro de la prosa, di la tripleta en castellano; si hace falta verla, ponla en un `<div class="triple">` propio o en un bloque de código.

**La raya (—).** Sigue vigente lo de siempre: paréntesis para lo secundario, dos puntos para introducir, raya solo para ritmo o énfasis real. En prosa de frases cortas casi nunca hace falta. El capítulo 29 no tiene ninguna en el cuerpo.

**El primer párrafo** lleva `class="entrada"` (capitular). Con el registro nuevo suele ser de una sola línea, y funciona: la capitular sobre una frase corta abre fuerte.

---

## 11. Comprobación

Antes de dar un capítulo por terminado:

- [ ] ¿Algún párrafo de prosa pasa de 60 palabras?
- [ ] ¿Algún párrafo dice dos cosas?
- [ ] ¿Hay un término técnico que aparece antes de su glosa?
- [ ] ¿El remate de cada sección va solo en su párrafo?
- [ ] ¿Quedan enumeraciones de tres o más enterradas en la prosa?
- [ ] ¿Queda algún resumen de capítulos anteriores de más de una línea?
- [ ] ¿Queda algún `<div class="columnas">`?
- [ ] ¿Queda algún `.nodo` fuera de un `.triple`?
- [ ] ¿Siguen intactos figuras, código, tripletas y cajas?
- [ ] ¿El HTML cierra bien?

Las cuatro últimas y las cifras se comprueban con esto, desde `libro/manuscrito2/`:

```python
# python3 revisar.py 29-prueba-reflexiva.html
import re, sys, html.parser

class P(html.parser.HTMLParser):
    VACIOS = {'meta','link','br','img','hr','input','path','circle',
              'line','rect','use','marker','stop'}
    def __init__(self): super().__init__(); self.pila = []
    def handle_starttag(self, t, a):
        if t not in self.VACIOS: self.pila.append(t)
    def handle_endtag(self, t):
        if self.pila and self.pila[-1] == t: self.pila.pop()
        elif t in self.pila: print(f'  DESBALANCE en <{t}>')

for archivo in sys.argv[1:]:
    src = open(archivo).read()
    p = P(); p.feed(src)
    cuerpo = re.search(r'<div class="contenido">(.*)</div>\s*</article>', src, re.S).group(1)
    prosa = re.sub(r'<figure.*?</figure>|<pre>.*?</pre>|<aside.*?</aside>', '', cuerpo, flags=re.S)
    ps = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', x)).strip()
          for x in re.findall(r'<p[^>]*>(.*?)</p>', prosa, re.S)]
    ps = [x for x in ps if x]
    largos = [len(x.split()) for x in ps]
    frases = sum(len([s for s in re.split(r'(?<=[.!?])\s', x) if s.strip()]) for x in ps)
    nodos = len(re.findall(r'class="nodo', cuerpo)) - 3 * cuerpo.count('class="triple')

    print(f'\n{archivo}')
    print(f'  balance HTML .... {"ok" if not p.pila else p.pila}')
    print(f'  media ........... {sum(largos)/len(largos):.1f} palabras/párrafo  (objetivo ≤ 25)')
    print(f'  máximo .......... {max(largos)} palabras                (objetivo ≤ 60)')
    print(f'  frase ........... {sum(largos)/frases:.1f} palabras/frase    (objetivo ≤ 14)')
    print(f'  columnas ........ {src.count(chr(34)+"columnas"+chr(34))}                        (objetivo 0)')
    print(f'  nodos sueltos ... {max(0, nodos)}                        (objetivo 0)')
    for x in ps:
        if len(x.split()) > 60: print(f'  LARGO ({len(x.split())}): {x[:90]}…')
```

El conteo de nodos sueltos asume tres `.nodo` por `.triple` (sujeto, enlace, valor); si un capítulo usa tripletas parciales, revísalo a ojo.

---

## 12. Lo que esta guía no cambia

Todo lo de [`GUIA-DE-ESTILO.md`](GUIA-DE-ESTILO.md) sigue en pie sin excepción:

- El tuteo neutro, sin voseo ni regionalismos.
- La numeración `Dn` y su mapa autoritativo. Ninguna `caja--decision` con un número inventado.
- El repertorio de ejemplos canónicos (§4) y los identificadores estables.
- Los componentes, el sistema de color por eje, el esqueleto HTML, el mapa de capítulos.
- El contenido sustantivo: la arquitectura, las reglas, las convenciones, los precedentes.

Simplificar el registro nunca es excusa para perder una idea. Si al reescribir un pasaje desaparece un matiz, el pasaje está mal reescrito: hay que partirlo en más frases, no en menos ideas.

---

## 13. Orden de trabajo por capítulo

0. **Invocar la skill `humanizalo`.** Obligatorio, siempre, antes de escribir una sola frase. Las excepciones donde manda este libro y no la skill están en [`GUIA-DE-ESTILO.md`](GUIA-DE-ESTILO.md) §1.
1. Leer el capítulo entero antes de tocar nada.
2. Correr el script para tener el punto de partida.
3. Reescribir la prosa por bloques, de arriba abajo. Figuras, código, tripletas y cajas se dejan donde están.
4. Quitar el envoltorio `columnas` y airear las cajas de más de una idea.
5. Recortar los resúmenes de capítulos previos.
6. Volver a correr el script y pasar la lista de §11.
7. Regenerar los PDF con `generar_pdf_html.py` cuando el lote esté cerrado, no capítulo a capítulo.
