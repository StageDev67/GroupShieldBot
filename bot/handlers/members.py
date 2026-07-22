from aiogram import Router
from aiogram.types import ChatMemberUpdated
from bot.database.db_manager import db
from bot.utils.helpers import log_action
from bot import bot

router = Router()

@router.chat_member()
async def handle_member_update(update: ChatMemberUpdated):
    """Обработка изменений участников"""
    chat_id = update.chat.id
    
    # Новый участник
    if update.new_chat_member.status in ["member", "administrator", "creator"] and update.old_chat_member.status == "left":
        settings = await db.get_settings(chat_id)
        welcome = settings["welcome_message"]
        if welcome:
            name = update.new_chat_member.user.full_name
            mention = f"<a href='tg://user?id={update.new_chat_member.user.id}'>{name}</a>"
            welcome = welcome.replace("{username}", name).replace("{user_mention}", mention)
            await bot.send_message(chat_id, welcome, parse_mode="HTML")
    
    # Вышел участник
    elif update.old_chat_member.status in ["member", "administrator", "creator"] and update.new_chat_member.status == "left":
        settings = await db.get_settings(chat_id)
        goodbye = settings["goodbye_message"]
        if goodbye:
            name = update.old_chat_member.user.full_name
            mention = f"<a href='tg://user?id={update.old_chat_member.user.id}'>{name}</a>"
            goodbye = goodbye.replace("{username}", name).replace("{user_mention}", mention)
            await bot.send_message(chat_id, goodbye, parse_mode="HTML")
        await db.reset_message_count(chat_id, update.old_chat_member.user.id)