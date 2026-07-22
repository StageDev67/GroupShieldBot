from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from bot.database.db_manager import db
from bot.utils.helpers import is_group_admin, ban_user, log_action
from config import config

router = Router()

@router.message(Command("warn"))
async def cmd_warn(message: Message, command: CommandObject):
    """Выдача предупреждения"""
    if message.chat.type not in ("group", "supergroup"):
        await message.answer("❌ Команда доступна только в группе!")
        return
    
    if not await is_group_admin(message):
        await message.answer("❌ Только администраторы могут выдавать предупреждения!")
        return
    
    if not command.args:
        await message.answer("❌ Использование: /warn @username [причина]")
        return
    
    args = command.args.split(" ", 1)
    username = args[0].strip()
    reason = args[1] if len(args) > 1 else "Нарушение правил"
    
    if username.startswith("@"):
        username = username[1:]
    
    try:
        from bot import bot
        user = await bot.get_chat_member(message.chat.id, f"@{username}")
        target_user = user.user
    except:
        await message.answer("❌ Пользователь не найден!")
        return
    
    if await is_group_admin(message, target_user.id):
        await message.answer("❌ Нельзя выдавать предупреждение администратору!")
        return
    
    warnings_count = await db.add_warning(
        message.chat.id, target_user.id, message.from_user.id, reason
    )
    
    await log_action(message, "Предупреждение", 
                     f"{target_user.full_name}, причина: {reason}, варнов: {warnings_count}/{config.MAX_WARNINGS}")
    
    if warnings_count >= config.MAX_WARNINGS:
        await ban_user(message.chat.id, target_user.id, f"3 предупреждения: {reason}")
        await db.clear_warnings(message.chat.id, target_user.id)
        await message.answer(f"🚫 {target_user.full_name} забанен за 3 предупреждения!\nПричина: {reason}")
    else:
        await message.answer(f"⚠️ {target_user.full_name} получил предупреждение #{warnings_count}/{config.MAX_WARNINGS}")

@router.message(Command("clear_warns"))
async def cmd_clear_warns(message: Message, command: CommandObject):
    """Очистка предупреждений"""
    if message.chat.type not in ("group", "supergroup"):
        await message.answer("❌ Команда доступна только в группе!")
        return
    
    if not await is_group_admin(message):
        await message.answer("❌ Только администраторы могут очищать предупреждения!")
        return
    
    if not command.args:
        await message.answer("❌ Использование: /clear_warns @username")
        return
    
    username = command.args.strip()
    if username.startswith("@"):
        username = username[1:]
    
    try:
        from bot import bot
        user = await bot.get_chat_member(message.chat.id, f"@{username}")
        target_user = user.user
    except:
        await message.answer("❌ Пользователь не найден!")
        return
    
    await db.clear_warnings(message.chat.id, target_user.id)
    await message.answer(f"✅ Предупреждения {target_user.full_name} очищены!")