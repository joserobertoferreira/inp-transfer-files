from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from src.config.settings import SCHEMA

db_schema = str(SCHEMA)

metadata_obj = MetaData(schema=db_schema)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    This class uses a custom metadata object to set the schema for all models.
    """

    metadata = metadata_obj
