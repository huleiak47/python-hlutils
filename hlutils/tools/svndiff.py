#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Colorful svn diff.
'''

import sys
import subprocess as sp
from hlutils import consolecolor as cc

def main():
    try:
        output = sp.check_output(["svn","diff"] + sys.argv[1:], shell = 0)
    except sp.CalledProcessError as e:
        sys.stdout.write(e.output)
        sys.exit(e.returncode)

    for line in output.split("\n"):
        if line.startswith("Index:") or line.startswith("==="):
            color = cc.YELLOW
        elif line.startswith("+++") or line.startswith("---"):
            color = cc.SKYBLUE
        elif line.startswith("@@"):
            color = cc.PURPLE
        elif line.startswith("-"):
            color = cc.RED
        elif line.startswith("+"):
            color = cc.GREEN
        elif line.startswith(" "):
            print line
            continue
        else:
            continue
        cc.output(line, color)
        print

if __name__ == "__main__":
    main()
