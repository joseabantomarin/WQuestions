import os
from wquestions_mcp.session import resolve_log_path, DEFAULT_LOG_PATH


def test_resolve_unset_uses_expanded_default():
    assert resolve_log_path(None) == os.path.expanduser(DEFAULT_LOG_PATH)


def test_resolve_off_sentinels_disable():
    for raw in ["off", "OFF", "none", ":memory:", "", "  "]:
        assert resolve_log_path(raw) is None


def test_resolve_explicit_path_is_expanded():
    assert resolve_log_path("/tmp/u.jsonl") == "/tmp/u.jsonl"
    assert resolve_log_path("~/x.jsonl") == os.path.expanduser("~/x.jsonl")


from wquestions_mcp.session import WQSession


def test_in_memory_session_writes_no_file(tmp_path):
    s = WQSession(log_path=None)
    s.add_entity("ana", "Q", "Ana")
    s.assert_situation("visit", roles={"agente": "ana"})
    assert list(tmp_path.iterdir()) == []  # nothing written anywhere we own


def test_round_trip_rebuilds_universe_and_corrections(tmp_path):
    p = str(tmp_path / "u.jsonl")
    s = WQSession(log_path=p)
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    s.add_entity("spa", "L", "Spa")
    out = s.assert_situation("visit", roles={"agente": "ana", "lugar_de": "spa"})
    s.correct(out["situation_id"], "agente", "beto")

    s2 = WQSession(log_path=p)  # simulates a restart
    assert "ana" in s2.universe.individuals and "beto" in s2.universe.individuals
    res = s2.ask(fixed={"lugar_de": "spa"}, ask=["agente"])
    assert res["results"][0]["agente"] == "beto"          # correction survived
    hist = s2.ask(fixed={"lugar_de": "spa"}, ask=["agente"], history=True)
    assert hist["results"][0]["agente"] == ["ana", "beto"]


def test_reset_marker_keeps_only_post_reset_state(tmp_path):
    p = str(tmp_path / "u.jsonl")
    s = WQSession(log_path=p)
    s.add_entity("ana", "Q", "Ana")
    s.reset()
    s.add_entity("beto", "Q", "Beto")

    s2 = WQSession(log_path=p)
    assert "beto" in s2.universe.individuals
    assert "ana" not in s2.universe.individuals


def test_load_example_round_trips_as_single_event(tmp_path):
    p = str(tmp_path / "u.jsonl")
    s = WQSession(log_path=p)
    s.load_example("spa")
    facts_before = s.show_model()["fact_count"]

    s2 = WQSession(log_path=p)
    assert s2.show_model()["fact_count"] == facts_before
    with open(p, encoding="utf-8") as f:
        ops = [__import__("json").loads(ln)["op"] for ln in f if ln.strip()]
    assert ops.count("load_example") == 1
    assert "add_entity" not in ops  # inner builder calls were not double-logged


def test_show_model_reports_persistence_when_active(tmp_path):
    p = str(tmp_path / "u.jsonl")
    s = WQSession(log_path=p)
    s.add_entity("ana", "Q", "Ana")
    s2 = WQSession(log_path=p)
    pers = s2.show_model()["persistence"]
    assert pers["path"] == p
    assert pers["replayed_events"] == 1
    assert pers["skipped_lines"] == 0


def test_show_model_reports_disabled_in_memory():
    s = WQSession(log_path=None)
    assert s.show_model()["persistence"] == {"enabled": False}


def test_replay_skips_and_counts_a_corrupt_line(tmp_path):
    p = tmp_path / "u.jsonl"
    s = WQSession(log_path=str(p))
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    # simulate a half-written trailing line from a crash
    with open(p, "a", encoding="utf-8") as f:
        f.write('{"v": 1, "op": "add_entity", "args": {"entity_id": "cor')

    s2 = WQSession(log_path=str(p))
    assert "ana" in s2.universe.individuals and "beto" in s2.universe.individuals
    pers = s2.show_model()["persistence"]
    assert pers["replayed_events"] == 2
    assert pers["skipped_lines"] == 1


def test_server_module_session_is_isolated_from_real_log():
    from wquestions_mcp import server
    assert server._session._log_path is None  # conftest pinned WQUESTIONS_LOG=off


def test_barbershop_capstone_survives_log_round_trip(tmp_path):
    """The full fidelity capstone (N-with-nested-unit + multi-correction on an
    invented role) must survive a persistence log round-trip losslessly."""
    p = str(tmp_path / "barber.jsonl")
    s = WQSession(log_path=p)
    s.add_entity("marcos", "Q", "Marcos")
    s.add_entity("pablo", "Q", "Pablo")
    s.add_entity("shave", "O", "Shave service")
    out = s.assert_situation("serve", roles={
        "agente": "marcos", "cliente": "pablo", "tema": "shave",
        "por_cuanto": {"id": "usd_12", "axis": "N", "value": 12,
                       "unit": {"id": "usd", "axis": "K", "label": "USD"}},
    })
    sid = out["situation_id"]
    s.correct(sid, "tipo_cambio",
              {"id": "tc_333", "axis": "N", "value": 3.33,
               "unit": {"id": "pen_per_usd", "axis": "K", "label": "PEN/USD"}})
    s.correct(sid, "tipo_cambio",
              {"id": "tc_339", "axis": "N", "value": 3.39, "unit": "pen_per_usd"})

    s2 = WQSession(log_path=p)  # restart: fresh session replays the log
    assert s2.universe.individuals["usd_12"].payload == {"value": 12, "unit": "usd"}
    cur = s2.ask(fixed={"cliente": "pablo"}, ask=["tipo_cambio"])
    assert cur["results"][0]["tipo_cambio"] == "tc_339"
    hist = s2.ask(fixed={"cliente": "pablo"}, ask=["tipo_cambio"], history=True)
    assert hist["results"][0]["tipo_cambio"] == ["tc_333", "tc_339"]
    assert s2.show_model()["persistence"]["replayed_events"] > 0


def test_assert_fact_survives_a_replay(tmp_path):
    from wquestions_mcp.session import WQSession
    log = str(tmp_path / "u.jsonl")
    s = WQSession(log_path=log)
    s.add_entity("juan", "Q", "juan")
    s.assert_fact("juan", "nombre",
                  {"id": "lit_juan", "axis": "K", "label": "Juan Pérez"})
    del s
    s2 = WQSession(log_path=log)
    assert s2._skipped_lines == 0
    assert s2._display("juan") == "Juan Pérez"
