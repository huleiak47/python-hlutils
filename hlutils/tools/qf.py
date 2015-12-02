#!/usr/bin/env python
# -*- coding:utf-8 -*-
r'''
quick find text in files.
'''

import sys
from subprocess import call

def main():
    argc = len(sys.argv)
    if argc == 1:
        print "usage: qf [wildcard ...] regex"
        sys.exit(1)

    ffargs = []
    for arg in sys.argv[1:-1]:
        ffargs.append("-p")
        ffargs.append('"%s"' % arg)

    pattern = sys.argv[-1]
    pattern = pattern.replace("^", "^^")

    ret = call(" ".join(["ff"] + ffargs + ["|", "pyargs", "pygrep", "-Hnt", '"%s"' % pattern]), shell = True)
    sys.exit(ret)

if __name__ == "__main__":
    main()
