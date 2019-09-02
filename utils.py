import os
import re
from typing import Any, Iterable, List, Optional, Sequence, Set, Tuple

import yaml
from aiohttp import ClientSession

import config

try:
    import progressbar

    HAS_PROGRESS_BAR = True
except ImportError:
    HAS_PROGRESS_BAR = False

BASE_DIR = "books"
RAW_DIR_NAME = "raw"
CONFIG_FILE_NAME = "config.yml"

DATA_FILE = "data.yml"

MISSING_CHAPTER_NAME = "X"


async def download_url(url: str, session: ClientSession, cookies: dict = None) -> str:
    async with session.get(url, cookies=cookies) as response:
        return await response.text(encoding="utf-8")


async def download_json(url: str, session: ClientSession, cookies: dict = None) -> dict:
    async with session.get(url, cookies=cookies) as response:
        return await response.json(encoding="utf-8", content_type=None)


async def download_cookie(url: str, name: str, session: ClientSession) -> str:
    async with session.get(url) as response:
        return response.cookies[name].value


def get_book_dir(book: str, *subdirs: str) -> str:
    return os.path.join(BASE_DIR, book.lower(), *subdirs)


def get_config_file(book: str) -> str:
    return get_book_dir(book, CONFIG_FILE_NAME)


def get_raw_dir(book: str) -> str:
    return get_book_dir(book, RAW_DIR_NAME)


def ensure_config(book: str):
    if not os.path.isfile(get_config_file(book)):
        config.create_config(book)


def input_yes_no(text: str, default: bool = True) -> bool:
    text = text.rstrip()
    help_text = " (Y/n) " if default else " (y/N) "
    user_input = input(text + help_text)

    while user_input and user_input[0].lower() not in ("y", "n"):
        print("Please enter either [Y]es or [N]o!")
        user_input = input(text + help_text)

    if user_input:
        return user_input[0].lower() == "y"

    return default


def input_int(
    text: str, minval: int = None, maxval: int = None, default: int = None
) -> int:
    user_input = input(text)

    while True:
        try:
            if default and not user_input:
                return default
            x = int(user_input)
            if minval is not None and x < minval or maxval is not None and x > maxval:
                if minval is not None:
                    if maxval is not None:
                        print("Value must be between", minval, "and", maxval)
                    else:
                        print("Value must not be less than", minval)
                else:
                    print("Value must not be larger than", maxval)
                user_input = input(text)
            else:
                return x
        except ValueError:
            user_input = input(text + "(Please enter a valid number) ")


def ensure_dir(directory: str):
    if not os.path.isdir(directory):
        os.makedirs(directory)


def chapter_name(chapter: int) -> str:
    return f"chapter-{chapter}"


def load_data() -> Optional[dict]:
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE) as f:
            return yaml.safe_load(f)
    return None


def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        yaml.dump(data, f, default_flow_style=False)


def get_data(key: str) -> Any:
    data = load_data()
    if data and key in data:
        return data[key]
    return None


def update_data(key: str, value: Any):
    data = load_data()
    if not data:
        data = {}
    data[key] = value
    save_data(data)


def list_books():
    if not os.path.isdir(BASE_DIR):
        print("No books.")
        return

    for book in sorted(os.listdir(BASE_DIR)):
        if os.path.isfile(get_config_file(book)):
            conf = config.load_config(book)
            if conf.name:
                print(book, "-", conf.name)
                continue

        print(book)


def group_chapters(chapters: Iterable[int]) -> List[Tuple[int, int]]:
    chapters = list(sorted(chapters))
    groups = []
    curr_min = chapters[0]
    curr_max = chapters[0]

    for chapter in chapters[1:]:
        if curr_max == chapter - 1:
            curr_max = chapter
        else:
            groups.append((curr_min, curr_max))
            curr_min = chapter
            curr_max = chapter

    groups.append((curr_min, curr_max))
    return groups


def get_chapters_on_disk(book: str) -> Set[int]:
    directory = get_raw_dir(book)
    chapters: Set[int] = set()

    if not os.path.isdir(directory):
        return chapters

    for chapter_name in os.listdir(directory):
        match = re.match(r"chapter-(\d+)", chapter_name)
        if match and match.groups() is not None:
            chapters.add(int(match.group(1)))

    return chapters


def format_range(start: int, end: int) -> str:
    if start == end:
        return str(start)
    return f"{start}-{end}"


def format_range_list(range_list: Sequence[Tuple[int, int]]) -> str:
    return ", ".join(format_range(*r) for r in range_list)


def format_list(ls: Sequence) -> str:
    if len(ls) == 1:
        return f"'{ls[0]}'"

    joined = "', '".join(ls[:-1])
    return f"'{joined}' or '{ls[-1]}'"


class ProgressBar:
    def __init__(self, maxval: int, text: str = "Processing"):
        self.maxval = maxval
        self.value = 0
        self.text = text

        if HAS_PROGRESS_BAR:
            widgets = [
                text + " ",
                progressbar.SimpleProgress(),
                " ",
                progressbar.Percentage(),
                " ",
                progressbar.Bar(left="[", right="]"),
                " ",
                progressbar.ETA(),
                " ",
            ]
            self.progressbar = progressbar.ProgressBar(
                widgets=widgets, max_value=self.maxval
            ).start()

    def update(self, newval: int = None):
        if newval is None:
            newval = self.value + 1

        self.value = newval
        if HAS_PROGRESS_BAR:
            self.progressbar.update(newval)
        else:
            print(self.text, newval, "out of", self.maxval)

    def finish(self):
        if HAS_PROGRESS_BAR:
            self.progressbar.finish()
        else:
            print("Done.")
