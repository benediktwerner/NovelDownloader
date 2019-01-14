import requests

import utils
from . import Website


COOKIES_DATA_KEY = "qidian_cookies"

BOOK_URL = "https://www.webnovel.com/book/{}"
TOC_URL = "https://www.webnovel.com/apiajax/chapter/GetChapterList?_csrfToken={}&bookId={}"
CHAPTER_URL = "https://www.webnovel.com/book/{}/{}"

TITLE_START = '<div class="cha-tit">'


class Qidian(Website):
    name = "qidian"
    url = "https://www.webnovels.com"

    chapter_separator_start = '<div class="cha-words">'
    chapter_separator_end = '</div>'

    tocs = {}
    cookies = {}

    @staticmethod
    def _get_toc(book_id):
        csrf_token = requests.get(BOOK_URL.format(book_id)).cookies["_csrfToken"]
        toc_json = requests.get(TOC_URL.format(csrf_token, book_id)).json()

        if toc_json["code"] != 0:
            raise Exception("Recieved return code {} when trying to get TOC".format(toc_json["code"]))

        toc = [None]

        for volume in toc_json["data"]["volumeItems"]:
            for chapter in volume["chapterItems"]:
                toc.append(chapter["id"])

        return toc

    @classmethod
    def get_chapter_url(cls, chapter, config):
        book_id = config["book_id"]

        if book_id not in cls.tocs:
            cls.tocs[book_id] = cls._get_toc(book_id)

        chapter_id = cls.tocs[book_id][chapter]
        return CHAPTER_URL.format(book_id, chapter_id)

    @classmethod
    def get_chapter_content(cls, content):
        title_start = content.find(TITLE_START)
        title_start = content.find("<h3>", title_start)
        title_end = content.find("</h3>", title_start)

        chapter_content = super().get_chapter_content(content).replace("\n", "")

        if title_start != -1 and title_end != -1 and title_start < title_end:
            chapter_content = content[title_start:title_end+len("</h3>")] + "\n" + chapter_content

        return chapter_content

    @classmethod
    def get_cookies(cls):
        if not cls.cookies:
            cls.cookies = utils.get_data(COOKIES_DATA_KEY)
        return cls.cookies

    @classmethod
    def cookies_expired(cls, content):
        template_start = content.find("ejs-template")
        return "Locked Chapter" in content[:template_start]

    @classmethod
    def update_cookies(cls):
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
