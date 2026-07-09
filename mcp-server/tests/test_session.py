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
