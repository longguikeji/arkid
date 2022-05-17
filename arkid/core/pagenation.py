from typing import Any, List
from ninja.pagination import paginate, PaginationBase
from ninja import Field, Schema
from arkid.core.schema import ResponseSchema



class CustomPagination(PaginationBase):
    # only `skip` param, defaults to 5 per page
    class Input(Schema):
        page: int = Field(
            default=0
        )

        limit: int = Field(
            default=10
        )

    class Output(ResponseSchema):
        items: List[Any]
        total: int
        previous: str
        next: str

    def paginate_queryset(self, queryset, pagination: Input, request, **params):
        page = pagination.page
        limit = pagination.limit
        items = list(queryset)[page*limit : page*limit+limit]
        return {
            'items': items,
            'total': len(list(queryset)),
            "previous": f"{request.path}?page={page-1}&limit={limit}" if page > 1 else "",
            "next": f"{request.path}?page={page+1}&limit={limit}" if (page+1) * limit < len(list(queryset)) else ""
        }
