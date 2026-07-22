from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import get_main_keyboard
from bot.database.db_manager import db
from bot.utils.helpers import is_group_creator

router = Router()

@router.message(F.text == "📊 Статистика")
async def handle_stats_button(message: Message):
    """Обработка кнопки Статистика"""
    if message.chat.type not in ["group", "supergroup"]:
        await message.reply("❌ Эта команда доступна только в группах!")
        return
    
    stats = await db.get_stats(message.chat.id)
    
    stats_text = (
        f"📊 *Статистика модерации*\n\n"
        f"🗑 Удалено сообщений: {stats['messages_deleted']}\n"
        f"⚠️ Выдано предупреждений: {stats['warnings_given']}\n"
        f"🚫 Забанено пользователей: {stats['users_banned']}"
    )
    
    await message.answer(
        stats_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "⚙️ Настройки")
async def handle_settings_button(message: Message):
    """Обработка кнопки Настройки"""
    if message.chat.type not in ["group", "supergroup"]:
        await message.reply("❌ Эта команда доступна только в группах!")
        return
    
    if not await is_group_creator(message):
        await message.reply("❌ Только создатель группы может менять настройки!")
        return
    
    settings = await db.get_settings(message.chat.id)
    
    from bot.keyboards.inline import get_settings_keyboard
    keyboard = get_settings_keyboard(settings)
    
    current_settings = (
        f"📋 *Текущие настройки группы*\n\n"
        f"🔗 Удаление ссылок: {'✅' if settings['delete_links'] else '❌'}\n"
        f"🚫 Удаление мата: {'✅' if settings['delete_bad_words'] else '❌'}\n"
        f"📨 Ограничение пересылок: {'✅' if settings['delete_forwards'] else '❌'}\n"
        f"👥 Ограничение упоминаний: {'✅' if settings['delete_mentions'] else '❌'}\n\n"
        f"📝 Приветствие: {settings['welcome_message'][:50]}...\n"
        f"📝 Прощание: {settings['goodbye_message'][:50]}...\n"
        f"🚫 Запрещенные слова: {settings['bad_words']}"
    )
    
    await message.answer(
        current_settings,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@router.message(F.text == "❓ Помощь")
async def handle_help_button(message: Message):
    """Обработка кнопки Помощь"""
    help_text = (
        "📖 *Помощь по GroupShieldBot*\n\n"
        "🛡️ *Модерация*\n"
        "• Удаление ссылок от новых пользователей\n"
        "• Фильтрация запрещенных слов\n"
        "• Ограничение пересылок (макс 3 подряд)\n"
        "• Ограничение упоминаний (макс 5)\n\n"
        "⚠️ *Система предупреждений*\n"
        "• 3 предупреждения = автоматический бан\n"
        "• Предупреждения сгорают через 7 дней\n\n"
        "👋 *Участники*\n"
        "• Приветствие новых участников\n"
        "• Прощание с вышедшими\n\n"
        "⚙️ *Команды*\n"
        "/settings - Настройка правил\n"
        "/stats - Статистика\n"
        "/warn - Выдать предупреждение\n"
        "/clear_warns - Очистить предупреждения"
    )
    
    await message.answer(
        help_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "ℹ️ О боте")
async def handle_about_button(message: Message):
    """Обработка кнопки О боте"""
    about_text = (
        "🤖 *GroupShieldBot v1.0*\n\n"
        "Бот для автоматической модерации групп в Telegram\n"
        "Разработан с использованием aiogram 3.x\n\n"
        "📊 *Возможности*\n"
        "• Автоматическая модерация\n"
        "• Система предупреждений\n"
        "• Статистика модерации\n"
        "• Гибкие настройки\n\n"
        "💡 *Требования*\n"
        "• Бот должен быть администратором\n"
        "• Права на удаление сообщений\n"
        "• Права на бан участников"
    )
    
    await message.answer(
        about_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "❌ Отменить")
async def handle_cancel_button(message: Message, state: FSMContext):
    """Обработка кнопки Отменить"""
    await state.clear()
    await message.answer(
        "❌ Операция отменена",
        reply_markup=get_main_keyboard()
    )