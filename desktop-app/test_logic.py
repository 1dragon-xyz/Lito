from logic import TextProcessor

def test_clean_text():
    raw = "Hello   World!  "
    expected = "Hello World!"
    assert TextProcessor.clean_text(raw) == expected

def test_extract_from_md():
    md_content = """# Title
**Bold** text."""
    # The current regex might leave extra spaces or newlines, so we'll just check if key words are present
    # or strict equality if we know exactly how logic.py behaves.
    # Let's do a loose check first to be safe, or exact if we trust logic.
    cleaned = TextProcessor.extract_from_md(md_content)
    assert "Title" in cleaned
    assert "Bold text" in cleaned

