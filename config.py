import yaml

import utils
import websites


def _format_url(url):
    if url.startswith("/"):
        url = "{base_url}" + url
        print("Added base_url:", url)
    if not url.startswith("http") and not url.startswith("{base_url}"):
        url = "https://" + url
        print("Added protocol:", url)
    return url


def _get_website():
    while True:
        website = input("Website? ({}) ".format(
            ", ".join(websites.WEBSITES)))
        if website in websites.WEBSITES:
            return websites
        print("Unknown website:", website)


def create_config(book):
    config = {}

    print("Creating new config for {}:".format(book))
    config["book"] = book
    config["website"] = _get_website()

    if config["website"] == websites.Qidian.name:
        config["book_id"] = input("Book id? ")
    else:
        config["chapter_url"] = _format_url(
            input("Chapter Url? (Use {volume}, {chapter}, {chapter_name}) "))

    name = input("Name? (optional)")
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
        if "base_url" not in config:
            config["website"] = websites.Wuxiaworld
            print("Warning: Config has no 'website' or 'base_url' attribute")
            print("         Assuming 'wuxiaworld'")
        else:
            for site in websites.WEBSITES:
                if site.name in config["base_url"]:
                    config["website"] = site
                    break
            else:
                print(
                    "Warning: Config has no 'website' and unknown 'base_url':", config["base_url"])
                print("         Assuming 'wuxiaworld'")
                config["website"] = websites.Wuxiaworld
    else:
        config["website"] = websites.from_name(config["website"])

    if "chapter_url" not in config and "url" in config:
        config["chapter_url"] = config["url"]

    config.setdefault("base_url", config["website"].url)
    config.setdefault("book", book)
    return config
