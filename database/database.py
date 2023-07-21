import json
import os
from dataclasses import dataclass

from config_data.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

import psycopg2
from psycopg2.extensions import connection


@dataclass
class BaseQueriesMixin:
    conn: connection

    def get_row_by_query(self, query: str, values: tuple = None) -> tuple:
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()
        if result:
            return result
        return (None,)

    def execute_query_and_commit(self, query, values=None):
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            self.conn.commit()


class UserInterface(BaseQueriesMixin):

    def _exists(self, user_id: int) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s);"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        return result[0]

    def create_if_not_exists(
            self,
            user_id: int,
            current_page: int,
            current_book: int | None,
            books: list,
            book_marks: dict
    ) -> None:
        if not self._exists(user_id):
            query = '''
            INSERT INTO users (user_id, current_page, current_book, books, book_marks)
            VALUES (%s, %s, %s, %s, %s);
            '''
            books_str = "{" + ",".join(map(str, books)) + "}"
            book_marks_json = json.dumps(book_marks)
            values = (user_id, current_page, current_book, books_str, book_marks_json)

            self.execute_query_and_commit(query, values)

    def book_exists(self, user_id: int, book_name: str) -> bool:
        return book_name in self.get_books(user_id)

    def get_books(self, user_id: int) -> list:
        query = "SELECT name FROM books WHERE id = ANY(SELECT unnest(books) FROM users WHERE user_id = %s);"
        values = (user_id,)

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchall()

        book_names = [row[0] for row in result]
        return book_names

    def get_current_book(self, user_id: int) -> str | None:
        query = "SELECT current_book FROM users WHERE user_id = %s;"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        book_id = result[0]

        if book_id:
            query2 = "SELECT name FROM books WHERE id = %s;"
            values2 = (book_id,)
            result2 = self.get_row_by_query(query2, values2)

            return result2[0]

    def _get_book_id_by_name(self, user_id: int, book_name: str) -> int:
        query = "SELECT id FROM books WHERE name = %s;"
        values = (book_name,)
        result = self.get_row_by_query(query, values)
        book_id = result[0]
        return book_id

    def remove_book(self, user_id: int, book_name: str) -> None:
        book_id = self._get_book_id_by_name(user_id, book_name)
        query = '''
        UPDATE users
         SET books = array_remove(books, %s),
             current_book = CASE WHEN current_book = %s THEN 1 ELSE current_book END
        WHERE user_id = %s;
        '''
        values = (book_id, book_id, user_id)
        self.execute_query_and_commit(query, values)

        query2 = "DELETE FROM books WHERE id = %s;"
        values2 = (book_id,)
        self.execute_query_and_commit(query2, values2)

    def set_current_book(self, user_id: int, book_name: str) -> None:
        book_id = self._get_book_id_by_name(user_id, book_name)
        query = "UPDATE users SET current_book = %s WHERE user_id = %s;"
        values = (book_id, user_id)
        self.execute_query_and_commit(query, values)

    def get_current_page(self, user_id: int) -> int:
        query = "SELECT current_page FROM users WHERE user_id = %s;"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        return result[0]

    def set_current_page(self, user_id: int, page: int) -> None:
        query = "UPDATE users SET current_page = %s WHERE user_id = %s;"
        values = (page, user_id)
        self.execute_query_and_commit(query, values)

    def get_book_marks(self, user_id: int) -> dict:
        query = "SELECT book_marks FROM users WHERE user_id = %s;"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        marks = result[0]
        if marks:
            return marks
        return {}

    def _save_book_marks(self, user_id: int, book_marks: dict) -> None:
        query = "UPDATE users SET book_marks = %s WHERE user_id = %s;"
        book_marks_json = json.dumps(book_marks)
        values = (book_marks_json, user_id)
        self.execute_query_and_commit(query, values)

    def add_book_mark(self, user_id: int, book_name: str, book_mark: str) -> None:
        book_marks: dict[str, list] = self.get_book_marks(user_id)
        if book_name in book_marks and book_mark in book_marks[book_name]:
            return
        book_marks.setdefault(book_name, []).append(book_mark)
        self._save_book_marks(user_id, book_marks)

    def remove_book_mark(self, user_id: int, book_name: str, book_mark: str) -> None:
        book_marks: dict[str, list] = self.get_book_marks(user_id)
        book_marks.get(book_name).remove(book_mark)
        if not book_marks[book_name]:
            del book_marks[book_name]
        self._save_book_marks(user_id, book_marks)

    def save_book(self, user_id: int, book_name: str, content: str) -> None:
        query = "INSERT INTO books (name, content) VALUES (%s, %s) RETURNING id;"
        values = (book_name, content)

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            book_id = cursor.fetchone()[0]
            self.conn.commit()

        query2 = "UPDATE users SET books = array_append(books, %s) WHERE user_id = %s;"
        values2 = (book_id, user_id)

        self.execute_query_and_commit(query2, values2)


class BookInterface(BaseQueriesMixin):

    def get_page_content(self, book_name: str, page: int) -> str:
        query = "SELECT content->%s FROM books WHERE name = %s;"
        values = (str(page), book_name)
        result = self.get_row_by_query(query, values)
        page_text = result[0]
        return page_text

    def get_length(self, book_name: str) -> int:
        query = "SELECT content FROM books WHERE name = %s;"
        values = (book_name,)
        result = self.get_row_by_query(query, values)
        content = result[0]
        return len(content)


class Database(BaseQueriesMixin):
    def __init__(self):
        self.conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        self.user_interface = UserInterface(self.conn)
        self.book_interface = BookInterface(self.conn)

    def get_table_data_as_dict(self, table_name: str) -> dict:
        with self.conn.cursor() as cursor:
            query = f"SELECT * FROM {table_name};"
            cursor.execute(query)
            results: list[tuple] = cursor.fetchall()
            return dict(results)


bot_database = Database()
