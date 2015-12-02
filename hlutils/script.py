#!/usr/bin/env python
#-*- coding:gbk -*-
# 模拟鼠标和键盘功能

from ctypes import *
import time

VK_LBUTTON        = 0x01
VK_RBUTTON        = 0x02
VK_CANCEL         = 0x03
VK_MBUTTON        = 0x04    #* NOT contiguous with L & RBUTTON */

VK_BACK           = 0x08
VK_TAB            = 0x09

VK_CLEAR          = 0x0C
VK_RETURN         = 0x0D

VK_SHIFT          = 0x10
VK_CONTROL        = 0x11
VK_MENU           = 0x12
VK_PAUSE          = 0x13
VK_CAPITAL        = 0x14

VK_KANA           = 0x15
VK_HANGEUL        = 0x15  #* old name - should be here for compatibility */
VK_HANGUL         = 0x15
VK_JUNJA          = 0x17
VK_FINAL          = 0x18
VK_HANJA          = 0x19
VK_KANJI          = 0x19

VK_ESCAPE         = 0x1B

VK_CONVERT        = 0x1C
VK_NONCONVERT     = 0x1D
VK_ACCEPT         = 0x1E
VK_MODECHANGE     = 0x1F

VK_SPACE          = 0x20
VK_PRIOR          = 0x21
VK_NEXT           = 0x22
VK_END            = 0x23
VK_HOME           = 0x24
VK_LEFT           = 0x25
VK_UP             = 0x26
VK_RIGHT          = 0x27
VK_DOWN           = 0x28
VK_SELECT         = 0x29
VK_PRINT          = 0x2A
VK_EXECUTE        = 0x2B
VK_SNAPSHOT       = 0x2C
VK_INSERT         = 0x2D
VK_DELETE         = 0x2E
VK_HELP           = 0x2F

VK_C0             = 0xC0 #“`”和“~”
VK_BD             = 0xBD #“-”和“_”
VK_BB             = 0xBB #“=”和“+”
VK_DC             = 0xDC #“\”和“|”
VK_DB             = 0xDB #“[”和“{”
VK_DD             = 0xDD #“]”和“}”
VK_BA             = 0xBA #“”和“:”
VK_DE             = 0xDE #“'”和“"”
VK_BC             = 0xBC #“,”和“<”
VK_BE             = 0xBE #“.”和“>”
VK_BF             = 0xBF #“/”和“?”

#{* VK_0 thru VK_9 are the same as ASCII '0' thru '9' (0x30 - 0x39) *}
VK_0              = 0x30
VK_1              = 0x31
VK_2              = 0x32
VK_3              = 0x33
VK_4              = 0x34
VK_5              = 0x35
VK_6              = 0x36
VK_7              = 0x37
VK_8              = 0x38
VK_9              = 0x39

#{* VK_A thru VK_Z are the same as ASCII 'A' thru 'Z' (0x41 - 0x5A) *}
VK_A              = 0x41
VK_B              = 0x42
VK_C              = 0x43
VK_D              = 0x44
VK_E              = 0x45
VK_F              = 0x46
VK_G              = 0x47
VK_H              = 0x48
VK_I              = 0x49
VK_J              = 0x4A
VK_K              = 0x4B
VK_L              = 0x4C
VK_M              = 0x4D
VK_N              = 0x4E
VK_O              = 0x4F
VK_P              = 0x50
VK_Q              = 0x51
VK_R              = 0x52
VK_S              = 0x53
VK_T              = 0x54
VK_U              = 0x55
VK_V              = 0x56
VK_W              = 0x57
VK_X              = 0x58
VK_Y              = 0x59
VK_Z              = 0x5A

VK_LWIN           = 0x5B
VK_RWIN           = 0x5C
VK_APPS           = 0x5D

VK_NUMPAD0        = 0x60
VK_NUMPAD1        = 0x61
VK_NUMPAD2        = 0x62
VK_NUMPAD3        = 0x63
VK_NUMPAD4        = 0x64
VK_NUMPAD5        = 0x65
VK_NUMPAD6        = 0x66
VK_NUMPAD7        = 0x67
VK_NUMPAD8        = 0x68
VK_NUMPAD9        = 0x69
VK_MULTIPLY       = 0x6A
VK_ADD            = 0x6B
VK_SEPARATOR      = 0x6C
VK_SUBTRACT       = 0x6D
VK_DECIMAL        = 0x6E
VK_DIVIDE         = 0x6F
VK_F1             = 0x70
VK_F2             = 0x71
VK_F3             = 0x72
VK_F4             = 0x73
VK_F5             = 0x74
VK_F6             = 0x75
VK_F7             = 0x76
VK_F8             = 0x77
VK_F9             = 0x78
VK_F10            = 0x79
VK_F11            = 0x7A
VK_F12            = 0x7B
VK_F13            = 0x7C
VK_F14            = 0x7D
VK_F15            = 0x7E
VK_F16            = 0x7F
VK_F17            = 0x80
VK_F18            = 0x81
VK_F19            = 0x82
VK_F20            = 0x83
VK_F21            = 0x84
VK_F22            = 0x85
VK_F23            = 0x86
VK_F24            = 0x87

VK_NUMLOCK        = 0x90
VK_SCROLL         = 0x91

#{*
# * VK_L* & VK_R* - left and right Alt, Ctrl and Shift virtual keys.
# * Used only as parameters to GetAsyncKeyState() and GetKeyState().
# * No other API or message will distinguish left and right keys in this way.
# *}
VK_LSHIFT         = 0xA0
VK_RSHIFT         = 0xA1
VK_LCONTROL       = 0xA2
VK_RCONTROL       = 0xA3
VK_LMENU          = 0xA4
VK_RMENU          = 0xA5

VK_PROCESSKEY     = 0xE5

VK_ATTN           = 0xF6
VK_CRSEL          = 0xF7
VK_EXSEL          = 0xF8
VK_EREOF          = 0xF9
VK_PLAY           = 0xFA
VK_ZOOM           = 0xFB
VK_NONAME         = 0xFC
VK_PA1            = 0xFD
VK_OEM_CLEAR      = 0xFE


class MOUSEINPUT(Structure):
    _fields_ = [("dx", c_long),
                ("dy", c_long),
                ("mouseData", c_ulong),
                ("dwFlags", c_ulong),
                ("time", c_ulong),
                ("dwExtraInfo", c_void_p)]

class KEYBDINPUT(Structure):
    _fields_ = [("wVk", c_ushort),
                ("wScan", c_ushort),
                ("dwFlags", c_ulong),
                ("time", c_ulong),
                ("dwExtraInfo", c_void_p)]

class INPUTUNION(Union):
    _fields_ = [("mi", MOUSEINPUT),
                ("ki", KEYBDINPUT)]

class INPUT(Structure):
    _fields_ = [("type", c_ulong),
                ("union", INPUTUNION)]

class PT(Structure):
    _fields_ = [("x", c_long),
                ("y", c_long)]



Prototype = WINFUNCTYPE(c_uint, c_uint, POINTER(INPUT), c_int)
paramflags = (1, "nInputs"), (1, "pInputs"), (1, "cbSize")
SendInput = Prototype(("SendInput", windll.user32), paramflags)

INPUT_MOUSE        = 0
INPUT_KEYBOARD     = 1

KEYEVENTF_KEYDOWN  = 0
KEYEVENTF_KEYUP    = 2

MOUSEEVENTF_LEFTDOWN   = 0x0002
MOUSEEVENTF_LEFTUP     = 0x0004
MOUSEEVENTF_RIGHTDOWN  = 0x0008
MOUSEEVENTF_RIGHTUP    = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP   = 0x0040
MOUSEEVENTF_WHEEL      = 0x0800

WHEEL_DELTA            = 120


g_input = INPUT()
g_pt = PT()

def wait(ms):
    "等待时间，单位：毫秒"
    time.sleep(ms / 1000.0)

def move(x, y, absolute = True):
    "移动光标，当absolute为True时，x, y表示屏幕的绝对座标， 否则表示相对光标当前位置的移动距离"
    if not absolute:
        windll.user32.GetCursorPos(byref(g_pt))
        x = g_pt.x + x
        y = g_pt.y + y
    windll.user32.SetCursorPos(x, y)

def left_down():
    "鼠标左键按下"
    memset(byref(g_input), 0, sizeof(INPUT))
    g_input.type = INPUT_MOUSE
    g_input.union.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
    SendInput(1, byref(g_input), sizeof(INPUT))

def left_up():
    "鼠标左键弹起"
    memset(byref(g_input), 0, sizeof(INPUT))
    g_input.type = INPUT_MOUSE
    g_input.union.mi.dwFlags = MOUSEEVENTF_LEFTUP
    SendInput(1, byref(g_input), sizeof(INPUT))

def left_click():
    "鼠标左健单击"
    left_down()
    left_up()

def right_down():
    "鼠标右键按下"
    memset(byref(g_input), 0, sizeof(INPUT))
    g_input.type = INPUT_MOUSE
    g_input.union.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN
    SendInput(1, byref(g_input), sizeof(INPUT))

def right_up():
    "鼠标右健弹起"
    memset(byref(g_input), 0, sizeof(INPUT))
    g_input.type = INPUT_MOUSE
    g_input.union.mi.dwFlags = MOUSEEVENTF_RIGHTUP
    SendInput(1, byref(g_input), sizeof(INPUT))

def right_click():
    "鼠标右健单击"
    right_down()
    right_up()

def middle_down():
    "鼠标中键按下"
    memset(byref(g_input), 0, sizeof(INPUT))
    g_input.type = INPUT_MOUSE
    g_input.union.mi.dwFlags = MOUSEEVENTF_MIDDLEDOWN
    SendInput(1, byref(g_input), sizeof(INPUT))

def middle_up():
    "鼠标中键弹起"
    memset(byref(g_input), 0, sizeof(INPUT))
    g_input.type = INPUT_MOUSE
    g_input.union.mi.dwFlags = MOUSEEVENTF_MIDDLEUP
    SendInput(1, byref(g_input), sizeof(INPUT))

def middle_click():
    "鼠标中键单击"
    middle_down()
    middle_up()

def wheel_move(delta):
    "鼠标滚轮滚动，正数表示向上， 负数表示向下"
    memset(byref(g_input), 0, sizeof(INPUT))
    g_input.type = INPUT_MOUSE
    g_input.union.mi.dwFlags = MOUSEEVENTF_WHEEL
    g_input.union.mi.mouseData = delta * WHEEL_DELTA
    SendInput(1, byref(g_input), sizeof(INPUT))

def key_down(key):
    "健盘按键按下， key为虚拟键值"
    memset(byref(g_input), 0, sizeof(INPUT))
    g_input.type = INPUT_KEYBOARD
    g_input.union.ki.wVk = c_ushort(key)
    g_input.union.ki.dwFlags = KEYEVENTF_KEYDOWN
    SendInput(1, byref(g_input), sizeof(INPUT))
    time.sleep(0.05)

def key_up(key):
    "健盘按键弹起， key为虚拟键值"
    memset(byref(g_input), 0, sizeof(INPUT))
    g_input.type = INPUT_KEYBOARD
    g_input.union.ki.wVk = c_ushort(key)
    g_input.union.ki.dwFlags = KEYEVENTF_KEYUP
    SendInput(1, byref(g_input), sizeof(INPUT))
    time.sleep(0.05)

def key_press(key):
    "健盘按键单击， key为虚拟键值"
    key_down(key)
    key_up(key)
