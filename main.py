#!/usr/bin/env python3

import converters
import utils
import downloader

import os


def main():
    # TODO: List books
    book = input("Which book? ")
    book_dir = utils.get_book_dir(book)
    
    if not os.path.isdir(book_dir):
        if not utils.input_yes_no("The book doesn't exist. Do you want to create it?"):
            return
        print("New book. Creating directory {}".format(book_dir))
        utils.ensure_dir(book_dir)
    utils.ensure_config(book)

    config = utils.load_config(book)
    
    if utils.input_yes_no("Do you want to download chapters?"):
        print("Which chapters do you want to download?")
        chapter_start = utils.input_int("First chapter? ")
        chapter_end = utils.input_int("Last chapter? ", chapter_start)

        try:
            downloader.download_chapters(chapter_start, chapter_end, book, config)
        except downloader.DownloadException as e:
            print("\nERROR:", e)
            return
        except:
            print()
            raise
        
        if not utils.input_yes_no("Do you also want to convert chapters?"):
            return
    
    print("\nWhich chapters do you want to convert?")

    if "volumes" in config and utils.input_yes_no("Select by volume instead of chapters?"):
        volume = utils.input_int("Which volume? ", 1, len(config["volumes"]))
        chapter_range = utils.get_chapters_from_volume(volume, config["volumes"])
    else:
        chapter_start = utils.input_int("First chapter? ")
        chapter_end = utils.input_int("Last chapter? ", chapter_start)
        chapter_range = (chapter_start, chapter_end)
    
    print("\nBook converters:")
    for i, converter in enumerate(converters.CONVERTERS):
        print("[{}] {}".format(i, converter.name))

    converter_id = utils.input_int("Converter: ", 0, i)
    converters.CONVERTERS[converter_id](book, config).convert_chapters(*chapter_range)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by Ctrl-C")
