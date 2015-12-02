#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Colorful svn status.
'''

import sys
import subprocess as sp
from hlutils import consolecolor as cc

def main():
    args = sys.argv[1:]
    if args and args[0] == "-s":
        single = True
        args = args[1:]
    else:
        single = False

    try:
        output = sp.check_output(["svn","st"] + args, shell = 0)
    except sp.CalledProcessError as e:
        sys.stdout.write(e.output)
        sys.exit(e.returncode)

    for line in output.split("\n"):
        if not line:
            continue
        if line.startswith("M"):
            color = cc.RED
        elif line.startswith("C"):
            color = cc.YELLOW
        elif line.startswith("A"):
            color = cc.PURPLE
        elif line.startswith("D"):
            color = cc.SKYBLUE
        else:
            print line.split()[1] if single else line
            continue
        cc.output(line.split()[1] if single else line, color)
        print

if __name__ == "__main__":
    main()
