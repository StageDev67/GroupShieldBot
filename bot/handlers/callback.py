from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.db_manager import db
from bot.states.settings import SettingsStates
from bot.keyboards.inline import get_settings_keyboard
from config import config

router = Router()

def status(value):
    return "🟢 Включено" if value else "🔴 Отключено"

@router.callback_query(F.data.startswith("toggle_"))
async def toggle_setting(callback: CallbackQuery):
    """Переключение настроек"""
    setting_map = {
        "toggle_links": "delete_links",
        "toggle_badwords": "delete_bad_words",
        "toggle_forwards": "delete_forwards",
        "toggle_mentions": "delete_mentions"
    }
    
    setting = setting_map.get(callback.data)
    if not setting:
        await callback.answer("❌ Ошибка!")
        return
    
    settings = await db.get_settings(callback.message.chat.id)
    current = settings[setting]
    new_value = 0 if current else 1
    await db.update_setting(callback.message.chat.id, setting, new_value)
    
    # Названия правил для уведомления
    names = {
        "delete_links": "Удаление ссылок",
        "delete_bad_words": "Удаление мата",
        "delete_forwards": "Ограничение пересылок",
        "delete_mentions": "Ограничение упоминаний"
    }
    
    await callback.answer(
        f"✅ {names[setting]} {'включено' if new_value else 'отключено'}!",
        show_alert=False
    )
    
    # Обновляем сообщение
    settings = await db.get_settings(callback.message.chat.id)
    keyboard = get_settings_keyboard(settings)
    
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
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(F.data == "edit_welcome")
async def edit_welcome(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SettingsStates.waiting_for_welcome)
    await state.update_data(chat_id=callback.message.chat.id)
    await callback.message.answer(
        "✏️ <b>Настройка приветствия</b>\n\n"
        "Отправьте новое приветственное сообщение\n\n"
        "📌 <b>Доступные переменные:</b>\n"
        "<code>{username}</code> - имя пользователя\n"
        "<code>{user_mention}</code> - упоминание пользователя\n\n"
        "Пример:\n"
        "<i>Добро пожаловать, {username}! Рады видеть тебя в нашей группе 🎉</i>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "edit_goodbye")
async def edit_goodbye(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SettingsStates.waiting_for_goodbye)
    await state.update_data(chat_id=callback.message.chat.id)
    await callback.message.answer(
        "✏️ <b>Настройка прощания</b>\n\n"
        "Отправьте новое сообщение прощания\n\n"
        "📌 <b>Доступные переменные:</b>\n"
        "<code>{username}</code> - имя пользователя\n"
        "<code>{user_mention}</code> - упоминание пользователя\n\n"
        "Пример:\n"
        "<i>До встречи, {username}! Мы будем скучать 😢</i>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "edit_badwords")
async def edit_badwords(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SettingsStates.waiting_for_bad_words)
    await state.update_data(chat_id=callback.message.chat.id)
    settings = await db.get_settings(callback.message.chat.id)
    await callback.message.answer(
        f"✏️ <b>Настройка запрещенных слов</b>\n\n"
        f"Отправьте новый список слов через запятую\n\n"
        f"📌 <b>Текущий список:</b>\n"
        f"<i>{settings['bad_words']}</i>\n\n"
        "Пример:\n"
        "<code>мат,ругательство,брань,нецензурно</code>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "reset_settings")
async def reset_settings(callback: CallbackQuery):
    await callback.answer("🔄 Настройки сброшены к стандартным", show_alert=True)
    
    await db.update_setting(callback.message.chat.id, "delete_links", 1)
    await db.update_setting(callback.message.chat.id, "delete_bad_words", 1)
    await db.update_setting(callback.message.chat.id, "delete_forwards", 1)
    await db.update_setting(callback.message.chat.id, "delete_mentions", 1)
    await db.update_setting(callback.message.chat.id, "welcome_message", "Добро пожаловать в группу!")
    await db.update_setting(callback.message.chat.id, "goodbye_message", "Пользователь покинул группу")
    await db.update_setting(callback.message.chat.id, "bad_words", ",".join(config.BAD_WORDS_DEFAULT))
    
    # Обновляем сообщение
    settings = await db.get_settings(callback.message.chat.id)
    keyboard = get_settings_keyboard(settings)
    
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
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)