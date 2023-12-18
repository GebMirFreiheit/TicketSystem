import datetime

from pydantic import BaseModel


class TicketBase(BaseModel):
    status: str
    customer_id: int


class TicketCreate(TicketBase):
    pass


class Ticket(TicketBase):
    id: int
    created: datetime.datetime

    class Config:
        orm_mode = True


class CustomerBase(BaseModel):
    full_name: str


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    id: int
    telegram_id: int

    class Config:
        orm_mode = True
