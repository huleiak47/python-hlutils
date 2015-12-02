#!/usr/bin/env python
#-*- coding:gbk -*-
u'''
һЩͨ�õĹ���,  ����ֱ�ӵ������ʹ��
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


    def get_clipboard_text(isunicode = False):
        u'''
        @brief �Ӽ�����ȡ���ַ���
        @param isunicode    �Ƿ�ȡ��UNICODE��ʽ���ַ���
        @return �������е��ַ���
        '''
        text = None
        if _OpenClipboard(0):
            if isunicode:
                hClipMem = _GetClipboardData(_CF_UNICODETEXT)
                _GlobalLock.restype = ctypes.c_wchar_p
            else:
                hClipMem = _GetClipboardData(_CF_TEXT)
                _GlobalLock.restype = ctypes.c_char_p
            text = _GlobalLock(hClipMem)
            _GlobalUnlock(hClipMem)
            _CloseClipboard()
        return text

    def set_clipboard_text(text):
        u'''
        @brief ���ַ������õ���������
        @param text ��Ҫ���õ��ַ�����������str��unicode����
        @throws TypeError     text�����Ͳ���ȷ
        @return None
        '''
        if not isinstance(text, basestring):
            raise ValueError("text must be a string")
        if isinstance(text, str):
            buffer = ctypes.create_string_buffer(text)
            bufferSize = len(text) + 1
            mode = _CF_TEXT
        else:
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


def bytes_to_str(bytes, lower=True, prefix=u'', suffix=u'', sep=u' '):
    u'''
    @brief ���ֽ���ת��unicode�ַ�����ʾ
    @param bytes      �ֽ���������Ϊstr
    @param lower      Trueʹ��Сд��a-f��Falseʹ�ô�дA-F
    @param prefix     ÿ���ֽڵ�ǰ׺��ʾ����'0x'
    @param suffix     ÿ���ֽڵĺ�׺��ʾ����'H'
    @param sep        �ֽ�֮��ķָ��ֽڴ�����','
    @throws TypeError bytes�����Ͳ���ȷ
    @return           unicode�ַ���
    '''
    if not isinstance(bytes, str):
        raise TypeError("bytes must be a str.")
    l = []
    for c in bytes:
        if lower:
            l.append(u'%s%02x%s' % (prefix, ord(c), suffix))
        else:
            l.append(u'%s%02X%s' % (prefix, ord(c), suffix))
    return sep.join(l)


import re

_RE_MATCH = re.compile(ur'^\s*((0[xX])?[a-fA-F0-9]{2}\s*)*\s*$')
_RE_GET_HEX = re.compile(ur'[a-fA-F0-9]{2}')
def str_to_bytes(s):
    u'''
    @brief ���ַ�����ʾ���ֽ���תΪstr���͵��ֽ���
    @param s      �ַ�����str��unicode
    @throws TypeError     s�����Ͳ���ȷ
    @return       str���͵��ֽ���
    '''
    if not isinstance(s, basestring):
        raise TypeError("s must be a str or unicode")
    if isinstance(s, str):
        s = s.decode('mbcs')
    if _RE_MATCH.match(s):
        hexes = []
        for hexstr in _RE_GET_HEX.findall(s):
            hexes.append(chr(int(hexstr, 16)))
        return ''.join(hexes)
    else:
        raise ValueError("cannot convert to bytes from \"%s\"" % s)

#-----------------------------------------------------------------------#
def readtext(filepath):
    u'''
    @brief һ�ζ�ȡ�ı��ļ����������ݲ��ر��ļ�
    @param filepath     �ļ�·��
    @return     �ı��ļ�������
    '''
    with open(filepath, 'r') as f:
        return f.read()

def readlines(filepath):
    u'''
    @brief һ�ζ�ȡ�ı��ļ��������в��ر��ļ�
    @param filepath     �ļ�·��
    @return     �ı��ļ���������
    '''
    with open(filepath, 'r') as f:
        return f.readlines()

def readbinary(filepath):
    u'''
    @brief һ�ζ�ȡ�������ļ����������ݲ��ر��ļ�
    @param filepath     �ļ�·��
    @return     �������ļ�������
    '''
    with open(filepath, 'rb') as f:
        return f.read()

def writetext(filepath, text, append=False):
    u'''
    @brief һ��д���ı����ļ����ر��ļ�
    @param filepath     �ļ�·��
    @param text         д������
    @param append       �Ƿ��ı����ӵ��ļ�β
    @return None
    '''
    with open(filepath, 'w' if not append else 'a') as f:
        f.write(text)

def writelines(filepath, lines, append=False):
    u'''
    @brief һ��д������ı����ļ����ر��ļ�
    @param filepath     �ļ�·��
    @param lines        д��Ķ����ı�
    @param append       �Ƿ��ı����ӵ��ļ�β
    @return None
    '''
    with open(filepath, 'w' if not append else 'a') as f:
        for line in lines:
            f.write(line)

def writebinary(filepath, bytes, append=False):
    u'''
    @brief һ��д����������ݵ��ļ����ر��ļ�
    @param filepath     �ļ�·��
    @param bytes        ����������
    @param append       �Ƿ��ı����ӵ��ļ�β
    @return None
    '''
    with open(filepath, 'wb' if not append else 'ab') as f:
        f.write(bytes)


def call(args):
    u'''
    @brief ͨ��ϵͳshell���������У��ܹ���ȷ����^��
    @param args     ���������ݣ�������һ��str������һ��list
    @return ����ķ���ֵ
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
#��ʱ������
class timer(object):
    u'''
    @brief ��ʱ��
    '''
    def __init__(self):
        u'''
        @brief ���췽��
        '''
        self.__start = 0.0
        self.__used = 0.0

    def reset(self):
        u'''
        @brief ��λ����������
        @return None

        �������������λ�������л���ͣ�ļ�ʱ������λ��ǰ�Ľ��ȱ�����
        '''
        self.__start = 0.0
        self.__used = 0.0

    def go(self):
        u'''
        @brief ������ʱ��
        @return None

        �����������������ʱ���������ʱ���Ѿ�����������ͣ״̬����ôʲôҲ����
        '''
        if self.__start == 0.0:
            self.__start = time.time()

    def reset_go(self):
        u'''
        @brief ��λ��������ʱ��
        @return None

        �൱�ڵ���reset()�ٵ���go()
        '''
        self.reset()
        self.go()

    def pause(self):
        u'''
        @brief ��ͣ��ʱ��
        @return None

        �������������ͣ��ʱ������ͣ�ڼ��ʱ�䲻��������Ľ�������Ҫ���ż�ʱ������go()�����Ҫ���¼�ʱ������reset_go()
        '''
        if self.__start != 0.0:
            now = time.time()
            self.__used += now - self.__start
            self.__start = 0.0

    def get(self):
        u'''
        @brief ȡ��ͳ�Ƶ�ʱ��ֵ
        @return ʱ��ֵ������Ϊ��λ

        �����������ȡ��reset()���һ�ε���go()������get()֮�����ĵ�ʱ�䣬����pause()��go()֮ǰ��ʱ�䲻��������
        '''
        used = self.__used
        if self.__start != 0.0:
            now = time.time()
            used += now - self.__start
        return used


__all__ = ["str_to_bytes", "bytes_to_str", "get_clipboard_text", "set_clipboard_text", "timer", "readtext", "readlines", "readbinary", "writetext", "writelines", "writebinary", "call"]

