#!/usr/bin/env python
#-*- coding:utf-8 -*-
u'''
loop up Windows error string from error code
'''

import sys
import ctypes
def help():
    print "winerr.py errnum"

def main():
    if len(sys.argv) != 2:
        help()
        return
    try:
        num = int(sys.argv[1], 0)
        errnum = ctypes.c_uint32(num)
        buf = ctypes.create_unicode_buffer(65535)
        ret = ctypes.windll.kernel32.FormatMessageW(0x00001000, 0, errnum, 0, buf, 65535, 0)
        if ret == 0:
            print "Cannot find error string."
        else:
            print buf.value[:ret]
    except Exception, e:
        print str(e)
        help()
        return

if __name__ == '__main__':
    main()
