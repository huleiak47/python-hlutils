#!/usr/bin/env python
# -*- coding:utf-8 -*-
r'''
An enhanced console for replacing cmd.exe.
'''
# Changes:
#   ** version 1.0.12 2016-04-11 Hulei **
#       1. 使用prompt_toolkit代替readline库
#
#   ** version 1.0.11 2015-03-26 Hulei **
#       1. 修正了命令行解析较复杂时不正常的问题
#
#   ** verison 1.0.10 2015-01-30 Hulei **
#       1. 对于每个路径使用不同的历史文件
#       2. 执行的批处理脚本如果改变了环境变量，会体现在cmdex环境中
#
#   ** version 1.0.9 2015-01-14 Hulei **
#       1. 将环境ERRORLEVEL改为ERRORLEVELEX，因为ERRORLEVEL不能主动设置
#       2. 返回非0值时以红色显示
#
#   ** version 1.0.8 2015-01-12 Hulei **
#       1. 修正无法补全中文文件名的问题
#
#   ** version 1.0.7 2015-01-11 Hulei **
#       1. 使用管道符号“|”或“||”及“&&”时，后面的命令补全也会查找全局命令
#       2. 全局补全的命令不显示后缀
#
#   ** version 1.0.6 2014-12-29 Hulei **
#       1. 增加命令执行时间显示
#
#   ** verison 1.0.5 2014-11-17 Hulei **
#       1. 当直接执行python脚本时，替换成python.exe调用，以修正64位Windows下的管道问题
#       2. 将命令返回值设到ERRORLEVEL环境变量中
#       3. 默认的可执行扩展名加入.py
#
#   ** version 1.0.4 2014-06-16 Hulei **
#       1. 去掉以:号起始命令，输入开始的第一个命令会补全全局命令，后续的只实例文件
#       2. 修正大写执行文件无法补全的问题
#       3. 增加cmd.exe内部命令补全
#
#   ** version 1.0.3 2014-04-22 Hulei **
#       1. ADD：以;号起始的命令不会阻塞
#       2. ADD：以:号起始的补全会搜索全局PATH指定的目录，后缀在PATHEXT中指定的文件
#
#   ** version 1.0 2014-02-12 Hulei **
#       1. first version

from __future__ import unicode_literals

__version__ = "1.0.12"

import os
import sys
import time
import subprocess as sp
import ctypes
import re
import random

os.environ["PATHEXT"] = ".COM;.EXE;.BAT;.PY"

from prompt_toolkit.contrib.completers import SystemCompleter, WordCompleter
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer
from prompt_toolkit.shortcuts import print_tokens
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
from prompt_toolkit.history import InMemoryHistory

CMDEXE_INT_CMDS = [
    "copy",
    "date",
    "time",
    "cls",
    "del",
    "start",
    "call",
    "attrib",
    "assoc",
    "break",
    "color",
    "mkdir",
    "md",
    "more",
    "move",
    "path",
    "rmdir",
    "rd",
    "mklink",
    "rename",
    "where",
    "echo",
    "title",
    "type",
    "dir",
    "exit",
    "quit",
    "set",
    "env",
]


class CmdExCompleter(Completer):

    def __init__(self):
        #self.word_completer = WordCompleter(CMDEXE_INT_CMDS, ignore_case=True)
        self.sys_completer = SystemCompleter()

    def get_completions(self, document, complete_event):
        # for cmp in self.word_completer.get_completions(
                # document, complete_event):
            # yield cmp
        for cmp in self.sys_completer.get_completions(
                document, complete_event):
            yield cmp


def dprint(msg):
    if 0:
        with open("C:/cmdex.log", "a") as f:
            print >> f, msg
    pass


def ch_title(title=None):
    if title:
        ctypes.windll.kernel32.SetConsoleTitleW(unicode(title))
    else:
        cwd = os.getcwdu()
        cwds = cwd.split(u"\\")
        cwds.reverse()
        ctypes.windll.kernel32.SetConsoleTitleW(u"/".join(cwds) + u" - CMDEX")


def dump_banner():
    print """cmdex.py %s  An enhanced console
    """ % __version__


def init():
    ch_title()
    dump_banner()
    os.environ["ERRORLEVELEX"] = "0"

##-------------------------------##


def process_exit(cmd):
    "exit"
    sys.exit(0)

_last_cwd = os.getcwd()


def _ch_dir(cwd):
    global _last_cwd
    _last_cwd = os.getcwd()
    os.chdir(cwd)
    ch_title()


def expand_env(param):
    def repl(mobj):
        return os.environ.get(mobj.group(0)[1:-1], mobj.group(0))
    return re.sub(r"%[^%]*%", repl, param)


def process_cd(cmd):
    "change current directory"
    cwd = os.getcwd()
    params = re.split(r"\s+", cmd, 1)
    if len(params) == 1 or params[1] == "":
        print cwd.replace("\\", "/")
        return
    param = expand_env(params[1].strip())
    if param == "-":
        _ch_dir(_last_cwd)
    elif param in ["/", "\\"]:
        _ch_dir(cwd.split(':')[0] + ":/")
    else:
        if not os.path.isdir(param):
            print "Cannot find directory: '%s'" % param
        else:
            _ch_dir(os.path.abspath(param))


def process_set(cmd):
    "set environment variables"
    params = re.split(r"\s+", cmd, 1)
    if len(params) == 1 or params[1] == "":
        # dump_env
        keys = sorted(os.environ.keys())
        for key in keys:
            print key, "=", os.environ[key]
    else:
        param = params[1].strip()
        if "=" in param:
            k, v = param.split("=", 1)
            os.environ[k.strip()] = expand_env(v.strip())
        else:
            count = 0
            keys = os.environ.keys()
            for key in keys:
                if key.upper().startswith(param.upper()):
                    print key, "=", os.environ[key]
                    count += 1
            if not count:
                print "Environment variable '%s' is not defined." % param

_InternalCmds = {
    "q": process_exit,
    "exit": process_exit,
    "quit": process_exit,
    "cd": process_cd,
    "set": process_set,
    "env": process_set,
}


def filter_cmd(cmd):
    "filter internal command"
    name = re.split(r"\s+", cmd, 1)[0].lower()
    if name in _InternalCmds:
        _InternalCmds[name](cmd)
        return True
    else:
        return False


def split_cmd_args(cmd):
    end = 0
    if cmd[0] == '"':
        try:
            end = cmd[1:].index('"')
        except Exception:
            pass
    try:
        end = cmd.index(' ', end)
    except Exception:
        end = len(cmd)
    return cmd[0:end], cmd[end:]

g_batch = None

BAT_TEMPLATE = """
@echo off

call "{0}" %*
set RETCODE=%ERRORLEVEL%

set > "{1}.env"

exit %RETCODE%
"""


def replace_batch_file(cmdf):
    tempfile = os.environ.get("TEMP", ".") + \
        "\\cmdex_%d.bat" % random.randint(100000, 999999)
    with open(tempfile, "w") as f:
        f.write(BAT_TEMPLATE.format(cmdf, tempfile))
    return tempfile


def update_batch_env():
    global g_batch
    if not g_batch:
        return
    if not os.path.isfile(g_batch + ".env"):
        return
    lines = open(g_batch + ".env").readlines()
    lines = [line.strip() for line in lines]
    envs = [line.split("=", 1) for line in lines]
    for k, v in envs:
        if os.environ.get(k) != v:
            os.environ[k] = v
    try:
        os.remove(g_batch)
        os.remove(g_batch + ".env")
        pass
    except:
        pass
    g_batch = None


def expand_exefile(cmdf):
    dprint("exefile is: " + cmdf)
    global g_batch
    g_batch = None
    if cmdf.lower() in CMDEXE_INT_CMDS:
        return cmdf
    cmdf = cmdf.replace("/", "\\")
    origcmd = cmdf
    if cmdf[0] == '"':
        cmdf = cmdf.strip('"')
    exts = [""] + os.environ.get("PATHEXT").lower().split(";")
    isbreak = 0
    for dir in ["."] + os.environ["PATH"].split(";"):
        for ext in exts:
            f = os.path.join(dir, cmdf + ext)
            if os.path.isfile(f):
                cmdf = f.replace("/", "\\")
                isbreak = 1
                break
        if isbreak:
            break

    if cmdf.lower().endswith(".py"):
        cmdf = 'python.exe "%s"' % cmdf
    elif sys.getwindowsversion().major < 6 and cmdf.lower().endswith(".bat"):
        cmdf = replace_batch_file(cmdf)
        g_batch = cmdf
        cmdf = '"' + cmdf + '"'
    else:
        cmdf = origcmd
    dprint("exefile expand as: " + cmdf)
    return cmdf

import ply.lex as lex

tokens = ("SPACE", "LOGIC", "PIPE", "DQSTRING", "STRING")


def t_DQSTRING(t):
    r'''(\\\\)*"(\\\\|\\"|""|[^"])*("|$)'''
    return t


def t_LOGIC(t):
    r"\|\||&&|&"
    return t


def t_PIPE(t):
    r"\|"
    return t


def t_SPACE(t):
    r"[ \t]+"
    return t


def t_STRING(t):
    r"[^ \t\"]+"
    return t


def t_error(t):
    print "Illegal char '%s'" % t.value[0]
    t.lexer.skip(1)

lexer = lex.lex()


def preproc_exefile(cmd):
    lexer.input(cmd)
    NEED_EXPAND = 1
    NORMAL = 0
    status = NEED_EXPAND
    string = ""
    ret = []
    for token in lexer:
        # print token
        if token.type in ("STRING", "DQSTRING"):
            string += token.value
        elif token.type in ("SPACE", "PIPE", "LOGIC"):
            if status == NEED_EXPAND and string:
                ret.append(expand_exefile(string))
                status = NORMAL
            else:
                ret.append(string)
            string = ""
            ret.append(token.value)
            if token.type != "SPACE":
                status = NEED_EXPAND
    if status == NEED_EXPAND and string:
        ret.append(expand_exefile(string))
    else:
        ret.append(string)
    # print ret
    return "".join(ret)


def call_sys_cmd(cmd):
    ch_title(cmd)
    try:
        if cmd[0] == ";":
            startwin = 1
            cmd = cmd[1:]
        elif cmd.startswith("start "):
            startwin = 1
            cmd = cmd[6:]
        else:
            startwin = 0
        cmd = preproc_exefile(cmd.strip())
        dprint("call: " + cmd)
        st = time.time()
        ret = 0
        try:
            if startwin:
                ret = sp.call('start "" %s' % cmd, shell=1)
            else:
                ret = sp.call(cmd, shell=1)
        finally:
            et = time.time()
            update_batch_env()
            if cmd != "cls":
                dump_summary(ret, st, et)
                os.environ["ERRORLEVELEX"] = str(ret)
    finally:
        ch_title()

SUMMARY_STYLE = style_from_dict({
    Token.NORMAL: "#00FF00",
    Token.ALERM: "#FF0000",
})


def dump_summary(retcode, start, end):
    tokens = [
        (Token.NORMAL, "\n" + "=" * 80 + "\n[Return "),
        (Token.NORMAL if retcode == 0 else Token.ALERM, "%d" % retcode),
        (Token.NORMAL, "] [Start %s] [End %s] [Elapsed %.3f sec]\n" %
         (
             time.strftime("%H:%M:%S", time.localtime(start)) +
             ".%d" % int(1000 * (start - int(start))),
             time.strftime("%H:%M:%S", time.localtime(end)) +
             ".%d" % int(1000 * (end - int(end))),
             end - start
         )
         )
    ]
    print_tokens(tokens, style=SUMMARY_STYLE)


def get_prompt_args():
    args = {
        "style": style_from_dict({
            Token.PATH: "#80C0FF",
            Token.HOST: "#00FF00",
            Token.TIP: "#FF0000",
        }),
        "get_prompt_tokens": lambda cli: [
            (Token.PATH, "[%s]\n" % os.getcwdu().replace("\\", "/")),
            (Token.HOST, "%s@%s" %
             (os.getenv("COMPUTERNAME", ""), os.getenv("USERNAME", ""))),
            (Token.TIP, "$ "),
        ],
        "completer": CmdExCompleter(),
        "display_completions_in_columns": True,
        "history": InMemoryHistory(),
    }
    return args


def main():
    init()
    args = get_prompt_args()
    while True:
        try:
            try:
                cmd = prompt(**args).strip()
            except KeyboardInterrupt:
                print
                continue
            if cmd:
                if filter_cmd(cmd):
                    pass
                else:
                    call_sys_cmd(cmd)
        except KeyboardInterrupt:
            continue
        except Exception as e:
            import traceback
            traceback.print_exc()
            print type(e).__name__, ":", str(e)

if __name__ == "__main__":
    main()
