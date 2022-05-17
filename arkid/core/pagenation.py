from typing import Any, List
from ninja.pagination import PaginationBase
from ninja import Field, Schema
from arkid.core.schema import ResponseSchema



class CustomPagination(PaginationBase):
    # only `skip` param, defaults to 5 per page
    class Input(Schema):
        page: int = Field(
            default=0
        )

        page_size: int = Field(
            default=10
        )

    class Output(ResponseSchema):
        items: List[Any]
        total: int
        previous: str
        next: str

    def paginate_queryset(self, queryset, pagination: Input, request, **params):
        page = pagination.page
        page_size = pagination.page_size
        items = list(queryset)[page*page_size : page*page_size+page_size]
        return {
            'items': items,
            'count': len(list(queryset)),
            "previous": f"{request.path}?page={page-1}&page_size={page_size}" if page > 1 else "",
            "next": f"{request.path}?page={page+1}&page_size={page_size}" if (page+1) * page_size < len(list(queryset)) else ""
        }
