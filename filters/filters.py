from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


class IsAddToBookMarksCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return '/' in callback.data and callback.data.replace('/', '').isdigit()


class IsBookCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> dict[str, str] | bool:
        if isinstance(callback.data, str) and '#$%book#$%' in callback.data:
            book_name = callback.data[:-10]
            return {'user_book': book_name}
        return False


class IsDelBookCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> dict[str, str] | bool:
        if isinstance(callback.data, str) and '#$%delbook#$%' in callback.data:
            book_name = callback.data[:-13]
            return {'user_book': book_name}
        return False


class IsBookmarkCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> dict[str, int] | bool:
        if isinstance(callback.data, str) and '#$%bookmark#$%' in callback.data:
            page = int(callback.data[:-14])
            return {'page': page}
        return False


class IsDelBookmarkCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> dict[str, int] | bool:
        if isinstance(callback.data, str) and '#$%delbookmark#$%' in callback.data \
                and callback.data[:-17].isdigit():
            page = int(callback.data[:-17])
            return {'page': page}
        return False
