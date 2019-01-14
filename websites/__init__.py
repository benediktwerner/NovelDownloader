import utils


class Website:
    name = None
    url = None

    @classmethod
    def get_chapter_url(cls, chapter, config):
        if "volumes" in config:
            volume = utils.get_volume_from_chapter(chapter, config["volumes"])
            return config["chapter_url"].format(
                chapter=chapter,
                volume=volume,
                base_url=config["base_url"]
            )

        return config["chapter_url"].format(
            chapter=chapter,
            base_url=config["base_url"]
        )

    chapter_separator_start = None
    chapter_separator_end = None

    @classmethod
    def get_chapter_content(cls, content):
        content_start = content.find(cls.chapter_separator_start)
        content_end = content.find(cls.chapter_separator_end, content_start)

        if content_start == -1 or content_end == -1 or content_start >= content_end:
            return None

        return content[content_start+len(cls.chapter_separator_start):content_end]

    @classmethod
    def get_cookies(cls):
        return {}

    @classmethod
    def cookies_expired(cls, content):
        return False

    @classmethod
    def update_cookies(cls):
        raise Exception("This website does not support updating cookies")


from .qidian import Qidian
from .wuxiaworld import Wuxiaworld


WEBSITES = [
    Qidian,
    Wuxiaworld
]

WEBSITES_DICT = {}

for site in WEBSITES:
    WEBSITES_DICT[site.name] = site


def from_name(name):
    return WEBSITES_DICT[name]
