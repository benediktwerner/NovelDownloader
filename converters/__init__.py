import importlib
import os
from abc import ABC, abstractmethod
from typing import List, Type

import utils
from config import Config


class BookConverter(ABC):
    name = "Unnamed converter"

    def __init__(self, config: Config):
        self.config = config

    def load_chapter(self, ch: int):
        with open(
            os.path.join(
                utils.get_raw_dir(self.config.book), utils.chapter_name(ch) + ".html"
            ),
            "br",
        ) as f:
            return "".join(map(lambda line: line.decode(), f))

    @abstractmethod
    def convert_chapters(self, chapter_start: int, chapter_end: int):
        pass


from .HtmlConverter import HtmlConverter
from .TxtConverter import TxtConverter


CONVERTERS: List[Type[BookConverter]] = [HtmlConverter, TxtConverter]
