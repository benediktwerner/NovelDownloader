import os
import re

import utils

from . import BookConverter

_OUTPUT_DIR = "html"

_HTML_BEFORE = """
<html>
<head>
    <title>{title}</title>
    <link rel="stylesheet" href="../../../style/style.css">
    <script src="../../../style/script.js"></script>
</head>
<body>
    <a id="prev" href="{prev}">Previous</a>
    <a id="next" href="{nxt}">Next</a>
    <div id="article">
"""

_HTML_AFTER = """
    </div>
    <a id="prev" href="{prev}">Previous</a>
    <a id="next" href="{nxt}">Next</a>
    </body>
</html>
"""


class HtmlConverter(BookConverter):
    name = "HTML Converter"

    def process_chapter(self, ch: int) -> str:
        text = self.load_chapter(ch)
        text = re.sub(
            r'<sentence class="original">.*?</sentence>', "", text, flags=re.DOTALL
        )
        text = text.replace("</sentence>", "</sentence><br /><br />")
        text = re.sub(r"<script.*?</script>", "", text, flags=re.DOTALL)
        text = re.sub(r"<pirate>.*?</pirate>", "", text, flags=re.DOTALL)

        # if self.config.add_chapter_titles:
        #     text = "<strong>Chapter {}</strong><br />".format(ch) + text

        return text

    def convert_chapters(self, chapter_start: int, chapter_end: int):
        output_dir = utils.get_book_dir(self.config.book, _OUTPUT_DIR)
        utils.ensure_dir(output_dir)
        progress = utils.ProgressBar(chapter_end - chapter_start + 1, "Converting")

        for ch in range(chapter_start, chapter_end + 1):
            progress.update()

            links = {
                "title": self.config.book.upper()
                + " &mdash; "
                + utils.chapter_name(ch),
                "prev": utils.chapter_name(ch - 1) + ".html",
                "nxt": utils.chapter_name(ch + 1) + ".html",
            }

            with open(
                os.path.join(output_dir, utils.chapter_name(ch) + ".html"), "wb"
            ) as f:
                before = _HTML_BEFORE.format(**links)
                after = _HTML_AFTER.format(**links)
                output = before + self.process_chapter(ch) + after
                f.write(output.encode("utf-8"))
        progress.finish()
        print("Result is in '{}'".format(output_dir))
