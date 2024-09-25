import strawberry
from typing import Optional, List
@strawberry.input
class QueryOperator:
    eq: Optional[str] = None
    ne: Optional[str] = None
    gt: Optional[str] = None
    gte: Optional[str] = None
    lt: Optional[str] = None
    lte: Optional[str] = None
    prefix: Optional[str] = None
    contains: Optional[str] = None
    postfix: Optional[str] = None
    in_: Optional[List[str]] = None
    nin: Optional[List[str]] = None
    ilike: Optional[str] = None
    is_null: Optional[bool] = None

@strawberry.input
class FieldFilter:
    field_path: str = strawberry.field(description="The path to the field to filter on")
    operator: QueryOperator

@strawberry.input
class QuerySchema:
    page: Optional[int] = 1
    page_size: Optional[int] = 20
    filters: Optional[List[FieldFilter]] = None
    sort: Optional[str] = None
