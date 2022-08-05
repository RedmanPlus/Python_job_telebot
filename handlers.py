from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command 

from bot import bot, dp
from keyboard import lang_keyboard, lvl_keyboard, binary_keyboard
from stack import Stack

@dp.message_handler(commands=['start', 'help'])
async def start(message: Message):
	await message.reply("test")

# Вывод вакансий по имеющемуся стеку

@dp.message_handler(Command('find'))
async def find_vacancy(message: Message):
	await message.answer("heyyyy")

# Сборка стека для поиска вакансий

@dp.message_handler(Command('stack'), state=None)
async def language(message: Message):
	await message.answer("Язык", reply_markup=lang_keyboard)

	await Stack.language.set()

@dp.message_handler(state=Stack.language)
async def level(message: Message, state: FSMContext):
	lang = message.text
	await state.update_data(
			{'language': lang}
		)

	await message.answer("Уровень", reply_markup=lvl_keyboard)
	await Stack.next()

@dp.message_handler(state=Stack.lvl)
async def stack(message: Message, state: FSMContext):
	lvl = message.text
	await state.update_data(
			{'level': lvl}
		)

	await message.answer("Технологии", reply_markup=ReplyKeyboardRemove())
	await Stack.next()

@dp.message_handler(state=Stack.stack)
async def location(message: Message, state: FSMContext):
	stack = message.text.split()
	await state.update_data(
			{'stack': stack}
		)

	await message.answer("Локация")
	await Stack.next()

@dp.message_handler(state=Stack.location)
async def remote(message: Message, state: FSMContext):
	loc = message.text
	await state.update_data(
			{'location': loc}
		)

	await message.answer("Удаленно", reply_markup=binary_keyboard)
	await Stack.next()

@dp.message_handler(state=Stack.remote)
async def relocation(message: Message, state: FSMContext):
	remote = message.text
	if remote == "Да":
		remote = True
	elif remote == "Нет":
		remote = False

	await state.update_data(
			{'remote': remote}
		)

	await message.answer("Релокация", reply_markup=binary_keyboard)
	await Stack.next()

@dp.message_handler(state=Stack.relocation)
async def min_salary(message: Message, state: FSMContext):
	reloc = message.text
	if reloc == "Да":
		reloc = True
	elif reloc == "Нет":
		reloc = False

	await state.update_data(
			{'reloc': reloc}
		)

	await message.answer("Минимальная зарплата", reply_markup=ReplyKeyboardRemove())
	await Stack.next()

@dp.message_handler(state=Stack.min_salary)
async def max_salary(message: Message, state: FSMContext):
	min_s = int(message.text)
	await state.update_data(
			{'min_salary': min_s}
		)

	await message.answer("Максимальная зарплата")
	await Stack.next()

@dp.message_handler(state=Stack.max_salary)
async def final(message: Message, state: FSMContext):
	max_s = int(message.text)
	await state.update_data(
			{'max_salary': max_s}
		)

	data = await state.get_data()

	print(data)

	await message.answer("Записали")
	await state.finish()

# TODO: Показ нынешнего стека и замена одного на другой