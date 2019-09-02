from __future__ import annotations

from typing import Dict, List

from aiohttp import ClientSession

import config
import utils

from . import Website

COOKIES_DATA_KEY = "qidian_cookies"

BOOK_URL = "https://www.webnovel.com/book/{}"
TOC_URL = (
    "https://www.webnovel.com/apiajax/chapter/GetChapterList?_csrfToken={}&bookId={}"
)
CHAPTER_URL = "https://www.webnovel.com/apiajax/chapter/GetContent?_csrfToken={}&bookId={}&chapterId={}"


class Qidian(Website):
    name = "qidian"

    csrf_token = None
    tocs: Dict[str, Dict[int, str]] = {}
    cookies: Dict[str, str] = {}

    @staticmethod
    def create_config() -> dict:
        return {
            "book_id": input("Book id? ")
        }

    async def __download_toc(
        self, book_id: str, session: ClientSession
    ) -> Dict[int, str]:
        toc_json = await utils.download_json(
            TOC_URL.format(self.csrf_token, book_id), session
        )

        if toc_json["code"] != 0:
            raise Exception(
                f"Recieved return code {toc_json['code']} when trying to get TOC"
            )

        toc = {}

        for volume in toc_json["data"]["volumeItems"]:
            for chapter in volume["chapterItems"]:
                toc[chapter["index"]] = chapter["id"]

        return toc

    async def prepare_download(self, config: config.Config, session: ClientSession):
        book_id = config.book_id
        if not self.csrf_token:
            self.csrf_token = await utils.download_cookie(
                BOOK_URL.format(book_id), "_csrfToken", session
            )

        if config.book_id not in self.tocs:
            self.tocs[book_id] = await self.__download_toc(book_id, session)

    def get_chapter_url(self, chapter: int, config: config.Config) -> str:
        chapter_id = self.tocs[config.book_id][chapter]
        return CHAPTER_URL.format(self.csrf_token, config.book_id, chapter_id)

    async def download_chapter(
        self, chapter: int, config: config.Config, session: ClientSession
    ) -> str:
        url = self.get_chapter_url(chapter, config)

        content = await utils.download_json(url, session, cookies=self.__get_cookies())
        if not content:
            raise Exception("Failed to download chapter from {}".format(url))

        if content["data"]["chapterInfo"]["isAuth"] == 0:
            self.__update_cookies()
            content = await utils.download_json(
                url, session, cookies=self.__get_cookies()
            )

            if content is None:
                raise Exception("Failed to download chapter from {}".format(url))
            elif content["data"]["chapterInfo"]["isAuth"] == 0:
                raise Exception("Failed to authorize chapter {}".format(url))

        chapter_index = content["data"]["chapterInfo"]["chapterIndex"]
        chapter_name = content["data"]["chapterInfo"]["chapterName"]
        chapter_content = content["data"]["chapterInfo"]["content"]

        chapter_title = (
            f"<strong>Chapter {chapter_index}: {chapter_name}</strong><br />"
        )
        return chapter_title + chapter_content

    @classmethod
    def __get_cookies(self) -> Dict[str, str]:
        if not self.cookies:
            self.cookies = utils.get_data(COOKIES_DATA_KEY)
        return self.cookies

    @classmethod
    def __update_cookies(self):
        print("\n")
        if "uuid" in self.cookies:
            if "ukey" in self.cookies:
                print("Qidian cookie expired!")
                ukey = input("Enter new ukey: ")
                self.cookies["ukey"] = ukey
            else:
                print("Qidian cookie incomplete!")
                self.cookies["ukey"] = input("Enter ukey: ")
        elif "ukey" in self.cookies:
            print("Qidian cookie incomplete!")
            self.cookies["uuid"] = input("Enter uuid: ")
        else:
            print("Qidian requires a cookie!")
            self.cookies["uuid"] = input("Enter uuid: ")
            self.cookies["ukey"] = input("Enter ukey: ")

        utils.update_data(COOKIES_DATA_KEY, self.cookies)
