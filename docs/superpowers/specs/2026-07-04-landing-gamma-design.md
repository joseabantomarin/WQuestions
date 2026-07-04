# Diseño — Landing de entrada estilo Gamma para GitHub Pages

**Fecha:** 2026-07-04
**Autor del proyecto:** José Abanto Marín
**Sitio:** https://joseabantomarin.github.io/WQuestions/ (sirve `libro/manuscrito2/`)
**Referencia de contenido:** https://wquestions-ubie-9finq2s.gamma.site/

## Contexto y objetivo

El sitio de GitHub Pages sirve el directorio `libro/manuscrito2/`, cuyo `index.html`
actual es la **portada + índice del libro** (héroe, franja de los 7 ejes, tabla de
contenidos por partes). El sitio de Gamma es una **landing de marketing** con una
narrativa persuasiva (problema → solución → 7 coordenadas → interoperabilidad →
IA/LLMs → casos de uso → código → autor → CTA).

**Objetivo:** crear una **nueva landing como puerta de entrada** al sitio, que tome la
narrativa del Gamma y conduzca al libro. La landing pasa a ser el `index.html` raíz;
el índice actual se muda a su propia página.

## Decisiones tomadas (brainstorming)

| Decisión | Elección |
|---|---|
| Enfoque | Nueva landing separada; el índice actual pasa a página propia |
| Estilo visual | Replicar el look de Gamma (tema claro, tarjetas, grid, botones sólidos) |
| Paleta de las 7 tarjetas | Los 7 colores de eje del libro (`--eje-q` … `--eje-m`) |
| Texto | Adaptar a la voz del libro (sin muletillas de IA ni auto-declarar rigor) |
| Título del héroe (H1) | «Las preguntas como coordenadas» (continuidad con el libro) |
| Casos de uso | Enlazar a capítulos reales de la Parte V |

## Arquitectura y archivos

1. **Renombrar** `libro/manuscrito2/index.html` → `libro/manuscrito2/indice.html`
   (con `git mv`). Queda intacto: sigue siendo la tabla de contenidos del libro.
   Su enlace de marca (`class="marca" href="index.html"`) sigue apuntando a `index.html`,
   que ahora es la landing (home). Correcto.
2. **Crear** un nuevo `libro/manuscrito2/index.html` = la landing estilo Gamma.
3. **Crear** `libro/manuscrito2/assets/landing.css`: hoja autónoma con el look Gamma
   que **reutiliza los tokens del libro** (variables `--eje-*`, `--acento` `#1f6f8b`,
   `--tinta`, papel, y el tema `data-tema="oscuro"`). No se modifica `estilo.css`.
4. **Reutilizar** `assets/interacciones.js` para el toggle de tema (botón «◐ Tema») y,
   opcionalmente, la barra de progreso. Si `interacciones.js` asume elementos del libro
   que no existen en la landing, se usa un guard mínimo o un script inline equivalente
   para el toggle (persistencia del tema en `localStorage`, igual que el resto del sitio).
5. **Copiar** `libro/portada.png` → `libro/manuscrito2/assets/img/portada.png` para usarla
   como visual del héroe / bloque «Leer el libro» (Pages solo sirve lo de `manuscrito2/`).

### Navegación (wiring)

- Los 34 capítulos ya enlazan `home` a `index.html`; con el cambio, «home» es la landing.
  **No se editan los capítulos.**
- CTAs de la landing:
  - «Leer el libro» / «Ver el índice» → `indice.html`
  - «Empezar por la introducción» → `00-introduccion.html`
  - «Ver el prototipo (Python)» → `33-anexo-prototipo.html`
  - «El código» → `32-anexo-codigo.html`
  - Casos de uso → capítulos concretos (ver mapeo abajo)
  - «Descargar PDF» → `WQuestions.pdf`

## Estructura de secciones y copy (adaptado a la voz del libro)

> El copy final se pasa por la guía de tono del libro: sin muletillas de IA, sin
> auto-declarar «rigor/honestidad», español neutro (tuteo neutro, no voseo).

1. **Header** — marca «WQuestions» (glifo de 6 puntos), botón «◐ Tema», CTA «Leer el libro».
2. **Héroe**
   - Super: «Arquitectura universal de la información»
   - H1: «Las preguntas como **coordenadas**»
   - Bajada: «Quién, qué, dónde, cuándo, cuánto, cuál y cómo. Siete preguntas bastan
     para organizar la información de cualquier dominio —y para que la inteligencia
     artificial trabaje con nuestros datos sin perder rigor.»
   - Franja de los 7 ejes (pills con punto de color, como en el índice actual).
   - CTAs: «Leer el libro» · «Ver el prototipo». Visual: `portada.png`.
3. **El problema — La torre de Babel de los datos**
   - Intro: «La información existe, pero no puede dialogar. Cada sistema habla su idioma.»
   - 3 tarjetas: Sistemas aislados · Vocabularios incompatibles · Fragmentación.
4. **La solución — Un modelo basado en siete preguntas**
   - «Cualquier hecho puede describirse respondiendo siete preguntas. Funcionan como
     coordenadas: ubican, relacionan y transmiten un dato sin ambigüedad, igual que la
     latitud y la longitud ubican un punto en el mapa.»
5. **Las 7 coordenadas** — 7 tarjetas numeradas, cada una con el color de su eje:
   - Q ¿Quién? · O ¿Qué? · L ¿Dónde? · T ¿Cuándo? · N ¿Cuánto? · K ¿Cuál? · M ¿Cómo?
   - Las tarjetas son informativas (sin enlace por tarjeta, porque no hay mapeo 1:1
     eje↔capítulo). Debajo de la sección, un único enlace «Conócelas en detalle»
     → `02-cuatro-pilares.html`.
6. **Interoperabilidad — Del caos a un idioma común**
   - Gramática común + escalabilidad sin acuerdos bilaterales.
   - 3 beneficios: sin middleware a medida · sin traducciones ad hoc · sin pérdida de contexto.
7. **IA & LLMs — El puente con los modelos de lenguaje**
   - Intro sobria (sin «el idioma que las máquinas ya comprenden»).
   - 3 pilares: unidades de significado · datos que un modelo consume sin preprocesar ·
     puente humano-máquina (el lexicon). Enlace → `26-llms.html`.
8. **Casos de uso — El mismo modelo en cualquier dominio** (grid, enlaza a capítulos):
   | Tarjeta | Capítulo |
   |---|---|
   | Una historia clínica | `18-clinica.html` |
   | El dominio más exigente: un banco | `19-banco.html` |
   | Una operación minera | `23-minera.html` |
   | Una municipalidad | `22-municipalidad.html` |
   | Una universidad | `21-universidad.html` |
   | Un sistema de ventas | `16-spa.html` |
   - Pie: «…y más en la Parte V» → `indice.html`.
9. **Del concepto al código** — enfoque empírico: Python + prototipo ejecutable.
   Enlaces → `32-anexo-codigo.html`, `33-anexo-prototipo.html`.
10. **El autor** — José Abanto Marín (bio breve del cap. 34). Enlace → `34-el-autor.html`.
11. **CTA final** — «Construye sistemas que hablen el mismo idioma.»
    Botones: «Leer el libro» → `indice.html` · «Empezar por la introducción» → `00-introduccion.html`.
12. **Footer** — índice · PDF · código/prototipo · © José Abanto Marín.

## Estilo visual

- **Tema claro por defecto** (aire Gamma): fondo claro, acento petróleo `#1f6f8b`.
  **Tema oscuro** soportado con el mismo `data-tema="oscuro"` y toggle del sitio.
- **Componentes**: tarjetas con esquinas redondeadas (~12px) y sombra suave; números
  grandes en las 7 coordenadas, tintados con el color/`--eje-*-suave` de su eje; grid
  responsivo (1 col móvil → 3-4 col escritorio) en las 7 coordenadas y en casos de uso;
  botones sólidos (acento) + botón secundario con borde.
- **Tipografía**: usa los tokens del libro (`--display`, `--serif`, `--sans`); títulos
  con `--display`, cuerpo con `--serif`/`--sans`.
- **Accesibilidad**: contraste AA en ambos temas; grid colapsa en móvil; imágenes con `alt`.

## Fuera de alcance (YAGNI)

- No se rediseña el interior del libro ni sus 34 capítulos.
- No se edita `estilo.css` ni el índice (`indice.html`) más allá del renombrado.
- No se añaden dependencias externas ni frameworks; todo CSS/JS local (CSP-friendly).
- No se cambia el workflow de Pages (`static.yml` ya publica todo `manuscrito2/`).

## Criterios de éxito / verificación

1. Abrir `index.html` local muestra la landing con las 12 secciones y los 7 colores de eje.
2. Toggle de tema funciona (claro ↔ oscuro) y persiste.
3. Todos los enlaces resuelven a archivos existentes (`indice.html`, capítulos, PDF, anexos).
4. `indice.html` sigue funcionando y su índice enlaza a los capítulos.
5. Responsivo: sin scroll horizontal en móvil; grids colapsan.
6. Copy sin muletillas de IA ni auto-declaraciones de rigor (revisión de tono).
