from collections.abc import Mapping, Sequence

from flask import url_for


def _sort_direction(value: str | None) -> str:
    if value == "desc":
        return "desc"
    return "asc"


def apply_sorting(query, request_args: Mapping[str, str], sort_map, default_sort_key: str):
    sort_key = request_args.get("sort") or default_sort_key
    if sort_key not in sort_map:
        sort_key = default_sort_key
    direction = _sort_direction(request_args.get("direction"))
    order_expression = sort_map[sort_key]
    if direction == "desc":
        return query.order_by(order_expression.desc()), sort_key, direction
    return query.order_by(order_expression.asc()), sort_key, direction


def build_sortable_columns(
    endpoint: str,
    request_args: Mapping[str, str],
    columns: Sequence[tuple[str, str | None]],
    current_sort_key: str,
    current_direction: str,
):
    query_args = {
        key: value
        for key, value in request_args.items()
        if key not in {"page", "page_size", "sort", "direction"}
    }
    return [
        {
            "label": label,
            "url": None
            if sort_key is None
            else url_for(
                endpoint,
                sort=sort_key,
                direction="desc"
                if sort_key == current_sort_key and current_direction == "asc"
                else "asc",
                **query_args,
            ),
            "active": sort_key == current_sort_key,
            "direction": current_direction if sort_key == current_sort_key else None,
        }
        for label, sort_key in columns
    ]
