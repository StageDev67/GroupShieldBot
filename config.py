import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Конфигурация бота"""
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
    DB_PATH = os.getenv("DB_PATH", "data/group_shield.db")
    
    # Константы
    MAX_WARNINGS = int(os.getenv("MAX_WARNINGS", 3))
    NEW_USER_MESSAGE_LIMIT = int(os.getenv("NEW_USER_MESSAGE_LIMIT", 5))
    MAX_FORWARDS = int(os.getenv("MAX_FORWARDS", 3))
    MAX_MENTIONS = int(os.getenv("MAX_MENTIONS", 5))
    WARNING_EXPIRY_DAYS = int(os.getenv("WARNING_EXPIRY_DAYS", 7))
    
    # Список запрещенных слов по умолчанию
    BAD_WORDS_DEFAULT = os.getenv("BAD_WORDS_DEFAULT", "мат,ругательство").split(",")

config = Config()