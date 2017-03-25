#!/usr/bin/env python
# -*- coding:utf-8 -*-
r'''
format C/C++/Java code using astyle
'''
import os
import sys
import subprocess as sp

stdin = os.fdopen(sys.stdin.fileno(), "rb")
stdout = os.fdopen(sys.stdout.fileno(), "wb")


def main():
    CMD = "astyle --style=allman --indent=spaces=4 --align-pointer=type --align-reference=type --indent-cases --indent-preproc-define --indent-col1-comments --pad-oper --pad-header --unpad-paren --add-brackets --convert-tabs --mode=c -z2 -n "

    if len(sys.argv) == 1:
        pop = sp.Popen(CMD, bufsize=-1, stdin=stdin, stdout=stdout, stderr =sp.DEVNULL, universal_newlines=True)
        pop.wait()
    else:
        sp.call(CMD + " ".join(['"' + arg + '"' for arg in sys.argv[1:]]))

if __name__ == "__main__":
    main()
