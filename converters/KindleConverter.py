import utils
from . import BookConverter

import re


_SPOILER_TEXT = 'class="collapseomatic_content'
_OUTPUT_DIR = "kindle"
_CHAPTER_SEPERATOR = "*****"
_LINES_BETWEEN_CHAPTERS = 6


class KindleConverter(BookConverter):
    name = "Kindle Converter"

    def convert_chapters(self, chapter_start, chapter_end):
        name = self.config.get("name", self.book)
        file_name = "{} - Chapters {}-{}.txt".format(name if len(name) <= 20 else self.book.upper(), chapter_start, chapter_end)
        output_file = utils.get_book_dir(self.book, _OUTPUT_DIR, file_name)
        title = "{} - Chapters {}-{}".format(name, chapter_start, chapter_end)
        skip_chapters = self.config.get("skip_chapters", [])

        utils.ensure_dir(utils.get_book_dir(self.book, _OUTPUT_DIR))
        progress = utils.ProgressBar(chapter_start, chapter_end, "Converting")

        with open(output_file, "wb") as f:
            f.write("{}\n\n\n".format(title).encode())

            for ch in range(chapter_start, chapter_end+1):
                if ch in skip_chapters:
                    continue
                
                progress.update()
                if self.config.get("add_chapter_titles", False):
                    f.write("Chapter {}\n\n".format(ch).encode())
                f.write(self.process_chapter(ch).encode())

                if ch != chapter_end:
                    f.write("{0}{1}{0}".format(
                        "\n"*_LINES_BETWEEN_CHAPTERS,
                            _CHAPTER_SEPERATOR).encode())
        progress.finish()

    def process_chapter(self, ch):
        text = self.load_chapter(ch)

        text = text.replace("\n", "")
        text = text.replace("<br>", "\n")
        text = text.replace("<br/>", "\n")
        text = text.replace("<br />", "\n")
        text = text.replace("<p>", "")
        text = text.replace("</p>", "\n\n")
        text = text.replace("<strong>", "")
        text = text.replace("</strong>", "\n")
        text = text.replace("<em>", "**")
        text = text.replace("</em>", "**")
        text = text.replace("&#8211;", "–")
        text = text.replace("&#8212;", "—")
        text = text.replace("&#8217;", "’")
        text = text.replace("&#8230;", "…")
        text = text.replace("&#8220;", "“")
        text = text.replace("&#8221;", "”")
        text = text.replace("&#8216;", "‘")
        text = text.replace("&hellip;", "…")
        text = re.sub(r'<sentence class="original">.*?</sentence>', "", text, flags=re.DOTALL)
        text = text.replace("</sentence>", "\n\n")

        # Remove chapter title spoiler tag
        spoiler = text.find(_SPOILER_TEXT)
        if spoiler != -1:
            text = text[text.find(">", spoiler)+1:]

        # Add Footnotes inline
        #text = process_footnotes(text)

        # Remove "sponsored by"
        text = re.sub(r"[—–-]*\n\n.*?This chapter.+?sponsored.*?\n", "", text)

        # Remove audio
        text = re.sub(r"[—–]{2,}.*?<script>document.createElement\('audio'\);</script>.*?</audio>", "", text, flags=re.S)
        text = re.sub(r'\n.*\n<audio.*?</audio>', "", text)

        # Clean <em> stars
        text = re.sub(r".\n\*\*\n", "**\n", text)

        # Clean leftover tags
        text = re.sub(r"<.*?>", "", text)

        return text.strip()


# def get_footnote_num(txt_before):
#     return int(txt_before[txt_before.find("-")+1:])

# def get_footnotes(text):
#     footnotes = []
#     footnotes_start = text.find('<div class="footnotedivider"></div>')
#     if footnotes_start == -1:
#         return footnotes

#     num = get_footnote_num(text[footnotes_start-11:footnotes_start-2])
#     footnotes.append(num)
#     text = text[footnotes_start+35:]

#     i = 1
#     while True:
#         pos = text.find('id="fn-{}-{}"'.format(num, i))
#         if pos == -1:
#             break
#         pos = pos + 10 + len(str(num)) + len(str(i))
#         end = text.find('<span class="footnotereverse">', pos)
#         footnotes.append(text[pos:end].strip())
#         i += 1
    
#     return footnotes

# def process_footnotes(text):
#     footnotes = get_footnotes(text)
#     if not footnotes:
#         return text
#     fnum = footnotes[0]
#     for i in range(len(footnotes)-1):
#         ftext = '<sup class="footnote"><a href="#fn-{0}-{1}" id="fnref-{0}-{1}" onclick="return fdfootnote_show({0})">{1}</a></sup>'.format(fnum, i+1)
#         if text.find(ftext) == -1:
#             print("Footnote", i+1,  "not found")
#             return "ERROR"
#         text = text.replace(ftext, "[{}]".format(footnotes[i+1]))
#     return text


# ISSTH_BOOK = 1

# ISSTH_BOOK_TITLES = ["",
#                "Patriarch Reliance", #1
#                "", #2
#                "", #3
#                "Five Color Paragon", #4
#                "Nirvanic Rebirth. Blood Everywhere!", #5
#                "Fame That Rocks the Ninth Mountain; the Path to True Immortality", #6
#                "Immortal Ancient Builds a Bridge Leaving the Ninth Mountain!", #7
#                "My Mountain and Sea Realm" #8
#                ]
# ISSTH_CHAPTERS = (1,96,205,314,629,801,1005,1212,1410,1558)
# ISSTH_SKIP_CHAPTERS = (583, 1377)
# ISSTH_TITLE = "I Shall Seal The Heavens - Book {} - {}".format(ISSTH_BOOK, ISSTH_BOOK_TITLES[ISSTH_BOOK])
# ISSTH_INPUT_FILENAME = "issth-new/book-{book}-chapter-{chapter}.html"
# ISSTH_OUTPUT_FILENAME = "ISSTH Book {} - {}.txt".format(ISSTH_BOOK, ISSTH_BOOK_TITLES[ISSTH_BOOK])
# ISSTH_CHAPTER_RANGE = (ISSTH_CHAPTERS[ISSTH_BOOK-1], ISSTH_CHAPTERS[ISSTH_BOOK])

# WMW_TITLE = "Warlock of the Magus World - Chapters {}-{}".format(*CHAPTER_RANGE)
# WMW_INPUT_FILENAME = "wmw-new/chapter-{chapter}.html"
# WMW_OUTPUT_FILENAME = "WMW Chapters {}-{}.txt".format(*CHAPTER_RANGE)

# SA_TITLE = "Skyfire Avenue - Chapters {}-{}".format(*CHAPTER_RANGE)
# SA_INPUT_FILENAME = "SA/chapter-{chapter}.html"
# SA_OUTPUT_FILENAME = "Skyfire Avenue - Chapters {}-{}.txt".format(*CHAPTER_RANGE)
