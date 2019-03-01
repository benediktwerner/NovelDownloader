import yaml

import utils
import websites


def _get_website():
    print("[0] Custom")
    for i, website in enumerate(websites.WEBSITES, 1):
        print("[{}] {}".format(i, website.name))

    website_index = utils.input_int("Website: ", 0, i)
    if website_index > 0:
        return websites.WEBSITES[website_index]

    return {
        "toc_url": input("TOC url: "),
        "toc_start": input("TOC start: "),
        "toc_end": input("TOC end: "),
        "toc_link": input("TOC link regex (default: 'href=\"(.*?)\"'): ") or 'href="(.*?)"',
        "chapter_url": input("Chapter url: "),
        "chapter_start": input("Chapter start: "),
        "chapter_end": input("Chapter end: "),
    }


def create_config(book):
    config = {}

    print("Creating new config for {}:".format(book))
    config["website"] = _get_website()

    config["book_id"] = input("Book id? ")

    name = input("Name? (optional) ")
    if name:
        config["name"] = name

    add_chapter_titles = utils.input_yes_no("Add chapter titles?", False)
    if add_chapter_titles:
        config["add_chapter_titles"] = True

    with open(utils.get_config_file(book), "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print("Config created at:", utils.get_config_file(book))
    print()


def load_config(book):
    with open(utils.get_config_file(book)) as f:
        config = yaml.load(f)

    if "website" not in config:
        print("Warning: Config has no 'website' attribute")
        print("         Assuming 'wuxiaworld'")
    elif isinstance(config["website"], str):
        config["website"] = websites.from_name(config["website"])
    else:
        config["website"] = websites.from_config(config["website"])

    config["book"] = book
    return config
