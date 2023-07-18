from dataclasses import dataclass

import psycopg2
from psycopg2.extensions import connection

from config_data.config import load_config, Config

bot_config: Config = load_config()


@dataclass
class UserInterface:
    conn: connection

    def _user_exists(self, user_id: int) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s);"
        values = (user_id,)

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()[0]
            return result

    def create_user_if_not_exists(self, user_id: int, page: int, book_marks: list) -> None:
        if not self._user_exists(user_id):
            query = "INSERT INTO users (user_id, page, book_marks) VALUES (%s, %s, %s);"
            book_marks_str = "{" + ",".join(map(str, book_marks)) + "}"
            values = (user_id, page, book_marks_str)

            with self.conn.cursor() as cursor:
                cursor.execute(query, values)
                self.conn.commit()

    def get_user_page(self, user_id: int) -> int:
        if not self._user_exists(user_id):
            raise ValueError('No such user')

        query = "SELECT page FROM users WHERE user_id = %s;"
        values = (user_id,)

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()

        page = result[0]
        return page

    def set_user_page(self, user_id: int, page: int) -> None:
        query = "UPDATE users SET page = %s WHERE user_id = %s;"
        values = (page, user_id)

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            self.conn.commit()

    def get_book_marks(self, user_id: int) -> list:
        query = "SELECT book_marks FROM users WHERE user_id = %s;"
        values = (user_id,)

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()

        return result[0]

    def add_book_mark(self, user_id: int, book_mark: str) -> None:
        query = "UPDATE users SET book_marks = array_append(book_marks, %s::text) WHERE user_id = %s;"
        values = (book_mark, user_id)

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            self.conn.commit()

    def remove_book_mark(self, user_id: int, book_mark: str) -> None:
        query = "UPDATE users SET book_marks = array_remove(book_marks, %s::text) WHERE user_id = %s;"
        values = (book_mark, user_id)

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            self.conn.commit()


@dataclass
class BookInterface:
    conn: connection

    BOOK_NAME = 'Bredberi_Marsianskie-hroniki'

    def get_book_page_content(self, page: int) -> str:
        query = "SELECT content->%s FROM books WHERE name = %s;"
        values = (str(page), self.BOOK_NAME)

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()

        if result:
            page_text = result[0]
            return page_text

        raise ValueError('No such page')

    def get_book_length(self) -> int:
        query = "SELECT content FROM books WHERE name = %s;"
        values = (self.BOOK_NAME,)

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()

        if not result:
            raise ValueError('No such book')

        content: dict = result[0]
        return len(content)


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=bot_config.book_bot_db.host,
            port=bot_config.book_bot_db.port,
            database=bot_config.book_bot_db.database,
            user=bot_config.book_bot_db.user,
            password=bot_config.book_bot_db.password,
        )
        self.user_interface = UserInterface(self.conn)
        self.book_interface = BookInterface(self.conn)
        self.lexicon = self.get_table_data_as_dict('lexicon_ru')
        self.menu_commands = self.get_table_data_as_dict('menu_commands')

    def get_table_data_as_dict(self, table_name: str) -> dict:
        with self.conn.cursor() as cursor:
            query = f"SELECT * FROM {table_name};"
            cursor.execute(query)
            results: list[tuple] = cursor.fetchall()
            return dict(results)


bot_database = Database()
