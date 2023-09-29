import logging
from typing import Annotated, Union
from contextlib import asynccontextmanager

import uvicorn
import telebot.async_telebot as aiotelebot
from telebot.types import Update
from fastapi import FastAPI, Response, Header, status

from kheft.bot.app import bot
from kheft.config import configs

WEBHOOK_LISTEN = "0.0.0.0"
WEBHOOK_PORT = configs.webhook_port

WEBHOOK_SECRET_TOKEN = configs.telegrambot_secret_roken

WEBHOOK_URL = configs.webhook_url

logger = aiotelebot.logger
aiotelebot.logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan() -> None:
    """Register webhook for telegram updates."""
    await bot.delete_webhook(drop_pending_updates=True)

    logger.debug(f"updating webhook url, new: {WEBHOOK_URL}")
    if not await bot.set_webhook(
        url=WEBHOOK_URL, secret_token=WEBHOOK_SECRET_TOKEN, drop_pending_updates=True
    ):
        raise RuntimeError("unable to set webhook")

    yield


app = FastAPI(docs=None, redoc_url=None, lifespan=lifespan)


@app.post("/")
async def process_webhook(
    update: dict,
    response: Response,
    x_telegram_bot_api_secret_token: Annotated[Union[str, None], Header()] = None,
):
    """
    Process webhook calls
    """
    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET_TOKEN:
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"message": "Forbidden"}

    await bot.process_new_updates([Update.de_json(update)])


uvicorn.run(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
)
