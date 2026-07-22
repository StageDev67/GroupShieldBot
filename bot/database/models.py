from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class GroupSettings:
    """Модель настроек группы"""
    group_id: int
    welcome_message: str = "Добро пожаловать в группу!"
    goodbye_message: str = "Пользователь покинул группу"
    delete_links: bool = True
    delete_bad_words: bool = True
    delete_forwards: bool = True
    delete_mentions: bool = True
    bad_words: str = "мат,ругательство"
    updated_at: Optional[datetime] = None

@dataclass
class UserStats:
    """Статистика пользователя в группе"""
    group_id: int
    user_id: int
    message_count: int = 0
    forward_count: int = 0
    last_message_time: Optional[datetime] = None

@dataclass
class Warning:
    """Модель предупреждения"""
    id: int
    group_id: int
    user_id: int
    warned_by: int
    reason: str
    warning_time: datetime