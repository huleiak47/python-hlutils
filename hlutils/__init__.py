#!/usr/bin/env python
#-*- coding:utf-8 -*-

__version__ = '1.1.3'

from . import util
from .util import *

__all__ = util.__all__ + [
    'hexctrl',
    'script',
    'args',
    'consolecolor',
    'rand',
]

