"""SQLAlchemy declarative base and metadata."""

from sqlalchemy.orm import declarative_base

Base = declarative_base()

metadata = Base.metadata
