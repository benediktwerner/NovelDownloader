import yaml

import utils
import websites


def _get_website():
    while True:
        website = input(
            "Website? ({}) ".format(", ".join(w.name for w in websites.WEBSITES))
        )
        if website in websites.WEBSITES_DICT:
            return website
        print("Unknown website:", website)


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
    else:
        config["website"] = websites.from_name(config["website"])

    config["book"] = book
    return config
