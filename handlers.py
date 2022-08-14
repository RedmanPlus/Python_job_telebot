from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram_dialog import DialogManager
from loader import dp
from keyboard import lang_keyboard, lvl_keyboard, binary_keyboard
from states import DialogState, PostDialogState
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

@dp.message_handler(Command('find'), state=PostDialogState.final_state)
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
	await dialog_manager.start(DialogState.select_technology)

@dp.message_handler(Command('stack'), state=PostDialogState.final_state)
async def language_restart(message: Message, state: FSMContext, dialog_manager: DialogManager):
	await state.finish()
	
	await dialog_manager.start(DialogState.select_technology)

@dp.message_handler(state=PostDialogState.select_min_salary)
async def select_min_salary(message: Message, state: FSMContext):
	min_salary = message.text
	await state.update_data(
		{'min_salary': min_salary}
	)

	await message.answer("Теперь введите максимальную желаемую зарплату")
	await PostDialogState.next()

@dp.message_handler(state=PostDialogState.select_max_salary)
async def select_max_salary(message: Message, state: FSMContext):
	max_salary = message.text
	await state.update_data(
		{'max_salary': max_salary}
	)

	data = await state.get_data()
	await message.answer(f"""Замечательно, мы будем искать вакансии с ЗП 
							в диапозоне {data['min_salary']}-{data['max_salary']}""")
	await message.answer("Теперь введите, в каком городе искать вакансию")
	await PostDialogState.next()

@dp.message_handler(state=PostDialogState.select_location)
async def select_location(message: Message, state: FSMContext):
	location = message.text
	await state.update_data(
		{'location': location}
	)

	data = await state.get_data()
	await message.answer(f"""
Все готово!
Теперь мы будем искать для вас вакансии по следующим параметрам:
Технологии: {data['technologies']}
Уровень разработчика: {data['skill']}
Удаленно: {data['remote']}
С релокацией: {data['relocation']}
Зарплата в {data['max_salary_currency']}
От {data['min_salary']} до {data['max_salary']}
В городе {data['location']}
	""")
	await message.answer("Чтобы начать получать вакансии, просто пришлите мне команду /find")
	await PostDialogState.next()

# TODO: Показ нынешнего стека и замена одного на другой
@dp.message_handler(Command('showstack'), state=PostDialogState.final_state)
async def show_stack(message: Message, state: FSMContext):
	data = await state.get_data()
	print(data)
	msg = f"""
Уровень: {data['skill']}
Технологии: {data['technology']}
ЗП: {data['min_salary']} - {data['max_salary']}
	"""

	await message.answer(msg)