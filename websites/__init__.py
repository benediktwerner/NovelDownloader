from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Dict, Optional, Type, Union

from aiohttp import ClientSession

import config
import utils


class Website(ABC):
    name: str
    chapter_separator_start: str
    chapter_separator_end: str

    @staticmethod
    def create_config() -> dict:
        return {}

    @abstractmethod
    def get_chapter_url(self, chapter: int, config: config.Config) -> str:
        pass

    async def prepare_download(self, config: config.Config, session: ClientSession):
        pass

    async def download_chapter(
        self, chapter: int, config: config.Config, session: ClientSession
    ) -> Optional[str]:
        url = self.get_chapter_url(chapter, config)

        content = await utils.download_url(url, session)
        if content is None:
            raise Exception("Failed to download chapter from {}".format(url))

        return self.extract_chapter_content(content)

    def extract_chapter_content(self, content: str) -> Optional[str]:
        content_start = content.find(self.chapter_separator_start)
        content_end = content.find(self.chapter_separator_end, content_start)

        if content_start == -1 or content_end == -1 or content_start >= content_end:
            return None

        return content[content_start + len(self.chapter_separator_start) : content_end]


class AnonymusWebsite(Website):
    def __init__(self, config):
        self.toc = []
        self.toc_url = config["toc_url"]
        self.toc_start = config["toc_start"]
        self.toc_end = config["toc_end"]
        self.toc_link = config["toc_link"]
        self.chapter_url = config["chapter_url"]
        self.chapter_separator_start = config["chapter_start"]
        self.chapter_separator_end = config["chapter_end"]

    async def __download_toc(self, session: ClientSession):
        toc_page = await utils.download_url(self.toc_url, session)

        start = toc_page.find(self.toc_start)
        end = toc_page.find(self.toc_end, start)
        toc_page = toc_page[start:end]

        return [None] + re.findall(self.toc_link, toc_page)

    async def prepare_download(self, config: config.Config, session: ClientSession):
        if not self.toc:
            self.toc = await self.__download_toc(session)

    def get_chapter_url(self, chapter, config):
        return self.chapter_url + self.toc[chapter]


from .qidian import Qidian
from .wuxiaworld import Wuxiaworld
from .lnmtl import Lnmtl

WEBSITES = [Wuxiaworld(), Qidian(), Lnmtl()]

WEBSITES_DICT: Dict[str, Website] = {}

for site in WEBSITES:
    WEBSITES_DICT[site.name] = site


def from_config(config: Union[str, dict]) -> Website:
    if isinstance(config, str):
        return WEBSITES_DICT[config]
    return AnonymusWebsite(config)
