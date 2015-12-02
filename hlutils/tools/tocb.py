#!/usr/bin/env python
#-*- coding:utf-8 -*-
u'''
@file tocb.py
@brief copy text from stdin to system clipboard.
@author hulei
@version 1.0
@date 2012-09-05
@copyright 2012 Hulei. All rights reserved.
'''

import sys
import hlutils

def main():
    hlutils.set_clipboard_text(sys.stdin.read())

if __name__ == '__main__':
    main()
