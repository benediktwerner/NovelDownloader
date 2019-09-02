from __future__ import annotations

import re
from typing import Dict

from aiohttp import ClientSession

import config
import utils

from . import Website

BASE_URL = "https://www.wuxiaworld.com"
TOC_URL = "https://www.wuxiaworld.com/novel/{}"

TOC_START = "list-chapters"
TOC_END = '<div id="sidebar'


class Wuxiaworld(Website):
    name = "wuxiaworld"

    chapter_separator_start = '<div id="chapter-content" class="fr-view">'
    chapter_separator_end = '<a href="/novel/'

    tocs: Dict[str, Dict[int, str]] = {}

    @staticmethod
    def create_config() -> dict:
        return {
            "book_id": input("Book id? ")
        }

    async def __download_toc(
        self, book_id: str, session: ClientSession
    ) -> Dict[int, str]:
        toc_page = await utils.download_url(TOC_URL.format(book_id), session)

        start = toc_page.find(TOC_START)
        end = toc_page.find(TOC_END, start)
        toc_page = toc_page[start:end]

        toc = {}
        for ch, url in enumerate(re.findall('"(/novel/.*?)"', toc_page), 1):
            toc[ch] = url

        return toc

    async def prepare_download(self, config: config.Config, session: ClientSession):
        book_id = config.book_id
        if book_id not in self.tocs:
            self.tocs[book_id] = await self.__download_toc(book_id, session)

    def get_chapter_url(self, chapter: int, config: config.Config) -> str:
        return BASE_URL + self.tocs[config.book_id][chapter]
