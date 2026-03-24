from typing import Any


def resolve_path(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        raise KeyError(path)
    return current


def evaluate_assertion(prediction: dict[str, Any], assertion: dict[str, Any]) -> dict[str, Any]:
    path = assertion["path"]
    op = assertion["op"]
    expected = assertion.get("value")

    try:
        actual = resolve_path(prediction, path)
    except KeyError:
        return {
            "path": path,
            "op": op,
            "expected": expected,
            "passed": False,
            "actual": None,
            "reason": "missing_path",
        }

    passed = False
    if op == "eq":
        passed = actual == expected
    elif op == "neq":
        passed = actual != expected
    elif op == "gte":
        passed = actual >= expected
    elif op == "lte":
        passed = actual <= expected
    elif op == "contains":
        passed = expected in actual
    elif op == "not_contains":
        passed = expected not in actual
    elif op == "len_eq":
        passed = len(actual) == expected
    elif op == "in":
        passed = actual in expected
    else:
        return {
            "path": path,
            "op": op,
            "expected": expected,
            "passed": False,
            "actual": actual,
            "reason": f"unsupported_op:{op}",
        }

    return {
        "path": path,
        "op": op,
        "expected": expected,
        "actual": actual,
        "passed": passed,
    }
