from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Статистика"),
                KeyboardButton(text="⚙️ Настройки")
            ],
            [
                KeyboardButton(text="❓ Помощь"),
                KeyboardButton(text="ℹ️ О боте")
            ]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return keyboard

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отменить")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return keyboard

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для администраторов"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Статистика"),
                KeyboardButton(text="⚙️ Настройки")
            ],
            [
                KeyboardButton(text="⚠️ Выдать варн"),
                KeyboardButton(text="🔄 Очистить варны")
            ],
            [
                KeyboardButton(text="❓ Помощь"),
                KeyboardButton(text="ℹ️ О боте")
            ]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return keyboard

def remove_keyboard() -> ReplyKeyboardRemove:
    """Удаление клавиатуры"""
    return ReplyKeyboardRemove()