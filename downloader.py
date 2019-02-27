import time
import re
import os.path as path

import utils
import websites


SLEEP_BETWEEN_DOWNLOADS = 1


def download_chapter(chapter, file_path, config):
    content = config["website"].download_chapter(chapter, config)

    if content is None:
        utils.ensure_dir("dumps")
        with open("dumps/content.html", "w") as f:
            f.write(content)

        raise Exception(
            "Got empty chapter content from chapter {}. Content dumped.".format(chapter)
        )

    with open(file_path, "bw") as f:
        f.write(content.encode("utf-8"))


def download_chapters(chapter_start, chapter_end, config):
    raw_dir = utils.get_raw_dir(config["book"])
    utils.ensure_dir(raw_dir)

    print("\nPreparing download ...\r", end="", flush=True)
    config["website"].prepare_download(config)

    progress = utils.ProgressBar(chapter_start, chapter_end, "Downloading")

    for ch in range(chapter_start, chapter_end + 1):
        progress.update()

        file_name = utils.chapter_name(ch)
        file_path = path.join(raw_dir, file_name + ".html")

        download_chapter(ch, file_path, config)
        time.sleep(SLEEP_BETWEEN_DOWNLOADS)

    progress.finish()
