from typing import TypeVar, Type, Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
# from pydantic import BaseModel


ModelType = TypeVar("ModelType")
# CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseData:
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, obj_in: Type[ModelType]):
        db_obj = self.model(**obj_in.model_dump())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def create_by_model(self, model: Type[ModelType]):
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_one(self, id: int):
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete(self, id: int) -> bool:
        db_obj = await self.get_one(id)
        await self.session.delete(db_obj)
        await self.session.commit()
        return True

    async def update(self, id: int, obj_in: Type[ModelType]) -> ModelType:
        db_obj = await self.get_one(id)
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    def _apply_filters(self, query, filters: Optional[Dict[str, any]]) -> Any:
        if not filters:
            return query
        for field, value in filters.items():
            if '__' in field:
                field, operator = field.split('__')
                if not hasattr(self.model, field) or value is None:
                    continue
                if operator == 'eq':
                    query = query.where(getattr(self.model, field) == value)
                elif operator == 'ne':
                    query = query.where(getattr(self.model, field) != value)
                # elif operator == 'gt':
                #     query = query.where(getattr(self.model, field) > value)
                # elif operator == 'lt':
                #     query = query.where(getattr(self.model, field) < value)
                # elif operator == 'gte':
                #     query = query.where(getattr(self.model, field) >= value)
                # elif operator == 'lte':
                #     query = query.where(getattr(self.model, field) <= value)
                elif operator == 'icontains':
                    query = query.where(getattr(self.model, field).ilike(f'%{value}%'))
                elif operator == 'istartswith':
                    query = query.where(getattr(self.model, field).ilike(f'{value}%'))
                elif operator == 'iendswith':
                    query = query.where(getattr(self.model, field).ilike(f'%{value}'))
                elif operator == 'is_null':
                    query = query.where(getattr(self.model, field).is_(None))
                elif operator == 'is_not_null':
                    query = query.where(getattr(self.model, field)._is_not(None))
            else:
                if not hasattr(self.model, field) or value is None:
                    continue
                query = query.where(getattr(self.model, field) == value)
        return query

    async def get_multi(
                            self,
                            skip: int = 0,
                            limit: int = 100,
                            filters: Optional[Dict[str, Any]] = None,
                            sort_field: Optional[str] = None,
                            sort_order: str = "asc",
                            eager_loads: Optional[List[Any]] = None,
                        ) -> List[ModelType]:
        """Return model and total count

        Args:
            skip (int, optional): Defaults to 0.
            limit (int, optional): Defaults to 100.
            filters (Optional[Dict[str, Any]], optional): Defaults to None.

        Returns:
            List[ModelType], int : return list of models and total count
        """
        query = select(self.model)
        query = self._apply_filters(query, filters)

        if eager_loads:
            query = query.options(*eager_loads)

        count_query = select(func.count()).select_from(self.model)
        count_query = self._apply_filters(count_query, filters)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        if sort_field and hasattr(self.model, sort_field):
            if sort_order.lower() == "desc":
                query = query.order_by(getattr(self.model, sort_field).desc())
            else:
                query = query.order_by(getattr(self.model, sort_field).asc())
        else:
            query = query.order_by(self.model.id.asc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)

        return result.scalars().all(), total
