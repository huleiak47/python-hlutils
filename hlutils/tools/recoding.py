#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
Change text encoding from stdin to stdout.
'''

import os
import sys
#import cchardet as chardet
import chardet

# open stdin/stdout as bytes mode
stdin = os.fdopen(sys.stdin.fileno(), 'rb')
stdout = os.fdopen(sys.stdout.fileno(), 'wb')

def try_decode(text):
    codecs = ['ascii', 'gb2312', 'utf-8', 'gbk']
    for codec in codecs:
        try:
            unistr = text.decode(codec)
            return codec, unistr
        except UnicodeError:
            pass
    return None, None

def test_decode(text, destcoding):
    ret = chardet.detect(text)

    if ret['encoding'] not in ['', 'ascii', destcoding]:
        try:
            text = text.decode(ret['encoding']).encode(destcoding)
        except Exception:
            pass
    stdout.write(text)


def main():
    destcoding = 'utf-8'

    if len(sys.argv) > 1:
        destcoding = sys.argv[1]

    text = stdin.read()
    codec, unistr = try_decode(text)
    mustenc = True
    if codec == 'ascii':
        mustenc = False
    elif codec in ('gb2312', 'gbk'):
        mustenc = destcoding.lower() not in ('gbk', 'gb2312', 'gb18030')
    elif codec == 'utf-8':
        mustenc = destcoding.lower() not in ('utf-8', 'utf8')
    else:
        test_decode(text, destcoding)
        return

    if mustenc:
        stdout.write(unistr.encode(destcoding, 'replace'))
    else:
        stdout.write(text)

if __name__ == '__main__':
    main()
