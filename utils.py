import traceback
import requests
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from serializers import Vacancy
from db.models import User

def get_vacancies_json(params: dict):
    response = requests.get("https://devseye.ru/api/vacancy", params=params)
    return response.json()

def get_vacancy_message_text(params: dict) -> list:
    response = get_vacancies_json(params)
    print(f'\n\n\n\nParams: {params}\n\n\n\n')
    try:
        vacancies = [Vacancy(vac_dct) for vac_dct in response['results']]
        if len(vacancies) < 1:
            return ["Нет вакансий с заданными параметрами 🤔"]
    except KeyError:
        return ["Больше вакансий с такими параметрами нет 🤔"]
    return_lst = [f"""
<strong>Дата публикации:</strong> {vacancy.datetime.date()}
<strong>Роль:</strong> {vacancy.role}
<strong>Ключевые навыки, указанные в описании:</strong> {', '.join(vacancy.technologies)}
<strong>Зарплата:</strong> от {vacancy.min_salary} до {vacancy.max_salary} {vacancy.salary_currency}
<strong>Описание:</strong> 
{vacancy.desc}
<strong>Задачи:</strong> 
{vacancy.tasks}
<strong>Требования:</strong> 
{vacancy.requirements}
<strong>Ссылка:</strong> https://t.me/{vacancy.channel}/{vacancy.message_id}?utm_source=devseye_bot
""" 
    for vacancy in vacancies]
    return return_lst

async def cancel(c: CallbackQuery, b: Button, d: DialogManager):
    await c.message.delete()
    await c.message.answer(text=f"Действие отменено.")
    await d.mark_closed()
    await d.data['state'].reset_state(with_data=True)
    
async def send_mailing(bot, text: str):
    users = User.objects.filter(is_admin=False)
    async for user in users:
        try:
            await bot.send_message(user.id, text)
        except:
            traceback.print_exc()

