import utils


class Website:
    name = None
    url = None

    @classmethod
    def get_chapter_url(cls, chapter, config):
        if "volumes" in config:
            volume = utils.get_volume_from_chapter(chapter, config["volumes"])
            return config["chapter_url"].format(
                chapter=chapter, volume=volume, base_url=config["base_url"]
            )

        return config["chapter_url"].format(
            chapter=chapter, base_url=config["base_url"]
        )

    chapter_separator_start = None
    chapter_separator_end = None

    @classmethod
    def prepare_download(cls, config):
        pass

    @classmethod
    def download_chapter(cls, chapter, config):
        url = cls.get_chapter_url(chapter, config)

        content = utils.download_url(url)
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
