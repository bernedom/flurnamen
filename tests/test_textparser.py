"""
An example test case with pytest.
See: https://docs.pytest.org/en/6.2.x/index.html
"""
# content of test_sample.py
from flurnamen import textparser


def test_textparser_returns_non_empty_for_existing_file():
    """Test that the textparser returns non-empty string for existing file."""
    parser = textparser.textparser()
    assert parser.parse('tests/test_textparser.py') != ''
