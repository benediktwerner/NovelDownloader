import time
import re
import os.path as path

import utils
import websites


SLEEP_BETWEEN_DOWNLOADS = 1


class DownloadException(Exception):
    pass


def download_chapter(url, file_path, config):
    website = config["website"]
    content = utils.download_url(url, cookies=website.get_cookies())
    if content is None:
        raise DownloadException(
            "Failed to download chapter from {}".format(url))

    if website.cookies_expired(content):
        website.update_cookies()
        content = utils.download_url(url, cookies=website.get_cookies())
        if content is None:
            raise DownloadException(
                "Failed to download chapter from {}".format(url))

    chapter_content = website.get_chapter_content(content)

    if chapter_content is None:
        utils.ensure_dir("dumps")
        with open("dumps/content.html", "w") as f:
            f.write(content)

        raise DownloadException(
            "Got empty chapter content from {}. Content dumped.".format(url))

    with open(file_path, "bw") as f:
        f.write(chapter_content.encode("utf-8"))


def download_chapters(chapter_start, chapter_end, config):
    raw_dir = utils.get_raw_dir(config["book"])
    utils.ensure_dir(raw_dir)

    progress = utils.ProgressBar(chapter_start, chapter_end, "Downloading")

    for ch in range(chapter_start, chapter_end+1):
        progress.update()

        url = config["website"].get_chapter_url(ch, config)
        file_name = utils.chapter_name(ch)
        file_path = path.join(raw_dir, file_name + ".html")

        download_chapter(url, file_path, config)
        time.sleep(SLEEP_BETWEEN_DOWNLOADS)

    progress.finish()
