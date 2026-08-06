# WQuestions — Fase 1: kit de lanzamiento

Todo listo para copiar y pegar. Idioma: inglés. Sin em dashes, sin jerga de IA, voz de autor honesto (no de marketing).

Orden sugerido en 24-48h (tú marcas el ritmo, con tus 2-4h basta):

1. Publica el **ensayo** en dev.to (es tu contenido ancla; el resto enlaza a él o al repo).
2. **Show HN** por la mañana (hora US, martes-jueves rinde mejor).
3. **r/LocalLLaMA** el mismo día.
4. Abre el **PR a awesome-mcp-servers**.
5. **Thread en X** con el GIF.
6. **r/MachineLearning** (opcional, más estricto) con tag [P].
7. Las primeras 48h: responde cada comentario. Ahí se decide.

Un aviso honesto: no publiques el mismo texto idéntico en 5 sitios a la vez sin adaptarlo; los mods de Reddit y HN lo penalizan. Cada pieza aquí ya está adaptada a su sitio.

---

## 1) Ensayo ancla (dev.to / blog / el "read more")

**Título:** Stop writing a new ontology for every domain

I spent two years on a book about one stubborn idea: you can model information from any field with the same seven questions. Who, what, where, when, how much, which kind, and how. Last week I turned it into something you can run.

The thing that kept biting me while writing it: every domain wants its own schema. Sales gets a CRM model. A clinic gets a patient model. A bank, a taxi app, a chemistry lab, each one a fresh data model built by hand. None of it transfers between fields. And almost none of it was built for a language model to reason over. So every time you want an AI to answer questions about a new domain, someone has to model that domain first.

The bet in the book is that you don't need an ontology per domain. You need one fixed set of coordinates that any fact already answers.

Take one fact: "Ana visited Spa Oasis on March 1st." Who (Ana, an agent). What (a visit, which becomes a thing you can point at and hang more facts on). Where (Spa Oasis). When (March 1st). The other questions sit empty for this fact, and that's fine; a different fact fills different ones. You model a domain by dropping facts onto these axes. You query it the same way whatever the domain is: fix a few coordinates, ask for the ones you left open.

That's the theory. I wanted to know if it survived contact with a real tool, so I built an MCP server.

Plug it into Claude Desktop or Cursor and you can watch it happen. You say "model my spa business" in plain English. The model works out the roles, calls the tools, and builds a small world of seven-axis facts. You ask "who visited in 2022?" and it answers off a model nobody hand-designed for spas. Then you say "now model my barbershop," and it runs on the exact same tools. No migration, no new schema. You never defined "haircut" anywhere; the server registers it the first time you use it.

Now the honest part, the stuff I'd rather tell you than have you find out. The engine underneath is a validation prototype: in-memory, no persistence yet, no inference engine firing rules on its own. The role vocabulary is still Spanish under the hood, because that's the language I wrote the book in (an English alias layer is on the list). I've hand-tested it across about fifteen domains, from an airport to a Peru-Argentina football match to a Peruvian rental contract, and it held. Fifteen is not a proof.

The claim I'm making is narrower, and I think more interesting than "universal schema": a fixed skeleton of seven questions can replace the per-domain ontology across fields as different as law, biology, and music. Others have circled this. Yang and Hu (2011) used the 5W1H questions as a heuristic for building OWL ontologies, one domain at a time. The Biolink Model is a working universal schema in biomedicine, so the idea isn't crazy. WQuestions keeps the questions and stores facts directly on them, instead of using them as scaffolding to build something else.

I don't know where this breaks yet. That's most of why I'm shipping it instead of writing another chapter. If you model your own domain and it falls apart, I want to see exactly where it cracks.

Two minutes to try it:

    uvx wquestions-mcp

Repo, config block for Claude Desktop, and a thirty-second demo: https://github.com/joseabantomarin/wquestions-mcp

The book is there too if you want the long argument for why these seven axes and not others. It's in Spanish. You don't need it to try the thing.

**dev.to front matter / tags:** ai, mcp, llm, opensource. Si publicas también en tu blog, marca el canonical URL en dev.to hacia tu blog.

---

## 2) Show HN

**Título (campo Title):**
Show HN: WQuestions – model any domain in 7 questions (MCP server)

**URL (campo URL):**
https://github.com/joseabantomarin/wquestions-mcp

**Primer comentario (lo pegas tú apenas aparezca el post):**

Author here. This started as a book about one idea: you can model information from any field with the same seven questions (who, what, where, when, how much, which kind, how), instead of building a new ontology per domain. I wanted to see if it held up as a real tool, so I wrapped the engine as an MCP server.

What it does: you talk to it through Claude Desktop or Cursor in plain English. It maps your sentences to roles on the seven axes, stores them as facts, and answers queries by projection. The README demo loads a small spa, then models a barbershop live with the same tools and no new schema.

What it isn't: the engine is a validation prototype (in-memory, no persistence yet, no rule inference). The role vocabulary is still Spanish under the hood since that's the language of the book; English aliases are on the list. I hand-tested about 15 domains (airport, clinical history, a rental contract, a methane combustion reaction, a football match); it held, but that's not proof.

I mostly want to find where it breaks. If you model your own domain and it falls apart, that's the useful bug report. `uvx wquestions-mcp` to try it. Happy to answer anything.

---

## 3) r/LocalLLaMA

**Título:**
I turned "7 questions to model any domain" into an MCP server. Watch an LLM model a spa, then a barbershop, with the same tools.

**Cuerpo:**

I've been writing a book on a simple bet: any fact in any domain answers the same seven questions (who, what, where, when, how much, which kind, how). So instead of a new schema per domain, you drop facts onto seven fixed axes and query by projection.

I wrapped it as an MCP server to see if the bet survives a real tool. You wire it into Claude Desktop or Cursor and just talk. It builds the model and answers queries off it. The demo models a spa, then a barbershop, no schema change between them.

[GIF aquí: sube el docs/demo.gif del repo]

Try it: `uvx wquestions-mcp`
Repo (config block + demo): https://github.com/joseabantomarin/wquestions-mcp

Fair warning: the engine is a prototype (in-memory, no persistence yet), and the role names are still Spanish under the hood. I'd genuinely like to know where it falls over, so if you model something weird and it breaks, tell me.

---

## 4) r/MachineLearning (opcional, más estricto)

Usa el tag [P] (Project). Este sub prefiere sobriedad y prior work citado.

**Título:**
[P] WQuestions: a fixed 7-axis schema as an alternative to per-domain ontologies (MCP server + prototype)

**Cuerpo:**

Premise: instead of building a domain-specific ontology each time, model every fact on one fixed set of seven question-axes (who, what, where, when, how much, which kind, how). Queries are partial assignments over the axes that project onto the free ones.

I built an MCP server over a Python prototype so an LLM client does the natural-language-to-roles step and the server handles storage and query. It's been hand-validated on ~15 domains (airport, clinical history, a rental contract, methane combustion, a football match).

Relation to prior work: Yang & Hu (2011) use 5W1H as a heuristic to build OWL ontologies per domain; this makes the questions the persistent structure instead. The Biolink Model is the closest working precedent for an explicit cross-domain schema. Reification of situations is neo-Davidsonian.

Honest limits: validation prototype, in-memory, no persistence or rule inference yet, role vocabulary currently Spanish. Not a benchmark, not a proof, and I'd like adversarial domains that break it.

Repo: https://github.com/joseabantomarin/wquestions-mcp

---

## 5) Thread de X / Twitter

**Tweet 1 (con el GIF):**
Every domain gets its own schema. Sales, a clinic, a bank, a taxi app: a new data model built by hand each time, and none of it built for an LLM to reason over.

The bet behind WQuestions: you don't need that. Seven questions cover any fact.

[adjunta docs/demo.gif]

**Tweet 2:**
Who, what, where, when, how much, which kind, how.

One fact, "Ana visited Spa Oasis on March 1st," fills a few of them and leaves the rest empty. You model a domain by dropping facts on these axes. You query by fixing some and asking for the others.

**Tweet 3:**
I wrapped it as an MCP server to see if the idea survives a real tool.

Wire it into Claude Desktop or Cursor, say "model my spa business" in plain English, then ask "who visited in 2022?" It answers off a model nobody designed for spas.

**Tweet 4:**
The part I like: say "now model my barbershop" and it runs on the exact same tools. No migration, no new schema. You never defined "haircut"; it registers the first time you use it.

Same seven questions. Any domain.

**Tweet 5:**
Honest limits: the engine is a validation prototype (in-memory, no persistence yet), and the role names are still Spanish under the hood. I want to know where it breaks.

Two minutes to try:
uvx wquestions-mcp

Repo: https://github.com/joseabantomarin/wquestions-mcp

---

## 6) PR a la lista de MCP servers (descubrimiento evergreen)

Lista principal de la comunidad: **punkpeye/awesome-mcp-servers** (GitHub).

Pasos:
1. Fork del repo.
2. Añade esta línea en la categoría más cercana (busca "Knowledge" / "Databases" / "Knowledge Bases"; si no, "Other Tools and Integrations").
3. PR con título claro: `Add wquestions-mcp (model any domain in 7 questions)`.

**Entrada (formato de la lista, 🐍 = Python, 🏠 = local):**

```
- [wquestions-mcp](https://github.com/joseabantomarin/wquestions-mcp) 🐍 🏠 - Model any domain in 7 questions: an LLM builds a 7-axis knowledge model of anything (spa, clinic, contract) and queries it, with no per-domain schema.
```

Bonus: el repo oficial **modelcontextprotocol/servers** tiene una sección de servidores de la comunidad en su README; si aplica, añade la misma línea ahí con un segundo PR.

---

## 7) Notas de operación (para tus 2-4h)

- El GIF vive en el repo (docs/demo.gif). Para X y Reddit, súbelo como archivo, no como link.
- Guarda respuestas cortas para las preguntas que se repetirán: "¿por qué no RDF/property graphs?", "¿persistencia?", "¿por qué 7 y no N ejes?". Contéstalas una vez bien y reúsalas.
- Métrica que importa: que alguien que no conoces modele su propio dominio y lo comparte. Lo demás (stars, upvotes) es señal adelantada.
- Lo que NO hacer: no montes Discord aún, no publiques a diario, no lideres con el libro en español.
