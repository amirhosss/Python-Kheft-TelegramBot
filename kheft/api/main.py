import logging

import fastapi
import uvicorn
import telebot.async_telebot as aiotelebot

from kheft.config import configs

API_TOKEN = configs.telegrambot_token

WEBHOOK_LISTEN = "0.0.0.0"
WEBHOOK_PORT = configs.webhook_port

WEBHOOK_URL = configs.webhook_url
WEBHOOK_URL_PATH = "/{}/".format(configs.telegrambot_token)

logger = aiotelebot.logger
aiotelebot.logger.setLevel(logging.INFO)

bot = aiotelebot.AsyncTeleBot(API_TOKEN, state_storage=aiotelebot.StateMemoryStorage())

app = fastapi.FastAPI(docs=None, redoc_url=None)


@app.post(f"/{API_TOKEN}/")
async def process_webhook(update: dict):
    """
    Process webhook calls
    """
    if update:
        update = aiotelebot.types.Update.de_json(update)
        await bot.process_new_updates([update])
    else:
        return


# Remove webhook, it fails sometimes the set if there is a previous webhook
@app.on_event("startup")
async def startup() -> None:
    """Register webhook for telegram updates."""
    webhook_info = await bot.get_webhook_info(30)
    if WEBHOOK_URL != webhook_info.url:
        logger.debug(
            f"updating webhook url, old: {webhook_info.url}, new: {WEBHOOK_URL}"
        )
        if not await bot.set_webhook(url=WEBHOOK_URL, secret_token=API_TOKEN):
            raise RuntimeError("unable to set webhook")


uvicorn.run(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
)
