from aiogram import Dispatcher
from .start import router as start_router
from .settings import router as settings_router
from .admin import router as admin_router
from .moderation import router as moderation_router
from .members import router as members_router
from .stats import router as stats_router
from .callback import router as callback_router

def setup_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    dp.include_router(start_router)
    dp.include_router(settings_router)  # settings ПЕРВЫЙ
    dp.include_router(stats_router)     # stats ВТОРОЙ
    dp.include_router(admin_router)
    dp.include_router(moderation_router)
    dp.include_router(members_router)
    dp.include_router(callback_router)