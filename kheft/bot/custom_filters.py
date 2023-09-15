from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import SimpleCustomFilter
from telebot.types import Message
from kheft.config import configs


class IsMember(SimpleCustomFilter):
    key = 'is_member'

    def __init__(self, bot: AsyncTeleBot) -> None:
        self._bot = bot

    async def check(self, message: Message):
        chat_memebr = await self._bot.get_chat_member(chat_id=configs.telegrambot_public_channel,
        user_id=message.chat.id)
        member_status = chat_memebr.status

        return member_status not in ['left', 'banned']