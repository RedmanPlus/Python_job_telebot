from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

async def is_user_subscribed(channel_ids: list, user_id: int, many=False):
    return True
    #всё что ниже сможет исполняться только при добавлении бота в администраторы канала
    from loader import bot
    if not many:
        return any([(await bot.get_chat_member(channel, user_id) != 'left') for channel in channel_ids])
    else:
        return all([(await bot.get_chat_member(channel, user_id) != 'left') for channel in channel_ids])