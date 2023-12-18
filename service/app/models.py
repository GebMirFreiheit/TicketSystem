import datetime
import enum
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship

from .database import Base


class Status(enum.Enum):
    is_open = 1
    in_progress = 2
    closed = 3


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(Status))
    created = Column(DateTime, default=datetime.datetime.now)
    modified = Column(DateTime, default=datetime.datetime.now)
    customer_id = Column(Integer, ForeignKey("customers.id"))

    items = relationship("Customer", back_populates="creator")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    telegram_id = Column(Integer, unique=True)

    items = relationship("Ticket", back_populates="tickets")
