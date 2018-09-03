#!/usr/bin/env python3

import os
import re
import utils

from sys import argv


if len(argv) != 5:
    print("Usage:", argv[0], "BOOK_NAME", "BOOK_ID", "FIRST_CHAPTER", "LAST_CHAPTER")
    exit(1)


BOOK = argv[1]
BOOK_ID = argv[2]
BASE_URL = "https://www.webnovel.com/book/"

FIRST_CHAPTER = int(argv[3])
LAST_CHAPTER = int(argv[4])


def download_chapter(ch):
    content = utils.download_url(BASE_URL + BOOK_ID + "/" + toc[ch])

    start = content.find('<div class="cha-words">')
    end = content.find("</div>", start)

    chapter = content[start+len('<div class="cha-words">'):end]

    with open(utils.get_book_dir(BOOK, "raw", "chapter-{}.html".format(ch)), "bw") as f:
        f.write(chapter.encode("utf-8"))


toc = [None] # There is no 0th chapter

with open(utils.get_book_dir(BOOK, "toc.txt")) as f:
    for line in f:
        toc.append(line.rstrip())

progress = utils.ProgressBar(FIRST_CHAPTER, LAST_CHAPTER, "Downloading")
os.makedirs(utils.get_book_dir(BOOK, "raw"), exist_ok=True)

for ch in range(FIRST_CHAPTER, LAST_CHAPTER + 1):
    progress.update()
    download_chapter(ch)

progress.finish()
