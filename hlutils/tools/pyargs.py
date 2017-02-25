#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
execute command using arguments from stdin.
'''

# Changes:
#   ** version 1.2 2013-10-11 Hulei **
#       1. 修正命令行有^字符会丢失的问题
#   ** version 1.1 2013-05-15 Hulei **

import os
import sys
import argparse
import re
from subprocess import call
from hlutils.args import to_windows_cmd

if sys.platform.startswith('win'):
    ARG_MAX = 8000
else:
    ARG_MAX = 255 * 1024

def parse_command():
    parser = argparse.ArgumentParser(prog='pyargs', add_help=False)
    parser.add_argument('-n', '--maxargs', type=int, default=0, help='set max args per command, default 0, means as many as possible.')
    parser.add_argument('-v', '--var', action='store_true', help='use var in commandline, auto set maxargs to 1, vars is $(PATH),$(DIR),$(NAME),$(BASE),$(EXT)')
    parser.add_argument('-p', '--printcmd', action='store_true', help='print command')
    parser.add_argument('-E', '--noexec', action='store_true', help='do not execute command(often use with -p)')
    parser.add_argument('-h', '--help', action='store_true', help='show this help message')

    index = 1
    while index < len(sys.argv):
        arg = sys.argv[index]
        if arg in ('-n', '--maxargs'):
            index += 1
        elif arg.startswith('--maxargs='):
            pass
        elif arg in ('--var', '--printcmd', '--noexec'):
            pass
        elif re.match(r'^-[vpE]+$', arg):
            pass
        elif arg in ('-h', '--help'):
            parser.print_help()
            sys.exit(0)
        else:
            break
        index += 1

    return parser.parse_args(sys.argv[1:index]), index

def replace_vars(cmdheads, path):
    dir = os.path.dirname(path)
    name = os.path.basename(path)
    base, ext = os.path.splitext(name)
    if ext.startswith('.'):
        ext = ext[1:]
        cmds = [command.replace('$(PATH)', path).replace('$(DIR)', dir).replace('$(NAME)', name).replace('$(BASE)', base).replace('$(EXT)', ext) for command in cmdheads]
    return cmds

def execute_command(cmds, ns):
    if cmds:
        if ns.printcmd:
            print(' '.join(cmds))
        if not ns.noexec:
            call(to_windows_cmd(cmds), shell=True)

def main():
    ns, index = parse_command()

    cmdheads = sys.argv[index:]
    offset = 0
    lines = sys.stdin.readlines()
    length = len(lines)

    if ns.var:
        for line in lines:
            cmds = replace_vars(cmdheads, line.strip())
            execute_command(cmds, ns)
    elif ns.maxargs == 0:
        prelen = sum([len(c) + 2 for c in cmdheads], len(cmdheads) - 1)
        totallen = prelen
        args = []
        while offset < length:
            arg = lines[offset].strip()
            arglen = len(arg) + 3
            if totallen + arglen > ARG_MAX:
                execute_command(cmdheads + args, ns)
                totallen = prelen
                args = []
            args.append(arg)
            totallen += arglen
            offset += 1
        if args:
            execute_command(cmdheads + args, ns)
    else:
        while offset < length:
            args = lines[offset : offset + ns.maxargs]
            cmds = cmdheads + args
            offset += ns.maxargs
            execute_command(cmds, ns)

if __name__ == '__main__':
    main()

