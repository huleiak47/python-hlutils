#!/usr/bin/env python
#-*- coding:utf-8 -*-
u'''
execute command in loop mode
'''

# Changes:
#   ** version 1.1 2013-10-11 Hulei **
#       1. 修正命令行有^字符会丢失的问题
#   ** version 1.0 2012-08-06 Hulei **
#       1. init update

import os
import sys
from subprocess import call
from hlutils.args import to_windows_cmd

def help():
    print """
    forcmd -n 100 -e command ...
    usage:
        -h, --help      show this help message
        -n maxloop      set loop count, default is {}
        -e              exit when command exit code is not 0
        """.format(sys.maxint)

def main():
    index = 1
    maxloop = sys.maxint
    exit_when_faild = 0
    while index < len(sys.argv):
        if sys.argv[index] == '-n':
            maxloop = int(sys.argv[index + 1], 0)
            index += 2
        elif sys.argv[index] == '-e':
            exit_when_faild = 1
            index += 1
        elif sys.argv[index] in ['-h', '--help']:
            help()
            sys.exit(0)
        else:
            break

    command = sys.argv[index:]
    for i in xrange(maxloop):
        print "Loop:", i + 1
        cmd = to_windows_cmd(command)
        print cmd
        ret = call(cmd, shell=True)
        if exit_when_faild and ret != 0:
            print "Exit code of command is %d." % ret
            sys.exit(ret)
    print "Loop over."
    sys.exit(0)

if __name__ == '__main__':
    main()
