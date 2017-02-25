#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
Update system environment.
'''

from ctypes import *

def main():
    HWND_BROADCAST = 0xffff
    WM_SETTINGCHANGE = 0x001A
    lparam = "Environment"
    print(windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, lparam, 0, 500, 0))

if __name__ == '__main__':
    main()
