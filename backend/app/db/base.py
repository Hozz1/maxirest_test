from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models so SQLAlchemy metadata is populated.
from app import models  # noqa: E402,F401
