from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

skip_salary_kbd = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Пропустить ввод зарплаты")]], 
                                      one_time_keyboard=True, resize_keyboard=True)


binary_keyboard = ReplyKeyboardMarkup(
	keyboard=[
		[
			KeyboardButton(text="Да"),
			KeyboardButton(text="Нет"),
		]
	],
	resize_keyboard=True
)

confirm_keyboard = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text="✅Подтвердить рассылку"),
		 KeyboardButton(text="❌Отменить")]
	],
	resize_keyboard=True, one_time_keyboard=True
)