from aiogram import Bot
from aiogram.types import BotCommand

from lexicon.lexicon import LEXICON_COMMANDS


async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(command=command, description=description)
                          for command, description in LEXICON_COMMANDS.items()]
    await bot.set_my_commands(main_menu_commands)
