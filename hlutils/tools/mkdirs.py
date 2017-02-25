#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Make dirs. This script is used to replace system mkdir command.
'''

import sys
import os
import argparse

def parse_commandline():
    '''
    @brief parse command line
    @return the parsed namespace
    '''
    parser = argparse.ArgumentParser(prog="mkdirs")
    parser.add_argument("dir", nargs="+", help="path of the directory")
    parser.add_argument("-s", "--stop", action="store_true", help="stop when error, otherwise skip and make next dir")
    return parser.parse_args(sys.argv[1:])

def makedir(dirname, ns):
    '''
    @brief make a dir named dirname
    @param dirname the path of the dir
    @param ns the parsed namespace
    @return None
    '''
    if os.path.isfile(dirname):
        print("'{}' is a file, cannot make dir!".format(dirname))
        if ns.stop:
            sys.exit(1)
        else:
            return
    if os.path.isdir(dirname):
        print("'{}' already exists!".format(dirname))
        if ns.stop:
            sys.exit(2)
        else:
            return
    try:
        os.makedirs(dirname)
        print("make dir '{}' succeeded!".format(dirname))
    except os.error:
        print("make dir '{}' failed!".format(dirname))
        if ns.stop:
            sys.exit(3)
        else:
            return


def main():
    '''
    @brief main
    @return None
    '''
    ns = parse_commandline()
    for dirname in ns.dir:
        makedir(dirname, ns)

if __name__ == "__main__":
    main()
