from aiogram.types import CallbackQuery, ChatMemberStatus
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

def is_button_selected(key: str = None):
    def wrapper(async_func):
        async def _wrapper(c: CallbackQuery, b: Button, d: DialogManager):
            if d.data['aiogd_context'].widget_data[key]:
                await async_func(c, b, d)
            else:
                await c.answer("Сначала нужно выбрать одну из опций")
        return _wrapper
    return wrapper

async def is_user_subscribed(channel_ids: list, user_id: int, many=False):
    #return True
    #всё что ниже сможет исполняться только при добавлении бота в администраторы канала
    from loader import bot
    user_statuses = [((await bot.get_chat_member(channel, user_id)).status != ChatMemberStatus.LEFT) 
                       for channel in channel_ids]
    if not many:
        return any(user_statuses)
    else:
        return all(user_statuses)