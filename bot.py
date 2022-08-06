import logging
from aiogram import executor

from loader import bot, dp, storage


async def close(dp):
	await storage.close()
	await bot.close()

if __name__ == '__main__':
	from handlers import dp
	logging.basicConfig(level=logging.DEBUG)
	executor.start_polling(dp, on_shutdown=close)