#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import glob
from setuptools import setup

from hlutils import __version__ as VERSION

NAME = 'hlutils'
DESCRIPTION = 'Useful python functions and scripts written by Hu Lei.'
LICENSE = 'Apache License 2.0'
PLATFORMS = ['win32']

consoles = []
for f in os.listdir("hlutils/tools"):
    if f.endswith(".py") and f != "__init__.py":
        consoles.append("{0} = hlutils.tools.{0}:main".format(f[:-3]))

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    license=LICENSE,
    platforms=PLATFORMS,
    url='',
    author='James Hu',
    author_email='huleiak47@gmail.com',
    packages=['hlutils', 'hlutils.tools'],
    package_dir={'hlutils': './hlutils', 'hlutils.tools': './hlutils/tools'},
    package_data={"hlutils.tools": ["*.html", "*.docx", "*.vim"]},
    entry_points={
        "console_scripts": consoles,
    },
    install_requires=["prompt_toolkit>=0.60",
                      "ply>=3.0",
                     "texttable>=0.8"],
)
