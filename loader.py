from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from config import TOKEN

bot = Bot(token=TOKEN, parse_mode="HTML")
storage = RedisStorage2(host="127.0.0.1", port="6379")
dp = Dispatcher(bot, storage=storage)