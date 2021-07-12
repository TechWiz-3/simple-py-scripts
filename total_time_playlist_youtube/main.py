#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import sys
from typing import List, Tuple

sys.path.append('../html_parsing')
from youtube_com__results_search_query import get_ytInitialData
from common import seconds_to_str


def get_video_list(data: dict) -> list:
    video_list = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']
    return [video['playlistVideoRenderer'] for video in video_list]


def parse_playlist_time(url: str) -> (int, List[Tuple[str, str]]):
    """Функция парсит страницу плейлиста и подсчитывает сумму продолжительности роликов."""

    data = get_ytInitialData(url)

    total_seconds = 0
    items = []

    for video in get_video_list(data):
        title = video['title']['runs'][0]['text']
        duration_text = video['lengthText']['simpleText']
        duration_secs = int(video['lengthSeconds'])

        total_seconds += duration_secs
        items.append((title, duration_text))

    return total_seconds, items


if __name__ == '__main__':
    url = 'https://www.youtube.com/playlist?list=PLndO6DOY2cLyxQYX7pkDspTJ42JWx07AO'

    total_seconds, items = parse_playlist_time(url)

    print('Playlist:')
    for i, (title, time) in enumerate(items, 1):
        print(f'  {i}. {title} ({time})')

    print()
    print(f'Total time: {seconds_to_str(total_seconds)} ({total_seconds} total seconds)')

    """
    Playlist:
      1. Горит от чатика - Dark Souls #1 (6:41:58)
      2. Нашествие Альтруистов - Dark Souls #2 (5:26:41)
      3. ГОРИТ ОЧАГ - Dark Souls #3 (7:53:18)
      4. БОЛЬШЕ ТУПЫХ СОВЕТОВ - Dark Souls #4 (8:27:04)
      5. ДА НАЧНЕТСЯ ГОРЕНИЕ - Dark Souls #5 (7:12:00)
      6. ЖАРЬ СОСИСКИ НА МОЕМ ПЕРДАКЕ - Dark Souls #6 (6:34:32)
      7. НАКОНЕЦ-ТО! - Dark Souls #7 [ФИНАЛ] (7:35:55)
    
    Total time: 49:51:28 (179488 total seconds)
    """