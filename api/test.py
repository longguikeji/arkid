from api.api import api

from typing import List

from pydantic import Field

from ninja import Query, Schema


class Filters(Schema):
    limit: int = 100
    offset: int = None
    query: str = None
    category__in: List[str] = Field(None, alias="categories")


@api.get("/filter", auth=None)
def events(request, filters: Filters = Query(...), ):
    return {"filters": filters.dict()}

from ninja import Schema


class Item(Schema):
    name: str
    description: str = None
    price: float
    quantity: int


@api.post("/items", auth=None)
def create(request, item: Item):
    return item