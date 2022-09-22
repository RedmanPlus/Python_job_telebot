from aiogram.dispatcher.filters.state import StatesGroup, State

class DialogState(StatesGroup):
	start = State()
	select_technology = State()
	select_lvl = State()
	select_remote = State()
	select_relocation = State()
	select_currency = State()

class PostDialogState(StatesGroup):
	select_min_salary = State()
	select_location = State()
	final_state = State()

class SearchVacancyState(StatesGroup):
	searching_vacancy = State()
	finished_searching = State()