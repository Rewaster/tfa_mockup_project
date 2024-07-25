import typing as t

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.ext.declarative import declared_attr

class_registry: t.Dict = {}


@as_declarative(class_registry=class_registry)
class Base:
    """Base class for accessing database information"""

    id = Column(Integer, primary_key=True, index=True)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()
