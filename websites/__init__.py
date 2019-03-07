import re

import utils


class Website:
    name = None

    @classmethod
    def get_chapter_url(cls, chapter, config):
        raise NotImplementedError

    chapter_separator_start = None
    chapter_separator_end = None

    @classmethod
    async def prepare_download(cls, config, session):
        pass

    @classmethod
    async def download_chapter(cls, chapter, config, session):
        url = cls.get_chapter_url(chapter, config)

        content = await utils.download_url(url, session)
        if content is None:
            raise Exception("Failed to download chapter from {}".format(url))

        return cls.extract_chapter_content(content)

    @classmethod
    def extract_chapter_content(cls, content):
        content_start = content.find(cls.chapter_separator_start)
        content_end = content.find(cls.chapter_separator_end, content_start)

        if content_start == -1 or content_end == -1 or content_start >= content_end:
            return None

        return content[content_start + len(cls.chapter_separator_start) : content_end]


from .qidian import Qidian
from .wuxiaworld import Wuxiaworld


WEBSITES = [Qidian, Wuxiaworld]

WEBSITES_DICT = {}

for site in WEBSITES:
    WEBSITES_DICT[site.name] = site


def from_name(name):
    return WEBSITES_DICT[name]


def from_config(config):
    async def __download_toc(cls, session):
        toc_page = await utils.download_url(cls.toc_url, session)

        start = toc_page.find(cls.toc_start)
        end = toc_page.find(cls.toc_end, start)
        toc_page = toc_page[start:end]

        return [None] + re.findall(cls.toc_link, toc_page)

    async def prepare_download(cls, config, session):
        if not cls.toc:
            cls.toc = await cls.__download_toc(session)

    def get_chapter_url(cls, chapter, config):
        return cls.chapter_url + cls.toc[chapter]

    return type(
        "AnonymusWebsite",
        (Website,),
        {
            "__download_toc": classmethod(__download_toc),
            "prepare_download": classmethod(prepare_download),
            "get_chapter_url": classmethod(get_chapter_url),
            "toc": [],
            "toc_url": config["toc_url"],
            "toc_start": config["toc_start"],
            "toc_end": config["toc_end"],
            "toc_link": config["toc_link"],
            "chapter_url": config["chapter_url"],
            "chapter_separator_start": config["chapter_start"],
            "chapter_separator_end": config["chapter_end"],
        },
    )
