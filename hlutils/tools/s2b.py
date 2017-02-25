#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
This script is used to covert hex string like "aa bb cc" to bytes "\\xaa\\xbb\\xcc"
'''

import sys
import hlutils

def help():
    print('''usage:
    s2b hexstr
    ''')

def main():
    if len(sys.argv) == 1:
        help()
    else:
        print(hlutils.str_to_bytes(''.join(sys.argv[1:])))

if __name__ == '__main__':
    main()
