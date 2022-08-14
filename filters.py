def is_button_selected(key: str = None):
    def wrapper(async_func):
        async def _wrapper(c: CallbackQuery, b: Button, d: DialogManager):
            if key in d.data['aiogd_context'].widget_data.keys():
                await async_func(c, b, d)
            else:
                await c.answer("Сначала нужно выбрать хотя бы одну из опций")
        return _wrapper
    return wrapper
    