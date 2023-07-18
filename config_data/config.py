from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str


@dataclass
class BookBotDB:
    host: str
    port: str
    database: str
    user: str
    password: str


@dataclass
class Config:
    tg_bot: TgBot
    book_bot_db: BookBotDB


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(token=env('BOT_TOKEN')),
        book_bot_db=BookBotDB(
            host=env('DB_HOST'),
            port=env('DB_PORT'),
            database=env('DB_NAME'),
            user=env('DB_USER'),
            password=env('DB_PASSWORD')
        )
    )
