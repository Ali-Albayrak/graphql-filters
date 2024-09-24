from typing import Generic, Optional, List, Any, TypeVar, Union
from pydantic import BaseModel, Field
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select, delete, update, insert, BinaryExpression, UnaryExpression

from core.logger import log
from core.depends import get_db
from core.filter_type import FieldFilter
from core.base_model import BaseModel as SQLBaseModel


class QueryBuilderSchema(BaseModel):
    limit: Optional[int] = Field(default=20, ge=0, description="Number of records to return")
    offset: Optional[int] = Field(default=0, ge=0, description="Number of records to skip")
    filters_list: Optional[List[Any]] = Field(default=[], description="List of filters as BinaryExpression objects")
    filters_dict: Optional[dict] = Field(default={}, description="pair of field name and its value")
    sort: Optional[Any] = Field(default=None, description="Sorting expression as UnaryExpression object")


T = TypeVar("T", bound=SQLBaseModel)

class Manager(Generic[T]):
    """
    A generic database interaction class for handling CRUD operations on a specified model.
    """

    def __init__(self, model: T, database: AsyncSession):
        if not database:
            database = next(get_db())
        self.db = database
        self.Model = model
        self._query = QueryBuilderSchema()  # Instantiate a query, update it on get/filter call

    def __str__(self):
        """
        Return a string representation of the instance
        """
        return "%s_%s" % (self.__class__.__name__, self.Model.__name__)

    def update_query(self, **kwargs) -> None:
        """
        Update the query for the instance.
        """
        if kwargs.get("limit"):
            self._query.limit = kwargs.get("limit")
        elif kwargs.get("page_size"):
            self._query.limit = kwargs.get("page_size")

        if kwargs.get("offset"):
            self._query.offset = kwargs.get("offset")
        elif kwargs.get("page"):
            self._query.offset = (kwargs["page"]-1)*self._query.limit

        if kwargs.get("filters_list"):
            self._query.filters_list = self._build_filter_list(kwargs.get("filters_list", []))
        if kwargs.get("filters_dict"):
            self._query.filters_dict = kwargs.get("filters_dict")
        if kwargs.get("sort"):
            self._query.sort = self._build_sort(kwargs.get("sort"))

    def _build_filter_list(self, filters: list[FieldFilter] = None) -> list[BinaryExpression]:
        filter_conditions = []
        log.debug("---- Building filter list ----")
        if not filters:
            return []
        for field_filter in filters:
            field_path = field_filter.field_path.split(".")
            operator = field_filter.operator

            # Resolve the nested relationship by traversing the field path
            current_model = self.Model
            for i, field in enumerate(field_path):
                if hasattr(current_model, field):
                    if i < len(field_path) - 1:
                        # Get the relationship
                        current_model = getattr(current_model, field).property.mapper.class_
                        log.debug(f"Current filtering model updated: {current_model}")

            if hasattr(current_model, field_path[-1]):
                column_attr = getattr(current_model, field_path[-1])
            else:
                log.warning(f"Column <{field_path[-1]}> not found in model <{self.Model.__name__}>")
                continue
            if not isinstance(column_attr, InstrumentedAttribute):
                log.warning(f"Column <{field_path[-1]}> not found in model <{self.Model.__name__}>")
                continue
            if operator.eq is not None:
                filter_conditions.append(column_attr == operator.eq)
            if operator.ne is not None:
                filter_conditions.append(column_attr != operator.ne)
            if operator.gt is not None:
                filter_conditions.append(column_attr > operator.gt)
            if operator.gte is not None:
                filter_conditions.append(column_attr >= operator.gte)
            if operator.lt is not None:
                filter_conditions.append(column_attr < operator.lt)
            if operator.lte is not None:
                filter_conditions.append(column_attr <= operator.lte)
            if operator.prefix is not None:
                filter_conditions.append(column_attr.startswith(operator.prefix))
            if operator.contains is not None:
                filter_conditions.append(column_attr.contains(operator.contains))
            if operator.postfix is not None:
                filter_conditions.append(column_attr.endswith(operator.postfix))
            if operator.ilike is not None:
                filter_conditions.append(column_attr.ilike(f"%{operator.ilike}%"))
            if operator.in_ is not None:
                filter_conditions.append(column_attr.in_(operator.in_))
            if operator.nin is not None:
                filter_conditions.append(column_attr.not_in(operator.nin))
            if operator.is_null == True:
                filter_conditions.append(column_attr.is_(None))
            else:
                filter_conditions.append(column_attr.isnot(None))
        log.debug(f"---- Filters built, Number of conditions: {len(filter_conditions)} ----")
        return filter_conditions

    def _build_sort(self, sort: str) -> UnaryExpression:
        reverse = False
        if not sort:
            return
        if sort.startswith("-"):
            sort = sort[1:]
            reverse = True
        
        if hasattr(self.Model, sort):
            column = getattr(self.Model, sort)
            if isinstance(column, InstrumentedAttribute):
                if reverse:
                    log.debug(f"Sorting by <{sort}> in DESC order")
                    return column.desc()
                else:
                    log.debug(f"Sorting by <{sort}> in ASC order")
                    return column.asc()
        else:
            log.warning(f"For sort, Column <{sort}> not found in model <{self.Model.__name__}>")
            return

    async def __fetch(self, paginate: bool = True):
        """
        Asynchronously fetch records from the database based on the current query.
        """
        statement = select(self.Model)
        
        if self._query.filters_list:
            statement = statement.filter(*self._query.filters_list)
        if self._query.filters_dict:
            statement = statement.filter_by(**self._query.filters_dict)
        if self._query.sort is not None:
            statement = statement.order_by(self._query.sort)
        if paginate:
            statement = statement.offset(self._query.offset).limit(self._query.limit)

        log.debug(f"Compiled SQL Statement: {statement.compile(compile_kwargs={'literal_binds': True})}")
        result = await self.db.execute(statement)
        return result
    
    async def get(self, **query) -> T:
        """
        Get a single record from the database based on the provided query.
        """
        # passing only filters_dict
        self.update_query(filters_dict=query)
        data = await self.__fetch()
        data = data.scalars().first()
        return data
    
    async def all(self, offset: int = None, limit: int = None, paginate: bool = True,
                    sort: str =  None, filters: list[FieldFilter] = None, **query) -> list[T]:
        """
        Retrieve all records from the database based on the current query, with optional offset and limit.
        """
        # build updated query with filters_list, filters_dict, sort, limit, offset
        self.update_query(
            filters_list=filters,
            filters_dict=query,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        data = await self.__fetch(paginate=paginate)
        data = data.unique().scalars().all()
        return data

    async def get_multiple(self, obj_ids):
        """
        THIS FUNCTION IS DEPRECATED, Use all() with filters_list instead
        TODO: Replace this function in all the places where it's used. NOT WORKING NOW
        Get a multi records from the database based on the provided IDs.
        """
        data = await self.db.execute(select(self.Model).filter(self.Model.id.in_(obj_ids)).filter_by(**self._query))
        return data.scalars().all()
        obj.all(filters=[FieldFilter(field_path="id", operator=QueryOperator(in_=obj_ids))])

    def filter(self, **query):
        """
        Update the query for filtering records.
        """
        self.update_query(query)
        return self

    async def create(self, only_add: bool = False, **kwargs) -> T:
        """
        Create a new record in the database and executing pre and post triggers if exist
        """
        model_data = kwargs.get("model_data", {})
        if kwargs.get("signal_data"):
            new_data = await self.pre_create(**kwargs["signal_data"])
            model_data.update(new_data)

        obj = self.Model(**model_data)
        await self.save(obj)
        
        if kwargs.get("signal_data"):
            kwargs.get("signal_data")["new_data"] = obj.__dict__
            await self.post_create(**kwargs["signal_data"])

        return obj

    async def save(self, obj):
        """
        Save changes to the database after adding a new record.
        """
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)

    async def update(self, obj_id, **kwargs):
        """
        Update an existing record in the database.
        """
        model_data = kwargs.get("model_data", {})
        if kwargs.get("signal_data"):
            model_data.update(await self.pre_update(**kwargs["signal_data"]))
        statement = update(self.Model)\
                    .filter(self.Model.id == obj_id)\
                    .values(model_data)
        
        await self.db.execute(statement)
        await self.db.commit()
        updated_row = await self.get(id=obj_id)
        await self.db.refresh(updated_row)

        if kwargs.get("signal_data"):
            kwargs.get("signal_data")["new_data"] = updated_row.to_dict()
            await self.post_update(**kwargs["signal_data"])
        return updated_row

    async def delete(self, obj_id, **kwargs):
        """
        Delete a record from the database.
        """
        is_delete = True
        if kwargs.get("signal_data"):
            is_delete = await self.pre_delete(**kwargs["signal_data"])
        if not is_delete:
            return
        
        await self.db.execute(delete(self.Model).filter(self.Model.id == obj_id))
        await self.db.commit()
        
        if kwargs.get("signal_data"):
            kwargs.get("signal_data")["new_data"] = is_delete
            await self.post_delete(**kwargs["signal_data"])

    async def delete_multiple(self, obj_ids: list, **kwargs):
        """
        Delete multiple records from the database.
        """      
        is_delete = True
        all_old_data = kwargs.get("signal_data")['old_data']
        if kwargs.get("signal_data"):
            for obj in all_old_data:
                kwargs["signal_data"]["old_data"] = dict(obj.__dict__) if obj else {}
                is_delete = await self.pre_delete(**kwargs["signal_data"])
        if not is_delete:
            return

        deleted = await self.db.execute(delete(self.Model).filter(self.Model.id.in_(obj_ids)))
        await self.db.commit()

        if kwargs.get("signal_data"):
            kwargs.get("signal_data")["new_data"] = is_delete
            for obj in all_old_data:
                kwargs["signal_data"]["old_data"] = dict(obj.__dict__) if obj else {}
                await self.post_delete(**kwargs["signal_data"])

        return deleted.rowcount

    async def pre_create(self, **kwargs):
        """
        Perform pre-save operations and return additional model data.
        """
        return kwargs.get("new_data")

    async def post_create(self, **kwargs):
        """
        Perform post-save operations.
        """
        pass

    async def pre_update(self, **kwargs):
        """
        Perform pre-update operations and return additional model data.
        """
        return kwargs.get("new_data")

    async def post_update(self, **kwargs):
        """
        Perform post-update operations.
        """
        pass

    async def pre_delete(self, **kwargs):
        """
        Perform pre-delete operations and return a boolean indicating whether to proceed with the delete.
        """
        return True

    async def post_delete(self, **kwargs):
        """
        Perform post-delete operations.
        """
        pass
