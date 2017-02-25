#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
set console color
'''
import ctypes
import sys

islinux = sys.platform.startswith("linux")

if not islinux:
    _SetConsoleTextAttribute             = ctypes.windll.kernel32.SetConsoleTextAttribute
    _SetConsoleTextAttribute.argtypes    = (ctypes.c_uint32, ctypes.c_uint16)
    _SetConsoleTextAttribute.restype     = ctypes.c_int32
    _GetStdHandle                        = ctypes.windll.kernel32.GetStdHandle
    _GetStdHandle.argtypes               = (ctypes.c_int32,)
    _GetStdHandle.restype                = ctypes.c_uint32
    _GetConsoleScreenBufferInfo          = ctypes.windll.kernel32.GetConsoleScreenBufferInfo
    _GetConsoleScreenBufferInfo.argtypes = (ctypes.c_uint32, ctypes.c_void_p)
    _GetConsoleScreenBufferInfo.restype  = ctypes.c_int32
    _STDOUT                              = _GetStdHandle(-11)

FOREGROUND_BLUE      = 1
FOREGROUND_GREEN     = 2
FOREGROUND_RED       = 4
FOREGROUND_INTENSITY = 8
BACKGROUND_BLUE      = 16
BACKGROUND_GREEN     = 32
BACKGROUND_RED       = 64
BACKGROUND_INTENSITY = 128
RED                  = FOREGROUND_RED | FOREGROUND_INTENSITY
BLUE                 = FOREGROUND_BLUE | FOREGROUND_INTENSITY
GREEN                = FOREGROUND_GREEN | FOREGROUND_INTENSITY
SKYBLUE              = BLUE | GREEN
PURPLE               = RED | BLUE
VIOLET               = PURPLE
YELLOW               = RED | GREEN
WHITE                = RED | GREEN | BLUE
GRAY                 = FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED
BLACK                = 0

if not islinux:
    def set_color(color):
        _SetConsoleTextAttribute(_STDOUT, color)

    def get_color():
        buf = ctypes.create_string_buffer(b'0x16' + b'\x00' * 21)
        _GetConsoleScreenBufferInfo(_STDOUT, buf)
        return buf.raw[8]

else:
    __cur_color = None
    def set_color(color):
        global __cur_color
        if color == None:
            fmt = "0m"
        else:
            front = 0
            back = 0
            isIntensity = False
            if color & FOREGROUND_RED:
                front |= 1
            if color & FOREGROUND_GREEN:
                front |= 2
            if color & FOREGROUND_BLUE:
                front |= 4
            if color & FOREGROUND_INTENSITY:
                isIntensity = True
            if color & BACKGROUND_RED:
                back |= 1
            if color & BACKGROUND_GREEN:
                back |= 2
            if color & BACKGROUND_BLUE:
                back |= 4
            fmts = []
            fmts.append("3%d" % front)
            if back != 0:
                fmts.append("4%d" % back)
            fmts.append("22" if not isIntensity else "1")
            fmt = ";".join(fmts) + "m"
        sys.stdout.write("\033[" + fmt)
        __cur_color = color

    def get_color():
        global __cur_color
        return __cur_color


def output(msg, color):
    sys.stdout.flush()
    origin = get_color()
    set_color(color)
    try:
        sys.stdout.write(msg)
        sys.stdout.flush()
    finally:
        set_color(origin)


__all__ = ["FOREGROUND_BLUE", "FOREGROUND_GREEN", "FOREGROUND_RED", "FOREGROUND_INTENSITY", "BACKGROUND_BLUE", "BACKGROUND_GREEN", "BACKGROUND_RED", "BACKGROUND_INTENSITY", "RED", "BLUE", "GREEN", 'SKYBLUE', 'PURPLE', 'VIOLET', 'YELLOW', 'WHITE', 'GRAY', 'BLACK', 'set_color', 'get_color', 'output']


if __name__ == '__main__':
    output('this is a test for red\n', RED | BACKGROUND_GREEN)
    output('this is a test for blue\n', BLUE)
    output('this is a test for dark blue\n', FOREGROUND_BLUE)
    output('this is a test for yellow\n', YELLOW)
    output('this is a test for purple\n', PURPLE)
    output('this is a test for violet\n', VIOLET)
    output('this is a test for skyblue\n', SKYBLUE)
    output('this is a test for gray\n', GRAY)
    output('this is a test for white\n', WHITE)
    output('this is a test for black\n', BLACK)
    print('this is a test for origin')
    print(get_color())

