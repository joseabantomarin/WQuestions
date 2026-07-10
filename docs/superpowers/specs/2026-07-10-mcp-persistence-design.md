# Design — Durable persistence for the WQuestions MCP (append-only event log)

**Date:** 2026-07-10
**Status:** Approved (design)
**Author:** brainstorming session (Jose + Claude)
**Depends on:** `2026-07-10-mcp-wquestions-fidelity-design.md` (implement fidelity first — this wraps the final method signatures `correct`, `add_entity(value, unit)`).

## Problem

The MCP holds one in-memory `WQSession` per process. State survives across tool
calls within a live process, but a server restart (new client session, config
reload, crash, idle timeout) wipes it. From the model's side this reads as
"persistence is unreliable — sometimes the universe survives, sometimes it starts
empty," which pushed it to invent a survival ritual (*"verify with show_model; if
empty, reset() + replay the triplets below"*). Rebuilding a domain every restart
is slow and defeats the point of a modeling session.

## North star

**The universe survives restarts automatically, with zero ritual.** The
persistence layer should also embody WQuestions' append-only soul: nothing is
overwritten or deleted — the log *is* the truth, and replay reconstructs the world.

## Approach: append-only JSONL event log + replay

Every **mutating** operation appends one event to a JSONL file. On startup the
session replays the file to rebuild the universe. Queries are never logged.

- **Logged ops:** `add_entity`, `define_verb`, `assert_situation`, `correct`,
  `load_example`, and a `reset` marker.
- **Not logged:** `ask`, `list_axes`, `list_roles`, `show_model`.
- **Event line:** `{"v": 1, "op": "assert_situation", "args": {...}}` — one JSON
  object per line. `args` are exactly the method's JSON-friendly parameters.

### Reset in an append-only file

`reset` appends a `{"op": "reset"}` marker; on replay, reaching the marker clears
the accumulated in-memory state. The file keeps everything (including that a reset
happened). Starting a new domain = a `reset`. One file can therefore hold the
history of several domains; only the segment after the last reset is "live".

### Correctness invariants (verified against the engine)

- **Valid-time preserved.** `valid_from`/`valid_to` travel in the event `args`
  (ISO-8601 strings) and are restored exactly.
- **Correction order preserved.** `tx_time` is regenerated during replay in the
  same *relative* order the events were logged, so 2b's "latest correction wins"
  still holds. Only relative order matters — nothing exposes absolute `tx_time`,
  and `ask(at=...)` uses valid-time, not `tx_time`.
- **Situation ids are MCP-controlled and logged.** The engine's mint counter is
  process-global, so re-minting on replay is fragile (two sessions appended to one
  file could collide). Instead the MCP assigns the situation id itself — a
  per-session sequence in the same `{situation_type}_{NNNNNN}` format — passes it
  to `ingest_situation(sit_id=...)` (an existing engine param; engine untouched),
  and stores it in the `assert_situation` event. Replay reuses the stored id
  verbatim, so reconstruction is a pure function of the log, independent of any
  global counter. The sequence high-water is bumped past every id seen (live or
  replayed) so live asserts never collide with logged ones; a `reset` restarts it
  (the cleared state makes id reuse safe).

### Robustness

- Single-process, single writer: `append` + `flush` per event.
- Tolerant load: a blank line, a trailing half-written line (crash mid-write), an
  unparseable line, or an event whose replay raises is **skipped and counted**,
  not fatal. The count is surfaced (see Observability) so silent partial loads are
  visible.

### Where the log lives / how it's toggled

- Resolution (pure function `resolve_log_path`):
  - env `WQUESTIONS_LOG` unset → default `~/.wquestions/universe.jsonl` (**on by
    default** — persistence "just works").
  - `WQUESTIONS_LOG=/path.jsonl` → that file.
  - `WQUESTIONS_LOG` = `off` / `none` / `:memory:` / empty → `None` (pure
    in-memory, today's behavior).
- To keep domains separate, point each MCP server entry in the client config at a
  different `WQUESTIONS_LOG` — which is where MCP servers are configured anyway.
- **Test/default isolation:** `WQSession(log_path=None)` (the class default) is
  pure in-memory, so existing and fidelity tests are unaffected and never touch
  disk. The default-on behavior lives only in `server.py`, which builds
  `WQSession(log_path=resolve_log_path(os.environ.get("WQUESTIONS_LOG")))`.

### Observability

`show_model` gains a `persistence` block: `{"path": ..., "replayed_events": N,
"skipped_lines": M}` when a log is active, or `{"enabled": false}` in-memory. This
lets the model confirm persistence is on and kills the "is it empty?" ritual.

## Non-goals

- **No log compaction / snapshotting** in this pass. The file grows append-only
  (that is the philosophy). If logs ever get large, a compaction pass
  (snapshot + truncate) is a future optimization.
- **No multi-writer / concurrency** support. One process owns the file.
- **No engine modification.** Serialization reads the public method surface only.
- **No cross-version log migration.** `v:1` is stamped for future-proofing; older
  formats are not migrated.

## Global constraints honored

- Engine untouched (persistence is pure `session.py` + `server.py`).
- User-facing strings English.
- `WQSession()` stays in-memory by default → all prior tests remain valid.

## Architecture

- `session.py`:
  - `resolve_log_path(raw: Optional[str]) -> Optional[str]` — pure resolution.
  - `WQSession.__init__(self, log_path: Optional[str] = None)` — store path;
    `_fresh()` (build empty universe, no logging); if `log_path` and the file
    exists, `_replay()`.
  - `_fresh()` — the old `reset` body (build catalog/universe/lexicon), no logging.
  - `_append_event(op, args)` — append+flush unless `self._log_path is None` or
    `self._suppress_log`.
  - `_replay()` — set `_suppress_log`, read the file line by line, dispatch each
    event to its method, count replayed/skipped, restore the flag.
  - Every mutating method appends its event on the success path; `reset` appends
    always; `load_example` suppresses its inner calls and logs a single event
    (save/restore of `_suppress_log` so replay nesting is safe).
  - `assert_situation` assigns the situation id from `self._sit_seq`
    (`{situation_type}_{NNNNNN}`), passes it via `ingest_situation(sit_id=...)`,
    accepts a private `_sit_id` for replay, and bumps `_sit_seq` past every id
    seen. `_fresh()` resets `_sit_seq = 1`.
  - `show_model` reports the `persistence` block.
- `server.py`:
  - `_session = WQSession(log_path=resolve_log_path(os.environ.get("WQUESTIONS_LOG")))`.

## Testing

- **Pure:** `resolve_log_path` for unset/path/off/`:memory:`.
- **Round-trip:** build a universe (entities + verbs + situation + a correction)
  against a temp log; construct a fresh `WQSession` on the same path; assert the
  universe (facts, current values via `ask`, correction history) matches.
- **Reset marker:** log ops, `reset`, more ops; reload; only post-reset state is
  live.
- **load_example:** logged as one event; reload reproduces the example; the inner
  add/assert calls are not double-logged.
- **In-memory default:** `WQSession()` writes no file and reports
  `persistence.enabled == false`.
- **Tolerance:** a corrupted/truncated trailing line is skipped and counted;
  reload still succeeds.
- **Regression:** the full existing suite stays green (no test touches disk).

## Open questions / follow-ups

- **Compaction** when logs grow large — deferred.
- **Pretty export** (a human-readable `.md` triplet view) — `show_model` already
  gives the readable view; a dedicated export is a nice-to-have, not needed now.
