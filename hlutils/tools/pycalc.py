#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
eval python expression
'''
# Changes:
#   ** version 1.0 2014-05-14 Hulei **
#       1. first version


import sys
from math import *

def main():
    print(eval(" ".join(sys.argv[1:])))

if __name__ == "__main__":
    main()
