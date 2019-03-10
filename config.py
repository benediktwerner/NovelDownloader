from typing import Any, Dict, Union

import yaml

import utils
import websites


class Config:
    def __init__(self, book: str, values: Dict[str, str]):
        self.book = book

        website = values.get("website")
        if website is None:
            self.website = websites.WEBSITES[0]
            print("Warning: Config has no 'website' attribute")
            print(f"         Assuming '{self.website.name}'")
        elif isinstance(website, str) or isinstance(website, dict):
            self.website = websites.from_config(website)
        else:
            raise ValueError(f"Invalid 'website' type {type(values['website'])}")

        self.book_id = values["book_id"]
        self.name = values.get("name")
        self.add_chapter_titles = values.get("add_chapter_titles", False)
        self.skip_chapters = values.get("skip_chapters", [])


def _get_website() -> Union[str, Dict[str, str]]:
    print("[0] Custom")
    for i, website in enumerate(websites.WEBSITES, 1):
        print("[{}] {}".format(i, website.name))

    website_index = utils.input_int("Website: ", 0, i)
    if website_index > 0:
        return websites.WEBSITES[website_index - 1].name

    return {
        "toc_url": input("TOC url: "),
        "toc_start": input("TOC start: "),
        "toc_end": input("TOC end: "),
        "toc_link": input("TOC link regex (optional): ") or 'href="(.*?)"',
        "chapter_url": input("Chapter url: "),
        "chapter_start": input("Chapter start: "),
        "chapter_end": input("Chapter end: "),
    }


def create_config(book: str):
    config: Dict[str, Any] = {}

    print("Creating new config for {}:".format(book))
    config["website"] = _get_website()

    config["book_id"] = input("Book id? ")

    name = input("Name? (optional) ")
    if name:
        config["name"] = name

    add_chapter_titles = utils.input_yes_no("Add additional chapter titles?", False)
    if add_chapter_titles:
        config["add_chapter_titles"] = True

    with open(utils.get_config_file(book), "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print("Config created at:", utils.get_config_file(book))
    print()


def load_config(book: str) -> Config:
    with open(utils.get_config_file(book)) as f:
        values = yaml.load(f)

    return Config(book, values)
