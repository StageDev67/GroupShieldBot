from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.database.db_manager import db
from bot.utils.helpers import is_group_creator
from bot.states.settings import SettingsStates
from bot.keyboards.inline import get_settings_keyboard
from config import config

router = Router()

@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Настройки группы"""
    if message.chat.type not in ("group", "supergroup"):
        await message.answer("❌ Команда доступна только в группе")
        return

    if not await is_group_creator(message):
        await message.answer("❌ Только создатель группы может менять настройки")
        return

    settings = await db.get_settings(message.chat.id)
    keyboard = get_settings_keyboard(settings)

    def status(value):
        return "🟢 Включено" if value else "🔴 Отключено"

    text = (
        "⚙️ <b>Панель управления GroupShieldBot</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "🛡️ <b>Правила модерации</b>\n"
        "▫️ Ссылки от новых:     {}\n"
        "▫️ Запрещенные слова:    {}\n"
        "▫️ Пересылки (макс 3):   {}\n"
        "▫️ Упоминания (макс 5):  {}\n\n"
        "📝 <b>Сообщения</b>\n"
        "▫️ Приветствие:\n"
        "   <i>{}</i>\n"
        "▫️ Прощание:\n"
        "   <i>{}</i>\n\n"
        "🚫 <b>Запрещенные слова</b>\n"
        "   <i>{}</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Нажмите на кнопку, чтобы изменить</i>"
    ).format(
        status(settings['delete_links']),
        status(settings['delete_bad_words']),
        status(settings['delete_forwards']),
        status(settings['delete_mentions']),
        settings['welcome_message'][:60] + ("..." if len(settings['welcome_message']) > 60 else ""),
        settings['goodbye_message'][:60] + ("..." if len(settings['goodbye_message']) > 60 else ""),
        settings['bad_words'][:50] + ("..." if len(settings['bad_words']) > 50 else "")
    )

    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

# FSM обработчики для настроек
@router.message(SettingsStates.waiting_for_welcome)
async def process_welcome(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data.get("chat_id")
    await db.update_setting(chat_id, "welcome_message", message.text)
    await state.clear()
    
    await message.answer(
        "✅ <b>Приветствие обновлено</b>\n\n"
        f"📝 Новое приветствие:\n<i>{message.text}</i>",
        parse_mode="HTML"
    )

@router.message(SettingsStates.waiting_for_goodbye)
async def process_goodbye(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data.get("chat_id")
    await db.update_setting(chat_id, "goodbye_message", message.text)
    await state.clear()
    
    await message.answer(
        "✅ <b>Прощание обновлено</b>\n\n"
        f"📝 Новое прощание:\n<i>{message.text}</i>",
        parse_mode="HTML"
    )

@router.message(SettingsStates.waiting_for_bad_words)
async def process_bad_words(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data.get("chat_id")
    words = [w.strip() for w in message.text.split(",") if w.strip()]
    
    if not words:
        await message.answer("❌ Список не может быть пустым! Отправьте слова через запятую")
        return
    
    await db.update_setting(chat_id, "bad_words", ",".join(words))
    await state.clear()
    
    await message.answer(
        "✅ <b>Список запрещенных слов обновлен</b>\n\n"
        f"🚫 Новые слова:\n<i>{', '.join(words)}</i>",
        parse_mode="HTML"
    )