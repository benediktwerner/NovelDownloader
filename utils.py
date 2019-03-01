import os
import re
import yaml

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


async def download_url(url, session, json=False, cookies=None):
    # header = {
    #     "User-Agent": 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7',
    # }
    async with session.get(url, cookies=cookies) as response:
        if json:
            return await response.json()
        return await response.text()


async def download_cookies(url, name, session):
    async with session.get(url) as response:
        return response.cookies[name].value


def get_book_dir(book, *subdirs):
    return os.path.join(BASE_DIR, book.lower(), *subdirs)


def get_config_file(book):
    return get_book_dir(book, CONFIG_FILE_NAME)


def get_raw_dir(book):
    return get_book_dir(book, RAW_DIR_NAME)


def ensure_config(book):
    if not os.path.isfile(get_config_file(book)):
        config.create_config(book)


def input_yes_no(text, default=True):
    text = text.rstrip()
    help_text = " (Y/n) " if default else " (y/N) "
    user_input = input(text + help_text)

    while user_input and user_input[0].lower() not in ("y", "n"):
        print("Please enter either [Y]es or [N]o!")
        user_input = input(text + help_text)

    if user_input:
        return user_input[0].lower() == "y"

    return default


def input_int(text, minval=None, maxval=None, default=None):
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


def ensure_dir(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)


def chapter_name(chapter):
    return "chapter-{}".format(chapter)


def load_data():
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE) as f:
            return yaml.load(f)
    return None


def save_data(data):
    with open(DATA_FILE, "w") as f:
        yaml.dump(data, f, default_flow_style=False)


def get_data(key):
    data = load_data()
    if data and key in data:
        return data[key]
    return None


def update_data(key, value):
    data = load_data()
    if not data:
        data = {}
    data[key] = value
    save_data(data)


def list_books():
    for book in sorted(os.listdir(BASE_DIR)):
        if os.path.isfile(get_config_file(book)):
            conf = config.load_config(book)
            if "name" in conf:
                print(book, "-", conf["name"])
                continue

        print(book)


def get_chapter_list(book, directory=RAW_DIR_NAME):
    directory = get_book_dir(book, directory)
    chapters = []

    if not os.path.isdir(directory):
        return chapters

    for chapter_name in os.listdir(directory):
        match = re.match(r"chapter-(\d+)", chapter_name)
        if match and match.groups() is not None:
            chapters.append(int(match.group(1)))

    if not chapters:
        return chapters

    chapters.sort()

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


def format_range(start, end):
    if start == end:
        return str(start)
    return "{}-{}".format(start, end)


class ProgressBar:
    def __init__(self, start, end, text="Processing"):
        self.maxval = end - start + 1
        self.value = 0
        self.text = text

        if HAS_PROGRESS_BAR:
            widgets = [
                text + " ",
                progressbar.SimpleProgress(" out of "),
                " ",
                progressbar.Percentage(),
                " ",
                progressbar.Bar(left="[", right="]"),
                " ",
                progressbar.ETA(),
                " ",
            ]
            self.progressbar = progressbar.ProgressBar(
                widgets=widgets, maxval=maxval
            ).start()

    def update(self, newval=None):
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
