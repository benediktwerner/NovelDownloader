import utils

import importlib
import os


class BookConverter:
    name = "Unnamed converter"

    def __init__(self, book, config):
        self.book = book
        self.config = config
        self.chapters = []

        if config["follow_links"]:
            with open(utils.get_book_dir(book, "chapter-names.txt"), "r") as f:
                for line in f:
                    self.chapters.append(line.strip())

    def filename_of_chapter(self, ch):
        if ch < 0:
            return ""
        
        if self.config["follow_links"]:
            if ch >= len(self.chapters):
                return ""
            return self.chapters[ch]
        volume = utils.get_volume_from_chapter(ch,self. config["volumes"]) if "volumes" in self.config else None
        return self.config["file_pattern"].format(chapter=ch, volume=volume)

    def load_chapter(self, ch):
        with open(os.path.join(utils.get_raw_dir(self.book), self.filename_of_chapter(ch) + ".html"), "br") as f:
            return "".join(map(lambda line: line.decode(), f))

    def convert_chapters(self, chapter_start, chapter_end):
        raise NotImplementedError()


CONVERTERS = []

for module_file in os.listdir(os.path.dirname(__file__)):
    if module_file == '__init__.py' or module_file[-3:] != '.py':
        continue

    module_name = module_file[:-3]
    module = importlib.import_module("converters." + module_name)
    
    if hasattr(module, module_name):
        CONVERTERS.append(getattr(module, module_name))
