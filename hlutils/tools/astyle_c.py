#!/usr/bin/env python
# -*- coding:utf-8 -*-
ur'''
format C/C++/Java code using astyle
'''
import os
import sys
import subprocess as sp

def main():
    CMD = "astyle --style=allman --indent=spaces=4 --align-pointer=type --align-reference=type --indent-cases --indent-preproc-define --indent-col1-comments --pad-oper --pad-header --unpad-paren --add-brackets --convert-tabs --mode=c -z2 -n "

    if len(sys.argv) == 1:
        pop = sp.Popen(CMD, bufsize = -1, stdout = sp.PIPE, stderr = sp.PIPE, universal_newlines = True)
        outdata, outerr = pop.communicate()
        if outdata:
            sys.stdout.write(outdata[:-1]) #astyle使用stdout输出时会多出一个换行符，所以这里要去掉
    else:
        sp.call(CMD + " ".join(['"' + arg + '"' for arg in sys.argv[1:]]))

if __name__ == "__main__":
    main()
