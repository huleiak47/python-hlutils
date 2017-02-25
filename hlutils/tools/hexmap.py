#!/usr/bin/env python
# -*- coding:utf-8 -*-

import texttable as ttl

def main():
    table = ttl.Texttable()

    table.set_cols_align(["c", "c", "c"])
    table.set_cols_valign(["m", "m", "m"])
    table.set_cols_width([10, 10, 10])
    table.header(["Oct", "Hex", "Bin"])

    for i in range(0, 16):
        table.add_row(["%2d" % i, "%X" % i, "b 0000"[0:6 - (len(bin(i)) - 2)] + bin(i)[2:]])

    print(table.draw())

if __name__ == '__main__':
    main()
