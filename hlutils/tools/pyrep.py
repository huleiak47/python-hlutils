#!/usr/bin/env python
#-*- coding:utf-8 -*-
u'''
Replace str from file or stdin
'''

import os
import sys
import argparse
import re

import locale
SYSENC = locale.getdefaultlocale()[1]

def parse_command():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--from', metavar='pattern', dest='pattern', action='store', help='pattern of string to be replaced')
    parser.add_argument('-t', '--to', metavar='str', action='store', help='pattern of string to replace')
    parser.add_argument('-e', '--encoding', action='store', default=SYSENC, help='encoding of file, default ' + SYSENC)
    parser.add_argument('-i', '--inplace', action='store_true', help='change file, not print to stdout')
    parser.add_argument('-u', '--backup', metavar='ext', action='store', help='backup file before change and set file extend name')
    parser.add_argument('-b', '--binary', action='store_true', help='use binary mode to open file')
    parser.add_argument('-I', '--ignorecase', action='store_true', help='ignore case')
    parser.add_argument('-M', '--multiline', action='store_true', help='`^` and `$` match beginning and end of each line')
    parser.add_argument('-D', '--dotall', action='store_true', help='Make the `.` special character match any character at all, including a newline; without this flag, `.` will match anything except a newline')
    parser.add_argument('filename', nargs='*', help='files, if not specified, read strings from stdin')
    ns = parser.parse_args(sys.argv[1:])
    return ns

def do_replace(string, reobj, to_str):
    if reobj is None or to_str is None:
        return string
    else:
        return reobj.sub(to_str, string)


def main():
    ns = parse_command()
    reobj = None
    if ns.pattern is not None:
        if ns.encoding != SYSENC:
            ns.pattern = ns.pattern.decode(SYSENC).encode(ns.encoding)
        flags = 0
        if ns.ignorecase:
            flags |= re.IGNORECASE
        if ns.multiline:
            flags |= re.MULTILINE
        if ns.dotall:
            flags |= re.DOTALL
        reobj = re.compile(ns.pattern, flags)
    to_str = None
    if ns.to is not None:
        to_str = ns.to
    binmode = ('b' if ns.binary else '')
    if ns.filename:
        for fname in ns.filename:
            with open(fname, 'r' + binmode) as f:
                string = f.read()
                retstr = do_replace(string, reobj, to_str)
                changed = (retstr != string)
            if ns.inplace:
                if changed:
                    if ns.backup:
                        if os.path.exists(fname + ns.backup):
                            os.remove(fname + ns.backup)
                        os.rename(fname, fname + ns.backup)
                    with open(fname, 'w' + binmode) as f:
                        f.write(retstr)
            else:
                sys.stdout.write(retstr)
    else:
        retstr = do_replace(sys.stdin.read(), reobj, to_str)
        sys.stdout.write(retstr)


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        import traceback
        traceback.print_exc()
        print str(e)
        sys.exit(1)
