import requests
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

def get_vacancies_json(params: dict):
    params['limit'] = 500
    print(f"params: {params}")
    response = requests.get("https://devseye.ru/api/vacancy", params=params)
    return response.json()

def get_vacancy_message_text(params: dict) -> str:
    response = get_vacancies_json(params)
    print(response)
    print(f"Launching get_vacancy_message_text with params {params}")
    vacancies = response['results']
    return_lst = [f"""
Роль: {vacancy['role']}
Локация: {vacancy['location']}
З/П: {vacancy['min_salary']} - {vacancy['max_salary']}

{vacancy['desc']}
    """ for vacancy in vacancies]
    print(f"Return list: {return_lst}")
    return return_lst

async def cancel(c: CallbackQuery, b: Button, d: DialogManager):
    await c.message.delete()
    await c.message.answer(text=f"Действие отменено.")
    await d.mark_closed()
    await d.data['state'].reset_state(with_data=True)
    