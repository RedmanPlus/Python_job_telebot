from aiogram.dispatcher.filters.state import StatesGroup, State

class DialogState(StatesGroup):
	select_technology = State()
	select_lvl = State()
	select_remote = State()
	select_relocation = State()
	select_currency = State()

class PostDialogState(StatesGroup):
	select_min_salary = State()
	select_max_salary = State()
	select_location = State()
	final_state = State()