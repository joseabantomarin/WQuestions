# wquestions-mcp

**Model any domain in 7 questions.**

An MCP server that lets Claude Desktop (or any MCP client) build and query a
knowledge model of *anything* — a spa, a barbershop, a clinic, a bank — using
one fixed set of tools. No per-domain schema to write, ever.

## The problem

Every domain today gets its own bespoke ontology or database schema: a CRM
schema for sales, a clinical model for a clinic, a different one again for a
bank or a taxi dispatcher. None of it transfers between domains, and none of
it was designed for an LLM to reason over — each new domain means new
modeling work before an AI can even start answering questions about it.

WQuestions replaces all of that with a single fixed index: **7 axes** that
any fact, in any domain, answers. Model a domain by asserting facts on those
7 axes; query it the same way no matter what the domain is.

## The 7 axes

| Axis | Question | Holds |
|---|---|---|
| Q | who | agents |
| O | what | objects, and reified situations (facts treated as things) |
| L | where | places |
| T | when | time points and intervals |
| N | how much | magnitudes with a unit |
| K | which / what kind | atemporal categories, types, states |
| M | how | the predicates that connect Q/O/L/T/N/K to each other — structural, not a value axis |

![demo](docs/demo.gif)

## Quickstart

Add this to your Claude Desktop config (`claude_desktop_config.json`) and
restart Claude Desktop:

```json
{
  "mcpServers": {
    "wquestions": {
      "command": "uvx",
      "args": ["wquestions-mcp"]
    }
  }
}
```

Until `wquestions-mcp` is published to PyPI, run it from source instead:
clone this repo, `pip install -e mcp-server` into a virtualenv, then point
`command`/`args` at that venv's `wquestions-mcp` script (e.g.
`command: ".../.venv/bin/wquestions-mcp"`, `args: []`) instead of `uvx`.

Then ask Claude: *"Load the spa example, then show me the model."* See
[`DEMO.md`](DEMO.md) for the full 30-second walkthrough.

## Tools

| Tool | Does |
|---|---|
| `list_axes` | Describe the 7 axes |
| `list_roles` | List canonical roles (who/what/where/... connectors), typed by domain and range |
| `add_entity` | Create an individual on a value axis (Q, O, L, T, N, K) |
| `define_verb` | Register a situation type and its roles — optional, `assert_situation` auto-registers unknown verbs |
| `assert_situation` | Assert a fact: reify a situation and attach its roles |
| `ask` | Query by projection — fix some roles, ask for others, optionally as of a point in time |
| `show_model` | Dump the current universe: every entity and fact |
| `load_example` | Load a prebuilt demo universe (`spa`) to try queries instantly |
| `reset` | Clear the model and start a fresh universe |

## How it works

The LLM client does the natural-language-to-structure step: it reads "Diego
cut Marco's hair at Barber Kings on 2025-06-11" and turns it into
role-labeled arguments (`agente: diego, paciente: marco, lugar_de:
barber_kings`). The server never parses English — it takes those roles,
validates them against the 7-axis model, and runs ingest and query over the
`wq` engine. Same engine, same 9 tools, whether the domain behind them is a
spa or a barbershop.

## Further reading

The 7-axis model — why it's fixed, what each axis actually commits to, and
how it holds up once you push on it — is worked out in full in *WQuestions*,
the book this project comes from (Spanish). Start with
[Chapter 8, El espacio multidimensional](https://joseabantomarin.github.io/WQuestions/08-espacio-multidimensional.html)
for the axis model itself, or the
[table of contents](https://joseabantomarin.github.io/WQuestions/00-introduccion.html).
