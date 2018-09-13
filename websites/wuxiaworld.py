from . import Website


class Wuxiaworld(Website):
    name = "wuxiaworld"
    url = "https://www.wuxiaworld.com"

    chapter_separator_start = '<div class="fr-view">'
    chapter_separator_end = '<a href="/novel/'
