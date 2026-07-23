from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.database.db_manager import db
from bot.utils.helpers import is_group_admin

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Статистика модерации"""
    if message.chat.type not in ("group", "supergroup"):
        await message.answer(
            "❌ <b>Ошибка</b>\n"
            "<blockquote>Команда доступна только в группах</blockquote>",
            parse_mode="HTML"
        )
        return
    
    if not await is_group_admin(message):
        await message.answer(
            "❌ <b>Доступ запрещен</b>\n"
            "<blockquote>Только администраторы могут просматривать статистику</blockquote>",
            parse_mode="HTML"
        )
        return
    
    stats = await db.get_stats(message.chat.id)
    
    text = (
        f"📊 <b>Статистика модерации</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🗑 Удалено сообщений:  <b>{stats['messages_deleted']}</b>\n"
        f"⚠️ Выдано предупреждений:  <b>{stats['warnings_given']}</b>\n"
        f"🚫 Забанено пользователей:  <b>{stats['users_banned']}</b>"
    )
    await message.answer(text, parse_mode="HTML")