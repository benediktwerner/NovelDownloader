import asyncio
import os.path as path
import re
import time
from typing import List

import aiohttp

import utils
import websites
from config import Config


class Downloader:
    def __init__(self, config: Config):
        self.config = config

    def download_chapters(self, chapter_list: List[int]):
        try:
            asyncio.get_event_loop().run_until_complete(
                self.__download_chapters(chapter_list)
            )
            return True
        except aiohttp.client_exceptions.ClientConnectorError as e:
            print("Error:", e)
            return False

    async def __download_chapters(self, chapter_list: List[int]):
        raw_dir = utils.get_raw_dir(self.config.book)
        utils.ensure_dir(raw_dir)

        async with aiohttp.ClientSession() as session:
            print("\nPreparing download ...\r", end="", flush=True)
            await self.config.website.prepare_download(self.config, session)

            self.progress = utils.ProgressBar(len(chapter_list), "Downloading")

            tasks = []
            for ch in chapter_list:
                tasks.append(self.__download_chapter(ch, session))

            await asyncio.gather(*tasks)
            self.progress.finish()

    async def __download_chapter(self, chapter: int, session: aiohttp.ClientSession):
        content = await self.config.website.download_chapter(
            chapter, self.config, session
        )

        if content is None:
            raise Exception(f"Got empty chapter content from chapter {chapter}")

        raw_dir = utils.get_raw_dir(self.config.book)
        file_name = utils.chapter_name(chapter)
        file_path = path.join(raw_dir, file_name + ".html")

        with open(file_path, "bw") as f:
            f.write(content.encode("utf-8"))

        self.progress.update()
