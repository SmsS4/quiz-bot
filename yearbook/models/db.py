import datetime
import uuid

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UUID
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Quiz(Base):
    __tablename__ = "quiz"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creation_time = Column(DateTime, default=datetime.datetime.utcnow)
    user = Column(Integer(), nullable=False)
    name = Column(String, nullable=False)
    answers = Column(postgresql.ARRAY(String))
