#!/usr/bin/env python3

import config
import converters
import utils
import downloader

import os


QUIT_ACTIONS = ("q", "quit", "exit")


def choose_book():
    print("Enter a book or '?' to list all current books:")

    action = input("> ")

    if action == "?":
        utils.list_books()
        print()
        action = input("> ")

    if action in QUIT_ACTIONS:
        print("Bye.")
        return None

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
        if not utils.input_yes_no("The book '{}' does not exist. Do you want to create it?".format(book)):
            print("Ok. Bye.")
            return None

        print("\nNew book. Creating directory {}".format(book_dir))
        utils.ensure_dir(book_dir)

    return book


def download_chapters(conf):
    print("Which chapters do you want to download?")

    chapter_start = utils.input_int("First chapter? ")
    chapter_end = utils.input_int("Last chapter? ", minval=chapter_start, default=chapter_start)

    try:
        downloader.download_chapters(chapter_start, chapter_end, conf)
        return chapter_start, chapter_end
    except:
        print()
        raise


def convert_chapters(conf, chapter_start=None, chapter_end=None):
    print("Which chapters do you want to convert?")

    if "volumes" in conf and utils.input_yes_no("Select by volume instead of chapters?"):
        volume = utils.input_int("Which volume? ", 1, len(conf["volumes"]))
        chapter_start, chapter_end = utils.get_chapters_from_volume(volume, conf["volumes"])
        print("Converting volume", volume, "from chapter", chapter_start, "to", chapter_end)
    else:
        chapter_start = utils.input_int("First chapter? ", default=chapter_start)
        chapter_end = utils.input_int("Last chapter? ", chapter_start, default=chapter_end)
        print("Converting from chapter", chapter_start, "to", chapter_end)

    print("\nBook converters:")
    for i, converter in enumerate(converters.CONVERTERS):
        print("[{}] {}".format(i, converter.name))

    converter_id = utils.input_int("Converter: ", 0, i)
    converters.CONVERTERS[converter_id](conf).convert_chapters(chapter_start, chapter_end)


def main():
    print("Welcome to BND (Bene's Novel Downloader)")

    book = choose_book()
    if book is None:
        return

    utils.ensure_config(book)
    conf = config.load_config(book)
    utils.update_data("last_book", book)

    if "name" in conf:
        print("Selected", book, "-", conf["name"])
    else:
        print("Selected", book)

    chapters = utils.get_chapter_list(book)
    if chapters:
        print("Chapters on disk:")
        print(", ".join(utils.format_range(*x) for x in chapters))
    else:
        print("No chapters on disk")
    print()

    if utils.input_yes_no("Do you want to download chapters?"):
        downloaded_chapters = download_chapters(conf)
        if downloaded_chapters is None:
            return

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
