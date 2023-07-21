from scripts.storage.add_book_query import query as add_book_query, values
from scripts.storage.creation_query import query as create_query
from database.database import bot_database as db


def setup_db():
    """
    This function will create all the relevant tables in your database
    (using environment variables to connect to your database from `.env`),
    and also fill it with all the data necessary for the bot to work.
    Be careful, comment out this function if you don't want to lose
    existing data in the database.
    """
    db.execute_query_and_commit(create_query)
    db.execute_query_and_commit(add_book_query, values)
