import httpx
from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    Message,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)

from kheft.config import configs
from kheft.bot.languages.reader import fa_lang
from kheft.bot.states import Advertisement
from kheft.bot.handlers.utils import normalize_from_en, normalize_to_en


async def non_member_greeting(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["messages"]["nonMember"]

    markup = InlineKeyboardMarkup()
    for btn, data in zip(fa_msg["btns"], fa_msg["failed"]):
        markup.add(InlineKeyboardButton(text=btn, callback_data="ok"))

    await bot.reply_to(
        msg,
        "\n".join(fa_msg["response"]).format(
            firstName=msg.chat.first_name,
            channelId=configs.telegrambot_public_channel,
        ),
        reply_markup=markup,
    )


async def member_greeting(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["messages"]["member"]

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in fa_msg["btns"]:
        markup.add(KeyboardButton(text=btn))

    await bot.send_message(
        msg.chat.id, "\n".join(fa_msg["response"]), reply_markup=markup
    )


async def cancel_conversation(msg: Message, bot: AsyncTeleBot):
    await bot.delete_state(msg.chat.id)
    await member_greeting(msg, bot)


async def user_registration(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["conversations"]["userRegistration"]

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for btn in fa_msg["btns"]:
        markup.add(KeyboardButton(text=btn))

    await bot.set_state(msg.from_user.id, Advertisement.registration)
    await bot.send_message(
        msg.chat.id,
        ("\n" * 2).join(fa_msg["response"]),
        reply_markup=markup,
    )


async def rules_acceptance(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["conversations"]

    if msg.text == fa_msg["userRegistration"]["btns"][0]:
        await bot.set_state(msg.chat.id, Advertisement.rules)
        await bot.send_message(
            msg.chat.id, "\n".join(fa_msg["userTelegramId"]["response"])
        )
    else:
        await bot.reply_to(msg, fa_msg["userRegistration"]["failed"])


async def get_telegram_id(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["conversations"]

    if msg.text.startswith("@"):
        await bot.send_message(msg.chat.id, "\n".join(fa_msg["bookName"]["response"]))
        await bot.set_state(msg.chat.id, Advertisement.user_telegram_id)
        async with bot.retrieve_data(msg.chat.id) as data:
            data["user_telegram_id"] = msg.text
    else:
        await bot.reply_to(msg, fa_msg["userTelegramId"]["failed"])


async def get_book_name(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["conversations"]

    await bot.send_message(
        msg.chat.id, "\n".join(fa_msg["bookDescription"]["response"])
    )
    await bot.set_state(msg.chat.id, Advertisement.book_name)
    async with bot.retrieve_data(msg.chat.id) as data:
        data["book_name"] = msg.text


async def get_book_description(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["conversations"]

    await bot.send_message(msg.chat.id, "\n".join(fa_msg["bookPrice"]["response"]))
    await bot.set_state(msg.chat.id, Advertisement.book_description)
    async with bot.retrieve_data(msg.chat.id) as data:
        data["book_description"] = msg.text


async def get_book_price(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["conversations"]

    price = normalize_to_en(msg.text)
    if price.isdigit():
        price = int(price)
        lower_limit = configs.book_price_limit[0]
        upper_limit = configs.book_price_limit[1]

        if lower_limit <= price <= upper_limit:
            current_msg = await bot.send_message(
                msg.chat.id, "\n".join(fa_msg["bookAdvertise"]["waiting"])
            )
            user_data = {}
            async with bot.retrieve_data(msg.chat.id) as data:
                data["book_price"] = price
                user_data = data

            async with httpx.AsyncClient(
                http2=True,
                proxies={
                    "http://": configs.telegrambot_proxy,
                    "https://": configs.telegrambot_proxy,
                },
            ) as client:
                try:
                    res = await client.post(
                        configs.backend_url + "/Book/Add",
                        headers={"X-Api-Key": configs.api_key},
                        json={
                            "bookName": user_data["book_name"],
                            "price": user_data["book_price"],
                            "description": user_data["book_description"],
                            "bookOwner": {
                                "telegramUsername": user_data["user_telegram_id"],
                                "fullName": msg.chat.first_name,
                                "telegramSerialId": msg.chat.id,
                            },
                        },
                    )
                    book_id = res.json()["message"]
                    async with bot.retrieve_data(msg.chat.id) as data:
                        data["book_id"] = book_id

                except Exception as e:
                    print(
                        f"an error occurred when using httpx to request the api by: {e}"
                    )
                    await bot.delete_state(msg.chat.id)
                    return

            await bot.delete_message(msg.chat.id, current_msg.id)
            sent_msg = await bot.send_message(
                msg.chat.id,
                "\n".join(fa_msg["bookAdvertise"]["response"]).format(
                    name=msg.chat.first_name,
                    bookName=user_data["book_name"],
                    description=user_data["book_description"],
                    username=user_data["user_telegram_id"],
                    price=normalize_from_en(user_data["book_price"]),
                    channelId=configs.telegrambot_public_channel,
                ),
            )

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(
                    text="Confirm ✅", callback_data=f"confirm,{book_id}"
                )
            )
            markup.add(
                InlineKeyboardButton(text="Reject ❌", callback_data=f"reject,{book_id}")
            )

            await bot.send_message(
                configs.telegrambot_private_group, sent_msg.text, reply_markup=markup
            )

        else:
            await bot.reply_to(
                msg,
                fa_msg["bookPrice"]["failedLimit"].format(
                    lowerLimit=normalize_from_en(lower_limit),
                    upperLimit=normalize_from_en(upper_limit),
                ),
            )
    else:
        await bot.reply_to(msg, fa_msg["bookPrice"]["failed"])
