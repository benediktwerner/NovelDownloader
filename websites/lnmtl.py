from __future__ import annotations

import re
from typing import Dict

from aiohttp import ClientSession

import config
import utils

from . import Website

BASE_URL = "https://www.lnmtl.com/chapter/{}-chapter-{}"


class Lnmtl(Website):
    name = "lnmtl"

    chapter_separator_start = 'class="chapter-body hyphenate" v-pre>'
    chapter_separator_end = '</div>'

    tocs: Dict[str, Dict[int, str]] = {}

    @staticmethod
    def create_config() -> dict:
        return {
            "book_id": input("Book id? ")
        }

    def get_chapter_url(self, chapter: int, config: config.Config) -> str:
        return BASE_URL.format(config.book_id, chapter)
