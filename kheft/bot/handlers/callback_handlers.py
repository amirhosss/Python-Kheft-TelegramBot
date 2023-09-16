from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery
from kheft.bot.handlers import message
from kheft.bot.custom_filters import IsMember
from kheft.bot.languages.reader import fa_lang


async def default_starting_callback(call: CallbackQuery, bot: AsyncTeleBot):
    fa_msg = fa_lang["commands"]["start"]
    is_member = await IsMember(bot).check(call.message)
    if is_member:
        await bot.delete_message(call.message.chat.id, call.message.id)
        await message.default_greeting(call.message, bot)
    else:
        await bot.answer_callback_query(
            call.id, "\n".join(fa_msg["default"]["texts"]["failed"]), show_alert=True
        )
