import asyncio

from telebot.asyncio_storage import StateMemoryStorage
from telebot.async_telebot import AsyncTeleBot, asyncio_helper
from telebot.asyncio_filters import (
    TextMatchFilter,
    TextStartsFilter,
    StateFilter,
    IsDigitFilter,
)
from kheft.config import configs
from kheft.bot.handlers import message_handlers, callback_handlers
from kheft.bot.states import Advertisement
from kheft.bot.custom_filters import IsMember
from kheft.bot.languages.reader import fa_lang

if configs.environment == "test":
    asyncio_helper.proxy = configs.telegrambot_proxy

bot = AsyncTeleBot(token=configs.telegrambot_token, state_storage=StateMemoryStorage())

bot.add_custom_filter(StateFilter(bot))
bot.add_custom_filter(TextMatchFilter())
bot.add_custom_filter(TextStartsFilter())
bot.add_custom_filter(IsDigitFilter())

# My custom filter
bot.add_custom_filter(IsMember(bot))

messages = fa_lang["messages"]
bot.register_message_handler(
    callback=message_handlers.default_greeting,
    commands=messages["nonMember"]["response"],
    pass_bot=True,
    is_member=False,
)

bot.register_message_handler(
    callback=message_handlers.already_membership_greeting,
    commands=messages["member"]["response"],
    pass_bot=True,
    is_member=True,
)

conversations = fa_lang["conversations"]
bot.register_message_handler(
    callback=message_handlers.advertise_registration,
    text=conversations["userRegistrations"]["response"],
    pass_bot=True,
    is_member=True,
)

bot.register_message_handler(
    callback=message_handlers.rules_acceptance,
    text=conversations["userRules"]["response"],
    state=Advertisement.rules,
    pass_bot=True,
    is_member=True,
)

bot.register_message_handler(
    callback=message_handlers.get_description,
    state=Advertisement.description,
    pass_bot=True,
    is_member=True,
)

bot.register_message_handler(
    callback=message_handlers.get_telegram_id,
    text_startswith="@",
    state=Advertisement.telegram_id,
    pass_bot=True,
    is_member=True,
)

bot.register_message_handler(
    callback=message_handlers.get_price,
    state=Advertisement.price,
    pass_bot=True,
    is_member=True,
    is_digit=True,
)


bot.register_callback_query_handler(
    callback_handlers.default_starting_callback,
    pass_bot=True,
    func=lambda call: call.message.text
    == fa_lang["commands"]["start"]["default"]["callbackData"][0],
)


asyncio.run(bot.polling())
