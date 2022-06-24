from typing import Any, List, Optional
from django.http import QueryDict
from ninja.pagination import PaginationBase
from ninja import Field, Schema
from arkid.core.schema import ResponseSchema



class CustomPagination(PaginationBase):
    class Input(Schema):
        page: int = Field(
            default=1
        )

        page_size: int = Field(
            default=10
        )

    class Output(ResponseSchema):
        items: Optional[List[Any]] = Field(
            default=[]
        )
        count: Optional[int]
        previous: Optional[str]
        next: Optional[str]

    def paginate_queryset(self, queryset, pagination: Input, request, **params):
        
        if not (isinstance(queryset,list) or isinstance(queryset,QueryDict)):
            queryset.update({"items":[]})
            return queryset
        
        page = pagination.page
        page_size = pagination.page_size
        items = list(queryset)[max(page-1,0)*page_size : page*page_size]
        return {
            'items': items,
            'count': len(list(queryset)),
            "previous": f"{request.path}?page={page-1}&page_size={page_size}" if page > 2 else "",
            "next": f"{request.path}?page={page+1}&page_size={page_size}" if page * page_size < len(list(queryset)) else ""
        }
