#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import xml.sax
import sys

from itertools import cycle

from tqdm import tqdm


# В файле значения HOUSEGUID дублируются
all_house_guid = set()


class AttrHandler(xml.sax.handler.ContentHandler):
    progress_bar = cycle('|/-\\|/-\\')

    def startElement(self, name, attrs):
        if 'HOUSEGUID' in attrs:
            all_house_guid.add(attrs['HOUSEGUID'])

        print('\r' + next(self.progress_bar), end='')
        sys.stdout.flush()

    def endDocument(self):
        print('\r', end='')


print('Сбор HOUSEGUID')

parser = xml.sax.make_parser()
parser.setContentHandler(AttrHandler())
parser.parse('AS_HOUSE_20210318_88f2df80-430a-400f-9373-da5b2c80e051.XML')

print(f'Найдено {len(all_house_guid)}')

print('Сохранение в JSON...')

with open('all_house_guid.json', 'w') as f:
    f.write('[')

    for i, guid in tqdm(enumerate(all_house_guid), total=len(all_house_guid)):
        if i > 0:
            f.write(',')
        f.write(f'"{guid}"')

    f.write(']')
