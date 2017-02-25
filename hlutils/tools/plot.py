#!/usr/bin/env python
# -*- coding:utf-8 -*-
r'''
Plot a function.
'''
# Changes:
#   ** version 1.0 2014-05-07 Hulei **
#       1. first version

import os
import sys
import argparse
import matplotlib.pyplot as plt
from math import *

def parse_cmd():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", '-s', default = 0.0, type = float, help = "start of the range")
    parser.add_argument("--end", '-e', default = 10.0, type = float, help = "end of the range")
    parser.add_argument("--quality", "-q", default = 200, type = int, help = "quality of the range")
    parser.add_argument("--xlabel", "-x", default = "x", help = "set label of x")
    parser.add_argument("--ylabel", "-y", default = "y", help = "set label of y")
    parser.add_argument("--title", "-t", default = None, help = "set title")
    parser.add_argument("--style", "-Y", default = "-", help = "set style, can be .,o,^")
    parser.add_argument("expression", nargs = "+", help = "a python expression, like: 1 * x**2 + 2 * x + 3")
    return parser.parse_args(sys.argv[1:])

def plot_expression(expression, xlist, style):
    xx = []
    ylist = []
    exp = eval("lambda x: %s" % expression)
    for x in xlist:
        try:
            ylist.append(exp(x))
            xx.append(x)
        except Exception:
            pass

    plt.plot(xx, ylist, style, label = expression)

def main():
    ns = parse_cmd()

    xlist = []
    step = (ns.end - ns.start) / ns.quality
    val = ns.start
    for i in range(ns.quality):
        xlist.append(val)
        val += step

    index = 0
    for expression in ns.expression:
        color = ("r", "b", "g", "c", "y", "k")[index % 6]
        plot_expression(expression, xlist, color + ns.style)
        index += 1

    plt.legend(bbox_to_anchor=(0.01, 0.99), loc=2, borderaxespad=0.)

    plt.grid(True)
    plt.xlabel(ns.xlabel)
    plt.ylabel(ns.ylabel)

    plt.show()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(type(e).__name__, ":", str(e))
        sys.exit(1)
