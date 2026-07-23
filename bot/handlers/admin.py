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
        await message.answer(
            "❌ <b>Ошибка</b>\n"
            "<blockquote>Команда доступна только в группах</blockquote>",
            parse_mode="HTML"
        )
        return
    
    if not await is_group_admin(message):
        await message.answer(
            "❌ <b>Доступ запрещен</b>\n"
            "<blockquote>Только администраторы могут выдавать предупреждения</blockquote>",
            parse_mode="HTML"
        )
        return
    
    target_user = None
    reason = "Нарушение правил"
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        if command.args:
            reason = command.args
    else:
        if not command.args:
            await message.answer(
                "❌ <b>Неверный формат</b>\n"
                "<blockquote>Использование:\n"
                "1. Ответьте на сообщение пользователя и напишите /warn [причина]\n"
                "2. Или: /warn @username [причина]\n"
                "3. Или: /warn 123456789 [причина]</blockquote>",
                parse_mode="HTML"
            )
            return
        
        args = command.args.split(" ", 1)
        username = args[0].strip()
        reason = args[1] if len(args) > 1 else "Нарушение правил"
        
        if username.startswith("@"):
            username = username[1:]
        
        try:
            from bot import bot
            
            try:
                member = await bot.get_chat_member(message.chat.id, username)
                target_user = member.user
            except:
                try:
                    admins = await bot.get_chat_administrators(message.chat.id)
                    for admin in admins:
                        if admin.user.username and admin.user.username.lower() == username.lower():
                            target_user = admin.user
                            break
                except:
                    pass
                
                if not target_user and username.isdigit():
                    try:
                        member = await bot.get_chat_member(message.chat.id, int(username))
                        target_user = member.user
                    except:
                        pass
        except Exception as e:
            print(f"Ошибка поиска: {e}")
    
    if not target_user:
        await message.answer(
            "❌ <b>Пользователь не найден</b>\n"
            "<blockquote>Не удалось найти пользователя\n\n"
            "💡 <b>Как найти ID пользователя:</b>\n"
            "Перешлите сообщение пользователя в @TgramUserIDBot\n\n"
            "📌 <b>Использование:</b>\n"
            "• Ответьте на сообщение: /warn [причина]\n"
            "• Или по ID: /warn 123456789 [причина]</blockquote>",
            parse_mode="HTML"
        )
        return
    
    if await is_group_admin(message, target_user.id):
        await message.answer(
            "❌ <b>Ошибка</b>\n"
            "<blockquote>Нельзя выдавать предупреждение администратору</blockquote>",
            parse_mode="HTML"
        )
        return
    
    warnings_count = await db.add_warning(
        message.chat.id, target_user.id, message.from_user.id, reason
    )
    
    await log_action(message, "Предупреждение", 
                     f"{target_user.full_name}, причина: {reason}, варнов: {warnings_count}/{config.MAX_WARNINGS}")
    
    if warnings_count >= config.MAX_WARNINGS:
        await ban_user(message.chat.id, target_user.id, f"3 предупреждения: {reason}")
        await db.clear_warnings(message.chat.id, target_user.id)
        await message.answer(
            f"🚫 <b>Пользователь забанен</b>\n"
            f"<blockquote>{target_user.full_name} забанен за 3 предупреждения\n"
            f"Причина: {reason}</blockquote>",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"⚠️ <b>Предупреждение #{warnings_count}/{config.MAX_WARNINGS}</b>\n"
            f"<blockquote>{target_user.full_name} получил предупреждение\n"
            f"Причина: {reason}</blockquote>",
            parse_mode="HTML"
        )

@router.message(Command("clear_warns"))
async def cmd_clear_warns(message: Message, command: CommandObject):
    """Очистка предупреждений"""
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
            "<blockquote>Только администраторы могут очищать предупреждения</blockquote>",
            parse_mode="HTML"
        )
        return
    
    target_user = None
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        if not command.args:
            await message.answer(
                "❌ <b>Неверный формат</b>\n"
                "<blockquote>Использование:\n"
                "1. Ответьте на сообщение пользователя и напишите /clear_warns\n"
                "2. Или: /clear_warns @username\n"
                "3. Или: /clear_warns 123456789</blockquote>",
                parse_mode="HTML"
            )
            return
        
        username = command.args.strip()
        if username.startswith("@"):
            username = username[1:]
        
        try:
            from bot import bot
            
            try:
                member = await bot.get_chat_member(message.chat.id, username)
                target_user = member.user
            except:
                try:
                    admins = await bot.get_chat_administrators(message.chat.id)
                    for admin in admins:
                        if admin.user.username and admin.user.username.lower() == username.lower():
                            target_user = admin.user
                            break
                except:
                    pass
                
                if not target_user and username.isdigit():
                    try:
                        member = await bot.get_chat_member(message.chat.id, int(username))
                        target_user = member.user
                    except:
                        pass
        except:
            pass
    
    if not target_user:
        await message.answer(
            "❌ <b>Пользователь не найден</b>\n"
            "<blockquote>Не удалось найти пользователя\n\n"
            "💡 <b>Как найти ID пользователя:</b>\n"
            "Перешлите сообщение пользователя в @TgramUserIDBot\n\n"
            "📌 <b>Использование:</b>\n"
            "• Ответьте на сообщение: /clear_warns\n"
            "• Или по ID: /clear_warns 123456789</blockquote>",
            parse_mode="HTML"
        )
        return
    
    await db.clear_warnings(message.chat.id, target_user.id)
    await message.answer(
        f"✅ <b>Предупреждения очищены</b>\n"
        f"<blockquote>У пользователя {target_user.full_name} очищены все предупреждения</blockquote>",
        parse_mode="HTML"
    )