from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

lang_keyboard = ReplyKeyboardMarkup(
	keyboard=[
		[
			KeyboardButton(text="a"),
			KeyboardButton(text="b")
		], [
			KeyboardButton(text="c")
		]
	],
	resize_keyboard=True
)

lvl_keyboard = ReplyKeyboardMarkup(
	keyboard=[
		[
			KeyboardButton(text="1"),
			KeyboardButton(text="2"),
		], [
			KeyboardButton(text="3"),
			KeyboardButton(text="4"),
		]
	],
	resize_keyboard=True
)

binary_keyboard = ReplyKeyboardMarkup(
	keyboard=[
		[
			KeyboardButton(text="Да"),
			KeyboardButton(text="Нет"),
		]
	],
	resize_keyboard=True
)