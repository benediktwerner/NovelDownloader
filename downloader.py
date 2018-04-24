import utils

import time
import re
import os

SLEEP_BETWEEN_DOWNLOADS = 1

#ARTICLE_START = '<div class="fr-view">'
#ARTICLE_END = '<a href="/novel/'
ARTICLE_START = '<div class="chapter-body hyphenate" v-pre>'
ARTICLE_END = '<nav>'

class DownloadException(Exception):
    pass

def download_chapter(url, file_path):
    # print("Downloading chapter from:", url)
    content = utils.download_url(url)
    if content is None:
        raise DownloadException("Failed to download chapter from {}".format(url))
    
    article_start = content.find(ARTICLE_START)
    article_end = content.find(ARTICLE_END, article_start)
    if article_end <= article_start:
        raise DownloadException("Empty chapter")
    
    if article_start == -1 or article_end == -1:
        raise DownloadException("Start or end of chapter not found! ({}, {})".format(article_start, article_end))
    
    article = content[article_start+len(ARTICLE_START):article_end]
    with open(file_path, "bw") as f:
        f.write(article.encode("utf-8"))

    next_chapter_url_match = re.search(
            r'<a href="(.*?)" class="chapter-nav">\s*?Next Chapter',
            content[article_end:]
        )
    if next_chapter_url_match:
        return next_chapter_url_match.groups()[0]

def download_chapters(chapter_start, chapter_end, book, config):
    raw_dir = utils.get_raw_dir(book)
    utils.ensure_dir(raw_dir)

    if config["follow_links"]:
        chapter_names = utils.load_chapter_names(book)
        ret = utils.find_last_existing_chatper_name(chapter_names, chapter_start)
        if ret is None:
            next_chapter_url = config["first_url"]
            chapter_start = 1
        else:
            next_chapter_url = config["url"].format(base_url=config["base_url"], chapter_name=ret[0])
            chapter_start = ret[1]
        print("Starting download chain from chapter", chapter_start)
    
    progress = utils.ProgressBar(chapter_start, chapter_end, "Downloading")
    
    for ch in range(chapter_start, chapter_end+1):
        volume = utils.get_volume_from_chapter(ch, config["volumes"]) if "volumes" in config else None
        progress.update()

        if config["follow_links"]:
            url = config["base_url"] + next_chapter_url
            file_name = url.split("/")[-1]
            utils.add_chapter_name(chapter_names, ch, file_name)
        else:
            url = config["url"].format(chapter=ch, volume=volume, base_url=config["base_url"])
            file_name = config["file_pattern"].format(chapter=ch, volume=volume)
        
        file_path = os.path.join(raw_dir, file_name + ".html")
        
        next_chapter_url = download_chapter(url, file_path)
        time.sleep(SLEEP_BETWEEN_DOWNLOADS)

    progress.finish()
    
    if config["follow_links"]:
        utils.save_chapter_names(chapter_names, book)
