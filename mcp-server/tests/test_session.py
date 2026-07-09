from wquestions_mcp.session import WQSession


def test_list_axes_returns_seven_axes():
    s = WQSession()
    out = s.list_axes()
    codes = [a["code"] for a in out["axes"]]
    assert codes == ["Q", "O", "L", "T", "N", "K", "M"]


def test_list_roles_includes_agente_with_signature():
    s = WQSession()
    roles = {r["name"]: r for r in s.list_roles()["roles"]}
    assert roles["agente"]["domain"] == "O"
    assert roles["agente"]["range"] == "Q"
    assert roles["agente"]["functional"] is True


def test_reset_gives_empty_universe():
    s = WQSession()
    s.reset()
    assert len(s.universe.facts) == 0


def test_add_entity_registers_individual():
    s = WQSession()
    out = s.add_entity("ana", "Q", "Ana")
    assert out["ok"] is True
    assert s.universe.individuals["ana"].axis.value == "Q"


def test_add_entity_rejects_predicate_axis():
    s = WQSession()
    out = s.add_entity("bad", "M", "nope")
    assert out["ok"] is False
    assert "axis" in out["error"].lower()


def test_define_verb_registers_entry():
    s = WQSession()
    out = s.define_verb("visit", "action_visit",
                        obligatory=["agente"], optional=["lugar_de", "momento"])
    assert out["ok"] is True
    entry = s.lexicon.resolve("visit")
    assert entry is not None
    assert entry.situation_type == "action_visit"
    assert entry.obligatory == ["agente"]


def test_assert_situation_auto_registers_verb_and_ingests():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("spa_oasis", "L", "Spa Oasis")
    out = s.assert_situation(
        "visit",
        roles={"agente": "ana", "lugar_de": "spa_oasis"},
    )
    assert out["ok"] is True
    # the reified situation carries the agente fact
    roles_seen = {f["role"] for f in out["facts"]}
    assert "agente" in roles_seen and "lugar_de" in roles_seen


def test_assert_situation_creates_inline_entities():
    s = WQSession()
    out = s.assert_situation(
        "visit",
        roles={"agente": {"id": "bob", "axis": "Q", "label": "Bob"}},
    )
    assert out["ok"] is True
    assert "bob" in s.universe.individuals


def test_assert_situation_reports_missing_entity():
    s = WQSession()
    out = s.assert_situation("visit", roles={"agente": "ghost"})
    assert out["ok"] is False
    assert "ghost" in out["error"]


def test_add_entity_axis_conflict_returns_error():
    s = WQSession()
    s.add_entity("x", "Q")
    out = s.add_entity("x", "O")
    assert out["ok"] is False
    assert "error" in out


def test_assert_situation_inline_spec_missing_axis_returns_error():
    s = WQSession()
    out = s.assert_situation("visit", roles={"agente": {"id": "bob"}})
    assert out["ok"] is False
    assert "error" in out


def test_ask_projects_the_asked_role():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("spa_oasis", "L", "Spa Oasis")
    s.assert_situation("visit", roles={"agente": "ana", "lugar_de": "spa_oasis"})

    out = s.ask(fixed={"lugar_de": "spa_oasis"}, ask=["agente"])
    assert out["count"] == 1
    assert out["results"][0]["agente"] == "ana"


def test_show_model_reports_counts():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.assert_situation("visit", roles={"agente": "ana"})
    out = s.show_model()
    assert out["fact_count"] >= 1
    assert any(f["role"] == "agente" for f in out["facts"])


def test_load_example_spa_populates_model():
    s = WQSession()
    out = s.load_example("spa")
    assert out["ok"] is True
    assert out["fact_count"] > 0


def test_load_example_unknown_name_errors():
    s = WQSession()
    out = s.load_example("does_not_exist")
    assert out["ok"] is False
