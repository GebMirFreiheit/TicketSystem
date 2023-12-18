import aiohttp
from typing import Union
from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine, get_db

app = FastAPI()
TOKEN = "your_bot_token"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def dashboard(
        db: Session = Depends(get_db),
        status: Union[str, None] = None,
        customer: Union[str, None] = None,
        sortby: Union[str, None] = None,
    ):
    if status:
        if status not in models.Status.__members__:
            return HTTPException(status_code=400, detail="No such status")
    # отобразить список тикетов, иметь возможность их сортировать
    tickets = db.query(schemas.Ticket).all()
    if len(tickets) > 0:
        return tickets
    else:
        return {"result": "no tickets yet"}


@app.post("/webhook/")
async def webhook(req: Request, db: Session = Depends(get_db)):
    """
    Хук для получения уведомлений от телеграма и их обработки: создание
    тикета в БД или ответа, что тикет создан
    """
    data = await req.json()
    customer_telegram_id = data["message"]["from"]["id"]
    chat_id = data['message']['chat']['id']
    # по id отправителя смотрим, есть ли у нас такой клиент
    customer = db.query(schemas.Customer)\
        .get(schemas.Customer.telegram_id == customer_telegram_id)
    if customer is not None:
        # смотрим, есть ли у клиента активные тикеты
        tickets = db.query(schemas.Ticket)\
            .filter(status=models.Status.is_open)\
            .filter(schemas.Ticket.customer_id == customer.telegram_id)
        # если есть, отправляем об этом сообщение
        if len(tickets) > 0:
            message_text = "По вашему обращению уже создан активный тикет"
            await aiohttp.request(
                "GET", 
                f"{BASE_URL}/sendMessage?chat_id={chat_id}&text={message_text}")
        # иначе создаём новый тикет
        else:
            ticket = models.Ticket(
                status=models.Status.is_open,
                customer_id=customer.id,
            )
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            message_text = "По вашему обращению создан тикет"
            await aiohttp.request(
                "GET", 
                f"{BASE_URL}/sendMessage?chat_id={chat_id}&text={message_text}")
    else:
        # создать кастомера
        pass
