from aiogram import Bot, Dispatcher
from aiogram_dialog import DialogRegistry
# from aiogram.contrib.fsm_storage.redis import RedisStorage2 - пока redis не нужен - комментим ненужную зависимость
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN
from dialog_kbds import query_dialog, vacancy_dialog, admin_dialog

bot = Bot(token=TOKEN, parse_mode="HTML")
storage = MemoryStorage()
#storage = RedisStorage2(host="127.0.0.1", port="6379")
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)
registry.register(query_dialog) 
registry.register(vacancy_dialog)
registry.register(admin_dialog)