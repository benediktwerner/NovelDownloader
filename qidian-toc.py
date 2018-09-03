#!/usr/bin/env python3

import re
import utils

from sys import argv


if len(sys.argv) != 2:
    print("Usage:  ", argv[0], "BOOK_NAME")
    print("Example:", argv[0], "LOHP")
    exit(1)

BOOK = argv[1]

with open(utils.get_book_dir(BOOK, "toc-raw.txt")) as f:
    toc_raw = "".join(f.readlines())

chapter_ids = re.findall('data-cid="(.*?)"', toc_raw)

with open(utils.get_book_dir(BOOK, "toc.txt"), "w") as f:
    for ch in chapter_ids:
        print(ch, file=f)

print("Extracted", len(chapter_ids), "chapter ids")
