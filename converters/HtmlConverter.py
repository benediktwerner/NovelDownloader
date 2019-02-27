import utils
from . import BookConverter

import os
import re


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
    name = "Html Converter"

    def process_chapter(self, ch):
        text = self.load_chapter(ch)
        text = re.sub(
            r'<sentence class="original">.*?</sentence>', "", text, flags=re.DOTALL
        )
        text = text.replace("</sentence>", "</sentence><br /><br />")
        return text

    def convert_chapters(self, chapter_start, chapter_end):
        output_dir = utils.get_book_dir(self.book, _OUTPUT_DIR)
        utils.ensure_dir(output_dir)
        skip_chapters = self.conf.get("skip_chapters", [])
        progress = utils.ProgressBar(chapter_start, chapter_end, "Converting")

        for ch in range(chapter_start, chapter_end + 1):
            if ch in skip_chapters:
                continue
            progress.update()

            links = {
                "title": self.book.upper() + " &mdash; " + utils.chapter_name(ch),
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
