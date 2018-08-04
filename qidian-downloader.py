#!/usr/bin/env python3

import re
import utils


BOOK = "LOHP"
BOOK_ID = "6831850602000905"
BASE_URL = "https://www.webnovel.com/book/"

FIRST_CHAPTER = 501
LAST_CHAPTER = 726


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

for ch in range(FIRST_CHAPTER, LAST_CHAPTER + 1):
    progress.update()
    download_chapter(ch)

progress.finish()
