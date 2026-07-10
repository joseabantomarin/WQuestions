# Design — Make the WQuestions MCP a faithful mirror of the standard

**Date:** 2026-07-10
**Status:** Approved (design), pending user review of spec
**Author:** brainstorming session (Jose + Claude)

## Problem

A stress test drove a model with **only** the `wquestions` MCP tools (no book, no
context) and asked it to build a new domain from scratch (a barbershop). The
model succeeded, but the survival notes it wrote for itself expose a pattern:

> **The model invents parallel structure wherever the MCP is silent or offers no
> canonical path.**

Concretely, it reconstructed by hand three things the WQuestions engine already
does or explicitly leaves out:

1. **Append-only auditing / corrections.** It invented `estatus_factual`
   (`vigente`/`rectificado`) + `rectifica`/`cancela` M-predicates to track which
   value is current — because the MCP gave it no way to say "this value replaces
   that one." The engine is already bitemporal (`valid_from`/`valid_to` for world
   time, `tx_time` for record time), but the MCP surfaces neither for corrections.
2. **Units on magnitudes.** It baked units into ids/labels (`pen_25` = "25 PEN")
   and invented a separate `unidad` role — because `add_entity` cannot express a
   value + unit, even though the engine has `quantity(value, unit_k)` with the
   K-unit mandatory by design.
3. **Provenance / authorship.** It modeled `agente`/`fuente` on every corrective
   action — a structure WQuestions does not have and does not want.

It also had to *discover by observation* things the tools never state:
reification into binary triplets, that the store is append-only and tolerates
contradictions, that obligatory roles are enforceable, and the semantics of the
M axis (it wrote a whole taxonomy of it).

## North star

**A model holding only the MCP should stay inside WQuestions and not confabulate.**
The user's framing: *"que el modelo no se invente nada por su cuenta, que se
mantenga dentro de los márgenes de lo que hace WQuestions"* — while keeping the
model's flow (WQuestions is deliberately open; inventing *domain vocabulary* is
the point).

The line we hold: **domain vocabulary stays free; parallel meta-mechanisms get
redirected to the canonical one.** Inventing `serv_corte`, `atiende`,
`estilo_punk` is WQuestions working. Inventing an auditing subsystem is the model
patching a hole. We fix it two ways at once:

- **Teach** — tell the model what WQuestions is and what mechanisms exist, on the
  surfaces it already reads, so it never needs to guess.
- **Unblock** — give a canonical path where today there is none (units,
  corrections), so it never needs to improvise.

## Non-goals

- **No provenance/authorship tracking.** Out of scope for WQuestions; the MCP
  will state so, not add it.
- **No controlled/closed vocabulary.** The liberal role policy stays (Global
  Constraint: never add per-domain roles to `catalog.py`). Inventing domain
  entities/verbs/roles remains free.
- **No durable persistence in this pass.** In-memory/per-process behavior is
  *documented*, not changed. (Parked as a follow-up — see Open questions.)
- **No engine modification.** Global Constraint (Fase 0 plan, line 15): *"Do not
  rewrite or 'fix' the `wq` engine. Wrap it as-is."* All new behavior lives in the
  MCP layer (`session.py`) over the engine's public API.

## Global constraints honored

- **Language:** every user-facing string (server `instructions`, docstrings,
  enriched returns, error messages) is **English**. Spanish stays in the book.
- **Engine untouched:** 2a uses the engine's public `quantity()`; 2b uses the
  public `assert_fact` / `facts_about` / `Fact.tx_time`. No edits to `wq/`.
- **Liberal roles preserved:** enrichment only *documents* the canonical roles in
  return payloads; it does not register them in the catalog.

---

## Section 1 — Teaching surface (Option 1 backbone, no new tools)

### 1a. Server `instructions` (the constitution)

`FastMCP("wquestions", instructions=...)` — always visible to the client. Draft
(English, final wording tuned in implementation):

```
WQuestions models any domain as one fact space over 7 axes:
Q who · O what · L where · T when · N how-much · K which/kind · M how (predicates).

How storage works
- Everything is stored as binary triplets: subject · role · value. No prose, no
  records, no rows — only triplets.
- A fact with many participants (a sale with seller, buyer, item, price, time) is
  reified: the situation becomes its own node in O and each participant is one
  triplet hanging off it. assert_situation does this and returns the triplets it
  created.

What is open — invent freely (this is the point)
- Entities, verbs, and roles are open-world. Coin new domain entities
  (add_entity), new verbs (assert_situation auto-registers them), and new roles as
  needed. No catalog, no permission required.

What is NOT yours to invent — the standard already provides it
- Corrections & time. To record that a fact changed in the world over time, set
  valid_from/valid_to and read the past with ask(at=...). To fix a value you
  recorded wrong, re-assert the role on the same situation (correct); the latest
  assertion is what ask returns and nothing is overwritten — the prior value stays
  queryable as history. Do NOT invent status / rectifies / supersedes roles.
- Magnitudes carry a unit. Every N value has a unit in K. Create magnitudes with a
  value and a unit; never bake the unit into an id or label, and never assume a
  currency or unit — if a number arrives without one, ask for it.
- Authorship / provenance is out of scope. WQuestions does not track who entered a
  fact or where it came from. Do not model it.

Ground rules
- The store is append-only and open-world: it does not check consistency.
  Contradictory facts coexist by design — not an error to fix.
- State is in-memory for this process and does not survive a restart. Use
  show_model to inspect and reset to start clean; don't build recovery rituals.
- Start with list_axes and list_roles — they describe the vocabulary and its
  typed signatures.
```

### 1b. Enrich the return payloads of the orientation tools (teach by use)

- **`list_axes`** — per axis add `how_to_use`, `example`, and `gotcha`. Key
  gotchas: `N` needs a unit in K; `M` is a predicate axis, not a value axis (no
  entities live there); `O` holds reified situations, not just "objects".
- **`list_roles`** — already flags the open policy. Add a `canonical` glossary of
  the recurring roles the model re-derived (`agente`, `cliente`, `tema`,
  `momento`, `lugar_de`, `por_cuanto`, `unidad`, ...) with their axis signatures
  and `functional` flag. Documentation only — not registered in the catalog.
- **`show_model`** — add a one-line legend: facts are binary projections of
  reified situations; the store is append-only.

### 1c. Richer tool docstrings

- `assert_situation`: explains reification (returns the triplets), and that
  `valid_from`/`valid_to` are the mechanism for world-time change.
- `add_entity`: explains N needs `value` + `unit` (see 2a).
- `ask`: explains `at` (time-travel over valid-time) and `history` (see 2b).
- `define_verb`: explains that a verb *may* declare obligatory roles and that
  `assert_situation` then enforces them (missing obligatory role → error). Leaving
  `obligatory` empty makes every role optional — that is a choice, not a limit.
- `correct` / `reset`: intent stated in one line each.

### 1d. Redirecting error messages

When the model reaches for a parallel mechanism, the error names the canonical
path instead of just failing:

- `add_entity(axis="N")` with no unit → *"N magnitudes require a unit in K. Pass
  `value` and `unit`; do not encode the unit in the id or label."*
- (Optional, low priority — skip if brittle) a hint when a correction-flavored
  invented role is used, pointing to `correct` + `valid_from`.

---

## Section 2 — The two affordance gaps (the only behavior changes)

### 2a. Magnitudes with units in `add_entity`

**Change:** when `axis == "N"`, accept `value: number` and `unit: str` (id of an
existing K entity, or an inline K spec). Build the individual via the engine's
public `quantity(value, unit_k)`, which stores `payload={"value", "unit"}` and a
`"<value> <unit>"` label. A bare N (no unit) returns the 1d redirect error.

**Why:** gives the model the canonical way to create a real N, so it stops faking
`pen_25` + a separate `unidad` role. Uses existing engine code; no engine change.

**Signature (illustrative, finalized in the plan):**
`add_entity(entity_id, axis, label=None, value=None, unit=None)`.
For non-N axes, `value`/`unit` are ignored (or rejected) as today.

### 2b. Corrections without invented vocabulary

The engine already: (i) is append-only, (ii) stamps every fact with `tx_time`,
(iii) sanctions "a change = a new fact/situation" (`universe.py` docstring).
What is missing at the MCP layer: a way to **attach a corrected value to an
existing situation**, and a way for **`ask` to return the current value** instead
of a list of all values ever asserted. We add both in `session.py`.

**New tool `correct` (name finalized in plan):**
`correct(situation_id, role, value, valid_from=None, valid_to=None)` — resolves
the O-situation by id and calls the engine's public `universe.assert_fact` to
append the corrected triplet. Nothing is overwritten; the prior fact remains.
(Alternative considered: extend `assert_situation` with an optional
`situation_id` that flows to `ingest_situation(sit_id=...)`. Rejected for the
default path because it re-asserts `instancia_de`, adding a duplicate; a dedicated
tool reads clearer to the model. Final call in the plan.)

**`ask` current-value resolution:**
- Default: for each asked role, `ask` returns the **current** value — the one with
  the latest `tx_time` among the facts valid at the query moment. Re-asserting a
  role *is* the correction; the newest assertion wins.
- `history=true`: return the full time-ordered list (current + superseded), so
  the audit trail the model wanted is available on demand — without any
  `estatus_factual` vocabulary.
- **Functional vs multi-valued disambiguation (explicit decision):** a role the
  catalog marks `functional=True` is single-valued → last-write-wins. A role
  marked `functional=False` is genuinely multi-valued → return all current values
  (today's behavior). For **invented roles with no catalog signature**, default to
  **last-write-wins** (the common correction case); `history=true` recovers the
  rest. This default is revisitable but must be stated in the docstring.
- Resolution lives entirely in `session.py` (reads `catalog._roles[...].functional`
  and `Fact.tx_time` via `universe.facts_about`); `wq/query.py` is not modified.

---

## Section 3 — Friction → fix coverage (the barbershop memo, item by item)

| What the model wrote in its notes | Where it's resolved |
|---|---|
| "Triple store; n-ary facts reified into a situation node" | 1a + 1c (assert_situation docstring) |
| "Persistence unreliable → verify with show_model, reset + replay" | 1a (ground rules: in-memory/per-process) |
| "No obligatory roles; don't ask for missing ones" | 1c (define_verb docstring: obligatory roles *are* declarable and then enforced) |
| "Every number travels with its unit; never assume; ask" | 1a + **2a** + 1d |
| "Append-only; corrections are new facts; `rectifica`/`estatus_factual`; derive current" | 1a + **2b** (redirect to `correct` + `tx_time`) |
| "Provenance: `agente`/`fuente` on every action" | 1a (explicitly out of scope) |
| "Eje M taxonomy: connectors vs `instancia_de`" | 1b (list_axes: M is a predicate axis, not a value axis) |
| "⚠ contradiction registered on purpose (Marcos absent + serving)" | 1a (append-only, no consistency checking, by design) |

---

## Testing

- **Unit (pytest, `tests/test_session.py`):** all logic is in `WQSession`, testable
  without an MCP runtime (per Fase 0 architecture).
  - 2a: `add_entity` N-with-unit builds a payload-bearing individual; bare N
    returns the redirect error; non-N ignores value/unit.
  - 2b: `correct` appends a fact to an existing situation; `ask` returns the
    latest-`tx_time` value by default; `history=true` returns all; functional vs
    non-functional vs invented-role resolution behaves as specified.
  - 1b: `list_axes` / `list_roles` / `show_model` payloads contain the new
    teaching fields (assert on keys/shape, not exact prose).
- **Behavioral replay (the real acceptance test):** re-run the barbershop stress
  test against the updated MCP and confirm the model reaches for `correct` +
  `valid_from` and unit-bearing N, and does **not** re-invent `estatus_factual`,
  a `unidad` role, or provenance triplets. This is the north-star check.

## Open questions / follow-ups

- **Durable persistence.** The in-memory/per-process model is documented, not
  fixed. If cross-restart durability is wanted, that's a separate design (a store
  backend + load/save tools). Parked.
- **`correct` tool name & shape** — `correct` vs `amend` vs extending
  `assert_situation`; finalized in the implementation plan.
- **Invented-role currency default** — last-write-wins is the chosen default;
  revisit if a real domain needs invented multi-valued roles without a catalog
  signature.
