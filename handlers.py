from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram_dialog import DialogManager, StartMode
from db.models import User
from loader import dp, bot
from states import DialogState, PostDialogState, SearchVacancyState
from config import CHANNELS
from filters import is_user_subscribed

@dp.message_handler(Command('contacts'))
async def send_contact(message: Message):
    await message.answer("""<strong>Каналы с вакансиями:</strong> <a href="https://t.me/best_ITjob?utm_source=devseye_bot">ITJOBS</a>
<strong>По вопросам рекламы:</strong> <a href="https://t.me/chri_grafova">Christina Grafova</a>
<strong>По вопросам сотрудничества:</strong> <a href="https://t.me/egormk">egormk</a>
<strong>Разработчики:</strong>
<a href="https://t.me/arseny_chebyshev">Арсений Чебышев</a>
<a href="https://t.me/redman_plus">Антон Румянцев</a>""")

@dp.callback_query_handler(lambda c: c.data.startswith('check'))
async def answer_callback(query: CallbackQuery, dialog_manager: DialogManager):
    if await is_user_subscribed(CHANNELS.keys(), query.from_user.id):
        await query.answer("Благодарим за подписку!")
        await dialog_manager.start(DialogState.start)
    else:
        text = "Перед тем, как использовать бота, пожалуйста, подпишись на один из наших каналов:\n"
        inline_kbd = InlineKeyboardMarkup(row_width=1)
        [inline_kbd.add(InlineKeyboardButton(text=f"{(await bot.get_chat(channel))['title']}", url=invite_link)) 
    					for channel, invite_link in CHANNELS.items()]
        inline_kbd.add(InlineKeyboardButton(text="✅Я подписался", callback_data='check_sub'))
        await query.message.delete()
        await query.message.answer(text, reply_markup=inline_kbd)

@dp.message_handler(commands=['start', 'help'])
async def start(message: Message, state: FSMContext):
    user_dict = {k: v for k ,v in dict(message.from_user).items() 
	             if k in [field.name for field in User._meta.get_fields()]}
    user = User.objects.filter(id=user_dict['id']).first()
    if not user:
        user = User.objects.create(**user_dict)
    await message.answer(f"""Привет, {user.first_name}👋! Я помогаю найти работу разработчикам ПО. 
Пройди опрос по команде /stack и я пришлю подходящие вакансии""")
    

@dp.message_handler(commands=['app'])
async def open_webapp(message: Message):
	await message.answer(
        "Нажми на кнопку, чтобы открыть приложение:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Открыть", web_app=WebAppInfo(url=f"https://devseye.ru"))]
				]
        ),
    )

@dp.message_handler(commands=['stack'], state=None)
async def language(message: Message, dialog_manager: DialogManager):
    if await is_user_subscribed(CHANNELS.keys(), message.from_user.id):
        await dialog_manager.start(DialogState.start)
    else:
        text = "Перед тем, как использовать бота, пожалуйста, подпишись на один из наших каналов:\n"
        inline_kbd = InlineKeyboardMarkup(row_width=1)
        [inline_kbd.add(InlineKeyboardButton(text=f"{(await bot.get_chat(channel))['title']}", url=invite_link)) 
						for channel, invite_link in CHANNELS.items()]
        inline_kbd.add(InlineKeyboardButton(text="✅Я подписался", callback_data='check_sub'))
        await message.answer(text, reply_markup=inline_kbd)


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
				msg += f'{f"Зарплата от: {v}" if int(v) > 0 else ""}' + "\n"
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
