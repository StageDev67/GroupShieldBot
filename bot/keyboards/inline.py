from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict

def get_settings_keyboard(settings: Dict) -> InlineKeyboardMarkup:
    """Клавиатура для настроек"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{'✅' if settings['delete_links'] else '❌'} Удаление ссылок",
                    callback_data="toggle_links"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{'✅' if settings['delete_bad_words'] else '❌'} Удаление мата",
                    callback_data="toggle_badwords"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{'✅' if settings['delete_forwards'] else '❌'} Ограничение пересылок",
                    callback_data="toggle_forwards"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{'✅' if settings['delete_mentions'] else '❌'} Ограничение упоминаний",
                    callback_data="toggle_mentions"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Изменить приветствие",
                    callback_data="edit_welcome"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Изменить прощание",
                    callback_data="edit_goodbye"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Изменить список запрещенных слов",
                    callback_data="edit_badwords"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Сбросить настройки",
                    callback_data="reset_settings"
                )
            ]
        ]
    )