import requests
import yaml
import os
from sys import stderr

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


def print_error(*args):
    print(*args, file=stderr)


def download_url(url):
    # header = {
    #     "User-Agent": 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7',
    # }
    try:
        return requests.get(url).text
    except Exception:
        print_error("Error while downloading URL:", url)
        return None


def in_range(r, i):
    """
    Checks if the integer i is in the range r.
    r is a string of the form "2-7".
    """
    a, b = map(int, r.split("-"))
    return a <= i <= b


def get_volume_from_chapter(c, volumes):
    for v, r in enumerate(volumes):
        if in_range(r, c):
            return v+1


def get_chapters_from_volume(v, volumes):
    return (int(x.strip()) for x in volumes[v-1].split("-"))


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


class ProgressBar:
    def __init__(self, start, end, text="Processing"):
        self.minval = start
        self.maxval = end
        self.value = None
        self.text = text

        if HAS_PROGRESS_BAR:
            widgets = [
                text +
                " ", ProgressBar.RelativeCounter(
                    start), " out of ", str(end), " ",
                progressbar.Percentage(), " ", progressbar.Bar(
                    left="[", right="]"), " ",
                progressbar.ETA(), " "
            ]
            self.progressbar = progressbar.ProgressBar(
                widgets=widgets, maxval=end-start).start()

    def update(self, newval=None):
        if newval is None:
            newval = self.value + 1 if self.value is not None else self.minval

        self.value = newval
        if HAS_PROGRESS_BAR:
            self.progressbar.update(newval - self.minval)
        else:
            print(self.text, newval, "out of", self.maxval)

    def finish(self):
        if HAS_PROGRESS_BAR:
            self.progressbar.finish()
        else:
            print("Done.")

    class RelativeCounter(progressbar.Widget):
        def __init__(self, minval):
            self.minval = minval

        def update(self, pbar):
            return "{}".format(self.minval + pbar.currval)
