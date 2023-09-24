from telebot.async_telebot import asyncio_helper
from telebot.asyncio_filters import (
    TextMatchFilter,
    TextStartsFilter,
    StateFilter,
    IsDigitFilter,
)

from kheft.api.main import bot
from kheft.config import configs
from kheft.bot.handlers import callback, message
from kheft.bot.states import Advertisement
from kheft.bot.custom_filters import IsMember
from kheft.bot.languages.reader import fa_lang

if configs.environment == "test":
    asyncio_helper.proxy = configs.telegrambot_proxy


bot.add_custom_filter(StateFilter(bot))
bot.add_custom_filter(TextMatchFilter())
bot.add_custom_filter(TextStartsFilter())
bot.add_custom_filter(IsDigitFilter())

# My custom filter
bot.add_custom_filter(IsMember(bot))


conversations = fa_lang["conversations"]
bot.register_message_handler(
    callback=message.cancel_conversation,
    commands="cancel",
    pass_bot=True,
    is_member=True,
)

bot.register_message_handler(
    callback=message.user_registration,
    text=conversations["userRegistration"]["query"],
    pass_bot=True,
    is_member=True,
)

bot.register_message_handler(
    callback=message.rules_acceptance,
    state=Advertisement.registration,
    pass_bot=True,
    is_member=True,
)

bot.register_message_handler(
    callback=message.get_telegram_id,
    state=Advertisement.rules,
    pass_bot=True,
    is_member=True,
)

bot.register_message_handler(
    callback=message.get_book_name,
    state=Advertisement.user_telegram_id,
    pass_bot=True,
    is_member=True,
)

bot.register_message_handler(
    callback=message.get_book_description,
    state=Advertisement.book_name,
    pass_bot=True,
    is_member=True,
)

bot.register_message_handler(
    callback=message.get_book_price,
    state=Advertisement.book_description,
    pass_bot=True,
    is_member=True,
)


messages = fa_lang["messages"]
bot.register_message_handler(
    callback=message.non_member_greeting,
    pass_bot=True,
    is_member=False,
)

bot.register_message_handler(
    callback=message.member_greeting,
    pass_bot=True,
    is_member=True,
)

bot.register_callback_query_handler(
    callback.default_starting_callback,
    pass_bot=True,
    func=lambda call: call.data == "ok",
)

bot.register_callback_query_handler(
    callback.admin_confirm_reject, pass_bot=True, func=lambda call: True
)
