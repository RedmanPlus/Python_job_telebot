import operator
import requests
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Radio, Button, Group, Multiselect, Back, Next ,Row
from aiogram_dialog.widgets.text import Format, Const
from states import DialogState, Stack
from keyboard import skip_salary_kbd
from utils import cancel
from filters import is_button_selected

cancel_button = Button(Const("❌ Отмена"), id='cancel', on_click=cancel)
back_button = Back(Const("⬅ Назад"))
#back_to_start_button = Button(Const("⬅ Назад"), id='back_to_start', on_click=erase_widget_data)
continue_button = Const("Продолжить ➡")
default_nav = Group(back_button, cancel_button, width=2)

async def get_technology(**kwargs):
    try:
        pagination_key = kwargs['aiogd_context'].widget_data['navigate_vacancy_button']
    except KeyError:
        kwargs['aiogd_context'].widget_data['navigate_vacancy_button'] = 1
        pagination_key = 1
    params = {}
    json = requests.get(f"https://devseye.ru/api/technology?page={pagination_key}",
                       params=params).json()
    technology = [tech['name'] for tech in json['results']]
    technology_list = [(item, item)
                    for item in technology]
    return {'technology': technology_list}

async def get_lvl(**kwargs):
    return {'lvl': [(item, item) for item in ('Intern', 'Junior', 
                                              'Middle', 'Team Lead',
                                              'Не указан')]}

async def get_binary_options(**kwargs):
    return {'binary': [(item, item) for item in ('Да', 'Нет')]}

async def get_currency(**kwargs):
    return {"currency": [(item, item) for item in ('RUB', 'USD', 'EUR')]}

async def switch_page(c: CallbackQuery, b: Button, d: DialogManager):
    pagination_key = d.data['aiogd_context'].widget_data['navigate_vacancy_button']
    if b.widget_id == "next_tech":
        pagination_key += 1
    elif b.widget_id == "prev_tech":
        if pagination_key > 1:
           pagination_key -= 1
        elif pagination_key == 1:
            await c.answer("Дальше технологий нет😕")
    d.data['aiogd_context'].widget_data['navigate_vacancy_button'] = pagination_key
    await d.switch_to(DialogState.select_technology)

    
@is_button_selected(key='m_tech')
async def switch_to_lvl(c: CallbackQuery, b: Button, d: DialogManager):
    dialog_data = d.data['aiogd_context'].widget_data['m_tech']
    await c.message.delete()
    await c.message.answer(f"Вы выбрали следующие технологии: {', '.join(dialog_data)}")
    await d.switch_to(DialogState.select_lvl)

@is_button_selected(key='r_lvl')
async def switch_to_remote(c: CallbackQuery, b: Button, d: DialogManager):
    await d.switch_to(DialogState.select_remote)

async def switch_to_relocation(c: CallbackQuery, b: Button, d: DialogManager):
    await d.switch_to(DialogState.select_relocation)

async def switch_to_currency(c: CallbackQuery, b: Button, d: DialogManager):
    await d.switch_to(DialogState.select_currency)

@is_button_selected(key='r_currency')
async def switch_to_min_salary(c: CallbackQuery, b: Button, d: DialogManager):
    widget_data = d.data['aiogd_context'].widget_data
    tech = ', '.join(widget_data['m_tech'])
    lvl = widget_data['r_lvl']
    remote = widget_data['r_remote']
    relocation = widget_data['r_relocation']
    currency = widget_data['r_currency']
    await d.data['state'].update_data({"technologies": tech, "skill": lvl,
                                       "remote": True if remote == "Да" else False, 
                                       "relocation": True if relocation == "Да" else False,
                                       "max_salary_currency": currency})
    await c.message.delete()
    await c.message.answer(f"""Следующие параметры поиска:
Технологии: {tech}
Уровень разработчика: {lvl}
Удаленно: {remote if remote else "Не указано"}
Релокация:{relocation if relocation else "Не указано"}
Валюта зарплаты: {currency}""")
    await c.message.answer("Напишите минимальную зарплату в числовом формате (например, 50000)",
    reply_markup=skip_salary_kbd)
    await d.mark_closed()
    await Stack.min_salary.set()

 
technology_keyboard = Window(Const("Выберите технологии:"),
                          Group(Multiselect(Format("✅ {item[0]}"),
                                            Format("🔘 {item[0]}"),
                                      id="m_tech", items='technology',
                                      item_id_getter=operator.itemgetter(1)),
                                Button(Const("<"), on_click=switch_page, id="prev_tech"),
                                Button(Const(">"), on_click=switch_page, id="next_tech"),
                                width=2),
                          
                          Button(continue_button,
                                 on_click=switch_to_lvl,
                                 id='continue'),
                          default_nav,
                          getter=get_technology,
                          state=DialogState.select_technology)

level_keyboard = Window(Const("Выбери подходящий уровень:"),
                          Group(Radio(Format("✅ {item[0]}"),
                                      Format("🔘 {item[0]}"),
                                      id="r_lvl", items='lvl',
                                      item_id_getter=operator.itemgetter(1)),
                                width=2),
                          Button(continue_button,
                                 on_click=switch_to_remote,
                                 id='continue'),
                          default_nav,
                          getter=get_lvl,
                          state=DialogState.select_lvl)

binary_widget = Group(Radio(Format("✅ {item[0]}"),
                            Format("🔘 {item[0]}"),
                                      id="r_binary", items='binary',
                                      item_id_getter=operator.itemgetter(1)),
                                width=2)

remote_keyboard = Window(Const("Удаленно? (Можно пропустить)"),
                         Group(Radio(Format("✅ {item[0]}"),
                            Format("🔘 {item[0]}"),
                                      id="r_remote", items='binary',
                                      item_id_getter=operator.itemgetter(1)),
                                width=2),
                         Button(continue_button, on_click=switch_to_relocation, id='continue'),
                         default_nav,
                         getter=get_binary_options,
                         state=DialogState.select_remote)

relocation_keyboard = Window(Const("Релокация? (Можно пропустить)"), 
                         Group(Radio(Format("✅ {item[0]}"),
                            Format("🔘 {item[0]}"),
                                      id="r_relocation", items='binary',
                                      item_id_getter=operator.itemgetter(1)),
                                width=2),
                         Button(continue_button, on_click=switch_to_currency, id='continue'),
                         default_nav,
                         getter=get_binary_options,
                         state=DialogState.select_relocation)

currency_keyboard = Window(Const("В какой валюте заработная плата?"),
                            Group(Radio(Format("✅ {item[0]}"),
                            Format("🔘 {item[0]}"),
                                      id="r_currency", items='currency',
                                      item_id_getter=operator.itemgetter(1)),
                                width=2),
                         Button(continue_button, on_click=switch_to_min_salary, id='continue'),
                         default_nav,
                         getter=get_currency,
                         state=DialogState.select_currency)

dialog = Dialog(technology_keyboard, level_keyboard, 
                remote_keyboard, relocation_keyboard, 
                currency_keyboard)