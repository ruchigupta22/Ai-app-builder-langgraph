import ast

from tools import read_file


def validate_file(filepath: str, content: str) -> dict:
    """
    Pure validation logic, separated from the agent function so it can be
    unit tested without needing LangGraph, an LLM, or the filesystem.
    """
    if not content:
        return {"file": filepath, "status": "MISSING", "detail": "File was not created or is empty"}

    if filepath.endswith(".py"):
        try:
            ast.parse(content)
            return {"file": filepath, "status": "OK", "detail": "Valid Python syntax"}
        except SyntaxError as e:
            return {"file": filepath, "status": "SYNTAX_ERROR", "detail": str(e)}

    return {
        "file": filepath,
        "status": "OK",
        "detail": "File exists and is non-empty (syntax not checked for this file type)",
    }


def reviewer_agent(state: dict) -> dict:
    """
    Validates that every file the Coder Agent was supposed to write actually
    exists and is non-empty, and that Python files parse without syntax
    errors. Runs after the coder loop finishes, before the graph ends.
    """
    coder_state = state["coder_state"]
    task_plan = coder_state.task_plan

    results = []
    for task in task_plan.implementation_steps:
        content = read_file.run(task.filepath)
        results.append(validate_file(task.filepath, content))

    passed = sum(1 for r in results if r["status"] == "OK")
    total = len(results)

    print(f"\n[Reviewer] Validated {total} files: {passed} OK, {total - passed} issue(s)")
    for r in results:
        marker = "PASS" if r["status"] == "OK" else "FAIL"
        print(f"  [{marker}] {r['file']}: {r['status']} - {r['detail']}")

    return {"coder_state": coder_state, "review_report": results, "status": "REVIEWED"}