#!/usr/bin/env python
#-*- coding:utf-8 -*-
u'''
This script is used to covert bytes "\\xaa\\xbb\\xcc" to hex string like "aa bb cc"
'''

import sys
import argparse
import hlutils

def parse_cmdline():
    parser = argparse.ArgumentParser(prog='b2s')
    parser.add_argument('--lower', '-l', action='store_true', help='use a-f instead of A-F')
    parser.add_argument('--prefix', '-p', default='', help='set prefix of hex bytes, \'0x\' is an example')
    parser.add_argument('--suffix', '-u', default='', help='set suffix of hex bytes, \'H\' is an example')
    parser.add_argument('--separator', '-s', default=' ', help='set separator of hex bytes')
    parser.add_argument('bytes', nargs='+', help='byte string')
    return parser.parse_args(sys.argv[1:])

def main():
    ns = parse_cmdline()
    for b in ns.bytes:
        print hlutils.bytes_to_str(b, ns.lower, ns.prefix, ns.suffix, ns.separator)

if __name__ == '__main__':
    main()
