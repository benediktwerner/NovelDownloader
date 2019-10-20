from typing import Any, Dict, Union

import yaml

import utils
import websites


class Config:
    def __init__(self, book: str, values: Dict[str, str]):
        self.book = book
        self.website = websites.from_config(values["website"])
        self.values = values

    def __getattr__(self, name):
        return self.values.get(name)


def _get_website(config: dict):
    print("[0] Custom")
    for i, website in enumerate(websites.WEBSITES, 1):
        print("[{}] {}".format(i, website.name))

    website_index = utils.input_int("Website: ", 0, i)
    if website_index > 0:
        website = websites.WEBSITES[website_index - 1]
        config["website"] = website.name
        config.update(website.create_config())
    else:
        config["website"] = {
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

    _get_website(config)

    name = input("Name? (optional) ")
    if name:
        config["name"] = name

    with open(utils.get_config_file(book), "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print("Config created at:", utils.get_config_file(book))
    print()


def load_config(book: str) -> Config:
    with open(utils.get_config_file(book)) as f:
        values = yaml.safe_load(f)

    return Config(book, values)
