import re
from aiogram import Router, F
from aiogram.types import Message
from bot.database.db_manager import db
from bot.utils.helpers import is_group_admin, delete_message_safe, log_action
from bot.utils.validators import contains_bad_words, contains_links
from config import config

router = Router()

@router.message(F.text & F.chat.type.in_({"group", "supergroup"}))
async def moderate_message(message: Message):
    """Модерация сообщений"""
    if message.from_user.is_bot:
        return
    
    if await is_group_admin(message):
        return
    
    settings = await db.get_settings(message.chat.id)
    msg_count = await db.get_message_count(message.chat.id, message.from_user.id)
    
    # 1. Ссылки от новых пользователей
    if settings["delete_links"] and msg_count < config.NEW_USER_MESSAGE_LIMIT:
        if contains_links(message.text):
            await delete_message_safe(message)
            await log_action(message, "Удаление ссылки", f"Новый пользователь ({msg_count} сообщений)")
            await message.reply("❌ Новым пользователям запрещено отправлять ссылки!")
            return
    
    # 2. Мат
    if settings["delete_bad_words"]:
        if contains_bad_words(message.text, settings["bad_words"]):
            await delete_message_safe(message)
            await log_action(message, "Удаление мата", "Обнаружено запрещенное слово")
            await message.reply("❌ Использование мата запрещено!")
            return
    
    # 3. Пересылки
    if settings["delete_forwards"] and message.forward_date:
        forward_count = await db.increment_forward_count(message.chat.id, message.from_user.id)
        if forward_count > config.MAX_FORWARDS:
            await delete_message_safe(message)
            await db.reset_forward_count(message.chat.id, message.from_user.id)
            await log_action(message, "Удаление пересылки", f"Слишком много пересылок ({forward_count})")
            await message.reply(f"❌ Нельзя пересылать более {config.MAX_FORWARDS} сообщений подряд!")
            return
    
    # 4. Упоминания
    if settings["delete_mentions"]:
        mention_count = len(re.findall(r'@\w+', message.text))
        if message.reply_to_message:
            mention_count += 1
        if mention_count > config.MAX_MENTIONS:
            await delete_message_safe(message)
            await log_action(message, "Удаление упоминаний", f"Слишком много упоминаний ({mention_count})")
            await message.reply(f"❌ Нельзя упоминать более {config.MAX_MENTIONS} пользователей!")
            return
    
    await db.increment_message_count(message.chat.id, message.from_user.id)