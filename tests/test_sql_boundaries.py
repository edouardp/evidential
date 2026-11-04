"""Token and identifier boundaries preserve valid authored SQL."""

import pytest

from evidential._sql import bind_parameters, quote_identifier


@pytest.mark.parametrize(
    "literal",
    [
        "'{ignore}'",
        '"a""{ignore}"',
        "$$ {ignore} $$",
        "$tag$ $ignore $tag$",
        "E'escaped\\' {ignore}'",
        "/* outer /* {ignore} */ $ignore */",
        "-- {ignore}\n",
    ],
)
@pytest.mark.parametrize("placeholder", ["{p}", "$p", "${p}"])
def test_only_unprotected_parameters_are_bound(literal, placeholder):
    source = literal + " " + placeholder + " " + placeholder
    assert bind_parameters(source, {"p": 3}) == (literal + " ? ?", [3, 3])


@pytest.mark.parametrize("literal", ["'unterminated {p}", "/* unterminated {p}", "$tag$ unterminated {p}"])
def test_unterminated_literals_are_left_for_the_sql_engine_to_diagnose(literal):
    assert bind_parameters(literal, {"p": 1}) == (literal, [])


def test_unknown_parameter_and_embedded_identifier_quote():
    with pytest.raises(KeyError, match="Unknown SQL parameter"):
        bind_parameters("{missing}", {})
    assert quote_identifier('a"b') == '"a""b"'
