#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
backup or recover files.
'''

import os, sys, argparse, shutil, glob, re

def print_info(msg, fobj = sys.stdout):
    print >> fobj, msg

def print_none(msg, fobj = None):
    pass

def parse_command_line():
    parser = argparse.ArgumentParser(prog='backup')
    parser.add_argument('file', nargs='+', metavar='FILE', help='file to backup or recover.')
    parser.add_argument('-x', '--extension', default='.bak', help='file extention of the backup file.')
    parser.add_argument('-o', '--overwrite', action='store_true', help='overwrite backup file instead of appending number to backup file name when exists.')
    parser.add_argument('-s', '--silent', action='store_true', help='do not print anything.')
    parser.add_argument('-r', '--recover', action='store_true', help='recover files from backup files.')
    parser.add_argument('-l', '--lower', action='store_true', help='recover files using lower version backup files.')
    return parser.parse_args(sys.argv[1:])

def backup_file(fname, ns):
    destname = fname + ns.extension
    if not ns.overwrite and os.path.isfile(destname):
        i = 1
        destname = fname + ns.extension + str(i)
        while os.path.isfile(destname):
            i += 1
            destname = fname + ns.extension + str(i)

    try:
        shutil.copy2(fname, destname)
        print_info("backup '%s' to '%s'" % (fname, destname))
    except shutil.Error, e:
        print_info("backup failed: '%s'" % fname, sys.stderr)

def recover_file(fname, ns):
    destname = fname + ns.extension
    namelen = len(destname)
    backups = glob.glob(destname + "*")
    backups = filter(lambda f: re.match(r'^\d*$', f[namelen:]), backups)
    backups = filter(lambda f: os.path.isfile(f), backups)
    if not backups:
        print_info("backup file not found for '%s'" % fname, sys.stderr)
        return
    backups.sort()
    backupname = backups[0 if ns.lower else -1]
    try:
        shutil.copy2(backupname, fname)
        print_info("recover '%s' from '%s'" % (fname, backupname))
    except shutil.Error, e:
        print_info("recover '%s' from '%s' failed!" % (fname, backupname), sys.stderr)

def main():
    ns = parse_command_line()
    if ns.silent:
        global print_info
        print_info = print_none

    for fname in ns.file:
        if not os.path.isfile(fname):
            if not ns.silent:
                print_info("not a file: '%s'" % fname, sys.stderr)
            continue
        if not ns.recover:
            backup_file(fname, ns)
        else:
            recover_file(fname, ns)

if __name__ == "__main__":
    main()
