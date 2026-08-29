from wall_tidbits.normalize import budget, strip_html


def test_strip_html_handles_mixed_case_elements():
    assert strip_html("A<BR>B<SCRIPT>hidden()</SCRIPT><STYLE>.x{}</STYLE>C") == "A B C"


def test_budget_ellipsis_respects_limit():
    result = budget("x" * 181, 180)
    assert len(result) == 180
    assert result.endswith("…")
