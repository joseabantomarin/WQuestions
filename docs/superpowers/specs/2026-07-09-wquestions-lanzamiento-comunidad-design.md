# WQuestions — Estrategia de lanzamiento y comunidad

**Fecha:** 2026-07-09
**Estado:** Diseño aprobado. Fase 0 en ejecución.
**Autor:** Jose Abanto (con Claude)

## Contexto

WQuestions es un estándar de modelado de información sobre 7 ejes-pregunta
(Q quién, O qué, L dónde, T cuándo, N cuánto, K clase, M cómo). Activos
existentes: libro (español, `libro/manuscrito2/` es la edición canónica),
prototipo Python funcional (`prototipo/`, motor `wq` sin dependencias, ~8
dominios modelados, 59 tests en verde), stress-tests documentados, y un
testbed real (yaku).

El problema no es el contenido, es la **distribución** y la **comunidad**.

## Decisiones que fijan la estrategia

| Eje | Decisión | Implicación |
|-----|----------|-------------|
| Audiencia núcleo | Devs de IA / LLM | Adoptan código que corre, no libros |
| Idioma de arranque | Inglés primero | El libro español es capa de profundidad, no la puerta |
| Dedicación | Baja (2-4 h/semana) | El motor de contenido debe ser reciclaje, no producción |
| Posicionamiento | Mixto | Jose al frente ahora; el estándar toma vida propia |
| Gancho viral inicial | Servidor MCP | Máximo "wow" para devs; aprovecha el prototipo |

## Tesis central

Para devs de IA **el libro no es la unidad viral**. La unidad viral es
**WQuestions empaquetado como estándar abierto + un servidor MCP** que deja
que un LLM modele cualquier dominio con el esquema de 7 ejes, sin ontología
por-dominio. La ruta de adopción ya estaba anticipada en las notas del
proyecto: *"el lexicon es esencialmente un function schema; exponer
WQuestions vía MCP a LLMs"*.

## Camino elegido: Repo-first / jugada de "protocolo"

Unidad viral = repo GitHub (estándar abierto) + demo MCP + ensayo-tesis.
Motor de contenido = serie *"Model X in 7 questions"* reciclando stress-tests
ya hechos. Comunidad = GitHub Discussions primero. Jose = maintainer visible.

Descartados: (B) grind de marca personal diario — exige 15h+/sem, choca con
la dedicación real; (C) jugada académica — público equivocado, poco viral.

---

## Fase 0 — El activo de lanzamiento (front-loaded, nada público aún)

Inversión única y reutilizable. Objetivo: tener listo el "gancho" antes de
hacer ruido. Cuatro entregables.

### 0.1 — Servidor MCP `wquestions-mcp` (la pieza crux, es código)

**Qué:** un servidor MCP que envuelve el motor `wq` existente. El LLM cliente
(Claude Desktop / Cursor) hace el parsing lenguaje-natural → roles; el
servidor hace ingest / query / validación. Esta división respeta el diseño
del motor, que deja el NL explícitamente al LLM.

**Tools expuestas (borrador, se refina en el plan):**

- `model_fact(verb, roles, extra?, valid_from?, valid_to?)` — ingesta una
  situación (envuelve `ingest_situation`). Devuelve la situación reificada y
  los hechos asentados.
- `query(fixed, ask, type?, at?)` — consulta WH por proyección (envuelve
  `query`/`Pattern`). Devuelve bindings.
- `list_axes()` — los 7 ejes y para qué sirve cada uno.
- `list_roles()` — el catálogo canónico de roles con su signatura tipada.
- `show_model()` — vuelca el universo actual (hechos/individuos) para que el
  LLM y el dev vean lo modelado.
- `explain_domain(domain?)` — carga un ejemplo pre-modelado (spa, taxi…) como
  demostración instantánea.

**Estado de sesión:** un `Universe` en memoria por sesión MCP. Persistencia
opcional a SQLite es "trabajo siguiente", no bloquea el demo.

**Distribución:** instalable de una línea (`uvx wquestions-mcp` o
`pip install`), con bloque de config listo para pegar en Claude Desktop /
Cursor. Fricción de arranque casi cero es requisito, no lujo.

**El "wow":** dev conecta el server, dice *"model my spa business"*, ve al
LLM construir el modelo de 7 ejes, y luego pregunta *"who visited in 2022?"*
y obtiene respuesta sobre un modelo que nadie diseñó a mano por dominio.

### 0.2 — Repo público `wquestions` (inglés)

README asesino con este arco: dolor (las ontologías por-dominio no escalan
para IA) → tesis (7 preguntas = índice universal) → GIF de 30s del MCP →
quickstart de 2 minutos → link al libro como deep-dive. Licencia abierta
(que lea como estándar, no como producto propietario). Estructura de repo que
invite a contribuir dialectos de dominio más adelante.

### 0.3 — UN demo grabado (GIF o video 30-60s)

Captura del LLM modelando un dominio nuevo en vivo vía el MCP server. Este
solo activo hace ~80% del trabajo de compartir. Va en el README y en cada
post del lanzamiento.

### 0.4 — GitHub Discussions activado

Hogar de comunidad de cero mantenimiento, donde los devs ya están. **Discord
NO todavía** — un servidor muerto es peor señal que no tener servidor.

**Definición de "Fase 0 terminada":** un dev externo puede, desde el README,
instalar el MCP en < 5 min, ver el demo, modelar un dominio propio, y tener
dónde comentar. Nada se publica/promociona hasta que esto se cumpla.

---

## Fases siguientes (resumen; cada una tendrá su propio ciclo)

- **Fase 1 — Lanzamiento:** ensayo-tesis en inglés + secuencia de disparo en
  24-48h (Show HN → r/LocalLLaMA + r/MachineLearning → PR a lista oficial de
  MCP servers → thread en X con el GIF → Lobsters/dev.to). Presencia total
  las primeras 48h.
- **Fase 2 — Motor sostenible (2-4h/sem):** serie *"Model X in 7 questions"*,
  un dominio/semana reciclado de stress-tests, en batch. CTA constante:
  prueba el MCP, star, Discussions. Siembra útil en hilos ajenos.
- **Fase 3 — Comunidad:** solo con tracción — Discord, destacar modelos de
  usuarios, `CONTRIBUTING` que invita dialectos como PRs.

## Métricas

- **Adelantadas:** stars, posts en Discussions, installs del MCP, vistas del demo.
- **Señal real:** alguien que Jose no conoce modela su propio dominio y lo comparte.

## Qué NO hacer (protege las 2-4h)

- Discord sin audiencia · grind diario de marca personal · liderar con el
  libro en español · rociar en 6 plataformas a la vez.

## Riesgos y mitigaciones

- **El motor `wq` está pensado para validación, no producción.** Mitigación:
  el MCP envuelve la API existente tal cual; no reescribir el motor. Bugs de
  borde se documentan, no se pulen antes del lanzamiento.
- **Fricción de instalación mata la viralidad.** Mitigación: el quickstart de
  < 5 min es criterio de aceptación de la Fase 0, se prueba en limpio.
- **Dispersión con 2-4h/sem.** Mitigación: un solo canal de lanzamiento por
  vez, un solo formato semanal después.
