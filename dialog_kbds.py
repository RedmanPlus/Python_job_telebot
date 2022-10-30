import operator
import requests
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Radio, Button, Group, Multiselect, Back, Next ,Row
from aiogram_dialog.widgets.text import Format, Const
from db.models import User
from states import AdminState, DialogState, PostDialogState, SearchVacancyState, AdminDialog
from utils import cancel, get_vacancy_message_text
from filters import is_button_selected

cancel_button = Button(Const("❌ Отмена"), id='cancel', on_click=cancel)
back_button = Back(Const("⬅ Назад"))
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
    try:
        technology = [tech['name'] for tech in json['results']]
        technology_list = [(item, item) for item in technology if int(len(item.encode('utf-8')) <= 52)]
    except KeyError:
        return {"technology": [], "empty": True}
    return {'technology': technology_list}

async def get_role(**kwargs):
    try:
        pagination_key = kwargs['aiogd_context'].widget_data['navigate_vacancy_button']
    except KeyError:
        kwargs['aiogd_context'].widget_data['navigate_vacancy_button'] = 1
        pagination_key = 1
    params = {}
    if kwargs['aiogd_context'].widget_data.get('no_code', None):
        params.update({'group': 'NoCode'})
    json = requests.get(f"https://devseye.ru/api/role?page={pagination_key}",
                       params=params).json()
    try:
        role = [role['name'] for role in json['results']]
        role_list = [(item, item) for item in role if int(len(item.encode('utf-8')) <= 52)]
    except KeyError:
        return {"role": [], "empty": True}                   
    return {'role': role_list}

async def get_lvl(**kwargs):
    dct = {'lvl': [(item, item) for item in ('Intern', 'Junior', 
                                              'Middle', 'Team Lead',
                                              'Не указан')], 
           'code': True}
    if 'no_code' in kwargs['aiogd_context'].widget_data.keys():
        dct['code'] = False
        dct.update({"no_code": True})
    return dct
    

async def get_binary_options(**kwargs):
    dct = {'binary': [(item, item) for item in ('Да', 'Нет', 'Пропустить')], "code": True}
    if 'no_code' in kwargs['aiogd_context'].widget_data.keys():
        dct['code'] = False
        dct.update({"no_code": True})
    return dct

async def get_currency(**kwargs):
    return {"currency": [(item, item) for item in ('RUB', 'USD', 'EUR', 'Пропустить')]}

async def switch_page(c: CallbackQuery, b: Button, d: DialogManager):
    pagination_key = d.data['aiogd_context'].widget_data['navigate_vacancy_button']
    if b.widget_id == "next_page":
        pagination_key += 1
    elif b.widget_id == "prev_page":
        if pagination_key > 1:
           pagination_key -= 1
        elif pagination_key == 1:
            await c.answer("Дальше ничего нет😕")
    d.data['aiogd_context'].widget_data['navigate_vacancy_button'] = pagination_key
    if 'no_code' in d.data['aiogd_context'].widget_data.keys():
        await d.switch_to(DialogState.select_role)
    else:
        await d.switch_to(DialogState.select_technology)

    
@is_button_selected(key='m_tech')
async def switch_to_lvl(c: CallbackQuery, b: Button, d: DialogManager):
    dialog_data = d.data['aiogd_context'].widget_data['m_tech']
    await c.message.delete()
    if dialog_data:
        await c.message.answer(f"Ты выбрал следующие технологии: {', '.join(dialog_data)}")
    await d.switch_to(DialogState.select_lvl)

async def switch_to_role(c: CallbackQuery, b: Button, d: DialogManager):
    if b.widget_id == 'no_code':
        d.data['aiogd_context'].widget_data['no_code'] = True
    await d.switch_to(DialogState.select_role)

async def switch_to_remote(c: CallbackQuery, b: Button, d: DialogManager):
    if not b.widget_id == 'no_code':
        dialog_data = d.data['aiogd_context'].widget_data['r_lvl']
        await c.message.delete()
        if dialog_data:
            await c.message.answer(f"Ты выбрал следующий уровень: {dialog_data}")
    else:
        await d.data['state'].update_data({'channel_id': 'itjobs_nocode'})
        d.data['aiogd_context'].widget_data['no_code'] = True
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
    tech = ', '.join(widget_data['m_tech']) if 'm_tech' in widget_data.keys() else None
    if 'r_lvl' in widget_data.keys():
        lvl = widget_data['r_lvl'] if widget_data['r_lvl'] != "Не указан" else None
    else:
        lvl = None
    role = widget_data.get('r_role', None)
    remote = widget_data['r_remote'] if ((widget_data['r_currency'] != "Пропустить") and (widget_data['r_currency'] != None)) else None
    relocation = widget_data['r_relocation'] if ((widget_data['r_relocation'] != "Пропустить") and (widget_data['r_relocation'] != None)) else None
    currency = widget_data['r_currency'] if ((widget_data['r_currency'] != "Пропустить") and (widget_data['r_currency'] != None)) else None
    
    if lvl:
        await d.data['state'].update_data({"skill": lvl})
    if role:
        await d.data['state'].update_data({"role": role})
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
{f'Позиция: {role}' if role else ''}
{f'Уровень компетенции (грейд): {lvl}' if ((lvl != "Не указан") and (lvl != None)) else ''}
{f'Технологии: {tech}' if tech else ''}
Удаленно: {remote if ((remote != "Пропустить") and (remote != None)) else "Не указано"}
Релокация: {relocation if ((relocation != "Пропустить") and (relocation != None)) else "Не указана"}
Валюта зарплаты: {currency if ((currency != "Пропустить") and (currency != None)) else "Не указана"}""")
    await c.message.answer("Напиши минимальную зарплату в числовом формате (например, 50000). Если не важна - напиши 0")
    await d.mark_closed()
    await PostDialogState.select_min_salary.set()


async def switch_to_technology(c: CallbackQuery, b: Button, d: DialogManager):
    await d.switch_to(DialogState.select_technology)

async def reset(c: CallbackQuery, b: Button, d: DialogManager):
    await d.mark_closed()
    await d.data['state'].reset_state(with_data=True)
    await d.start(DialogState.start)

start_keyboard = Window(Const("Какие вакансии тебя интересуют: Code или No-Code?"),
                        Group(Button(Const("Code"), id='code', on_click=switch_to_technology),
                              Button(Const("No-Code"), id='no_code', on_click=switch_to_role),
                              width=2),
                            state=DialogState.start)

technology_keyboard = Window(Const("Выбери технологии:", when="technology"),
                             Group(Multiselect(Format("✅ {item[0]}"),
                                               Format("🔘 {item[0]}"),
                                         id="m_tech", items='technology',
                                         item_id_getter=operator.itemgetter(1)),
                                   width=2),
                             Group(Button(Const("<"), on_click=switch_page, id="prev_page"),
                                   Button(Const(">"), on_click=switch_page, id="next_page"),
                                   width=2),
                             Button(continue_button,
                                    on_click=switch_to_lvl,
                                    id='continue'),
                             Group(Button(Const("⬅ Назад"), id='back', on_click=reset), 
                                   cancel_button,
                                   width=2),
                             getter=get_technology,
                             state=DialogState.select_technology)

role_keyboard = Window(Const("Выбери подходящую позицию:", when="role"),
                             Group(Radio(Format("✅ {item[0]}"),
                                         Format("🔘 {item[0]}"),
                                         id="r_role", items="role",
                                         item_id_getter=operator.itemgetter(1)),
                                   width=2),
                             Const("Дальше позиций нет😕", when='empty'),
                             Group(Button(Const("<"), on_click=switch_page, id="prev_page"),
                                   Button(Const(">"), on_click=switch_page, id="next_page"),
                                   width=2),
                             Button(continue_button,
                                    on_click=switch_to_remote,
                                    id='no_code'),
                             Group(Button(Const("⬅ Назад"), id='back', on_click=reset), 
                                   cancel_button,
                                   width=2),
                             getter=get_role,
                             state=DialogState.select_role)

level_keyboard = Window(Const("Выбери подходящий уровень:"),
                          Group(Radio(Format("✅ {item[0]}"),
                                      Format("🔘 {item[0]}"),
                                      id="r_lvl", items='lvl',
                                      item_id_getter=operator.itemgetter(1)),
                                width=2),
                          Button(continue_button,
                                 on_click=switch_to_remote,
                                 id='continue'),
                          Group(Back(Const("⬅ Назад"), when="code"),
                                Button(Const("⬅ Назад"), id="back", on_click=switch_to_role, when="no_code"),
                                cancel_button, width=2),
                          getter=get_lvl,
                          state=DialogState.select_lvl)

remote_keyboard = Window(Const("Удаленно?"),
                         Group(Radio(Format("✅ {item[0]}"),
                                     Format("🔘 {item[0]}"),
                                     id="r_remote", items='binary',
                                     item_id_getter=operator.itemgetter(1)),
                                width=2),
                         Button(continue_button, on_click=switch_to_relocation, id='continue'),
                         Group(Back(Const("⬅ Назад"), when="code"),
                               Button(Const("⬅ Назад"), id='back', on_click=switch_to_role, when="no_code"),
                               cancel_button, width=2),
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

query_dialog = Dialog(start_keyboard, role_keyboard, technology_keyboard, level_keyboard, 
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

async def select_menu(c: CallbackQuery, b: Button, d: DialogManager):
    match b.widget_id:
        case 'get_stats':
            await d.start(AdminDialog.stat)
        case 'create_mailing':
            await d.mark_closed()
            await c.message.delete()
            await c.message.answer("Напиши текст сообщения для рассылки:")
            await AdminState.insert_mailing.set()


admin_start_keyboard = Window(Const("""Пожалуйста, выбери действие:"""),
                       Group(Button(Const("Статистика"),
                             id="get_stats", on_click=select_menu),
                             Button(Const("Сделать рассылку пользователям"),
                             id="create_mailing", on_click=select_menu), 
                             width=2),
                             cancel_button,
                       state=AdminDialog.start)

async def get_users(**kwargs):
    stat = User.get_summary()
    return {"stat": stat}

user_stat = Window(Format("Общее количество пользователей бота: {stat}"),
                   default_nav,
                   getter=get_users,
                   state=AdminDialog.stat)

admin_dialog = Dialog(admin_start_keyboard, user_stat, )