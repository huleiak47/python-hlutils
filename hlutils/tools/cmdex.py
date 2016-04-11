#!/usr/bin/env python
# -*- coding:utf-8 -*-
r'''
An enhanced console for replacing cmd.exe.
'''
# Changes:
#   ** version 1.0.13 2016-04-12 Hulei **
#       1. 优化的提示
#       2. 绑定快捷键ESC和CTRL-V
#
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

__version__ = "1.0.13"

import os
import sys
import time
import subprocess as sp
import ctypes
import re
import random

os.environ["PATHEXT"] = ".COM;.EXE;.BAT;.PY"
EXE_EXTS = os.environ["PATHEXT"].lower().split(os.pathsep)

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from prompt_toolkit.contrib.regular_languages.compiler import compile
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import print_tokens
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys


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


class PathCompleter(Completer):
    """
    Complete for Path variables.

    :param get_paths: Callable which returns a list of directories to look into
                      when the user enters a relative path.
    :param file_filter: Callable which takes a filename and returns whether
                        this file should show up in the completion. ``None``
                        when no filtering has to be done.
    :param min_input_len: Don't do autocompletion when the input string is shorter.
    """

    def __init__(self, only_directories=False, get_paths=None, file_filter=None,
                 min_input_len=0, expanduser=False):
        assert get_paths is None or callable(get_paths)
        assert file_filter is None or callable(file_filter)
        assert isinstance(min_input_len, int)
        assert isinstance(expanduser, bool)

        self.only_directories = only_directories
        self.get_paths = get_paths or (lambda: ['.'])
        self.file_filter = file_filter or (lambda _: True)
        self.min_input_len = min_input_len
        self.expanduser = expanduser

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        # Complete only when we have at least the minimal input length,
        # otherwise, we can too many results and autocompletion will become too
        # heavy.
        if len(text) < self.min_input_len:
            return

        try:
            # Do tilde expansion.
            if self.expanduser:
                text = os.path.expanduser(text)

            # Directories where to look.
            dirname = os.path.dirname(text)
            if dirname:
                directories = [os.path.dirname(os.path.join(p, text))
                               for p in self.get_paths()]
            else:
                directories = self.get_paths()

            # Start of current file.
            prefix = os.path.basename(text)

            # Get all filenames.
            filenames = []
            for directory in directories:
                # Look for matches in this directory.
                if os.path.isdir(directory):
                    for filename in os.listdir(directory):
                        if filename.lower().startswith(prefix.lower()):  # ignore case
                            filenames.append((directory, filename))

            # Sort
            filenames = sorted(filenames, key=lambda k: k[1])

            # Yield them.
            for directory, filename in filenames:
                completion = filename
                full_name = os.path.join(directory, filename)

                if os.path.isdir(full_name):
                    # For directories, add a slash to the filename.
                    # (We don't add them to the `completion`. Users can type it
                    # to trigger the autocompletion themself.)
                    filename += '/'
                else:
                    if self.only_directories or not self.file_filter(
                            full_name):
                        continue

                yield Completion(completion, -len(prefix), display=filename)
        except OSError:
            pass


class ExecutableCompleter(Completer):
    """
    Complete only excutable files in the current path.
    """

    def __init__(self):
        self.pathcompleter = PathCompleter(
            only_directories=False,
            min_input_len=1,
            file_filter=lambda name: os.path.splitext(name)[1].lower() in EXE_EXTS,
            expanduser=True)
        self.wordcompleter = WordCompleter(CMDEXE_INT_CMDS, ignore_case=True)

    def get_completions(self, document, complete_event):
        text_prefix = document.text_before_cursor
        if len(text_prefix) < 1:
            return

        # windows cmd.exe command
        for completion in self.wordcompleter.get_completions(
                document, complete_event):
            yield completion

        # executeable in PATH
        for _dir in os.environ["PATH"].split(os.pathsep):
            if not os.path.exists(_dir):
                continue
            for f in os.listdir(_dir):
                if f.lower().startswith(text_prefix.lower()) \
                and os.path.isfile(os.path.join(_dir, f)) \
                and os.path.splitext(f)[1].lower() in EXE_EXTS:
                    yield Completion(f, -len(text_prefix), display=f)

        # current dir files
        for completion in self.pathcompleter.get_completions(
                document, complete_event):
            yield completion


class CmdExCompleter(GrammarCompleter):

    def __init__(self):
        # Compile grammar.
        g = compile(
            r"""
                ;? # a semicolon get a start command
                # First we have an executable.
                (
                    (?P<executable>[^\s]+) |
                    "(?P<double_quoted_executable>[^\s]+)"
                )

                # Ignore literals in between.
                (
                    \s+
                    ("[^"]*" | '[^']*' | [^'"]+ )
                )*

                \s+

                # Filename as parameters.
                (
                    (?P<filename>[^\s]+) |
                    "(?P<double_quoted_filename>[^\s]+)"
                )
            """,
            escape_funcs={
                'double_quoted_filename': (lambda string: string.replace('"', '\\"')),
                'double_quoted_executable': (lambda string: string.replace('"', '\\"')),
            },
            unescape_funcs={
                # XXX: not enterily correct.
                'double_quoted_filename': (lambda string: string.replace('\\"', '"')),
                'double_quoted_executable': (lambda string: string.replace('\\"', '"')),
            })

        # Create GrammarCompleter
        super(CmdExCompleter, self).__init__(
            g,
            {
                'executable': ExecutableCompleter(),
                'double_quoted_executable': ExecutableCompleter(),
                'filename': PathCompleter(only_directories=False, expanduser=True),
                'double_quoted_filename': PathCompleter(only_directories=False, expanduser=True),
            })


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
        cwds = cwd.split("\\")
        cwds.reverse()
        ctypes.windll.kernel32.SetConsoleTitleW("/".join(cwds) + " - CMDEX")


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
    key_bindings_manager = KeyBindingManager.for_prompt()

    @key_bindings_manager.registry.add_binding(Keys.Escape)
    def h1(event):
        """
        When ESC has been pressed, clear the input text.
        """
        event.cli.current_buffer.cursor_right(999)
        event.cli.current_buffer.delete_before_cursor(999)

    @key_bindings_manager.registry.add_binding(Keys.ControlV)
    def h2(event):
        """
        When Ctrl-V has been pressed, insert clipboard text to the cursor.
        """
        from hlutils import get_clipboard_text
        text = get_clipboard_text(True)
        event.cli.current_buffer.insert_text(text)

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
        "key_bindings_registry": key_bindings_manager.registry,
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
