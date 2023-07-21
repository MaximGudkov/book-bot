import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_data.config import BOT_TOKEN
from handlers import other_handlers, user_handlers
from keyboards.main_menu import set_main_menu

from services.file_handling import BadBookError

from scripts.setup_db import setup_db

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )

    logger.info('Starting bot')

    # WARNING: This will delete all existing tables and will
    # re-fill the data for the bot's lexicon. See docstring
    setup_db()

    bot: Bot = Bot(token=BOT_TOKEN)
    dp: Dispatcher = Dispatcher()

    await set_main_menu(bot)

    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
