from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.database import bot_database as db
from lexicon.lexicon import LEXICON


def create_bookmarks_keyboard(*args: int) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for button in sorted(args):
        kb_builder.row(
            InlineKeyboardButton(
                text=f'{button} - {db.book_interface.get_book_page_content(button)[:100]}',
                callback_data=str(button)
            )
        )

    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['edit_bookmarks_button'],
            callback_data='edit_bookmarks'
        ),
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel'
        ),
        width=2
    )
    return kb_builder.as_markup()


def create_edit_keyboard(*args: int) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for button in sorted(args):
        kb_builder.row(
            InlineKeyboardButton(
                text=f'{LEXICON["del"]} {button} - {db.book_interface.get_book_page_content(button)[:100]}',
                callback_data=f'{button}del'
            )
        )

    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel'
        )
    )
    return kb_builder.as_markup()
