from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON


def create_books_keyboard(*args: str) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for book_name in sorted(args):
        kb_builder.row(
            InlineKeyboardButton(
                text=book_name,
                callback_data=f'{book_name}#$%book#$%'
            )
        )

    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['edit_button'],
            callback_data='edit_books'
        ),
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel'
        ),
        width=2
    )

    return kb_builder.as_markup()


def create_edit_books_keyboard(*args: str) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for book_name in sorted(args):
        if book_name == '📖 Ray Bradbury `The Martian Chronicles`':
            continue
        kb_builder.row(
            InlineKeyboardButton(
                text=f'{LEXICON["del"]} {book_name}',
                callback_data=f'{book_name}#$%delbook#$%'
            )
        )

    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel_edit_book'
        )
    )
    return kb_builder.as_markup()
