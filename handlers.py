from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram_dialog import DialogManager
from loader import dp
from keyboard import lang_keyboard, lvl_keyboard, binary_keyboard
from stack import Stack
from states import DialogState
from utils import get_vacancy_message_text

@dp.message_handler(commands=["reset"])
async def reset_state(message: Message, state: FSMContext):
	await state.reset_state(with_data=True)
	await message.answer("State сброшен.")

@dp.message_handler(commands=['start', 'help'])
async def start(message: Message, state: FSMContext):
	await message.reply("test")
	print(f"State storage: {state.storage.__dict__}")

# Вывод вакансий по имеющемуся стеку

@dp.message_handler(Command('find'), state=Stack.finish)
async def find_vacancy(message: Message, state: FSMContext):
	data = await state.get_data()
	try:
		result = data['vacancies']
	except KeyError:
		result = get_vacancy_message_text(data)
	
	print(type(result))
	if not result:
		await message.answer("Подходящих вакансий нет")
	else:
		await state.update_data(
			{'vacancies': result[:len(result) - 1]}
		)
		await message.answer(result[len(result) - 1])
		if len(result) - 1 <= 0:
			await message.answer("Больше вакансий по данным параметрам нет")

@dp.message_handler(Command('find'), state=None)
async def send_to_stack_filling(message: Message):
	await message.answer("Пройдите опрос по команде /stack")

# Сборка стека для поиска вакансий


@dp.message_handler(commands=['stack'], state=None)
async def language(message: Message, dialog_manager: DialogManager):
	await dialog_manager.start(DialogState.choosing_technology)
	"""await message.answer("Язык", reply_markup=lang_keyboard)

	await Stack.language.set()"""

@dp.message_handler(Command('stack'), state=Stack.finish)
async def language_restart(message: Message, state: FSMContext):
	await state.finish()
	await message.answer("Язык", reply_markup=lang_keyboard)

	await Stack.language.set()

@dp.message_handler(state=Stack.language)
async def level(message: Message, state: FSMContext):
	lang = message.text
	await state.update_data(
			{'technologies': [lang]}
		)

	await message.answer("Технологии", reply_markup=ReplyKeyboardRemove())
	await Stack.next()

@dp.message_handler(state=Stack.technologies)
async def technologies(message: Message, state: FSMContext):
	new_technologies = message.text.split(', ')
	data = await state.get_data()
	old_technologies = data['technologies']
	old_technologies += new_technologies
	await state.update_data({"technologies": ", ".join(old_technologies)})
	await message.answer("Уровень", reply_markup=lvl_keyboard)
	await Stack.next()

@dp.message_handler(state=Stack.lvl)
async def location(message: Message, state: FSMContext):
	lvl = message.text
	await state.update_data(
			{'skill': lvl}
		)

	await message.answer("Локация", reply_markup=ReplyKeyboardRemove())
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
			{'relocation': reloc}
		)

	await message.answer("Минимальная зарплата", reply_markup=ReplyKeyboardRemove())
	await Stack.next()

@dp.message_handler(state=Stack.min_salary)
async def max_salary(message: Message, state: FSMContext):
	try:
		min_s = int(message.text)
		await state.update_data(
				{'min_salary': min_s}
			)

		await message.answer("Максимальная зарплата")
		await Stack.next()
	except ValueError:
		await message.answer("Недопустимое значение")

@dp.message_handler(state=Stack.max_salary)
async def final(message: Message, state: FSMContext):
	try:
		max_s = int(message.text)
		await state.update_data(
				{'max_salary': max_s}
			)

		data = await state.get_data()

		print(data)

		await message.answer("Записали")
		await Stack.next()
	except ValueError:
		await message.answer("Недопустимое значение")
    

# TODO: Показ нынешнего стека и замена одного на другой
@dp.message_handler(Command('showstack'))
async def show_stack(message: Message, state: FSMContext):
	data = await state.get_data()
	msg = f"""
Язык: {data['technologies'][0]}
Уровень: {data['skill']}
Технологии: {data['technologies'][1:]}
Локация: {data['location']}
ЗП: {data['min_salary']} - {data['max_salary']}
	"""

	await message.answer(msg)