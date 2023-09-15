from email import message
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
from kheft.bot.handlers.utils import normalize_from_en


async def default_greeting(msg: Message, bot: AsyncTeleBot):
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


async def already_membership_greeting(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["messages"]["member"]

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in fa_msg["btns"]:
        markup.add(KeyboardButton(text=btn))

    await bot.send_message(
        msg.chat.id, "\n".join(fa_msg["response"]), reply_markup=markup
    )


async def advertise_registration(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["conversations"]["userRegistration"]

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for btn in fa_msg["btns"]:
        markup.add(KeyboardButton(text=btn))

    await bot.set_state(msg.from_user.id, Advertisement.rules)
    await bot.send_message(
        msg.chat.id,
        ("\n" * 2)
        .join(fa_msg["response"])
        .format(advertisePrice=normalize_from_en(configs.advertise_price)),
        reply_markup=markup,
    )


async def rules_acceptance(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["rulesAcceptance"]

    await bot.set_state(msg.chat.id, Advertisement.description)
    await bot.send_message(msg.chat.id, "\n".join(fa_msg["responses"]))


async def get_description(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["getDescription"]

    await bot.send_message(msg.chat.id, "\n".join(fa_msg["responses"]))
    await bot.set_state(msg.chat.id, Advertisement.telegram_id)
    async with bot.retrieve_data(msg.chat.id) as data:
        data["description"] = msg.text


async def get_telegram_id(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["getTelegramId"]

    await bot.send_message(
        msg.chat.id, "\n".join(fa_msg["responses"]), parse_mode="markdown"
    )
    await bot.set_state(msg.chat.id, Advertisement.price)
    async with bot.retrieve_data(msg.chat.id) as data:
        data["telegram_id"] = msg.text


async def get_price(msg: Message, bot: AsyncTeleBot):
    fa_msg = fa_lang["getPrice"]

    await bot.send_message(msg.chat.id, "\n".join(fa_msg["responses"]))
    async with bot.retrieve_data(msg.chat.id) as data:
        data["price"] = msg.text
    await bot.delete_state(msg.chat.id)
