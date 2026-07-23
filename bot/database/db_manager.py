import aiosqlite
from contextlib import asynccontextmanager
from typing import Dict, Optional, List
from config import config
from .models import GroupSettings, Warning

class Database:
    """Менеджер базы данных"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @asynccontextmanager
    async def get_connection(self):
        """Контекстный менеджер для подключения к БД"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            yield db
    
    async def init_db(self):
        """Инициализация таблиц"""
        async with self.get_connection() as db:
            # Таблица настроек
            await db.execute("""
                CREATE TABLE IF NOT EXISTS group_settings (
                    group_id INTEGER PRIMARY KEY,
                    welcome_message TEXT DEFAULT 'Добро пожаловать в группу!',
                    goodbye_message TEXT DEFAULT 'Пользователь покинул группу',
                    delete_links BOOLEAN DEFAULT 1,
                    delete_bad_words BOOLEAN DEFAULT 1,
                    delete_forwards BOOLEAN DEFAULT 1,
                    delete_mentions BOOLEAN DEFAULT 1,
                    bad_words TEXT DEFAULT 'мат,ругательство',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица статистики пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER,
                    user_id INTEGER,
                    message_count INTEGER DEFAULT 0,
                    forward_count INTEGER DEFAULT 0,
                    last_message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(group_id, user_id)
                )
            """)
            
            # Таблица предупреждений
            await db.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER,
                    user_id INTEGER,
                    warned_by INTEGER,
                    reason TEXT,
                    warning_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица глобальной статистики
            await db.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    group_id INTEGER PRIMARY KEY,
                    messages_deleted INTEGER DEFAULT 0,
                    users_banned INTEGER DEFAULT 0,
                    warnings_given INTEGER DEFAULT 0
                )
            """)
            
            await db.commit()
    
    # --- Методы для работы с настройками ---
    
    async def get_settings(self, group_id: int) -> Dict:
        """Получение настроек группы"""
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT * FROM group_settings WHERE group_id = ?",
                (group_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                # Создаем настройки по умолчанию
                await db.execute(
                    "INSERT INTO group_settings (group_id) VALUES (?)",
                    (group_id,)
                )
                await db.commit()
                return await self.get_settings(group_id)
            
            return dict(row)
    
    async def update_setting(self, group_id: int, setting: str, value):
        """Обновление настройки"""
        async with self.get_connection() as db:
            await db.execute(
                f"UPDATE group_settings SET {setting} = ?, updated_at = CURRENT_TIMESTAMP WHERE group_id = ?",
                (value, group_id)
            )
            await db.commit()
    
    # --- Методы для работы с сообщениями ---
    
    async def increment_message_count(self, group_id: int, user_id: int) -> int:
        """Увеличение счетчика сообщений"""
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT message_count FROM user_messages WHERE group_id = ? AND user_id = ?",
                (group_id, user_id)
            )
            row = await cursor.fetchone()
            
            if row:
                new_count = row["message_count"] + 1
                await db.execute(
                    "UPDATE user_messages SET message_count = ?, last_message_time = CURRENT_TIMESTAMP "
                    "WHERE group_id = ? AND user_id = ?",
                    (new_count, group_id, user_id)
                )
            else:
                new_count = 1
                await db.execute(
                    "INSERT INTO user_messages (group_id, user_id, message_count) VALUES (?, ?, ?)",
                    (group_id, user_id, new_count)
                )
            
            await db.commit()
            return new_count
    
    async def get_message_count(self, group_id: int, user_id: int) -> int:
        """Получение количества сообщений"""
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT message_count FROM user_messages WHERE group_id = ? AND user_id = ?",
                (group_id, user_id)
            )
            row = await cursor.fetchone()
            return row["message_count"] if row else 0
    
    async def reset_message_count(self, group_id: int, user_id: int):
        """Сброс счетчика сообщений"""
        async with self.get_connection() as db:
            await db.execute(
                "DELETE FROM user_messages WHERE group_id = ? AND user_id = ?",
                (group_id, user_id)
            )
            await db.commit()
    
    async def increment_forward_count(self, group_id: int, user_id: int) -> int:
        """Увеличение счетчика пересылок"""
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT forward_count FROM user_messages WHERE group_id = ? AND user_id = ?",
                (group_id, user_id)
            )
            row = await cursor.fetchone()
            
            if row:
                new_count = row["forward_count"] + 1
                await db.execute(
                    "UPDATE user_messages SET forward_count = ?, last_message_time = CURRENT_TIMESTAMP "
                    "WHERE group_id = ? AND user_id = ?",
                    (new_count, group_id, user_id)
                )
            else:
                new_count = 1
                await db.execute(
                    "INSERT INTO user_messages (group_id, user_id, forward_count) VALUES (?, ?, ?)",
                    (group_id, user_id, new_count)
                )
            
            await db.commit()
            return new_count
    
    async def reset_forward_count(self, group_id: int, user_id: int):
        """Сброс счетчика пересылок"""
        async with self.get_connection() as db:
            await db.execute(
                "UPDATE user_messages SET forward_count = 0 WHERE group_id = ? AND user_id = ?",
                (group_id, user_id)
            )
            await db.commit()
    
    # --- Методы для работы с предупреждениями ---
    
    async def add_warning(self, group_id: int, user_id: int, warned_by: int, reason: str = "") -> int:
        """Добавление предупреждения"""
        from datetime import datetime, timedelta
        from config import config
        
        async with self.get_connection() as db:
            # Удаляем старые предупреждения
            expiry_date = datetime.now() - timedelta(days=config.WARNING_EXPIRY_DAYS)
            await db.execute(
                "DELETE FROM warnings WHERE group_id = ? AND user_id = ? AND warning_time < ?",
                (group_id, user_id, expiry_date)
            )
            
            # Добавляем новое
            await db.execute(
                "INSERT INTO warnings (group_id, user_id, warned_by, reason) VALUES (?, ?, ?, ?)",
                (group_id, user_id, warned_by, reason)
            )
            
            # Считаем количество
            cursor = await db.execute(
                "SELECT COUNT(*) as count FROM warnings WHERE group_id = ? AND user_id = ?",
                (group_id, user_id)
            )
            row = await cursor.fetchone()
            count = row["count"] if row else 0
            
            # Обновляем статистику
            await db.execute(
                "UPDATE stats SET warnings_given = warnings_given + 1 WHERE group_id = ?",
                (group_id,)
            )
            
            await db.commit()
            return count
    
    async def get_warnings_count(self, group_id: int, user_id: int) -> int:
        """Получение количества предупреждений"""
        from datetime import datetime, timedelta
        from config import config
        
        async with self.get_connection() as db:
            expiry_date = datetime.now() - timedelta(days=config.WARNING_EXPIRY_DAYS)
            cursor = await db.execute(
                "SELECT COUNT(*) as count FROM warnings WHERE group_id = ? AND user_id = ? AND warning_time > ?",
                (group_id, user_id, expiry_date)
            )
            row = await cursor.fetchone()
            return row["count"] if row else 0
    
    async def clear_warnings(self, group_id: int, user_id: int):
        """Очистка предупреждений"""
        async with self.get_connection() as db:
            await db.execute(
                "DELETE FROM warnings WHERE group_id = ? AND user_id = ?",
                (group_id, user_id)
            )
            await db.commit()
    
    # --- Методы для работы со статистикой ---
    
    async def increment_deleted_messages(self, group_id: int):
        """Увеличение счетчика удаленных сообщений"""
        async with self.get_connection() as db:
            await db.execute(
                "INSERT INTO stats (group_id, messages_deleted) VALUES (?, 1) "
                "ON CONFLICT(group_id) DO UPDATE SET messages_deleted = messages_deleted + 1",
                (group_id,)
            )
            await db.commit()
    
    async def increment_banned_users(self, group_id: int):
        """Увеличение счетчика забаненных пользователей"""
        async with self.get_connection() as db:
            await db.execute(
                "INSERT INTO stats (group_id, users_banned) VALUES (?, 1) "
                "ON CONFLICT(group_id) DO UPDATE SET users_banned = users_banned + 1",
                (group_id,)
            )
            await db.commit()
    
    async def get_stats(self, group_id: int) -> Dict:
        """Получение статистики"""
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT * FROM stats WHERE group_id = ?",
                (group_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return dict(row)
            else:
                return {
                    "group_id": group_id,
                    "messages_deleted": 0,
                    "users_banned": 0,
                    "warnings_given": 0
                }

    async def get_last_message_time(self, group_id: int, user_id: int):
        """Получение времени последнего сообщения пользователя"""
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT last_message_time FROM user_messages WHERE group_id = ? AND user_id = ?",
                (group_id, user_id)
            )
            row = await cursor.fetchone()
            if row:
                from datetime import datetime
                return datetime.fromisoformat(row["last_message_time"])
            return None      

# Создаем глобальный экземпляр
db = Database(config.DB_PATH)