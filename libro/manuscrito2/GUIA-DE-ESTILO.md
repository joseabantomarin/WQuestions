# Guía de estilo — manuscrito2 (HTML)

> Documento **interno**, no forma parte del libro. Define el canon para que los 33 archivos sean coherentes en voz, ejemplos y componentes.

## 1. Voz y redacción

- **Español neutro.** Tuteo neutro (`tú tienes`, `puedes`, `quieres`, `imagina`, `piensa`). **Prohibido el voseo argentino** (`vos tenés`, `podés`, `querés`) y los regionalismos.
- **Estilo:** académico pero claro y explicativo (aspiración Hofstadter / Pinker). Cada capítulo abre con una escena o anécdota concreta, nunca con una definición seca; sube densidad técnica hacia el final.
- **Estratificado en tres capas:** lector general (primer tercio), profesional técnico (modelado, código), académico (precedentes citados). El texto debe poder leerse "en superficie" o "a profundidad".
- **Redacción desde cero:** no copiar frases del manuscrito original. Reescribir con prosa nueva.
- **Conceptos y decisiones de diseño (Dn): preservar fielmente.** El contenido sustantivo (la arquitectura, las reglas Dn, las convenciones, los precedentes) NO cambia. **Respeta la numeración `Dn` exactamente como aparece en el `.md` fuente del capítulo; no la inventes ni la "corrijas". NUNCA introduzcas una caja `caja--decision` con un `Dn` que no esté definido en tu `.md` fuente** (las Dn se referencian entre capítulos; inventar una colisiona con otro capítulo). Si un punto es importante pero no es una Dn formal del fuente, usa `caja--idea`/`caja--definicion`/`caja--practica`, sin número.

  **Mapa autoritativo de las decisiones de diseño** (cada una se ENUNCIA formalmente solo en su capítulo; en otros capítulos solo se REFERENCIA por su número):

  | Dn | Qué decide | Se define en |
  |----|-----------|--------------|
  | D1 | En K viven los conceptos atemporales (plantillas); en O y los pilares, las entidades situadas (instancias) | Cap 3 (clase) |
  | D2 | Propiedades y relaciones se unifican: son cables del eje M; solo difieren en cardinalidad (funcional vs múltiple) | Cap 5 (predicados) |
  | D3 | Todo hecho es una tripleta tipada `(sujeto, cable, objeto)`; lo complejo se apila | Cap 7 (hecho atómico) |
  | D4 | Un evento/relación se reifica como situación en O solo si cumple ≥1 de 4 requisitos | Cap 9 (situaciones) |
  | D5 | Agencia contextual: el rol `agente` lo pueden ocupar humanos, organizaciones, software o sensores, según el verbo | Cap 9 (situaciones) |
  | D6 | Vigencia: las propiedades que cambian se reifican con rango `inicio`/`fin` (bitemporalidad) | Cap 9 (situaciones) |
  | D7 | No hay eje "por qué"; el porqué se divide en 4 cables: `causado_por`, `motivado_por`, `con_finalidad`, `justificado_por` | Cap 10 (por qué) |
  | D8 | El catálogo canónico es invisible; el lexicon es la interfaz | Cap 12 (lexicon) |
  | D9 | El usuario final nunca toca etiquetas canónicas; usa su vocabulario y el sistema traduce | Cap 12/13 (lexicon / lingüística) |

  Verifica el número EXACTO en tu `.md` fuente antes de escribir una `caja--decision`. Si tu capítulo solo referencia una Dn (no la define), menciónala en prosa o en una `nota-margen`, no en una `caja--decision`.
- **Ejemplos nuevos:** usa el repertorio de §4. No uses los ejemplos del original (risotto, gol de Messi, Yesterday, decreto presidencial).

## 2. Esqueleto HTML de un capítulo

Todos los capítulos comparten esta plantilla. `assets/` se enlaza con ruta relativa (los archivos están en la misma carpeta que `assets/`).

```html
<!DOCTYPE html>
<html lang="es" data-tema="claro">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cap. N · Título — WQuestions</title>
  <link rel="stylesheet" href="assets/estilo.css">
  <script>document.documentElement.classList.add('js')</script>
</head>
<body>
  <div class="barra-progreso" aria-hidden="true"></div>

  <header class="cabecera">
    <a class="marca" href="index.html">
      <span class="glifo"><i></i><i></i><i></i><i></i><i></i><i></i></span>
      WQuestions
    </a>
    <div class="acciones">
      <button class="btn-cromo" data-accion="tema" aria-label="Cambiar tema">◐ Tema</button>
      <button class="btn-cromo" data-accion="indice" aria-expanded="false">☰ Índice</button>
    </div>
  </header>

  <div class="velo" data-abierto="no"></div>
  <aside class="drawer-indice" data-abierto="no" aria-label="Índice del capítulo">
    <h2>En este capítulo</h2>
    <nav class="lista-secciones"></nav>
    <p style="margin-top:1.4rem"><a href="index.html">← Índice completo del libro</a></p>
  </aside>

  <main class="libro">
    <article class="capitulo" style="--cap:'N'">
      <header class="portada-cap">
        <p class="parte">Parte II · Las siete coordenadas</p>
        <div class="num-cap">02</div>
        <h1>Título del capítulo</h1>
        <p class="lede">Frase-resumen evocadora de una o dos líneas.</p>
      </header>

      <div class="contenido">
        <p class="entrada">Primer párrafo (lleva capitular automática)…</p>
        <!-- secciones con <h2>, componentes, etc. -->
      </div>
    </article>

    <nav class="nav-cap">
      <a class="ant" href="01-....html"><span class="dir">← Anterior</span><span class="tit">Título previo</span></a>
      <a class="sig" href="03-....html"><span class="dir">Siguiente →</span><span class="tit">Título siguiente</span></a>
    </nav>
  </main>

  <script src="assets/interacciones.js"></script>
</body>
</html>
```

- `--cap:'N'` en `<article>` numera las figuras como `Figura N.x` (lo pone el atributo, no el JS).
- El primer párrafo del cuerpo usa `class="entrada"` (o `class="capitular"`) para la letra capitular.
- El JS construye solo el índice lateral (scrollspy) y el resaltado; no hay que listar las secciones a mano.

## 3. Componentes (clases)

| Propósito | Marcado |
|---|---|
| **Caja: decisión de diseño** | `<div class="caja caja--decision"><p class="caja-tit"><span class="codigo-d">D3</span> El hecho atómico</p>…</div>` |
| **Caja: idea clave** | `<div class="caja caja--idea"><p class="caja-tit">Idea clave</p>…</div>` |
| **Caja: en la práctica** | `caja caja--practica` |
| **Caja: trampa/alerta** | `caja caja--alerta` |
| **Caja: precedente académico** | `caja caja--precedente` |
| **Caja: definición** | `caja caja--definicion` |
| **Cita destacada (pull quote)** | `<p class="cita-destacada">…<cite>Atribución</cite></p>` |
| **Nota al margen** | `<aside class="nota-margen"><span class="etq">Nota</span>…</aside>` (colócala justo antes del párrafo al que acompaña) |
| **Dos columnas** | `<div class="columnas">…</div>` (para pasajes densos / listas largas) |
| **Rejilla comparativa** | `<div class="rejilla-2">` o `rejilla-3` con `<div class="tarjeta">` |
| **Chip de eje** | `<span class="eje eje--q">Q</span>` · rótulo: `<span class="eje-rotulo"><span class="eje eje--q">Q</span> quién</span>` |

### Tripleta (componente insignia)

```html
<div class="triple">
  <span class="nodo nodo--o"><span>venta_001</span><small>O</small></span>
  <span class="enlace">agente<span class="firma">M(O→Q)</span></span>
  <span class="nodo nodo--q"><span>vendedor_17</span><small>Q</small></span>
</div>
```

### Bloque de código

`data-lang` ∈ `triple` · `json` · `sql` · `python` · `text`. El resaltador y el botón copiar son automáticos.

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">tripletas</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="triple">(venta_001, agente, vendedor_17)   ∈ M(O, Q)
(venta_001, monto,  49.90)         ∈ M(O, N)</code></pre>
</div>
```

### Figura SVG / infografía

```html
<figure class="figura figura--ancha revelar">
  <div class="lienzo"><!-- SVG inline, usa var(--eje-q) … para colorear --></div>
  <figcaption><span class="fnum">Figura 2.1.</span> Texto de la figura.</figcaption>
</figure>
```
Variantes: `figura--ancha` (texto + margen), `figura--margen` (mete la figura en el margen). Añade `revelar` para animación de entrada.

### Chart (dato cuantitativo)

```html
<figure class="figura revelar">
  <div class="lienzo" data-chart>
    <script type="application/json">
      {"tipo":"barras","eje":"n","unidad":"%","datos":[{"l":"SQL","v":34},{"l":"WQ","v":3,"color":"k"}]}
    </script>
  </div>
  <figcaption><span class="fnum">Figura 7.2.</span> …</figcaption>
</figure>
```
Tipos: `barras` (datos `{l,v,color?}`), `lineas` (`series:[{nombre,color,datos:[{x,y}]}]`), `dispersion` (`{x,y,l,color,r}`). `eje` fija el color por defecto (q/o/l/t/n/k/m).

## 4. Repertorio de ejemplos (canon — usar identificadores estables)

Reemplaza al repertorio original. Hílalo de forma consistente por todo el libro.

| Dominio | Para ilustrar | Identificadores canónicos |
|---|---|---|
| 👕 **Venta (camiseta)** | transacción cotidiana, composición (apilar tripletas), reificación, unidades (monto/moneda, cantidad, impuesto) | venta `venta_001`; vendedor `vendedor_17`; cliente `cliente_1042`; objeto `camiseta_88`; N: monto 49.90, moneda `Currency:USD`, cantidad, impuesto 18 %; T: `2026-05-14T16:32`; L: `tienda_centro`; K: `venta`, `camiseta` |
| ⚽ **Fútbol (gol)** | evento con varios agentes, reificación n-aria, concurrencia, estado derivado | gol `gol_001` (agente `messi`, asistente `di_maria`, `parte_de partido_arg_per_2026`, minuto 87, pierna zurda); pase `pase_001` (agente `messi`, beneficiario `di_maria`, `objeto_pase balon_partido_001`, instrumento `pierna_izquierda`, minuto 87) |
| 🎬 **Cine** | autoría (roles distintos), recursión/composición, tiempo narrativo | obra `pelicula_marea`; directora `serra`; guionista `haddad`; escena `escena_42` (`parte_de pelicula_marea`); T narrativo "final del segundo acto"; K: `largometraje`, `genero_drama` |
| 🏛️ **Ordenanza municipal** | fechas, vigencia, entidades afectadas, tiempo derivado por reglas | `ordenanza_142` (micromovilidad); agente `municipalidad_centro` / `alcalde_reyes`; `fecha_publicacion`, `entra_en_vigor` (a los 30 días); `afecta_a`: `gerencia_transito`, `gerencia_fiscalizacion`; K: `ordenanza_municipal` |
| 🤖 **Agente de IA** | telemetría moderna, unidades nuevas, K = modelos/herramientas | sesión `sesion_ia_5521`; modelo `modelo_lumen_2026`; usuaria `paredes`; N: tokens_entrada 4180, tokens_salida 920, latencia_ms 2100, costo_usd 0.015; herramientas `busqueda_web`, `consulta_grafo` |
| 🏥 **Urgencias** | narrativa marco (abre Cap. 1, cierra Conclusión) | paciente `vega`; episodio `urgencias_2026_xxx`; historia repartida entre cardiólogo, endocrinóloga y dos hospitales |

Los **8 dominios industriales** de la Parte V (spa, taxi, clínica, banco, ERP, universidad, municipalidad, minera) y los **4 dominios de estrés** (música, química, fútbol, contratos) son parte sustantiva del libro: **se conservan como dominios**, pero con datos y escenarios nuevos (no copiar los del original).

## 5. Mapa de capítulos (archivo · parte · prev/next)

| # | Archivo | Parte | Título corto |
|---|---|---|---|
| — | `00-introduccion.html` | Frontal | Introducción |
| 1 | `01-torre-de-babel.html` | I — El problema | La torre de Babel de los datos |
| 2 | `02-cuatro-pilares.html` | II — Las siete coordenadas | Quién, qué, dónde, cuándo |
| 3 | `03-clase.html` | II | Cuál: el zócalo categórico (K) |
| 4 | `04-cuanto.html` | II | Cuánto: el eje cuantitativo (N) |
| 5 | `05-predicados.html` | II | Cómo: los predicados (P y M) |
| 6 | `06-raices.html` | II | Las raíces: por qué estas preguntas |
| 7 | `07-hecho-atomico.html` | III — Cómo funcionan juntas | El hecho atómico |
| 8 | `08-espacio-multidimensional.html` | III | El espacio multidimensional |
| 9 | `09-situaciones.html` | III | Situaciones, contextos y agencia |
| 10 | `10-por-que.html` | III | El "por qué" no es un eje |
| 11 | `11-identidad.html` | III | La identidad a través de los sistemas |
| 12 | `12-puentes.html` | III | Puentes: objetos, bits, grafos y cadenas |
| 13 | `13-verbo.html` | IV — Del lenguaje a los hechos | El verbo como signatura |
| 14 | `14-lexicon.html` | IV | El lexicon como compilador |
| 15 | `15-bajo-presion.html` | IV | El modelo bajo presión |
| 16 | `16-spa.html` | V — En la práctica | Un sistema de ventas (spa) |
| 17 | `17-taxi.html` | V | Un servicio on-demand (taxi) |
| 18 | `18-clinica.html` | V | Una historia clínica (+ hospitalización, farmacia) |
| 19 | `19-banco.html` | V | El dominio más exigente: un banco |
| 20 | `20-erp.html` | V | Un ERP multi-módulo |
| 21 | `21-universidad.html` | V | Una universidad |
| 22 | `22-municipalidad.html` | V | Una municipalidad (+ trámites, expediente) |
| 23 | `23-minera.html` | V | Una operación minera (+ comisionamiento, punchlists) |
| 24 | `24-yaku.html` | V | Arqueología de un sistema real (yaku) |
| 25 | `25-cuatro-dominios.html` | V | Música, química, fútbol, contratos |
| 26 | `26-llms.html` | VI — IA, futuro y cierre | WQuestions y los LLMs |
| 27 | `27-aplicaciones.html` | VI | Aplicaciones futuras |
| 28 | `28-prueba-reflexiva.html` | VI | La prueba reflexiva |
| 29 | `29-seguridad.html` | VI | Seguridad y privacidad |
| 30 | `30-que-falta.html` | VI | Qué falta |
| 31 | `31-conclusion.html` | VI | Conclusión: por qué importan |
| 32 | `32-anexo-codigo.html` | Anexos | Anexo: el código |
| 33 | `33-anexo-prototipo.html` | Anexos | Anexo: el prototipo |
| 34 | `34-el-autor.html` | Anexos | El autor |

## 6. Sistema de color por eje

| Eje | Pregunta | Rol | Token | Clase chip / nodo / token-código |
|---|---|---|---|---|
| Q | quién | agente | `--eje-q` | `eje--q` / `nodo--q` / `tk-q` |
| O | qué | objeto | `--eje-o` | `eje--o` / `nodo--o` / `tk-o` |
| L | dónde | lugar | `--eje-l` | `eje--l` / `nodo--l` / `tk-l` |
| T | cuándo | tiempo | `--eje-t` | `eje--t` / `nodo--t` / `tk-t` |
| N | cuánto | número | `--eje-n` | `eje--n` / `nodo--n` / `tk-n` |
| K | cuál | clase | `--eje-k` | `eje--k` / `nodo--k` / `tk-k` |
| M | cómo | predicado | `--eje-m` | `eje--m` / (enlace) / `tk-m` |

Usa estos colores de forma consistente en figuras y código: el lector aprende a "ver" los ejes.
