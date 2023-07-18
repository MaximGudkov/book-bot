from database.database import bot_database as db

LEXICON: dict[str, str] = db.lexicon
LEXICON_COMMANDS: dict[str, str] = db.menu_commands
