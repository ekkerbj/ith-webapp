from typing import Any


def Nnz(value: Any) -> float | int:
    if value is None or value == "":
        return 0

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def Zero(number: Any, keyword: Any) -> Any:
    if keyword is None:
        return number

    if isinstance(keyword, str):
        if keyword.strip().lower() in {"0", "t", "true", "y", "yes", "z", "zero"}:
            return 0
        return number

    return 0 if keyword else number
