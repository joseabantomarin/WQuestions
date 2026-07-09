# Recorded-demo script

30-60 seconds, runnable verbatim in Claude Desktop once `wquestions` is wired
up (see `README.md` Quickstart). This is the script to screen-record for
`docs/demo.gif`.

The point it has to land: **the same 9 tools model a spa and a barbershop,
with zero per-domain schema.**

## Script

**1. Load a prebuilt domain and look at it.**

> Say: "Load the spa example, then show me the model."

Claude calls `load_example("spa")`, then `show_model()`. The response is a
small universe built entirely from the 7 axes — two clients (Q), a spa (L),
and three visits, each reified as its own situation (O) that links who went
where and when. No spa-specific code, no schema.

**2. Query it.**

> Say: "Who visited Spa Oasis?"

Claude calls `ask(fixed={"lugar_de": "spa_oasis"}, ask=["agente"])` and
reports back the visitors: Ana (twice) and Beto.

**3. Model a brand-new domain, live, with the same tools.**

> Say: "Now model my business: a barbershop. Diego cut Marco's hair on
> 2025-06-11 at Barber Kings."

Claude calls:
- `add_entity("diego", "Q", "Diego")`
- `add_entity("marco", "Q", "Marco")`
- `add_entity("barber_kings", "L", "Barber Kings")`
- `assert_situation(verb="corta_cabello", roles={"agente": "diego", "paciente": "marco", "lugar_de": "barber_kings"}, valid_from="2025-06-11")`

No schema migration, no new tool, no code written for "barbershop" — the
verb is auto-registered on the fly.

**4. Query the new domain.**

> Say: "Who did Diego serve, and where?"

Claude calls `ask(fixed={"agente": "diego"}, ask=["paciente", "lugar_de"])`
and reports: Marco, at Barber Kings.

## Cut it here

Stop the recording once the answer to step 4 is on screen. That's the whole
pitch: one fixed 7-axis model, one set of 9 tools, any domain — spa or
barbershop — with nothing rewritten in between.
