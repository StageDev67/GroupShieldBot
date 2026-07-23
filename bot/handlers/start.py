from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from pathlib import Path
from bot.utils.helpers import is_group_admin

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start"""
    # Проверяем, что команда в группе
    if message.chat.type in ("group", "supergroup"):
        # Проверяем, является ли пользователь админом
        if not await is_group_admin(message):
            await message.answer(
                "❌ <b>Доступ запрещен</b>\n"
                "<blockquote>Эта команда доступна только администраторам группы</blockquote>",
                parse_mode="HTML"
            )
            return
    
    # Если в личке - показываем приветствие
    welcome_text = (
        "💫 <b>Я GroupShieldBot</b>\n\n"
        "Помогаю модерировать группы и защищать их от спама и нарушений\n\n"
        "📌 <b>Команды</b>\n"
        "<blockquote>/settings - Настройка правил (только для создателя группы)\n"
        "/stats - Статистика модерации (только для админов)\n"
        "/warn @username [причина] - Предупредить пользователя (только для админов)\n"
        "/clear_warns @username - Очистить предупреждения (только для админов)\n\n</blockquote>"
        "➕ <b>Как использовать</b>\n"
        "<blockquote>1️⃣ Добавьте меня в группу\n"
        "2️⃣ Сделайте меня администратором\n"
        "3️⃣ Настройте правила через /settings</blockquote>"
    )
    
    image_path = Path(__file__).parent.parent / "static" / "welcome.jpg"
    
    if image_path.exists():
        photo = FSInputFile(str(image_path))
        await message.answer_photo(
            photo=photo,
            caption=welcome_text,
            parse_mode="HTML"
        )
    else:
        await message.answer(welcome_text, parse_mode="HTML")