#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
sys.argv.insert(1, "--format=html")

from mdconvert import main

if __name__ == "__main__":
    main()
