from reviewer import validate_file


def test_missing_file_when_content_empty():
    result = validate_file("app.py", "")
    assert result["status"] == "MISSING"


def test_valid_python_syntax():
    result = validate_file("app.py", "def foo():\n    return 1\n")
    assert result["status"] == "OK"


def test_invalid_python_syntax():
    result = validate_file("app.py", "def foo(:\n    return 1\n")
    assert result["status"] == "SYNTAX_ERROR"


def test_non_python_file_skips_syntax_check():
    result = validate_file("index.html", "<html></html>")
    assert result["status"] == "OK"
    assert "not checked" in result["detail"]