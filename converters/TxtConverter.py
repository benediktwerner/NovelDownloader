import html
import re

import utils

from . import BookConverter

_SPOILER_TEXT = 'class="collapseomatic_content'
_OUTPUT_DIR = "txt"
_CHAPTER_SEPERATOR = "*****"
_LINES_BETWEEN_CHAPTERS = 6


class TxtConverter(BookConverter):
    name = "TXT Converter"

    def convert_chapters(self, chapter_start: int, chapter_end: int):
        name = self.config.name or self.config.book
        file_name = "{} - Chapters {}-{}.txt".format(
            name if len(name) <= 20 else self.config.book.upper(),
            chapter_start,
            chapter_end,
        )
        output_file = utils.get_book_dir(self.config.book, _OUTPUT_DIR, file_name)
        title = f"{name} - Chapters {chapter_start}-{chapter_end}"

        utils.ensure_dir(utils.get_book_dir(self.config.book, _OUTPUT_DIR))
        progress = utils.ProgressBar(chapter_end - chapter_start + 1, "Converting")

        with open(output_file, "wb") as f:
            f.write("{}\n\n\n".format(title).encode())

            for ch in range(chapter_start, chapter_end + 1):
                if ch in self.config.skip_chapters:
                    continue

                progress.update()
                if self.config.add_chapter_titles:
                    f.write("Chapter {}\n\n".format(ch).encode())
                f.write(self.process_chapter(ch).encode())

                if ch != chapter_end:
                    f.write(
                        "{0}{1}{0}".format(
                            "\n" * _LINES_BETWEEN_CHAPTERS, _CHAPTER_SEPERATOR
                        ).encode()
                    )
        progress.finish()
        print("Result is in '{}'".format(output_file))

    def process_chapter(self, ch: int) -> str:
        text = self.load_chapter(ch)

        text = re.sub(r"\n\s*", "", text)
        text = text.replace("<br>", "\n")
        text = text.replace("<br/>", "\n")
        text = text.replace("<br />", "\n")
        text = text.replace("<p>", "")
        text = text.replace("</p>", "\n\n")
        text = text.replace("<strong>", "")
        text = text.replace("</strong>", "\n")
        text = text.replace("<em>", "**")
        text = text.replace("</em>", "**")
        text = re.sub(
            r'<sentence class="original">.*?</sentence>', "", text, flags=re.DOTALL
        )
        text = text.replace("</sentence>", "\n\n")

        # Remove chapter title spoiler tag
        spoiler = text.find(_SPOILER_TEXT)
        if spoiler != -1:
            text = text[text.find(">", spoiler) + 1 :]

        # Add Footnotes inline
        # text = process_footnotes(text)

        # Remove "sponsored by"
        text = re.sub(r"[—–-]*\n\n.*?This chapter.+?sponsored.*?\n", "", text)

        # Remove audio
        text = re.sub(
            r"[—–]{2,}.*?<script>document.createElement\('audio'\);</script>.*?</audio>",
            "",
            text,
            flags=re.S,
        )
        text = re.sub(r"\n.*\n<audio.*?</audio>", "", text)

        # Clean <em> stars
        text = re.sub(r".\n\*\*\n", "**\n", text)

        # Clean leftover tags
        text = re.sub(r"<.*?>", "", text)

        return html.unescape(text.strip())


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
