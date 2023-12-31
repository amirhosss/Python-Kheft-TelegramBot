import httpx
from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from kheft.bot.handlers import message
from kheft.bot.custom_filters import IsMember
from kheft.bot.languages.reader import fa_lang

from kheft.bot.handlers.utils import normalize_from_en
from kheft.config import configs


async def default_starting_callback(call: CallbackQuery, bot: AsyncTeleBot):
    fa_msg = fa_lang["messages"]["nonMember"]
    is_member = await IsMember(bot).check(call.message)
    if is_member:
        await bot.delete_message(call.message.chat.id, call.message.id)
        await message.member_greeting(call.message, bot)
    else:
        await bot.answer_callback_query(call.id, fa_msg["failed"], show_alert=True)


async def admin_confirm_reject(call: CallbackQuery, bot: AsyncTeleBot):
    data = call.data
    status, book_id = data.split(",")

    if status in ["reject", "confirm"]:
        async with httpx.AsyncClient(http2=True) as client:
            try:
                res = await client.patch(
                    configs.backend_url + "/Book/Accept",
                    headers={"X-Api-Key": configs.backend_api_key},
                    json={
                        "bookId": book_id,
                        "isAccepted": True if status == "confirm" else False,
                    },
                )

            except Exception as e:
                print(f"an error occurred when sending book acceptance {e}")
                return

            await bot.answer_callback_query(
                call.id,
                text="Accepted ✅" if status == "confirm" else "Rejected ❌",
                show_alert=True,
            )
            await bot.edit_message_reply_markup(
                configs.telegrambot_private_group,
                call.message.id,
                reply_markup=None,
            )
            if status == "confirm":
                data = res.json()["message"]

                await bot.send_message(
                    configs.telegrambot_public_channel,
                    text=(2 * "\n")
                    .join(fa_lang["conversations"]["publicBookAdvertise"]["response"])
                    .format(
                        bookName=data["book"]["name"],
                        description=data["book"]["description"],
                        username=data["bookOwner"]["telegramUsername"],
                        price=normalize_from_en(data["book"]["price"]),
                    ),
                )
