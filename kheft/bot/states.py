from telebot.asyncio_handler_backends import State, StatesGroup


class Advertisement(StatesGroup):
    rules = State()
    description = State()
    telegram_id = State()
    price = State()
