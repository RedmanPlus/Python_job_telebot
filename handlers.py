from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram_dialog import DialogManager
from loader import dp
from states import DialogState, PostDialogState, SearchVacancyState
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
	if min_salary == "Пропустить ввод зарплаты":
		await message.answer("Теперь введите, в каком городе искать вакансию")
		await PostDialogState.next()
	elif min_salary.isdigit():
		await state.update_data(
			{'salary_above': min_salary}
		)

		data = await state.get_data()
		await message.answer(f"Замечательно, мы будем искать вакансии с ЗП от {data['salary_above']}")
		await message.answer("Теперь введите, в каком городе искать вакансию, чтобы пропустить это шаг, напишите 'Не указывать' ")
		await PostDialogState.next()
	else:
		await message.answer("Тут нужно ввести число или пропустить шаг")

@dp.message_handler(state=PostDialogState.select_location)
async def select_location(message: Message, state: FSMContext):
	location = message.text

	if location != "Не указывать":
		await state.update_data(
			{'location': location}
		)

	data = await state.get_data()
	msg = "Отлично! Теперь мы будем искать вакансии по следующим параметрам:\n"
	for k, v in data.items():
		match k:
			case 'technologies':
				msg += f"Технологии: {v}" + "\n"
			case 'skill':
				msg += f"Уроевнь разработчика: {v}" + '\n'
			case 'remote':
				msg += f"Удаленно: {v}" + "\n"
			case 'relocation':
				msg += f"Релокация: {v}" + "\n"
			case 'max_salary_currency':
				msg += f"Валюта заработной платы: {v}" + "\n"
			case 'salary_above':
				msg += f"Зарплата от: {v}" + "\n"
			case 'location':
				msg += f"Локация: {v}" + "\n"	
	
	await message.answer(msg)
	await message.answer("Чтобы начать получать вакансии, просто пришлите мне команду /find")
	await PostDialogState.next()

@dp.message_handler(Command("f"), state=PostDialogState.final_state)
async def list_vacancy(message: Message, state: FSMContext, dialog_manager: DialogManager):
	print(f"WIDGET DATA IN HANDLER: {await state.get_data()}")
	print(dialog_manager)
	await dialog_manager.start(SearchVacancyState.searching_vacancy)
	dialog_manager.data['aiogd_context'].widget_data = await state.get_data()
	print(f"WIDGET DATA IN DIALOG MANAGER: {dialog_manager.data['aiogd_context'].widget_data}")

@dp.message_handler(Command('showstack'), state=PostDialogState.final_state)
async def show_stack(message: Message, state: FSMContext):
	data = await state.get_data()
	print(data)
	msg = f"""
Уровень: {data['skill']}
Технологии: {data['technologies']}
ЗП: от {data['salary_above']}
	"""

	await message.answer(msg)