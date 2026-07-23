import re
import time
from aiogram import Router, F
from aiogram.types import Message
from bot.database.db_manager import db
from bot.utils.helpers import is_group_admin, delete_message_safe, log_action
from bot.utils.validators import contains_bad_words, contains_links
from config import config

router = Router()

# Хранилище для антиспама
user_last_message = {}

@router.message(F.text & F.chat.type.in_({"group", "supergroup"}))
async def moderate_message(message: Message):
    """Модерация сообщений"""
    if message.from_user.is_bot:
        return
    
    if await is_group_admin(message):
        return
    
    settings = await db.get_settings(message.chat.id)
    msg_count = await db.get_message_count(message.chat.id, message.from_user.id)
    
    user_id = message.from_user.id
    current_time = time.time()
    
    # ============ АНТИСПАМ ============
    if user_id in user_last_message:
        if current_time - user_last_message[user_id] < 1.0:
            await delete_message_safe(message)
            await log_action(message, "Удаление спама", "Слишком частые сообщения")
            await message.answer(
                "❌ <b>Не спамьте</b>\n"
                "<blockquote>Подождите 1 секунду между сообщениями</blockquote>",
                parse_mode="HTML"
            )
            return
    user_last_message[user_id] = current_time
    
    # ============ ССЫЛКИ (ДЛЯ ВСЕХ!) ============
    if settings["delete_links"] and contains_links(message.text):
        await delete_message_safe(message)
        await log_action(message, "Удаление ссылки", f"Пользователь ({msg_count} сообщений)")
        await message.answer(
            "❌ <b>Отправка ссылок запрещена</b>\n"
            "<blockquote>Ссылки удаляются автоматически</blockquote>",
            parse_mode="HTML"
        )
        return
    
    # ============ МАТ ============
    if settings["delete_bad_words"] and contains_bad_words(message.text, settings["bad_words"]):
        await delete_message_safe(message)
        await log_action(message, "Удаление мата", "Обнаружено запрещенное слово")
        await message.answer(
            "❌ <b>Использование мата запрещено</b>\n"
            "<blockquote>Сообщение удалено за нарушение правил</blockquote>",
            parse_mode="HTML"
        )
        return
    
    # ============ ПЕРЕСЫЛКИ ============
    if settings["delete_forwards"] and message.forward_date:
        forward_count = await db.increment_forward_count(message.chat.id, user_id)
        if forward_count > config.MAX_FORWARDS:
            await delete_message_safe(message)
            await db.reset_forward_count(message.chat.id, user_id)
            await log_action(message, "Удаление пересылки", f"Слишком много пересылок ({forward_count})")
            await message.answer(
                f"❌ <b>Пересылки ограничены</b>\n"
                f"<blockquote>Нельзя пересылать более {config.MAX_FORWARDS} сообщений подряд</blockquote>",
                parse_mode="HTML"
            )
            return
    
    # ============ УПОМИНАНИЯ ============
    if settings["delete_mentions"]:
        mention_count = len(re.findall(r'@\w+', message.text))
        if message.reply_to_message:
            mention_count += 1
        if mention_count > config.MAX_MENTIONS:
            await delete_message_safe(message)
            await log_action(message, "Удаление упоминаний", f"Слишком много упоминаний ({mention_count})")
            await message.answer(
                f"❌ <b>Слишком много упоминаний</b>\n"
                f"<blockquote>Нельзя упоминать более {config.MAX_MENTIONS} пользователей в одном сообщении</blockquote>",
                parse_mode="HTML"
            )
            return
    
    await db.increment_message_count(message.chat.id, user_id)