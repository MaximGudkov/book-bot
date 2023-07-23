import json
import re

import requests

from config_data.config import BOT_TOKEN

PAGE_SIZE = 1050


class BadBookError(Exception):
    def __init__(self, *args, **kwargs):
        self.message = "Can't parse this file"
        super().__init__(self.message, *args, **kwargs)


def _get_part_text(text: str, start: int, page_size: int) -> tuple[str, int] | None:
    # we use HTML parse mode in our bot, so we need to edit some symbols
    text = text.replace('<', '&lt').replace('>', '&gt').replace('&', '&amp')
    end = start + page_size
    if end >= len(text):
        return text[start:], len(text) - start

    for i in range(end - 1, start - 1, -1):
        if text[i] in ",.!:;?":
            return text[start:i + 1], i + 1 - start

    raise BadBookError()


def prepare_book(text: str) -> str:
    content = {}
    cur_idx = cur_page = 0
    while cur_idx < len(text):
        cur_page += 1
        page_text, page_length = _get_part_text(text, cur_idx, PAGE_SIZE)
        content[cur_page] = page_text.lstrip()
        cur_idx += page_length

    return json.dumps(content)


def get_file_text_from_server(file_id: str) -> str:
    file_info_url = f'https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}'
    response = requests.get(file_info_url)
    file_info = response.json()
    file_path = file_info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    response = requests.get(file_url)
    return response.text


def pretty_name(name: str) -> str:
    name = name.replace('.txt', '')
    pretty = re.sub(r'\W', '_', name.lower())
    pretty = re.sub(r'_+', '_', pretty)
    return pretty[:35]
