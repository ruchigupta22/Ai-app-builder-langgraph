import pytest
from tools import safe_path_for_project, PROJECT_ROOT


def test_normal_path_allowed():
    p = safe_path_for_project("index.html")
    assert p.parent == PROJECT_ROOT.resolve()


def test_nested_path_allowed():
    p = safe_path_for_project("assets/style.css")
    assert PROJECT_ROOT.resolve() in p.parents


def test_path_traversal_blocked():
    with pytest.raises(ValueError):
        safe_path_for_project("../../etc/passwd")