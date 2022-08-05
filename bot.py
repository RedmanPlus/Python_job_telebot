import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TOKEN

loop = asyncio.new_event_loop()
bot = Bot(token=TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, loop=loop, storage=storage)

async def close(dp):
	await storage.close()
	await bot.close()

if __name__ == '__main__':
	from handlers import dp
	executor.start_polling(dp, on_shutdown=close)