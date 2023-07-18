from aiogram import Router
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message

from database.database import bot_database as db
from filters.filters import IsDigitCallbackData, IsDelBookmarkCallbackData
from keyboards.bookmarks_kb import create_bookmarks_keyboard, create_edit_keyboard
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON


router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    db.user_interface.create_user_if_not_exists(
        user_id=message.from_user.id,
        page=1,
        book_marks=[]
    )
    await message.answer(LEXICON[message.text])


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])


@router.message(Command(commands='beginning'))
async def process_beginning_command(message: Message):
    db.user_interface.set_user_page(message.from_user.id, 1)

    user_page = db.user_interface.get_user_page(message.from_user.id)
    text = db.book_interface.get_book_page_content(user_page)
    book_length = db.book_interface.get_book_length()

    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard('backward', f'{user_page}/{book_length}', 'forward')
    )


@router.message(Command(commands='continue'))
async def process_continue_command(message: Message):
    user_page = db.user_interface.get_user_page(message.from_user.id)
    text = db.book_interface.get_book_page_content(user_page)
    book_length = db.book_interface.get_book_length()

    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard('backward', f'{user_page}/{book_length}', 'forward')
    )


@router.message(Command(commands='bookmarks'))
async def process_bookmarks_command(message: Message):
    book_marks = db.user_interface.get_book_marks(message.from_user.id)
    if book_marks:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(*book_marks)
        )
    else:
        await message.answer(text=LEXICON['no_bookmarks'])


@router.callback_query(Text(text='forward'))
async def process_forward_press(callback: CallbackQuery):
    user_page = db.user_interface.get_user_page(callback.from_user.id)
    book_length = db.book_interface.get_book_length()
    if user_page < book_length:
        db.user_interface.set_user_page(callback.from_user.id, user_page + 1)
        current_user_page = db.user_interface.get_user_page(callback.from_user.id)
        text = db.book_interface.get_book_page_content(current_user_page)

        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard('backward', f'{current_user_page}/{book_length}', 'forward')
        )
    else:
        await callback.answer()


@router.callback_query(Text(text='backward'))
async def process_backward_press(callback: CallbackQuery):
    user_page = db.user_interface.get_user_page(callback.from_user.id)
    book_length = db.book_interface.get_book_length()
    if user_page > 1:
        db.user_interface.set_user_page(callback.from_user.id, user_page - 1)
        current_user_page = db.user_interface.get_user_page(callback.from_user.id)
        text = db.book_interface.get_book_page_content(current_user_page)
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard('backward', f'{current_user_page}/{book_length}', 'forward')
        )
    await callback.answer()


@router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit())
async def process_page_press(callback: CallbackQuery):
    user_page = db.user_interface.get_user_page(callback.from_user.id)
    db.user_interface.add_book_mark(callback.from_user.id, user_page)
    await callback.answer('Страница добавлена в закладки!')


@router.callback_query(IsDigitCallbackData())
async def process_bookmark_press(callback: CallbackQuery):
    text = db.book_interface.get_book_page_content(int(callback.data))
    current_user_page = db.user_interface.get_user_page(callback.from_user.id)
    book_length = db.book_interface.get_book_length()
    # users_db[callback.from_user.id]['page'] = int(callback.data)
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard('backward', f'{current_user_page}/{book_length}', 'forward')
    )
    await callback.answer()


@router.callback_query(Text(text='edit_bookmarks'))
async def process_edit_press(callback: CallbackQuery):
    book_marks = db.user_interface.get_book_marks(callback.from_user.id)
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_keyboard(*book_marks)
    )
    await callback.answer()


@router.callback_query(Text(text='cancel'))
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['cancel_text'])
    await callback.answer()


@router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery):
    db.user_interface.remove_book_mark(callback.from_user.id, int(callback.data[:-3]))
    book_marks = db.user_interface.get_book_marks(callback.from_user.id)
    if book_marks:
        await callback.message.edit_text(
            text=LEXICON['/bookmarks'],
            reply_markup=create_edit_keyboard(*book_marks)
        )
    else:
        await callback.message.edit_text(text=LEXICON['no_bookmarks'])
    await callback.answer()
