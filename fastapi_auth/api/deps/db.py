from typing import Generator

from fastapi_auth.db.session import SessionLocal


async def get_db() -> Generator:
    """Try to commit information to the database; rollback changes if commit fails"""
    try:
        db = SessionLocal()
        yield db
        await db.commit()
        print("committed in db...")
    except Exception as ex:  # pylint:disable = broad-exception-caught
        print(f"rolling db for exception {ex} ...")
        await db.rollback()
    finally:
        print("closing db...")
        await db.close()
        print("..db closed!")
