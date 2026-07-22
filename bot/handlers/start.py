from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from pathlib import Path

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start"""
    welcome_text = (
        "💫 <b>Привет! Я GroupShieldBot</b>\n\n"
        "Я помогаю модерировать группы и защищать их от спама и нарушений\n\n"
        "📌 <b>Команды</b>\n"
        "/settings - Настройка правил (только для создателя группы)\n"
        "/stats - Статистика модерации\n"
        "/warn @username [причина] - Предупредить пользователя (3 варна = бан)\n"
        "/clear_warns @username - Очистить предупреждения пользователя\n\n"
        "➕ <b>Как использовать</b>\n"
        "1️⃣ Добавьте меня в группу\n"
        "2️⃣ Сделайте меня администратором\n"
        "3️⃣ Настройте правила через /settings"
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