from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from bot.database.db_manager import db

router = Router()

# ТАКОЙ ЖЕ ОБРАБОТЧИК КАК ДЛЯ /settings
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Статистика модерации"""
    print("🔴 КОМАНДА /stats СРАБОТАЛА!")
    print(f"   Чат: {message.chat.type} ({message.chat.id})")
    
    if message.chat.type not in ("group", "supergroup"):
        await message.answer("❌ Команда доступна только в группе!")
        return
    
    stats = await db.get_stats(message.chat.id)
    
    text = (
        f"📊 <b>Статистика модерации</b>\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🗑 Удалено сообщений:  <b>{stats['messages_deleted']}</b>\n"
        f"⚠️ Выдано предупреждений:  <b>{stats['warnings_given']}</b>\n"
        f"🚫 Забанено пользователей:  <b>{stats['users_banned']}</b>"
    )
    await message.answer(text, parse_mode="HTML")