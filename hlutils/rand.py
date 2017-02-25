#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
random utils
'''
# Changes:
#   ** version 1.0 2013-10-22 Hulei **
#       1. first version

def randbytes(length):
    '''
    @brief generate a byte string with random data
    @param length   byte string length
    @return a random data string
    '''
    import random
    lst = []
    if length < 0:
        raise ValueError("length must be larger than 0")
    while length:
        lst.append(random.randint(0, 255))
        length -= 1
    return bytes(lst)

__all__ = ["randbytes"]

def test():
    import util
    print(util.bytes_to_str(randbytes(10)))

if __name__ == "__main__":
    test()
