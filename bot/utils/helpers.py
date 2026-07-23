from aiogram.types import Message, ChatMemberUpdated
from bot import bot
from config import config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def is_group_admin(message: Message, user_id: int = None) -> bool:
    """Проверка, является ли пользователь администратором группы"""
    if user_id is None:
        user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(message.chat.id, user_id)
        return member.status in ["creator", "administrator"]
    except Exception as e:
        print(f"Ошибка проверки админа: {e}")
        return False

async def is_group_creator(message: Message, user_id: int = None) -> bool:
    """Проверка, является ли пользователь создателем группы"""
    if user_id is None:
        user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(message.chat.id, user_id)
        return member.status == "creator"
    except Exception as e:
        logger.error(f"Error checking creator status: {e}")
        return False

async def delete_message_safe(message: Message) -> bool:
    """Безопасное удаление сообщения"""
    try:
        await message.delete()
        from bot.database.db_manager import db
        await db.increment_deleted_messages(message.chat.id)
        return True
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")
        return False

async def ban_user(chat_id: int, user_id: int, reason: str = "") -> bool:
    """Бан пользователя"""
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
    """Логирование действий в канал"""
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

async def reset_user_counters(group_id: int, user_id: int):
    """Сброс счетчиков пользователя"""
    from bot.database.db_manager import db
    await db.reset_message_count(group_id, user_id)
    await db.reset_forward_count(group_id, user_id)
    
async def get_user_by_username(chat_id: int, username: str):
    """Поиск пользователя по username в группе"""
    from bot import bot
    
    # Убираем @ если есть
    if username.startswith("@"):
        username = username[1:]
    
    # 1. Пробуем через get_chat_member
    try:
        member = await bot.get_chat_member(chat_id, f"@{username}")
        return member.user
    except:
        pass
    
    # 2. Ищем среди администраторов
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.username and admin.user.username.lower() == username.lower():
                return admin.user
    except:
        pass
    
    # 3. Ищем среди всех участников
    try:
        async for member in bot.get_chat_members(chat_id):
            if member.user.username and member.user.username.lower() == username.lower():
                return member.user
            if member.user.full_name and username.lower() in member.user.full_name.lower():
                return member.user
    except:
        pass
    
    return None    