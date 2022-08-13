import operator
import requests
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Radio, Button, Group, Multiselect, Back, Row
from aiogram_dialog.widgets.text import Format, Const
from states import DialogState, Stack
from utils import cancel

cancel_button = Button(Const("❌ Отмена"), id='cancel', on_click=cancel)
back_button = Back(Const("⬅ Назад"))
#back_to_start_button = Button(Const("⬅ Назад"), id='back_to_start', on_click=erase_widget_data)
continue_button = Const("Продолжить ➡")
default_nav = Group(back_button, cancel_button, width=2)

async def get_technology(**kwargs):
    params = {}
    json = requests.get("https://devseye.ru/api/technology",
                       params=params).json()
    technology = [tech['name'] for tech in json['results']]
    technology_list = [(item, item)
                    for item in technology]
    return {'technology': technology_list}

def is_button_selected(key: str = None):
    def wrapper(async_func):
        async def _wrapper(c: CallbackQuery, b: Button, d: DialogManager):
            if key in d.data['aiogd_context'].widget_data.keys():
                await async_func(c, b, d)
            else:
                await c.answer("Сначала нужно выбрать хотя бы одну из опций")
        return _wrapper
    return wrapper

@is_button_selected(key='m_tech')
async def next(c: CallbackQuery, b: Button, d: DialogManager):
    print(f"d.data: {d.data}")
    print(f"d.data['state']: {d.data['state']}")
    dialog_data = d.data['aiogd_context'].widget_data['m_tech']
    await d.mark_closed()
    await d.data['state'].reset_state(with_data=True)
    print(dialog_data)
    await c.message.delete()
    await c.message.answer(f"Вы выбрали следующие технологии: {', '.join(dialog_data)}")
    await c.message.answer("Напишите желаемый уровень разработчика:")
    await Stack.lvl.set()


technology_keyboard = Window(Const("Выбери технологии:"),
                          Group(Multiselect(Format("✅ {item[0]}"),
                                      Format("🔘 {item[0]}"),
                                      id="m_tech", items='technology',
                                      item_id_getter=operator.itemgetter(1)),
                                width=2),
                          Button(continue_button,
                                 on_click=next,
                                 id='continue'),
                          default_nav,
                          getter=get_technology,
                          state=DialogState.choosing_technology)

level_keyboard = Window(Const("Выбери уровень:"),
                        Group(
                            Row(
                                Button(Const("Intern"), id='Intern'),
                                Button(Const("Junior"), id='Junior') 
                        ), Row(
                            Button(Const("Middle"), id='Middle'),
                            Button(Const("Senior"), id='Senior')
                        )
                    )
                )

dialog = Dialog(technology_keyboard, )