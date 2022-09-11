from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram_dialog import DialogManager
from loader import dp
from states import DialogState, PostDialogState, SearchVacancyState
from config import CHANNELS_FOR_SUB
from filters import is_user_subscribed

@dp.message_handler(commands=['start', 'help'])
async def start(message: Message, state: FSMContext):
    await message.answer("""Привет👋! Я помогаю найти работу разработчикам ПО. 
Пройди опрос по команде /stack и я пришлю подходящие вакансии""")

@dp.message_handler(commands=['stack'], state=None)
async def language(message: Message, dialog_manager: DialogManager):
    if is_user_subscribed(CHANNELS_FOR_SUB, message.from_user.id):
        await dialog_manager.start(DialogState.select_technology)
    else:
        await message.answer('Необходимо подписаться на канал')

@dp.message_handler(Command('stack'), state=PostDialogState.final_state)
async def language_restart(message: Message, state: FSMContext, dialog_manager: DialogManager):
	await state.finish()
	await dialog_manager.start(DialogState.select_technology)

@dp.message_handler(state=PostDialogState.select_min_salary)
async def select_min_salary(message: Message, state: FSMContext):
	min_salary = message.text
	if min_salary.isdigit():
		await state.update_data({'salary_above': min_salary})
		await message.answer(f"Замечательно, будем искать вакансии с зарплатой от {min_salary}")
		await message.answer("Теперь введи, в каком городе искать вакансию. Чтобы пропустить это шаг, напиши '-' ")
		await PostDialogState.next()
	else:
		await message.answer("Тут нужно ввести число или пропустить шаг")

@dp.message_handler(state=PostDialogState.select_location)
async def select_location(message: Message, state: FSMContext):
	location = message.text
	if location != "-":
		await state.update_data({'location': location})
	data = await state.get_data()
	msg = "Отлично! Теперь будем искать вакансии по следующим параметрам:\n"
	for k, v in data.items():
		match k:
			case 'technologies':
				msg += f"Технологии: {v}" + "\n"
			case 'skill':
				msg += f"Уровень разработчика: {v}" + '\n'
			case 'remote':
				msg += f"Удаленно: {'Да' if v else 'Нет'}" + "\n"
			case 'relocation':
				msg += f"Релокация: {'Да' if v else 'Нет'}" + "\n"
			case 'max_salary_currency':
				msg += f"Валюта заработной платы: {v}" + "\n"
			case 'salary_above':
				msg += f"Зарплата от: {v}" + "\n"
			case 'location':
				msg += f"Локация: {v}" + "\n"	
	
	await message.answer(msg)
	await message.answer("Чтобы начать получать вакансии, просто пришли мне команду /find")
	await PostDialogState.next()

@dp.message_handler(Command("find"), state=PostDialogState.final_state)
async def list_vacancy(message: Message, state: FSMContext, dialog_manager: DialogManager):
	await dialog_manager.start(SearchVacancyState.searching_vacancy)

@dp.message_handler(Command('find'), state=None)
async def send_to_stack_filling(message: Message):
	await message.answer("Пройди опрос по команде /stack")
