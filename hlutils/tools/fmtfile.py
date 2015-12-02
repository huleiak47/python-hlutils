#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
Format EOL of file.
"""

import sys
import argparse

MODE_DOS = 0
MODE_UNIX = 1
MODE_MAC = 2

def format_file(file, mode):
    with open(file, 'rb') as f:
        content = f.read()
    if mode == MODE_DOS:
        content = content.replace('\r\n', '\n')
        content = content.replace('\r', '\n')
        content = content.replace('\n', '\r\n')
    elif mode == MODE_UNIX:
        content = content.replace('\r\n', '\n')
        content = content.replace('\r', '\n')
    else:
        content = content.replace('\r\n', '\r')
        content = content.replace('\n', '\r')
    with open(file, 'wb') as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description="format EOL of file", usage='%(prog)s [--dos|--unix|--mac] file ...')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--dos', dest='mode', action='store_const', const=MODE_DOS, default=MODE_DOS, help='set EOL to dos mode (\\r\\n).')
    group.add_argument('-u', '--unix', dest='mode', action='store_const', const=MODE_UNIX, help='set EOL to unix mode (\\n).')
    group.add_argument('-m', '--mac', dest='mode', action='store_const', const=MODE_MAC, help='set EOL to mac mode (\\r).')
    parser.add_argument('file', nargs='+', type=str, help='files to be formatted.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    opts = parser.parse_args(sys.argv[1:])
    for file in opts.file:
        try:
            format_file(file, opts.mode)
        except Exception, e:
            print 'format "%s" failed. %s' % (file, str(e))



if __name__ == '__main__':
    main()

