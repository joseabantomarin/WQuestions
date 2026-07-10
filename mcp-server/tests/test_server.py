from wquestions_mcp.server import mcp, INSTRUCTIONS


def test_instructions_cover_key_mechanisms():
    text = INSTRUCTIONS.lower()
    for phrase in ["triplet", "reified", "valid_from", "unit",
                   "append-only", "in-memory", "correct("]:
        assert phrase in text, f"instructions missing: {phrase}"


def test_fastmcp_is_wired_with_instructions():
    assert mcp.instructions
    assert "wquestions" in mcp.instructions.lower()
