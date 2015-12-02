#!/usr/bin/env python
#-*- coding:gbk -*-
##
# @file hexctrl.py
# @brief 一个只能输入HEX字符的控件实现
# @author hulei
# @version 1.0
# @date 2011-06-01

import wx
import util

##
# @brief 实现只能输入HEX字符的文本控件
class HexTextCtrl(wx.TextCtrl):
    '''实现只能输入HEX字符的文本控件'''
    HEX_CHAR = (ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9'),
                  ord('A'), ord('B'), ord('C'), ord('D'), ord('E'), ord('F'),)
    HEX_LCHAR = (ord('a'), ord('b'), ord('c'), ord('d'), ord('e'), ord('f'),)
    HEX_CTRL = (wx.WXK_DELETE, wx.WXK_BACK, wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_END, wx.WXK_HOME)

    @staticmethod
    def __get_hex_str(s):
        if isinstance(s, str):
            s = unicode(s, 'gbk', 'replace')
        ps = []
        for c in s:
            if ord(c) in HexTextCtrl.HEX_CHAR:
                ps.append(c)
            elif ord(c) in HexTextCtrl.HEX_LCHAR:
                ps.append(c.upper())
            else:pass

        return u"".join(ps)


    ##
    # @brief 构造方法
    #
    # @param parent     父窗口
    # @param id         窗口ID
    # @param hexvalue   初始字节流
    # @param args
    # @param kwargs
    #
    # @return
    def __init__(self, parent, id, hexvalue = '', *args, **kwargs):
        wx.TextCtrl.__init__(self, parent, id, '', *args, **kwargs)
        try:
            self.__value = self.__get_hex_str(hexvalue)
        except Exception:
            self.__value = u''
        self.__maxLen = 32768
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)

        self.popupID_SELALL = wx.NewId()
        self.popupID_COPY = wx.NewId()
        self.popupID_PASTE = wx.NewId()
        self.popupID_CUT = wx.NewId()
        self.popupID_DELETE = wx.NewId()

        self.Bind(wx.EVT_MENU, self.OnMenu, id = self.popupID_SELALL)
        self.Bind(wx.EVT_MENU, self.OnMenu, id = self.popupID_COPY)
        self.Bind(wx.EVT_MENU, self.OnMenu, id = self.popupID_PASTE)
        self.Bind(wx.EVT_MENU, self.OnMenu, id = self.popupID_CUT)
        self.Bind(wx.EVT_MENU, self.OnMenu, id = self.popupID_DELETE)

        self.__setLogicText(self.__value)

    def OnMenu(self, event):
        id = event.GetId()
        if id == self.popupID_SELALL:
            self.SetSelection(0, len(self.__value))
        elif id == self.popupID_COPY:
            self.Copy()
        elif id == self.popupID_PASTE:
            self.Paste()
        elif id == self.popupID_CUT:
            self.Cut()
        elif id == self.popupID_DELETE:
            self.__ctrlChar(wx.WXK_DELETE)

    def __logicLen2physicLen(self, logicLen):
        assert(logicLen % 2 == 0)
        if logicLen == 0:
            return 0
        else:
            return logicLen / 2 * 3 - 1

    def __logicPos2PhysicPos(self, logicPos):
        if logicPos == 0:
            return 0

        if logicPos % 2 == 1:
            return logicPos / 2 * 3 + 1
        else:
            return logicPos / 2 * 3 - 1

    def __physicPos2LogicPos(self, physicPos):
        if physicPos == 0:
            return 0

        mod = physicPos % 3
        if mod == 0:
            return physicPos / 3 * 2
        elif mod == 2:
            return (physicPos + 1) / 3 * 2
        else:
            return (physicPos + 2) / 3 * 2 - 1

    def __setLogicText(self, text):
        wx.TextCtrl.SetValue(self, u' '.join([text[i:i + 2] for i in range(0, len(text), 2)]))

    def __getLogicText(self):
        s = wx.TextCtrl.GetValue(self)
        return s.replace(u" ", u"")

    def __remove(self, start, end):
        self.__value = self.__value[:start] + self.__value[end:]
        self.__setLogicText(self.__value)

    def __setChar(self, keyCode):
        if not self.IsEditable():
            return
        start, end = self.GetSelection()
        if start == end and len(self.__value) == self.__maxLen * 2:
            return
        self.__value = self.__value[:start] + unichr(keyCode) + self.__value[end:]
        self.__setLogicText(self.__value)
        self.SetSelection(start + 1, start + 1)

    def __ctrlChar(self, keyCode):
        if keyCode == wx.WXK_DELETE:
            if not self.IsEditable():
                return
            start, end = self.GetSelection()
            if start == end:
                self.__remove(start, start + 1)
            else:
                self.__remove(start, end)
            self.SetSelection(start, start)

        elif keyCode == wx.WXK_BACK:
            if not self.IsEditable():
                return
            start, end = self.GetSelection()
            if start == end:
                if start != 0:
                    self.__remove(start - 1, start)
                    self.SetSelection(start - 1, start - 1)
                else:
                    pass
            else:
                self.__remove(start, end)
                self.SetSelection(start, end)

        elif keyCode == wx.WXK_LEFT:
            start, end = self.GetSelection()
            if start == end:
                if start != 0:
                    start -= 1
                    self.SetSelection(start, start)
            else:
                self.SetSelection(start, start)
        elif keyCode == wx.WXK_RIGHT:
            start, end = self.GetSelection()
            if start == end:
                if start != len(self.__value):
                    start += 1
                    self.SetSelection(start, start)
            else:
                self.SetSelection(end, end)

        elif keyCode == wx.WXK_HOME:
            self.SetSelection(0, 0)
        elif keyCode == wx.WXK_END:
            self.SetSelection(len(self.__value), len(self.__value))


    def Cut(self):
        if not self.IsEditable():
            return
        wx.TextCtrl.Copy(self)
        start, end = self.GetSelection()
        self.__remove(start, end)
        self.SetSelection(start, start)

    def Paste(self):
#        print "Paste"
        if not self.IsEditable():
            return
        start, end = self.GetSelection()
        value = self.__getLogicText()

        p = None
        theClipboard = wx.Clipboard.Get()
        if theClipboard.Open():
            data = wx.TextDataObject(text = "")
            if theClipboard.GetData(data):
                p = data.GetText()

        if not p:
            return

        p = self.__get_hex_str(p)

        length = self.__maxLen * 2 - (len(value) - (end - start))
        p = p[:length]
        self.__value = u"".join([value[:start], p, value[end:]])
        self.__setLogicText(self.__value)
        self.SetSelection(start + len(p), start + len(p))

    def OnMouse(self, event):
        if event.RightUp():
            self.SetFocus()
            menu = wx.Menu()
            menu.Append(self.popupID_CUT, u"Cu&t\t(T)")
            menu.Append(self.popupID_COPY, u"&Copy\t(C)")
            menu.Append(self.popupID_PASTE, u"&Paste\t(P)")
            menu.Append(self.popupID_DELETE, u"&Delete\t(D)")
            menu.AppendSeparator()
            menu.Append(self.popupID_SELALL, u"Sel &All\t(A)")
            self.PopupMenu(menu)
            menu.Destroy()
            return
        event.Skip()

    def OnChar(self, event):
        keyCode = event.GetKeyCode()
        if event.GetModifiers() == wx.MOD_CONTROL:
            if keyCode == 1:# ctrl - A
                self.SetSelection(0, len(self.__value))
            elif keyCode == 3: # ctrl - C
                self.Copy()
            elif keyCode == 24: # ctrl - X
                self.Cut()
            elif keyCode == 22: # ctrl - V
                self.Paste()
            elif keyCode == 26: #ctrl - Z
                self.Undo()

        else:
            if keyCode in HexTextCtrl.HEX_LCHAR:
                keyCode -= 32

            if keyCode in HexTextCtrl.HEX_CHAR:
                self.__setChar(keyCode)
            elif keyCode in HexTextCtrl.HEX_CTRL:
                self.__ctrlChar(keyCode)


    ##
    # @brief 把字符串设置到控件中，不在0-9A-F的字符会被抛弃
    #
    # @param s  字符串
    #
    # @return
    def SetValue(self, s):
        self.__value = self.__get_hex_str(s)
        self.__setLogicText(self.__value)

    ##
    # @brief 设置选中的位置
    #
    # @param start  选中的开始位置
    # @param end    选中的结束位置
    #
    # @return
    def SetSelection(self, start, end):
        wx.TextCtrl.SetSelection(self, self.__logicPos2PhysicPos(start), self.__logicPos2PhysicPos(end))

    ##
    # @brief 取得选中文本的开始和结束位置
    #
    # @return (start, end)
    def GetSelection(self):
        start, end = wx.TextCtrl.GetSelection(self)
        return (self.__physicPos2LogicPos(start), self.__physicPos2LogicPos(end))

    ##
    # @brief 把字节流设置到控件中
    #
    # @param bytes  str类型的字节流
    # @throws TypeError bytes的类型不对
    #
    # @return
    def SetBytes(self, bytes):
        if not isinstance(bytes, str):
            raise TypeError("bytes must be a str.")
        self.__value = util.bytes_to_str(bytes[:self.__maxLen], lower = False, sep = u'')
        self.__setLogicText(self.__value)

    ##
    # @brief 取得文本表示的字节流
    #
    # @return str类型的字节流
    def GetBytes(self):
        return util.str_to_bytes(self.__value)

    ##
    # @brief 设置控制表示的字节流的最大长度
    #
    # @param maxlen  字节流的最大长度，以字节为单位，必须大于等于0
    # @throws ValueError  maxlen的值不正确
    #
    # @return
    def SetMaxBytesLength(self, maxlen):
        if maxlen < 0:
            raise ValueError("maxlen must be bigger than 0.")
        self.__maxLen = maxlen



if __name__ == '__main__':
    app = wx.PySimpleApp()
    dlg = wx.Dialog(None, -1, "Main")
    hexText = HexTextCtrl(dlg, -1, hexvalue = 'abcdefcczzc', pos = (10, 10), size = (300, 20))
    hexText.SetBytes("abcd")
    print hexText.GetBytes()
    hexText2 = wx.TextCtrl(dlg, -1, value = 'ABCDE', pos = (10, 40), size = (300, 20))
    dlg.ShowModal()
