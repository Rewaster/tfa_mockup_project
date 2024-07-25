from typing import Any

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_auth.core.security import get_password_hash
from fastapi_auth.core.security import verify_password
from fastapi_auth.crud.base_crud import CrudBase
from fastapi_auth.models.users import User
from fastapi_auth.schemas.user_schema import UserCreate
from fastapi_auth.schemas.user_schema import UserUpdate


class UserCrud(CrudBase[User, UserCreate, UserUpdate]):
    """Database user information interaction interface"""

    async def create(self, db: Session, user: UserCreate) -> User:  # pylint: disable = arguments-differ
        """Create a new user in the database"""
        db_obj = User(
            email=user.email,
            hashed_password=get_password_hash(user.password),
            tfa_enabled=user.tfa_enabled,
            full_name=user.full_name,
        )
        db.add(db_obj)
        if await self.handle_commit(db):
            await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def authenticate(db: Session, email: EmailStr, password: str) -> User | None:
        """Authenticate an existing user in the database"""
        user: User = await UserCrud.get_by_email(db=db, email=email)
        if not user:
            return None
        user = user[0]
        if not verify_password(password=password, hashed_password=user.hashed_password):
            return None
        return user

    # pylint: disable = arguments-differ
    async def update(self, db: Session, db_obj: User, obj_in: UserUpdate | dict[str, Any]) -> User:
        """Update the existing user's information in the database"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db=db, db_obj=db_obj, obj_in=obj_in)

    @staticmethod
    async def get_by_email(db: Session, email: EmailStr) -> User | None:
        """Find a user based on his e-mail"""
        query = select(User).where(User.email == email)
        model_query = await db.execute(query)
        model_instance = model_query.first()
        return model_instance


user_crud = UserCrud(model=User)
