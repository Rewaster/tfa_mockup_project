from typing import Generator

from fastapi_auth.api import common_logger
from fastapi_auth.db.session import SessionLocal


async def get_db() -> Generator:
    """Try to commit information to the database; rollback changes if commit fails"""
    try:
        db = SessionLocal()
        yield db
        await db.commit()
        common_logger.debug("committed in db...")
    except Exception as ex:  # pylint:disable = broad-exception-caught
        common_logger.debug(f"rolling db for exception {ex} ...")
        await db.rollback()
    finally:
        common_logger.debug("closing db...")
        await db.close()
        common_logger.debug("..db closed!")
