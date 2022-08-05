from aiogram.dispatcher.filters.state import StatesGroup, State

class Stack(StatesGroup):
	language = State()
	lvl = State()
	stack = State()
	location = State()
	remote = State()
	relocation = State()
	min_salary = State()
	max_salary = State()
