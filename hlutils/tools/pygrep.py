#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
grep written in python.
'''

import sys
import platform
import argparse
import re
import hlutils.consolecolor as cc
try:
    import cchardet as chardet
except:
    import chardet

import locale
SYSENC = locale.getdefaultlocale()[1]

FILES_NONE = 0
FILES_MATCH = 1
FILES_NOMATCH = 2
FILES_COUNT = 3

ns = None
pattern = None
onlyone = True

def parse_command():
    parser = argparse.ArgumentParser()
    parser.add_argument('-I', '--ignorecase', action='store_true', help='ignore case')
    parser.add_argument('-M', '--multiline', action='store_true', help='`^` and `$` match beginning and end of each line')
    parser.add_argument('-D', '--dotall', action='store_true', help='Make the `.` special character match any character at all, including a newline; without this flag, `.` will match anything except a newline')
    parser.add_argument('-t', '--highlight', action='store_true', help='highlight matchings')
    parser.add_argument('-v', '--invertmatch', action='store_true', help='select non-matching lines')
    parser.add_argument('-s', '--nomessages', action='store_true', help='suppress error messages')
    parser.add_argument('-H', '--withfilename', action='store_true', help='print the filename for each match')
    parser.add_argument('-n', '--linenumber', action='store_true', help='print line number with output lines')
    parser.add_argument('-C', '--column', action='store_true', help='print column number with output lines')
    parser.add_argument('-S', '--separately', action='store_true', help='matchings in one line will be printed separately')
    parser.add_argument('-o', '--onlymatching', action='store_true', help='show only the part of a line matching PATTERN')
    parser.add_argument('--label', action='store', default='(standard input)', help='set label of stdin, default is (standard input)')
    parser.add_argument('-l', '--fileswithmatching', dest='showfiles', default=FILES_NONE, action='store_const', const=FILES_MATCH, help='print only names of FILEs containing matches')
    parser.add_argument('-L', '--fileswithoutmatching', dest='showfiles', action='store_const', const=FILES_NOMATCH, help='print only names of FILEs containing no matche')
    parser.add_argument('-c', '--count', dest='showfiles', action='store_const', const=FILES_COUNT, help='print only a count of matching lines per FILE')
    parser.add_argument('pattern', help='pattern use python regex')
    parser.add_argument('file', nargs='*', help='file to search')
    global ns
    ns = parser.parse_args(sys.argv[1:])

def show_error(msg):
    if not ns.nomessages:
        print(msg)

def decode_bytes(string):
    encs = ["utf-8", "gbk", "big5", "latin-1"]
    for enc in encs:
        try:
            return string.decode(enc, "strict")
        except UnicodeError:
            pass
    return string.decode("utf-8", "ignore")


def search_file(fname):
    if fname == ns.label:
        string = sys.stdin.read()
    else:
        try:
            string = open(fname, 'rb').read()
            string = string.replace(b"\r", b"")
        except IOError as e:
            show_error(str(e))
            return
    string = decode_bytes(string)
    if ns.showfiles == FILES_NONE:
        search(string.split('\n'), fname)
    elif ns.showfiles == FILES_COUNT:
        ret = 0
        for obj in pattern.finditer(string):
            ret += 1
        print('%s:%d' % (fname, ret))
    elif ns.showfiles == FILES_MATCH and pattern.search(string):
        print(fname)
    elif ns.showfiles == FILES_NOMATCH and not pattern.search(string):
        print(fname)


def search(lines, fname):
    number = 0
    if lines[-1] == "":
        lines = lines[:-1]
    for line in lines:
        number += 1
        out = []
        if ns.withfilename or not onlyone:
            out.append(fname)
        if ns.linenumber:
            out.append(str(number))
        if ns.invertmatch:
            if not pattern.search(line):
                out.append(line)
                print(':'.join(out))
        else:
            if not ns.highlight:
                if not ns.separately:
                    obj = pattern.search(line)
                    if obj:
                        if ns.onlymatching:
                            line = obj.group(0)
                        if ns.column:
                            out.append(str(obj.start() + 1))
                        out.append(line)
                        print(':'.join(out))
                else:
                    for obj in pattern.finditer(line):
                        if ns.column:
                            print(':'.join(out + [str(obj.start() + 1), line]))
                        else:
                            print(':'.join(out + [line]))
            else:
                if not ns.separately:
                    offset = 0
                    first = 1
                    for obj in pattern.finditer(line):
                        if first:
                            if ns.column:
                                out.append(str(obj.start() + 1))
                            print(':'.join(out), end='')
                            if len(out):
                                print(':', end='')
                            first = 0
                        print(line[offset:obj.start()], end='')
                        cc.output(obj.group(0), cc.YELLOW)
                        offset = obj.end()
                    if not first:
                        print(line[offset:])
                else:
                    for obj in pattern.finditer(line):
                        if ns.column:
                            print(':'.join(out + [str(obj.start() + 1)]), end='')
                            print(':', end='')
                        else:
                            print(':'.join(out), end='')
                            if len(out):
                                print(':', end='')
                        print(line[:obj.start()], end='')
                        cc.output(obj.group(0), cc.YELLOW)
                        print(line[obj.end():])

def main():
    parse_command()
    global pattern
    flags = 0
    if ns.ignorecase:
        flags |= re.IGNORECASE
    if ns.multiline:
        flags |= re.MULTILINE
    if ns.dotall:
        flags |= re.DOTALL
    pattern = re.compile(ns.pattern, flags)
    if not ns.file:
        ns.file.append(ns.label)
    global onlyone
    onlyone = len(ns.file) == 1
    for fname in ns.file:
        search_file(fname)

if __name__ == '__main__':
    main()
