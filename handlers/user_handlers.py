from aiogram import Router, F
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message

from callback_factories.edit_items import EditItemsCallbackFactory
from database.database import bot_database as db
from filters.filters import (
    IsAddToBookMarksCallbackData,
    IsBookmarkCallbackData,
    IsDelBookmarkCallbackData,
    IsBookCallbackData,
    IsDelBookCallbackData
)
from keyboards.bookmarks_kb import create_bookmarks_keyboard, create_edit_bookmarks_keyboard
from keyboards.books_kb import create_books_keyboard, create_edit_books_keyboard
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON
from services.file_handling import get_file_text_from_server, prepare_book, pretty_name, BadBookError


router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    db.user_interface.create_if_not_exists(
        user_id=message.from_user.id,
        current_page=1,
        current_book=1,
        books=[1],
        book_marks={}
    )
    await message.answer(LEXICON[message.text])


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])


@router.message(Command(commands='books'))
async def process_books_command(message: Message):
    user_books = db.user_interface.get_books(message.from_user.id)
    if user_books:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_books_keyboard(*user_books)
        )
    else:
        await message.answer(LEXICON['no_books'])


@router.message(Command(commands='bookmarks'))
async def process_bookmarks_command(message: Message):
    user_book = db.user_interface.get_current_book(message.from_user.id)
    book_marks = db.user_interface.get_book_marks(message.from_user.id)
    if book_marks:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(user_book, *book_marks[user_book])
        )
    else:
        await message.answer(text=LEXICON['no_bookmarks'])


@router.message(Command(commands='continue'))
async def process_continue_command(message: Message):
    user_book = db.user_interface.get_current_book(message.from_user.id)
    user_page = db.user_interface.get_current_page(message.from_user.id)
    text = db.book_interface.get_page_content(user_book, user_page)
    book_length = db.book_interface.get_length(user_book)
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard('backward', f'{user_page}/{book_length}', 'forward')
    )


@router.message(F.document)
async def process_load_book(message: Message):
    if message.document.mime_type == 'text/plain':
        book_name = message.caption or pretty_name(message.document.file_name)
        beautiful_name = '📖 ' + book_name
        if db.user_interface.book_exists(message.from_user.id, beautiful_name):
            answer = LEXICON['book_exists']
        else:
            text = get_file_text_from_server(message.document.file_id)
            try:
                content = prepare_book(text)
                db.user_interface.save_book(message.from_user.id, beautiful_name, content)
                answer = f'Книга успешно сохранена под именем "{book_name}"'
            except BadBookError:
                answer = LEXICON['cant_parse']
    else:
        answer = LEXICON['miss_message']

    await message.answer(answer)


@router.callback_query(IsBookCallbackData())
async def process_book_press(callback: CallbackQuery, user_book: str):
    db.user_interface.set_current_book(callback.from_user.id, user_book)
    db.user_interface.set_current_page(callback.from_user.id, 1)
    text = db.book_interface.get_page_content(user_book, 1)
    book_length = db.book_interface.get_length(user_book)
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard('backward', f'1/{book_length}', 'forward')
    )


@router.callback_query(EditItemsCallbackFactory.filter(F.item_type == 'books'))
async def process_edit_books_press(callback: CallbackQuery):
    user_books = db.user_interface.get_books(callback.from_user.id)
    if len(user_books) > 1:
        answer = LEXICON['edit']
        await callback.message.edit_text(
            text=LEXICON[callback.data],
            reply_markup=create_edit_books_keyboard(*user_books)
        )
    else:
        answer = LEXICON['no_books_to_delete']

    await callback.answer(answer)


@router.callback_query(Text(text='cancel_edit_book'))
async def process_edit_books_press(callback: CallbackQuery):
    user_books = db.user_interface.get_books(callback.from_user.id)
    await callback.message.edit_text(
        text=LEXICON['/books'],
        reply_markup=create_books_keyboard(*user_books)
    )


@router.callback_query(IsDelBookCallbackData())
async def process_del_book_press(callback: CallbackQuery, user_book: str):
    db.user_interface.remove_book(callback.from_user.id, user_book)
    user_books = db.user_interface.get_books(callback.from_user.id)
    reply_markup = create_books_keyboard(*user_books)
    if len(user_books) > 1:
        text = LEXICON['edit_books']
        answer = LEXICON['deleted_book']
    else:
        text = LEXICON['/books']
        answer = LEXICON['no_books_to_delete']

    await callback.message.edit_text(text=text, reply_markup=reply_markup)
    await callback.answer(answer)


@router.callback_query(Text(text='forward'))
async def process_forward_press(callback: CallbackQuery):
    user_page = db.user_interface.get_current_page(callback.from_user.id)
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    book_length = db.book_interface.get_length(user_book)

    next_page = user_page + 1
    if user_page == book_length:
        next_page = 1
    db.user_interface.set_current_page(callback.from_user.id, next_page)
    text = db.book_interface.get_page_content(user_book, next_page)

    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard('backward', f'{next_page}/{book_length}', 'forward')
    )


@router.callback_query(Text(text='backward'))
async def process_backward_press(callback: CallbackQuery):
    user_page = db.user_interface.get_current_page(callback.from_user.id)
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    book_length = db.book_interface.get_length(user_book)

    next_page = user_page - 1
    if user_page == 0:
        next_page = book_length
    db.user_interface.set_current_page(callback.from_user.id, next_page)
    text = db.book_interface.get_page_content(user_book, next_page)

    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard('backward', f'{next_page}/{book_length}', 'forward')
    )


@router.callback_query(IsAddToBookMarksCallbackData())
async def process_page_press(callback: CallbackQuery):
    user_page = db.user_interface.get_current_page(callback.from_user.id)
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    db.user_interface.add_book_mark(callback.from_user.id, user_book, user_page)
    await callback.answer(f'Страница {user_page} добавлена в закладки!')


@router.callback_query(EditItemsCallbackFactory.filter(F.item_type == 'bookmarks'))
async def process_edit_bookmarks_press(callback: CallbackQuery):
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    book_marks = db.user_interface.get_book_marks(callback.from_user.id)
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_bookmarks_keyboard(user_book, *book_marks[user_book])
    )
    await callback.answer()


@router.callback_query(IsBookmarkCallbackData())
async def process_bookmark_press(callback: CallbackQuery, page: int):
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    text = db.book_interface.get_page_content(user_book, page)
    book_length = db.book_interface.get_length(user_book)
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard('backward', f'{page}/{book_length}', 'forward')
    )
    await callback.answer()


@router.callback_query(Text(text='cancel'))
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['cancel_text'])
    await callback.answer()


@router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery, page: int):
    user_book = db.user_interface.get_current_book(callback.from_user.id)
    db.user_interface.remove_book_mark(callback.from_user.id, user_book, page)
    book_marks = db.user_interface.get_book_marks(callback.from_user.id)
    if book_marks:
        await callback.message.edit_text(
            text=LEXICON['edit_bookmarks'],
            reply_markup=create_edit_bookmarks_keyboard(user_book, *book_marks[user_book])
        )
    else:
        await callback.message.edit_text(text=LEXICON['no_bookmarks'])
    await callback.answer()
