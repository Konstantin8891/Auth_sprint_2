"""Базовый круд."""
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Any)
CreateUpdateSchemaType = TypeVar("CreateUpdateSchemaType", bound=BaseModel)


class CRUDAbstract(ABC):
    """Абстрактный круд."""

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Инит."""
        pass

    @abstractmethod
    async def get_by_field_name(self, *args, **kwargs) -> ModelType:
        """Получение сущности."""
        pass

    @abstractmethod
    async def get_list(self, *args, **kwargs) -> List[ModelType]:
        """Получение списка."""
        pass

    @abstractmethod
    async def create(self, *args, **kwargs) -> ModelType:
        """Создание."""
        pass

    @abstractmethod
    async def update(self, *args, **kwargs) -> ModelType:
        """Обновление."""
        pass

    @abstractmethod
    async def remove(self, *args, **kwargs) -> None:
        """Удаление."""
        pass


class CRUDSQLAlchemy:
    """Круд алхимии."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инит."""
        self.model = model

    async def get_by_field_name(
        self,
        field_name: Any,
        field_value: Any,
        db: AsyncSession,
        _select: Type[ModelType],
        selection_load_options: Optional[List[Tuple]] = None,
        conditions: Optional[List[Tuple]] = None,
        joins: Optional[List[Tuple]] = None,
        outerjoins: Optional[List[Tuple]] = None,
        condition_any: Optional[List[Dict]] = None,
    ) -> ModelType:
        """Получение сущности."""
        query = select(_select)
        if joins:
            for table, condition in joins:
                query = query.join(table, condition)
        if outerjoins:
            for table, condition in outerjoins:
                query = query.outerjoin(table, condition)
        if selection_load_options:
            for options_tuple in selection_load_options:
                options_obj = None
                for option in options_tuple:
                    if options_obj is None:
                        options_obj = selectinload(option)
                    else:
                        options_obj = options_obj.selectinload(option)
                if options_obj:
                    query = query.options(options_obj)
        if conditions:
            for key, value, comparison in conditions:
                query = query.where(comparison(key, value))
        if condition_any:
            where_conditions = []
            for condition in condition_any:
                for key, value in condition.items():
                    where_conditions.append(key.in_(value))
            query = query.where(or_(*where_conditions))
        query = query.where(field_name == field_value)  # noqa
        try:
            query = query.group_by(self.model.id)
        except Exception:
            pass
        result = await db.execute(query)
        if outerjoins:
            return result.unique().scalars().first()
        return result.scalars().first()

    async def get_list(
        self,
        _select: Type[ModelType],
        db: AsyncSession,
        selection_load_options: Optional[List[Tuple]] = None,
        condition_any: Optional[List[Dict]] = None,
        conditions: Optional[List[Tuple]] = None,
        joins: Optional[List[Tuple]] = None,
        search_list: Optional[List[Tuple]] = None,
        order: Optional[Any] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[ModelType]:
        """Получение списка."""
        query = select(_select)
        if joins:
            for table, condition in joins:
                query = query.join(table, condition)
        if selection_load_options:
            for options_tuple in selection_load_options:
                options_obj = None
                for option in options_tuple:
                    if options_obj is None:
                        options_obj = selectinload(option)
                    else:
                        options_obj = options_obj.options(selectinload(option))
                if options_obj:
                    query = query.options(options_obj)
        if condition_any:
            where_conditions = []
            for condition in condition_any:
                for key, value in condition.items():
                    where_conditions.append(key.in_(value))
            query = query.where(or_(*where_conditions))
        if conditions:
            for key, value, comparison in conditions:
                query = query.where(comparison(key, value))
        if search_list:
            for value in search_list[1]:
                search_conditions_equals = [func.lower(field).contains(value) for field in search_list[0]]
                query = query.where(or_(*search_conditions_equals))
        if order is not None:
            query = query.order_by(order)
        if limit:
            query = query.limit(limit=limit)
        if offset:
            query = query.offset(offset=offset)
        query = query.distinct()
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: Union[CreateUpdateSchemaType, Dict[str, Any]]) -> ModelType:
        """Создание."""
        obj_in = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: Union[CreateUpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Обновление."""
        obj_data = jsonable_encoder(obj_in)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, _id: Union[int, uuid.UUID]) -> None:
        """Удаление."""
        obj = await self.get_by_field_name(db=db, field_name=self.model.id, field_value=_id, _select=self.model)
        await db.delete(obj)
        await db.commit()
