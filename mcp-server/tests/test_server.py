from wquestions_mcp.server import mcp, INSTRUCTIONS


def test_instructions_cover_key_mechanisms():
    text = INSTRUCTIONS.lower()
    for phrase in ["triplet", "reified", "valid_from", "unit",
                   "append-only", "in-memory", "correct("]:
        assert phrase in text, f"instructions missing: {phrase}"


def test_fastmcp_is_wired_with_instructions():
    assert mcp.instructions
    assert "wquestions" in mcp.instructions.lower()


def test_instructions_separate_correction_from_identity():
    # El error que costó una migración: usar correct() para unificar dos
    # identificadores legítimos de la misma persona. Las instrucciones deben
    # distinguir los tres casos, o el siguiente cliente lo repite.
    text = INSTRUCTIONS.lower()
    for phrase in ["mismo_que", "identidades", "assert_fact", "find",
                   "history=true", "at=..."]:
        assert phrase in text, f"instructions missing: {phrase}"


def test_instructions_warn_that_ask_sees_the_present_by_default():
    text = INSTRUCTIONS.lower()
    assert "current value" in text
    assert "no longer holds" in text or "never true" in text
