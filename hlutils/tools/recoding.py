#!/usr/bin/env python
#-*- coding:utf-8 -*-
u'''
Change text encoding from stdin to stdout.
'''

import sys
#import cchardet as chardet
import chardet

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
    sys.stdout.write(text)


def main():
    destcoding = 'utf-8'

    if len(sys.argv) > 1:
        destcoding = sys.argv[1]

    text = sys.stdin.read()
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
        sys.stdout.write(unistr.encode(destcoding, 'replace'))
    else:
        sys.stdout.write(text)

if __name__ == '__main__':
    main()
