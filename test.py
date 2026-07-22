from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

TOKEN = "8726682461:AAF-jQtrzNvqhmbdvwL179Rn1XhXj5AVU14"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("settings"))
async def settings(message: types.Message):
    print("🔴 КОМАНДА /settings СРАБОТАЛА!")
    await message.answer("✅ /settings РАБОТАЕТ!")

@dp.message()
async def all_messages(message: types.Message):
    print(f"🔍 ЛЮБОЕ СООБЩЕНИЕ: {message.text} от {message.from_user.id} в {message.chat.type}")
    await message.answer(f"Я ВИЖУ: {message.text}")

async def main():
    print("🚀 ТЕСТОВЫЙ БОТ ЗАПУЩЕН!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())