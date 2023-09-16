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
        markup.add(InlineKeyboardButton(text=btn, callback_data=data))

    await bot.reply_to(
        msg,
        "\n".join(fa_msg["response"]).format(
            userId=msg.chat.id,
            channelId=configs.telegrambot_public_channel,
        ),
        parse_mode="MARKDOWN",
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


async def user_registration(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["conversations"]["userRegistration"]

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for btn in fa_msg["btns"]:
        markup.add(KeyboardButton(text=btn))

    await bot.set_state(msg.from_user.id, Advertisement.registration)
    await bot.send_message(
        msg.chat.id,
        ("\n" * 2)
        .join(fa_msg["response"])
        .format(advertisePrice=normalize_from_en(configs.advertise_price)),
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
        await bot.send_message(
            msg.chat.id,
            "\n".join(fa_msg["bookDescription"]["response"]),
            parse_mode="markdown",
        )
        await bot.set_state(msg.chat.id, Advertisement.user_telegram_id)
        async with bot.retrieve_data(msg.chat.id) as data:
            data["user_telegram_id"] = msg.text
    else:
        await bot.reply_to(msg, fa_msg["userTelegramId"]["failed"])


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
            await bot.send_message(
                msg.chat.id, "\n".join(fa_msg["bookAdvertise"]["response"]).format()
            )
            async with bot.retrieve_data(msg.chat.id) as data:
                data["book_price"] = price
            await bot.delete_state(msg.chat.id)
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
