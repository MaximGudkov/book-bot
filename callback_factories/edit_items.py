from aiogram.filters.callback_data import CallbackData


class EditItemsCallbackFactory(CallbackData, prefix='edit_items'):
    item_type: str
