from aiogram.types import Message, ChatMemberUpdated
from bot import bot
from config import config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def is_group_admin(message: Message, user_id: int = None) -> bool:
    if user_id is None:
        user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(message.chat.id, user_id)
        return member.status in ["creator", "administrator"]
    except:
        return False

async def is_group_creator(message: Message, user_id: int = None) -> bool:
    if user_id is None:
        user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(message.chat.id, user_id)
        return member.status == "creator"
    except:
        return False

async def delete_message_safe(message: Message) -> bool:
    try:
        await message.delete()
        from bot.database.db_manager import db
        await db.increment_deleted_messages(message.chat.id)
        return True
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")
        return False

async def ban_user(chat_id: int, user_id: int, reason: str = "") -> bool:
    try:
        await bot.ban_chat_member(chat_id, user_id)
        from bot.database.db_manager import db
        await db.increment_banned_users(chat_id)
        logger.info(f"User {user_id} banned in chat {chat_id} for: {reason}")
        return True
    except Exception as e:
        logger.error(f"Failed to ban user {user_id}: {e}")
        return False

async def log_action(message_or_update, action: str, details: str = ""):
    if not config.LOG_CHANNEL_ID:
        return
    try:
        if hasattr(message_or_update, 'chat'):
            chat = message_or_update.chat
            user = message_or_update.from_user
        else:
            chat = message_or_update.chat
            user = message_or_update.new_chat_member.user
        log_text = (
            f"📋 <b>Действие модерации</b>\n"
            f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📌 Группа: {chat.title} (ID: {chat.id})\n"
            f"👤 Пользователь: {user.full_name} (@{user.username or 'нет'})\n"
            f"⚡ Действие: {action}\n"
            f"📝 Детали: {details}"
        )
        await bot.send_message(config.LOG_CHANNEL_ID, log_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to log action: {e}")