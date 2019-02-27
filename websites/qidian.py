import requests

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
    url = "https://www.webnovels.com"

    csrf_token = None
    tocs = {}
    cookies = {}

    @classmethod
    def __get_csrf_token(cls, book_id):
        if not cls.csrf_token:
            cls.csrf_token = requests.get(BOOK_URL.format(book_id)).cookies[
                "_csrfToken"
            ]
        return cls.csrf_token

    @classmethod
    def __download_toc(cls, book_id):
        toc_json = utils.download_url(
            TOC_URL.format(cls.__get_csrf_token(book_id), book_id), json=True
        )

        if toc_json["code"] != 0:
            raise Exception(
                "Recieved return code {} when trying to get TOC".format(
                    toc_json["code"]
                )
            )

        toc = [None]

        for volume in toc_json["data"]["volumeItems"]:
            for chapter in volume["chapterItems"]:
                toc.append(chapter["id"])

        return toc

    @classmethod
    def prepare_download(cls, config):
        book_id = config["book_id"]
        if book_id not in cls.tocs:
            cls.tocs[book_id] = cls.__download_toc(book_id)

    @classmethod
    def get_chapter_url(cls, chapter, config):
        book_id = config["book_id"]
        chapter_id = cls.tocs[book_id][chapter]
        return CHAPTER_URL.format(cls.__get_csrf_token(book_id), book_id, chapter_id)

    @classmethod
    def download_chapter(cls, chapter, config):
        url = cls.get_chapter_url(chapter, config)

        content = utils.download_url(url, json=True, cookies=cls.__get_cookies())
        if not content:
            raise Exception("Failed to download chapter from {}".format(url))

        if content["data"]["chapterInfo"]["isAuth"] == 0:
            cls.__update_cookies()
            content = utils.download_url(url, json=True, cookies=cls.__get_cookies())

            if content is None:
                raise Exception("Failed to download chapter from {}".format(url))
            elif content["data"]["chapterInfo"]["isAuth"] == 0:
                raise Exception("Failed to authorize chapter {}".format(url))

        return content["data"]["chapterInfo"]["content"]

    @classmethod
    def __get_cookies(cls):
        if not cls.cookies:
            cls.cookies = utils.get_data(COOKIES_DATA_KEY)
        return cls.cookies

    @classmethod
    def __update_cookies(cls):
        print("\n")
        if "uuid" in cls.cookies:
            if "ukey" in cls.cookies:
                print("Qidian cookie expired!")
                ukey = input("Enter new ukey: ")
                cls.cookies["ukey"] = ukey
            else:
                print("Qidian cookie incomplete!")
                cls.cookies["ukey"] = input("Enter ukey: ")
        elif "ukey" in cls.cookies:
            print("Qidian cookie incomplete!")
            cls.cookies["uuid"] = input("Enter uuid: ")
        else:
            print("Qidian requires a cookie!")
            cls.cookies["uuid"] = input("Enter uuid: ")
            cls.cookies["ukey"] = input("Enter ukey: ")

        utils.update_data(COOKIES_DATA_KEY, cls.cookies)
