#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import json
import os
import time
from pathlib import Path

from main import find


DIR = Path(__file__).resolve().parent
DIR_CACHE = DIR / 'cache.json'

try:
    cache = json.load(open(DIR_CACHE, encoding='utf-8'))
except:
    cache = dict()

DIR_GAMES = Path(os.path.expanduser(r'~\Desktop\Пройти'))
game_names = [p.stem for p in DIR_GAMES.glob('*.lnk')]

changed = False
for game in game_names:
    if game in cache:
        continue

    data = find(game)
    if data:
        time_obj = data['Основной сюжет']
        cache[game] = {
            'text': time_obj.text,
            'seconds': time_obj.seconds,
        }
        changed = True
    else:
        cache[game] = None

    time.sleep(1)

if changed:
    json.dump(cache, open(DIR_CACHE, 'w', encoding='utf-8'), indent=4, ensure_ascii=False)

items = [
    (game, time_obj['text'], time_obj['seconds'])
    for game, time_obj in cache.items()
    if time_obj
]

# Сортировка по возрастанию времени прохождения
items.sort(key=lambda x: x[2])

print('Первые 10 игр с минимум времени прохождения:')
for i, (game, time_text, _) in enumerate(items[:10], 1):
    print(f'{i:2}. {game!r}: {time_text}')
"""
Первые 10 игр с минимум времени прохождения:
 1. 'FOTONICA': 2 ч. 11 мин.
 2. 'The Wild Eight': 4 ч.
 3. 'Sonic Forces': 4 ч. 12 мин.
 4. 'Halo - Spartan Assault': 4 ч. 17 мин.
 5. 'NecroVision Lost Company': 4 ч. 52 мин.
 6. 'Niko - Through the Dream': 5 ч. 21 мин.
 7. 'FEZ': 5 ч. 52 мин.
 8. 'Lucius': 6 ч. 13 мин.
 9. 'Flashback': 6 ч. 14 мин.
10. 'True Crime - New York City': 7 ч.
"""
