#!/usr/bin/env python3

import config
import converters
import utils
import downloader

import os


HELP_ACTIONS = ("?", "help")
LIST_ACTIONS = ("l", "ls", "list")
QUIT_ACTIONS = ("q", "quit", "exit")

HELP = """\
Enter a book's shortname to download or convert chapters for it.
If no local info for the book exists it will be created.

Enter nothing to select the last used book.

Enter {list_actions} to list all books on this device.
Enter {help_actions} to show this help.
Enter {quit_actions} to quit.
""".format(
    list_actions=utils.format_list(LIST_ACTIONS),
    help_actions=utils.format_list(HELP_ACTIONS),
    quit_actions=utils.format_list(QUIT_ACTIONS),
)


def choose_book():
    print("Enter a book or '?' for help:")

    while True:
        action = input("> ")

        if action in HELP_ACTIONS:
            print(HELP)
        elif action in LIST_ACTIONS:
            utils.list_books()
            print()
        elif action in QUIT_ACTIONS:
            print("Bye.")
            return None
        else:
            break

    book = action

    if not book:
        book = utils.get_data("last_book")

        if not book:
            print("No book entered. Bye.")
            return None
        else:
            print("Using last book:", book)

    print()
    book_dir = utils.get_book_dir(book)

    if not os.path.isdir(book_dir):
        if not utils.input_yes_no(
            "The book '{}' does not exist. Do you want to create it?".format(book)
        ):
            print("Ok. Bye.")
            return None

        print("\nNew book. Creating directory {}".format(book_dir))
        utils.ensure_dir(book_dir)

    return book


def download_chapters(conf):
    print("Which chapters do you want to download?")

    chapter_start = utils.input_int("First chapter? ")
    chapter_end = utils.input_int(
        "Last chapter? ", minval=chapter_start, default=chapter_start
    )

    chapters_on_disk = utils.get_chapters_on_disk(conf["book"])
    chapters = list(range(chapter_start, chapter_end + 1))

    if any(ch in chapters_on_disk for ch in chapters):
        if not utils.input_yes_no(
            "Some of these chapters are already on disk. Do you want to redownload them?"
        ):
            chapters = [ch for ch in chapters if ch not in chapters_on_disk]
            if not chapters:
                print("All chapters are already on disk. Bye.")
                return None

    try:
        result = downloader.download_chapters(chapters, conf)
        if result:
            return chapter_start, chapter_end
        return None
    except:
        print()
        raise


def convert_chapters(conf, chapter_start=None, chapter_end=None):
    print("Which chapters do you want to convert?")
    if chapter_start is not None and chapter_end is not None:
        print("Enter nothing to convert the chapters just downloaded.")

    chapter_start = utils.input_int("First chapter? ", default=chapter_start)
    chapter_end = utils.input_int("Last chapter? ", chapter_start, default=chapter_end)

    chapters = set(range(chapter_start, chapter_end + 1))
    chapters_on_disk = utils.get_chapters_on_disk(conf["book"])
    missing_chapters = chapters - chapters_on_disk

    if missing_chapters:
        print("The following chapters are not on disk:")
        print(utils.format_range_list(utils.group_chapters(missing_chapters)))

        available_chapters = utils.group_chapters(chapters - missing_chapters)
        new_range = max(available_chapters, key=len)

        if utils.input_yes_no(
            f"Do you want to convert {utils.format_range_list(new_range)} instead?"
        ):
            chapter_start, chapter_end = new_range
        else:
            print("Ok. Bye.")
            return

    print("Converting from chapter", chapter_start, "to", chapter_end)

    print("\nBook converters:")
    for i, converter in enumerate(converters.CONVERTERS):
        print("[{}] {}".format(i, converter.name))

    converter_id = utils.input_int("Converter: ", 0, i)
    converters.CONVERTERS[converter_id](conf).convert_chapters(
        chapter_start, chapter_end
    )


def main():
    print("Welcome to BND (Bene's Novel Downloader)")

    book = choose_book()
    if book is None:
        return

    utils.update_data("last_book", book)
    utils.ensure_config(book)
    conf = config.load_config(book)

    if conf is None:
        return

    if "name" in conf:
        print("Selected", book, "-", conf["name"])
    else:
        print("Selected", book)

    chapters = utils.get_chapters_on_disk(book)
    if chapters:
        print("Chapters on disk:")
        print(utils.format_range_list(utils.group_chapters(chapters)))
    else:
        print("No chapters on disk")
    print()

    if utils.input_yes_no("Do you want to download chapters?"):
        downloaded_chapters = download_chapters(conf)
        if downloaded_chapters is None:
            return

        print()
        if not utils.input_yes_no("Do you also want to convert chapters?"):
            print("Ok. Bye.")
            return

        convert_chapters(conf, *downloaded_chapters)
        return

    print()
    convert_chapters(conf)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by Ctrl-C\nBye.")
    except EOFError:
        print("\nBye.")
