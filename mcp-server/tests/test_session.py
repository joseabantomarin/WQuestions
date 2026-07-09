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
