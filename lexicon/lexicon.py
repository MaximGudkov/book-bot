from database.database import bot_database as db


LEXICON: dict[str, str] = db.get_table_data_as_dict('lexicon')
LEXICON_COMMANDS: dict[str, str] = db.get_table_data_as_dict('menu_commands')
