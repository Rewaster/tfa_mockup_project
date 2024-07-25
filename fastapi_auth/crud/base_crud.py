from typing import Any
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import Session

from fastapi_auth.db.base_class import Base

# SqlAlchemy Model
ModelType = TypeVar("ModelType", bound=Base)
# Pydantic Create schema
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# Pydantic Update schema
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CrudBase(
    Generic[
        ModelType,  # XXX SqlAlchemy Model,
        CreateSchemaType,  # Pydantic Create Schema,
        UpdateSchemaType,  # Pydantic Update Schema
    ]
):
    """CRUD interfacing base class"""

    def __init__(self, model: Type[ModelType], transaction: bool = False):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model (Type[ModelType]): A SQLAlchemy model class
            transaction (bool, optional): if True, changes won't be committed.
                Defaults to False.
        """

        self.model = model
        self.transaction = transaction

    def __call__(self, transaction: bool) -> "CrudBase":
        self.transaction = transaction
        return self

    async def handle_commit(self, db: Session) -> bool:
        """Process the commit provided"""
        committed = False
        if not self.transaction:
            print(f"{self} is NOT under transaction, committing..")
            await db.commit()
            committed = True
        print(f"{self} is under transaction, NOT committing..")
        return committed

    async def get(self, db: Session, id: Any) -> Optional[ModelType]:  # pylint: disable = redefined-builtin
        """Get the required information from the database"""
        query = select(self.model).where(self.model.id == id)
        model_query = await db.execute(query)
        (model_instance,) = model_query.first()
        return model_instance

    async def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get several entries from the database"""
        model_list = await db.execute(select(self.model).offset(skip).limit(limit))
        return model_list.scalars().all()

    async def create(self, db: Session, *, obj_in: CreateSchemaType):
        """Create a new entry in the database"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj: ModelType = self.model(**obj_in_data)
        db.add(db_obj)
        if await self.handle_commit(db):
            await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update the existing entry in the database"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        query = (
            update(self.model)
            .where(self.model.id == db_obj.id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        if await self.handle_commit(db):
            await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: Session, *, id: int) -> bool:  # pylint: disable = redefined-builtin
        """Remove the existing entry from the database"""
        query = delete(self.model).where(self.model.id == id)
        await db.execute(query)
        return await self.handle_commit(db)
