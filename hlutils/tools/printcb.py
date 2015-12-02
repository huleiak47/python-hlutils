#!/usr/bin/env python
#-*- coding:utf-8 -*-
u'''
print clipboard text to stdout
'''

import hlutils
import sys

def main():
    sys.stdout.write(hlutils.get_clipboard_text())

if __name__ == '__main__':
    main()
