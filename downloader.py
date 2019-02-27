import asyncio
import os.path as path
import re
import time

import aiohttp

import utils
import websites


async def download_chapter(chapter, config, progress, session):

    content = await config["website"].download_chapter(chapter, config, session)

    if content is None:
        utils.ensure_dir("dumps")
        with open("dumps/content.html", "w") as f:
            f.write(content)

        raise Exception(
            "Got empty chapter content from chapter {}. Content dumped.".format(chapter)
        )

    raw_dir = utils.get_raw_dir(config["book"])
    file_name = utils.chapter_name(chapter)
    file_path = path.join(raw_dir, file_name + ".html")

    with open(file_path, "bw") as f:
        f.write(content.encode("utf-8"))

    progress.update()


async def __download_chapters(chapter_start, chapter_end, config):
    raw_dir = utils.get_raw_dir(config["book"])
    utils.ensure_dir(raw_dir)

    async with aiohttp.ClientSession() as session:
        print("\nPreparing download ...\r", end="", flush=True)
        await config["website"].prepare_download(config, session)

        progress = utils.ProgressBar(chapter_start, chapter_end, "Downloading")

        tasks = []
        for ch in range(chapter_start, chapter_end + 1):
            tasks.append(download_chapter(ch, config, progress, session))

        await asyncio.gather(*tasks)

        progress.finish()


def download_chapters(chapter_start, chapter_end, config):
    asyncio.get_event_loop().run_until_complete(
        __download_chapters(chapter_start, chapter_end, config)
    )
