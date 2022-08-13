from aiogram.dispatcher.filters.state import StatesGroup, State

class Stack(StatesGroup):
	language = State()
	technologies = State()
	lvl = State()
	location = State()
	remote = State()
	relocation = State()
	min_salary = State()
	max_salary = State()
	finish = State()

class DialogState(StatesGroup):
	select_technology = State()
	select_lvl = State()
	select_remote = State()
	select_relocation = State()
	select_currency = State()