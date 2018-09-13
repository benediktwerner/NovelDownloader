import importlib
import os

import utils


class BookConverter:
    name = "Unnamed converter"

    def __init__(self, book, config):
        self.book = book
        self.config = config

    def load_chapter(self, ch):
        with open(os.path.join(utils.get_raw_dir(self.book), utils.chapter_name(ch) + ".html"), "br") as f:
            return "".join(map(lambda line: line.decode(), f))

    def convert_chapters(self, chapter_start, chapter_end):
        raise NotImplementedError()


from .HtmlConverter import HtmlConverter
from .KindleConverter import KindleConverter

CONVERTERS = [
    HtmlConverter,
    KindleConverter
]
