import utils
from . import BookConverter

import os


_OUTPUT_DIR = "html"

_HTML_BEFORE = """
<html>
<head>
    <link rel="stylesheet" href="style.css">
    <script src="script.js"></script>
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

    def convert_chapters(self, chapter_start, chapter_end):
        output_dir = utils.get_book_dir(self.book, _OUTPUT_DIR)
        utils.ensure_dir(output_dir)
        skip_chapters = self.config.get("skip_chapters", [])

        for ch in range(chapter_start, chapter_end + 1):
            if ch in skip_chapters:
                print("Skipping chapter", ch)
                continue
            print("Processing chapter", ch)
            
            links = {
                "prev": self.filename_of_chapter(ch - 1) + ".html",
                "nxt": self.filename_of_chapter(ch + 1) + ".html"
            }
            
            with open(os.path.join(output_dir, self.filename_of_chapter(ch) + ".html"), "wb") as f:
                before = _HTML_BEFORE.format(**links)
                after = _HTML_AFTER.format(**links)
                output = before + self.load_chapter(ch) + after
                f.write(output.encode("utf-8"))
