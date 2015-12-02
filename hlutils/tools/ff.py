#!/usr/bin/env python
#-*- coding:utf-8 -*-

u'''
find file by patterns.
'''

import os, sys
import platform
import argparse
import re

import locale
SYSENC = locale.getdefaultlocale()[1]
reload(sys)
sys.setdefaultencoding(SYSENC)

class patternerror(Exception):pass

class pattern(object):
    def __init__(self):
        pass

    def match(self, path):
        return False

class pattern_and(pattern):
    def __init__(self, patterns):
        self.__patterns = []
        self.__patterns += patterns

    def match(self, path):
        for ptn in self.__patterns:
            if not ptn.match(path):
                return False
        return True

class pattern_or(pattern):
    def __init__(self, patterns):
        self.__patterns = []
        self.__patterns += patterns

    def match(self, path):
        for ptn in self.__patterns:
            if ptn.match(path):
                return True
        return False

class pattern_not(pattern):
    def __init__(self, ptn):
        self.__ptn = ptn

    def match(self, path):
        return not self.__ptn.match(path)

class pattern_regex(pattern):
    def __init__(self, strpattern, casesense):
        if casesense:
            flag = 0
        else:
            flag = re.IGNORECASE
        self.__re = re.compile(strpattern, flag)

    def match(self, path):
        return self.__re.match(os.path.basename(path))

class pattern_glob(pattern_regex):
    def __init__(self, strpattern, casesense):
        chars = []
        chars.append(u'^')
        for c in strpattern:
            if c in [u'^', u'$', u'.', u'+', u'{', u'}', u'[', u']', u'(', u')', u'|']:
                chars.append(u'\\')
            elif c in [u'?', u'*']:
                chars.append(u'.')
            chars.append(c)
        chars.append(u'$')
        strpattern = u''.join(chars)
        super(pattern_glob, self).__init__(strpattern, casesense)

class pattern_size(pattern):
    RE_PTN = re.compile(ur'^\s*(?:(0[x][a-f0-9]+|\d+(?:\.\d+)?)([KMG]?))?\s*:\s*(?:(0[x][a-f0-9]+|\d+(?:\.\d+)?)([KMG]?))?\s*$', re.IGNORECASE)
    def __init__(self, strpattern):
        matchobj = self.RE_PTN.match(strpattern)
        if not matchobj:
            raise patternerror(u'size pattern error: %s' % strpattern)
        min_n, min_u, max_n, max_u = map(matchobj.group, range(1, 5))
        min = pattern_size.get_number(min_n, min_u)
        max = pattern_size.get_number(max_n, max_u)
        if min is None:
            min = 0
        if max is None:
            max = 0xffffffffffffffff
        if min > max:
            raise patternerror(u'size pattern error: %s' % strpattern)
        self.__min = min
        self.__max = max

    @staticmethod
    def get_number(n, u):
        if not n:
            return None
        if n.lower().startswith(u'0x'):
            nn = int(n, 16)
        else:
            nn = float(n)
        u = u.lower()
        if u == 'k':
            nn *= 1024
        elif u == 'm':
            nn *= 1024 ** 2
        elif u == 'g':
            nn *= 1024 ** 3
        return nn

    def match(self, path):
        size = os.stat(path).st_size
        return self.__min <= size <= self.__max

def parse_command_line():
    parser = argparse.ArgumentParser(prog=u'ff')
    parser.add_argument(u'dirname', nargs=u'*', default=['.'], help=u'dir for searching')
    parser.add_argument(u'-p', u'--pattern', action=u'append', help=u'file name pattern use ? and *')
    parser.add_argument(u'-e', u'--regex', action=u'append', help=u'file name pattern use regex expression')
    parser.add_argument(u'-z', u'--size', action=u'append', help=u'file size pattern like 1M:2.5G')
    parser.add_argument(u'-R', u'--norecurse', action=u'store_true', help=u'do NOT recurse the dir')
    parser.add_argument(u'-c', u'--casesense', action=u'store_true', help=u'case sencse')
    parser.add_argument(u'-S', u'--backslash', action=u'store_true', help=u'use "\\" instead of "/"')
    parser.add_argument(u'-q', u'--quote', action=u'store_true', help=u'add quote around file names')
    parser.add_argument(u'-v', u'--invert', action=u'store_true', help=u'print files NOT matching')
    parser.add_argument(u'-d', u'--dir', action=u'store_true', help=u'search dirs instead of files')

    return parser.parse_args(sys.argv[1:])

def make_patterns(ns):
    allptns = []
    nameptns = []
    if ns.pattern:
        nameptns += map(lambda p: pattern_glob(p.decode(SYSENC, 'replace'), ns.casesense), ns.pattern)
    if ns.regex:
        nameptns += map(lambda r: pattern_regex(r.decode(SYSENC, 'replace'), ns.casesense), ns.regex)
    if not nameptns:
        nameptns.append(pattern_regex(u'.*', ns.casesense))
    allptns.append(pattern_or(nameptns))

    sizeptns = []
    if not ns.dir and ns.size:
        sizeptns += map(lambda s: pattern_size(s.decode(SYSENC, 'replace')), ns.size)
    if sizeptns:
        allptns.append(pattern_or(sizeptns))

    ptn = pattern_and(allptns)

    if ns.invert:
        return pattern_not(ptn)
    else:
        return ptn


def print_path(path, ns):
    quote = "'" if not platform.platform().startswith("Windows") else '"'
    if ns.quote:
        sys.stdout.write(quote)
    sys.stdout.write(path.replace('/', '\\') if ns.backslash else path.replace('\\', '/'))
    if ns.quote:
        sys.stdout.write(quote)
    sys.stdout.write('\n')

def search_file(ptn, ns):
    if not ns.dirname:
        ns.dirname.append('.')
    for dir in ns.dirname:
        if re.match(r'^\s*[a-zA-Z]:\s*$', dir):
            #if is C: D: add / to the tail
            dir = dir + '/'
        if ns.norecurse:
            files = os.listdir(dir.decode(SYSENC, 'replace'))
            for f in files:
                path = os.path.join(dir, f).encode(SYSENC, 'replace')
                if (not ns.dir and os.path.isfile(path)) or (ns.dir and os.path.isdir(path)):
                    if ptn.match(path):
                        print_path(path, ns)
        else:
            for root, dirs, files in os.walk(dir.decode(SYSENC, 'replace')):
                for f in (dirs if ns.dir else files):
                    path = os.path.join(root, f).encode(SYSENC, 'replace')
                    if ptn.match(path):
                        print_path(path, ns)


def main():
    ns = parse_command_line()
    try:
        ptn = make_patterns(ns)
        search_file(ptn, ns)
    except Exception, e:
        print str(e)

if __name__ == '__main__':
    main()
