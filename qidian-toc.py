#!/usr/bin/env python3

import re
import utils


BOOK = "LOHP"


with open(utils.get_book_dir(BOOK, "toc-raw.txt")) as f:
    toc_raw = "".join(f.readlines())

chapter_ids = re.findall('data-cid="(.*?)"', toc_raw)

with open(utils.get_book_dir(BOOK, "toc.txt"), "w") as f:
    for ch in chapter_ids:
        print(ch, file=f)
