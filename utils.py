import urllib.request as urllib
import urllib.error as urlerror
import yaml
import os

try:
    import progressbar
    HAS_PROGRESS_BAR = True
except ImportError:
    HAS_PROGRESS_BAR = False

BASE_DIR = "books"
RAW_DIR_NAME = "raw"
CONFIG_FILE_NAME = "config.yml"
CHAPTER_NAMES_FILE_NAME = "chapter-names.txt"

MISSING_CHAPTER_NAME = "X"

DEFAULT_BASE_URL = "https://www.wuxiaworld.com"
DEFAULT_FOLLOW_LINKS = False

def download_url(url):
    header = {"User-Agent":'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}
    req = urllib.Request(url, headers=header)
    try:
        page = urllib.urlopen(req)
    except urlerror.HTTPError:
        return None
    return page.read().decode()

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
    return os.path.join(BASE_DIR, book, *subdirs)

def get_config_file(book):
    return get_book_dir(book, CONFIG_FILE_NAME)

def get_raw_dir(book):
    return get_book_dir(book, RAW_DIR_NAME)

def get_chapter_names_file(book):
    return get_book_dir(book, CHAPTER_NAMES_FILE_NAME)

def load_chapter_names(book):
    chapter_names = []
    with open(get_chapter_names_file(book)) as f:
        for line in f:
            if line == MISSING_CHAPTER_NAME:
                chapter_names.append(None)
            elif line:
                chapter_names.append(line)
    return chapter_names

def add_chapter_name(chapter_names, number, name):
    len_plus_one = len(chapter_names) + 1
    if number > len_plus_one:
        for i in range(number - len_plus_one - 1):
            chapter_names.append(None)
        chapter_names.append(name)
    elif number == len_plus_one:
        chapter_names.append(name)
    else:
        chapter_names[number-1] = name

def save_chapter_names(chapter_names, book):
    with open(get_chapter_names_file(book), "w") as f:
        for ch_name in chapter_names:
            if ch_name:
                print(ch_name, file=f)
            else:
                print(MISSING_CHAPTER_NAME, file=f)

def find_last_existing_chatper_name(chapter_names, start=None):
    if not chapter_names:
        return None
    if start is None or start > len(chapter_names):
        start = len(chapter_names)
    for i in range(start-1, 0, -1):
        if chapter_names[i]:
            return chapter_names[i], i+1
    return None

def create_config(book):
    config = {}

    print("\nCreating new config:")
    
    config["base_url"] = add_protocol(input("Base url? "))
    if not config["base_url"]:
        config["base_url"] = DEFAULT_BASE_URL
    config["url"] = add_protocol(input("Url? (Use {volume}, {chapter}, {base_url}, {chapter_name}) "))

    if input_yes_no("Follow links?", False):
        config["follow_links"] = True

    if "follow_links" in config and config["follow_links"]:
        config["first_url"] = input("First url? ")
    else:
        file_pattern = input("File pattern? (Use {volume} and/or {chapter}) ")
        if file_pattern:
            config["file_pattern"] = file_pattern
    
    name = input("Name? ")
    if name:
        config["name"] = name
    
    with open(get_config_file(book), "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    print("Config created at:", get_config_file(book), end="\n\n")

def add_protocol(url):
    if not url.startswith("http") and not url.startswith("{base_url}"):
        return "https://" + url

def input_yes_no(text, default=True):
    text = text.rstrip()
    help_text = " (Y/n) " if default else " (y/N) "
    user_input = input(text + help_text)
    while user_input and user_input.lower() not in ("y", "n"):
        print("Please enter either [Y]es or [N]o!")
        user_input = input(text + help_text)
    if user_input:
        return user_input.lower() == "y"
    return default

def input_int(text, minval=None, maxval=None):
    user_input = input(text)
    while True:
        try:
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

def load_config(book):
    with open(get_config_file(book)) as f:
        config = yaml.load(f)
    config.setdefault("base_url", DEFAULT_BASE_URL)
    config.setdefault("follow_links", DEFAULT_FOLLOW_LINKS)
    return config

def ensure_config(book):
    if not os.path.isfile(get_config_file(book)):
        create_config(book)

def ensure_dir(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)

class ProgressBar:
    def __init__(self, start, end, text="Processing"):
        self.minval = start
        self.maxval = end
        self.value = None
        self.text = text

        if HAS_PROGRESS_BAR:
            widgets = [
                text + " ", ProgressBar.RelativeCounter(start), " out of ", str(end), " ",
                progressbar.Percentage(), " ", progressbar.Bar(left="[", right="]"), " ",
                progressbar.ETA(), " "
            ]
            self.progressbar = progressbar.ProgressBar(widgets=widgets, maxval=end-start).start()
    
    def update(self, newval=None):
        if newval is None:
            newval =  self.value + 1 if self.value is not None else self.minval

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
