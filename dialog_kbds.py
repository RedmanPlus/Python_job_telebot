import operator
import requests
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Radio, Button, Group, Multiselect, Back, Next ,Row
from aiogram_dialog.widgets.text import Format, Const
from states import DialogState, PostDialogState, SearchVacancyState
from utils import cancel, get_vacancy_message_text

cancel_button = Button(Const("❌ Отмена"), id='cancel', on_click=cancel)
back_button = Back(Const("⬅ Назад"))
continue_button = Const("Продолжить ➡")
default_nav = Group(back_button, cancel_button, width=2)

def is_button_selected(key: str = None):
    def wrapper(async_func):
        async def _wrapper(c: CallbackQuery, b: Button, d: DialogManager):
            if key in d.data['aiogd_context'].widget_data.keys():
                await async_func(c, b, d)
            else:
                await c.answer("Сначала нужно выбрать хотя бы одну из опций")
        return _wrapper
    return wrapper

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
    return {'binary': [(item, item) for item in ('Да', 'Нет', 'Пропустить')]}

async def get_currency(**kwargs):
    return {"currency": [(item, item) for item in ('RUB', 'USD', 'EUR', 'Пропустить')]}

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
    if dialog_data:
        await c.message.answer(f"Вы выбрали следующие технологии: {', '.join(dialog_data)}")
    await d.switch_to(DialogState.select_lvl)

@is_button_selected(key='r_lvl')
async def switch_to_remote(c: CallbackQuery, b: Button, d: DialogManager):
    dialog_data = d.data['aiogd_context'].widget_data['r_lvl']
    await c.message.delete()
    if dialog_data:
        await c.message.answer(f"Вы выбрали следующий уровень: {dialog_data}")
    await d.switch_to(DialogState.select_remote)

@is_button_selected(key='r_remote')
async def switch_to_relocation(c: CallbackQuery, b: Button, d: DialogManager):
    await d.switch_to(DialogState.select_relocation)

@is_button_selected(key='r_relocation')
async def switch_to_currency(c: CallbackQuery, b: Button, d: DialogManager):
    await d.switch_to(DialogState.select_currency)

@is_button_selected(key='r_currency')
async def switch_to_min_salary(c: CallbackQuery, b: Button, d: DialogManager):
    widget_data = d.data['aiogd_context'].widget_data
    tech = ', '.join(widget_data['m_tech'])
    lvl = widget_data['r_lvl'] if ((widget_data['r_lvl'] != "Не указан") or (widget_data['r_lvl'] != None)) else None
    remote = widget_data['r_remote'] if ((widget_data['r_currency'] != "Пропустить") and (widget_data['r_currency'] != None)) else None
    relocation = widget_data['r_relocation'] if ((widget_data['r_relocation'] != "Пропустить") and (widget_data['r_relocation'] != None)) else None
    currency = widget_data['r_currency'] if ((widget_data['r_currency'] != "Пропустить") and (widget_data['r_currency'] != None)) else None
    
    if lvl and lvl != 'Не указан':
        await d.data['state'].update_data({"skill": lvl})
    if remote:
        await d.data['state'].update_data({"remote":True if remote == "Да" else False})
    if relocation:
        await d.data['state'].update_data({"relocation":True if remote == "Да" else False})
    if currency:
        await d.data['state'].update_data({"max_salary_currency": currency})
    if tech:
        await d.data['state'].update_data({"technologies": tech})
    
    await c.message.delete()
    await c.message.answer(f"""Следующие параметры поиска:
Технологии: {tech if tech else 'Не указаны'}
Уровень разработчика: {lvl if ((lvl != "Не указан") and (lvl != None)) else 'Не указан'}
Удаленно: {remote if ((remote != "Пропустить") and (remote != None)) else "Не указано"}
Релокация: {relocation if ((relocation != "Пропустить") and (relocation != None)) else "Не указана"}
Валюта зарплаты: {currency if ((currency != "Пропустить") and (currency != None)) else "Не указана"}""")
    await c.message.answer("Напиши минимальную зарплату в числовом формате (например, 50000). Если не важна - напиши 0")
    await d.mark_closed()
    await PostDialogState.select_min_salary.set()

 
technology_keyboard = Window(Const("Выбери технологии:"),
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
                             cancel_button,
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

remote_keyboard = Window(Const("Удаленно?"),
                         Group(Radio(Format("✅ {item[0]}"),
                            Format("🔘 {item[0]}"),
                                      id="r_remote", items='binary',
                                      item_id_getter=operator.itemgetter(1)),
                                width=2),
                         Button(continue_button, on_click=switch_to_relocation, id='continue'),
                         default_nav,
                         getter=get_binary_options,
                         state=DialogState.select_remote)

relocation_keyboard = Window(Const("Релокация?"), 
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

query_dialog = Dialog(technology_keyboard, level_keyboard, 
                remote_keyboard, relocation_keyboard, 
                currency_keyboard)

async def get_vacancy(**kwargs):
    try:
        pagination_key = (await kwargs['dialog_manager'].data['state'].get_data())['page']
    except KeyError:
        pagination_key = 1
        await kwargs['dialog_manager'].data['state'].update_data({'page': pagination_key})
    params = await kwargs['dialog_manager'].data['state'].get_data()
    if int(params['salary_above']) == 0:
        params.pop('salary_above')
    params['limit'] = 1
    return {"vacancy": get_vacancy_message_text(params=params)[0]}

async def switch_vacancy(c: CallbackQuery, b: Button, d: DialogManager):
    pagination_key = (await d.data['state'].get_data())['page']
    match b.widget_id:
        case "next_vac":
            pagination_key += 1
        case "prev_vac":
            if pagination_key > 1:
               pagination_key -= 1
            elif pagination_key == 1:
                await c.answer("Дальше вакансий нет😕")
    await d.data['state'].update_data({"page": pagination_key})
    await d.switch_to(SearchVacancyState.searching_vacancy)

vacancy_keyboard = Window(Format(text="{vacancy}"),
                             Group(Button(Const("<"), on_click=switch_vacancy, id="prev_vac"),
                                   Button(Const(">"), on_click=switch_vacancy, id="next_vac"),
                                   width=2),
                          cancel_button,
                      getter=get_vacancy,
                      state=SearchVacancyState.searching_vacancy)

vacancy_dialog = Dialog(vacancy_keyboard)