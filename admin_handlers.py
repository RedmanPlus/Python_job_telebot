from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram_dialog import DialogManager, StartMode
from db.models import User
from loader import dp, bot
from keyboard import confirm_keyboard
from states import AdminState, DialogState, PostDialogState, SearchVacancyState, AdminDialog
from filters import is_user_subscribed

@dp.message_handler(commands=['admin'])
async def get_user_stat(message: Message, state:FSMContext, dialog_manager: DialogManager):
    user_dict = {k: v for k ,v in dict(message.from_user).items() 
	             if k in [field.name for field in User._meta.get_fields()]}
    user = User.objects.filter(id=user_dict['id']).first()
    if not user:
        user = User.objects.create(**user_dict)
    if user.is_admin:
        await dialog_manager.start(AdminDialog.start)
    else:
        await message.answer("Нет прав администратора!")
        
@dp.message_handler(state=AdminState.insert_mailing)
async def create_mailing(message: Message, state: FSMContext):
    mailing_text = message.html_text
    await message.answer(f"Сообщение будет выглядеть следующим образом (подтверди или отмени рассылку):")
    await message.answer(mailing_text, reply_markup=confirm_keyboard)
    await state.update_data({"mailing_text": mailing_text})
    await AdminState.confirm_mailing.set()

@dp.message_handler(Text(equals=["❌Отменить"]), state=AdminState.confirm_mailing)
async def cancel_record(msg: Message, state: FSMContext, dialog_manager: DialogManager):
    await msg.answer("Рассылка отменена.", reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=True)
    await dialog_manager.start(AdminDialog.start)

@dp.message_handler(Text(equals=["✅Подтвердить рассылку"]), state=AdminState.confirm_mailing)
async def create_order(msg: Message, state: FSMContext):
    from utils import send_mailing
    data = await state.get_data()
    await send_mailing(bot, data['mailing_text'])
    await msg.answer("Рассылка отправлена!")
    await state.reset_state(with_data=True)

@dp.message_handler(state=AdminState.confirm_mailing)
async def require_push(msg: Message, state: FSMContext):
    await msg.answer("Пожалуйста, нажми на одну из кнопок. Я не смогу продолжать диалог дальше, пока они тут 😓")
