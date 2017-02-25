#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
一些通用的功能,  可以直接导入包名使用
'''

import ctypes
import sys

islinux = sys.platform.startswith("linux")


if not islinux:
    _OpenClipboard = ctypes.windll.user32.OpenClipboard
    _OpenClipboard.argtypes = [ctypes.c_uint32]
    _OpenClipboard.restype = ctypes.c_uint32
    _EmptyClipboard = ctypes.windll.user32.EmptyClipboard
    _EmptyClipboard.argtypes = []
    _EmptyClipboard.restype = ctypes.c_uint32
    _GetClipboardData = ctypes.windll.user32.GetClipboardData
    _GetClipboardData.argtypes = [ctypes.c_uint32]
    _GetClipboardData.restype = ctypes.c_uint32
    _SetClipboardData = ctypes.windll.user32.SetClipboardData
    _SetClipboardData.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    _SetClipboardData.restype = ctypes.c_uint32
    _CloseClipboard = ctypes.windll.user32.CloseClipboard
    _CloseClipboard.argtypes = []
    _CloseClipboard.restype = ctypes.c_uint32
    _GlobalLock = ctypes.windll.kernel32.GlobalLock
    _GlobalLock.argtypes = [ctypes.c_uint32]
    _GlobalLock.restype = ctypes.c_void_p
    _GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
    _GlobalAlloc.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    _GlobalAlloc.restype = ctypes.c_uint32
    _GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock
    _GlobalUnlock.argtypes = [ctypes.c_uint32]
    _GlobalUnlock.restype = ctypes.c_uint32
    _memcpy = ctypes.cdll.msvcrt.memcpy
    _memcpy.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
    _memcpy.restype = None

    _CF_TEXT = 1
    _CF_UNICODETEXT = 13
    _GHND = 0x42


    def get_clipboard_text():
        '''
        @brief 从剪贴板取得字符串
        @param isunicode    是否取得UNICODE格式的字符串
        @return 剪贴板中的字符串
        '''
        text = None
        if _OpenClipboard(0):
            hClipMem = _GetClipboardData(_CF_UNICODETEXT)
            _GlobalLock.restype = ctypes.c_wchar_p
            text = _GlobalLock(hClipMem)
            _GlobalUnlock(hClipMem)
            _CloseClipboard()
        return text

    def set_clipboard_text(text):
        '''
        @brief 把字符串设置到剪贴板中
        @param text 需要设置的字符串，必须是str或unicode类型
        @throws TypeError     text的类型不正确
        @return None
        '''
        if isinstance(text, bytes):
            text = text.decode("mbcs")
        if not isinstance(text, str):
            raise ValueError("text must be a string")
        buffer = ctypes.create_unicode_buffer(text)
        bufferSize = len(text) * 2 + 2
        mode = _CF_UNICODETEXT
        hGlobalMem = _GlobalAlloc(_GHND, bufferSize)
        _GlobalLock.restype = ctypes.c_void_p
        lpGlobalMem = _GlobalLock(hGlobalMem)
        _memcpy(lpGlobalMem, ctypes.addressof(buffer), bufferSize)
        _GlobalUnlock(hGlobalMem)
        if _OpenClipboard(0):
            _EmptyClipboard()
            _SetClipboardData(mode, hGlobalMem)
            _CloseClipboard()

else:
    def get_clipboard_text(isunicode = False):
        pass

    def set_clipboard_text(text):
        pass


def bytes_to_str(b, lower=True, prefix='', suffix='', sep=' '):
    '''
    @brief 把字节流转成unicode字符串表示
    @param bytes      字节流，类型为str
    @param lower      True使用小写的a-f，False使用大写A-F
    @param prefix     每个字节的前缀表示，如'0x'
    @param suffix     每个字节的后缀表示，如'H'
    @param sep        字节之间的分隔字节串，如','
    @throws TypeError bytes的类型不正确
    @return           unicode字符串
    '''
    if not isinstance(b, bytes):
        raise TypeError("b must be a bytes.")
    l = []
    for c in b:
        if lower:
            l.append('%s%02x%s' % (prefix, c, suffix))
        else:
            l.append('%s%02X%s' % (prefix, c, suffix))
    return sep.join(l)


import re

_RE_MATCH = re.compile(r'^\s*((0[xX])?[a-fA-F0-9]{2}\s*)*\s*$')
_RE_GET_HEX = re.compile(r'[a-fA-F0-9]{2}')
def str_to_bytes(s):
    '''
    @brief 把字符串表示的字节流转为str类型的字节流
    @param s      字符串，str或unicode
    @throws TypeError     s的类型不正确
    @return       str类型的字节流
    '''
    if not isinstance(s, (str, bytes)):
        raise TypeError("s must be a str or bytes")
    if isinstance(s, bytes):
        s = s.decode('mbcs')
    if _RE_MATCH.match(s):
        hexes = []
        for hexstr in _RE_GET_HEX.findall(s):
            hexes.append(int(hexstr, 16))
        return bytes(hexes)
    else:
        raise ValueError("cannot convert to bytes from \"%s\"" % s)

#-----------------------------------------------------------------------#
def readtext(filepath):
    '''
    @brief 一次读取文本文件的所有内容并关闭文件
    @param filepath     文件路径
    @return     文本文件的内容
    '''
    with open(filepath, 'r') as f:
        return f.read()

def readlines(filepath):
    '''
    @brief 一次读取文本文件的所有行并关闭文件
    @param filepath     文件路径
    @return     文本文件的所有行
    '''
    with open(filepath, 'r') as f:
        return f.readlines()

def readbinary(filepath):
    '''
    @brief 一次读取二进制文件的所有内容并关闭文件
    @param filepath     文件路径
    @return     二进制文件的内容
    '''
    with open(filepath, 'rb') as f:
        return f.read()

def writetext(filepath, text, append=False):
    '''
    @brief 一次写入文本到文件并关闭文件
    @param filepath     文件路径
    @param text         写入内容
    @param append       是否将文本附加到文件尾
    @return None
    '''
    with open(filepath, 'w' if not append else 'a') as f:
        f.write(text)

def writelines(filepath, lines, append=False):
    '''
    @brief 一次写入多行文本到文件并关闭文件
    @param filepath     文件路径
    @param lines        写入的多行文本
    @param append       是否将文本附加到文件尾
    @return None
    '''
    with open(filepath, 'w' if not append else 'a') as f:
        for line in lines:
            f.write(line)

def writebinary(filepath, bytes, append=False):
    '''
    @brief 一次写入二进制数据到文件并关闭文件
    @param filepath     文件路径
    @param bytes        二进制数据
    @param append       是否将文本附加到文件尾
    @return None
    '''
    with open(filepath, 'wb' if not append else 'ab') as f:
        f.write(bytes)


def call(args):
    '''
    @brief 通过系统shell调用命令行，能够正确输入^符
    @param args     命令行内容，可以是一个str，或者一个list
    @return 命令的返回值
    '''
    if not islinux:
        if isinstance(args, str):
            if "^" in args:
                args = args.replace("^", "^^")
        else:
            args = [arg.replace("^", "^^") for arg in args]
    import subprocess
    return subprocess.call(args, shell=1)


#-----------------------------------------------------------------------#
import time
#计时器功能
class timer(object):
    '''
    @brief 计时器
    '''
    def __init__(self):
        '''
        @brief 构造方法
        '''
        self.__start = 0.0
        self.__used = 0.0

    def reset(self):
        '''
        @brief 复位，数据清零
        @return None

        这个方法用来复位正在运行或暂停的计时器，复位后当前的进度被清零
        '''
        self.__start = 0.0
        self.__used = 0.0

    def go(self):
        '''
        @brief 启动计时器
        @return None

        这个方法用来启动计时器，如果计时器已经启动或处于暂停状态，那么什么也不做
        '''
        if self.__start == 0.0:
            self.__start = time.time()

    def reset_go(self):
        '''
        @brief 复位并启动计时器
        @return None

        相当于调用reset()再调用go()
        '''
        self.reset()
        self.go()

    def pause(self):
        '''
        @brief 暂停计时器
        @return None

        这个方法用来暂停计时器，暂停期间的时间不会计入最后的结果，如果要接着计时，调用go()，如果要重新计时，调用reset_go()
        '''
        if self.__start != 0.0:
            now = time.time()
            self.__used += now - self.__start
            self.__start = 0.0

    def get(self):
        '''
        @brief 取得统计的时间值
        @return 时间值，以秒为单位

        这个方法用于取得reset()后第一次调用go()到调用get()之间消耗的时间，调用pause()到go()之前的时间不计算在内
        '''
        used = self.__used
        if self.__start != 0.0:
            now = time.time()
            used += now - self.__start
        return used


__all__ = ["str_to_bytes", "bytes_to_str", "get_clipboard_text", "set_clipboard_text", "timer", "readtext", "readlines", "readbinary", "writetext", "writelines", "writebinary", "call"]

