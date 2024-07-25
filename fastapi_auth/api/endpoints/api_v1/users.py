from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from fastapi_auth.api.deps.db import get_db
from fastapi_auth.crud.users import user_crud
from fastapi_auth.schemas import user_schema

user_router = APIRouter()


@user_router.get("/users", response_model=list[user_schema.UserOut])
async def get_user(
    db: Session = Depends(get_db),
) -> Any:
    """Return the information on all of the existing users"""
    return await user_crud.get_multi(db=db)
