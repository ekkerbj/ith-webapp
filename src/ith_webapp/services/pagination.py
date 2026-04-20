from dataclasses import dataclass
from math import ceil
from typing import Mapping

from flask import url_for


@dataclass(frozen=True)
class Pagination:
    page: int
    page_size: int
    total_items: int
    total_pages: int
    start_item: int
    end_item: int
    previous_url: str | None
    next_url: str | None


def paginate_query(query, endpoint: str, request_args: Mapping[str, str], page: int, page_size: int):
    page_size = max(1, page_size)
    total_items = query.order_by(None).count()
    total_pages = max(1, ceil(total_items / page_size))
    page = min(max(page, 1), total_pages)
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    pagination = Pagination(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        start_item=0 if total_items == 0 else ((page - 1) * page_size) + 1,
        end_item=min(page * page_size, total_items),
        previous_url=_page_url(endpoint, request_args, page - 1, page_size, total_pages),
        next_url=_page_url(endpoint, request_args, page + 1, page_size, total_pages),
    )
    return items, pagination


def _page_url(
    endpoint: str,
    request_args: Mapping[str, str],
    page: int,
    page_size: int,
    total_pages: int,
) -> str | None:
    if page < 1 or page > total_pages:
        return None
    query_args = {
        key: value
        for key, value in request_args.items()
        if key not in {"page", "page_size"}
    }
    return url_for(endpoint, page=page, page_size=page_size, **query_args)
