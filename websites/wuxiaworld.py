import re

import utils
from . import Website


TOC_URL = "https://www.wuxiaworld.com/novel/{}"

TOC_START = "list-chapters"
TOC_END = '<div id="sidebar'


class Wuxiaworld(Website):
    name = "wuxiaworld"
    url = "https://www.wuxiaworld.com"

    chapter_separator_start = '<div class="fr-view">'
    chapter_separator_end = '<a href="/novel/'

    tocs = {}

    @classmethod
    def __download_toc(cls, book_id):
        toc_page = utils.download_url(TOC_URL.format(book_id))

        start = toc_page.find(TOC_START)
        end = toc_page.find(TOC_END, start)
        toc_page = toc_page[start:end]

        return [None] + re.findall('"(/novel/.*?)"', toc_page)

    @classmethod
    def prepare_download(cls, config):
        book_id = config["book_id"]
        if book_id not in cls.tocs:
            cls.tocs[book_id] = cls.__download_toc(book_id)

    @classmethod
    def get_chapter_url(cls, chapter, config):
        return Wuxiaworld.url + cls.tocs[config["book_id"]][chapter]
