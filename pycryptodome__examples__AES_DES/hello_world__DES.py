#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


# SOURCE: https://github.com/Legrandin/pycryptodome


# pip install pycryptodome
# OR:
# pip install pycryptodomex


from Crypto.Cipher import DES


# SOURCE: https://github.com/gil9red/SimplePyScripts/blob/713f8b9c4f607b4016c2b1d3209084c752691460/pycryptodome__examples__AES_DES/info_security.py#L38
def pad(s: bytes, bs=8) -> bytes:
    pad_size = bs - (len(s) % bs)
    return s + bytes([pad_size] * pad_size)


def unpad(s: bytes) -> bytes:
    return s[:-ord(s[len(s) - 1:])]


key = b'abcdefgh'


des = DES.new(key, DES.MODE_ECB)
text = b'Hello World!'
padded_text = pad(text)

encrypted_text = des.encrypt(padded_text)
print(encrypted_text)  # b'\x95\x123.Y\x8dN\x17\xcc\xf1\xc7\\\xc7\xac\xbc\x7f'

data = des.decrypt(encrypted_text)
print(data)  # b'Hello World!\x04\x04\x04\x04'

data = unpad(data)
print(data)  # b'Hello World!'
