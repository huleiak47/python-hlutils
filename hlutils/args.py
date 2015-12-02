#!/usr/bin/env python
#-*- coding:utf-8 -*-
u'''
@file args.py
@brief args
@author hulei
@version 1.0
@date 2012-08-15
@copyright 2012 Hulei. All rights reserved.
'''

import sys

_q = "'" if sys.platform.startswith("linux") else '"'
def to_shell_arg(s):
    return _q + s + _q

def to_shell_cmd(args):
    return ' '.join([to_shell_arg(s) for s in args])

to_windows_cmd = to_shell_cmd

__all__ = ['to_windows_cmd', 'to_shell_cmd']
