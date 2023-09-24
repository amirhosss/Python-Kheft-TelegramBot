import logging
from typing import Annotated, Union

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
WEBHOOK_URL_PATH = "/{}/".format(configs.telegrambot_token)

logger = aiotelebot.logger
aiotelebot.logger.setLevel(logging.INFO)


app = FastAPI(docs=None, redoc_url=None)


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


# Remove webhook, it fails sometimes the set if there is a previous webhook
@app.on_event("startup")
async def startup() -> None:
    """Register webhook for telegram updates."""
    webhook_info = await bot.get_webhook_info(30)
    if WEBHOOK_URL != webhook_info.url:
        logger.debug(
            f"updating webhook url, old: {webhook_info.url}, new: {WEBHOOK_URL}"
        )
        if not await bot.set_webhook(
            url=WEBHOOK_URL, secret_token=WEBHOOK_SECRET_TOKEN
        ):
            raise RuntimeError("unable to set webhook")


uvicorn.run(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
)
