#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
An enhanced console for replacing cmd.exe.
'''

__version__ = "1.0.19"

import os
import sys
import time
import subprocess as sp
import ctypes
import re
import random
from functools import cmp_to_key as cmpkey

from pygments.token import Token
from pygments.lexers.shell import BatchLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from prompt_toolkit.contrib.regular_languages.compiler import compile
from prompt_toolkit import print_formatted_text, PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.shortcuts.prompt import CompleteStyle
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.document import Document
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import PygmentsTokens

from hlutils import get_clipboard_text


def dprint(msg):
    if 1:
        ctypes.windll.kernel32.OutputDebugStringA(str(msg))
    pass


os.environ["PATHEXT"] = ".COM;.EXE;.BAT;.CMD;.VBS;.VBE;.MSC;.PY;.PYW"
EXE_EXTS = os.environ["PATHEXT"].lower().split(os.pathsep)

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


class GitCmdCompeter(WordCompleter):
    def __init__(self):
        GIT_CMDS = [
            "add",
            "gc",
            "receive-pack",
            "add--interactive",
            "get-tar-commit-id",
            "reflog",
            "am",
            "grep",
            "relink",
            "annotate",
            "gui",
            "remote",
            "apply",
            "gui--askpass",
            "remote-ext",
            "archimport",
            "gui--askyesno",
            "remote-fd",
            "archive",
            "gui.tcl",
            "remote-ftp",
            "bisect",
            "hash-object",
            "remote-ftps",
            "bisect--helper",
            "help",
            "remote-http",
            "blame",
            "http-backend",
            "remote-https",
            "branch",
            "http-fetch",
            "repack",
            "bundle",
            "http-push",
            "replace",
            "cat-file",
            "imap-send",
            "request-pull",
            "check-attr",
            "index-pack",
            "rerere",
            "check-ignore",
            "init",
            "reset",
            "check-mailmap",
            "init-db",
            "rev-list",
            "check-ref-format",
            "instaweb",
            "rev-parse",
            "checkout",
            "interpret-trailers",
            "revert",
            "checkout-index",
            "log",
            "rm",
            "cherry",
            "ls-files",
            "send-email",
            "cherry-pick",
            "ls-remote",
            "send-pack",
            "citool",
            "ls-tree",
            "sh-i18n--envsubst",
            "clean",
            "mailinfo",
            "shortlog",
            "clone",
            "mailsplit",
            "show",
            "column",
            "merge",
            "show-branch",
            "commit",
            "merge-base",
            "show-index",
            "commit-tree",
            "merge-file",
            "show-ref",
            "config",
            "merge-index",
            "stage",
            "count-objects",
            "merge-octopus",
            "stash",
            "credential",
            "merge-one-file",
            "status",
            "credential-store",
            "merge-ours",
            "stripspace",
            "credential-wincred",
            "merge-recursive",
            "submodule",
            "cvsexportcommit",
            "merge-resolve",
            "submodule--helper",
            "cvsimport",
            "merge-subtree",
            "subtree",
            "cvsserver",
            "merge-tree",
            "svn",
            "daemon",
            "mergetool",
            "symbolic-ref",
            "describe",
            "mktag",
            "tag",
            "diff",
            "mktree",
            "unpack-file",
            "diff-files",
            "mv",
            "unpack-objects",
            "diff-index",
            "name-rev",
            "update-index",
            "diff-tree",
            "notes",
            "update-ref",
            "difftool",
            "p4",
            "update-server-info",
            "difftool--helper",
            "pack-objects",
            "upload-archive",
            "fast-export",
            "pack-redundant",
            "upload-pack",
            "fast-import",
            "pack-refs",
            "var",
            "fetch",
            "patch-id",
            "verify-commit",
            "fetch-pack",
            "prune",
            "verify-pack",
            "filter-branch",
            "prune-packed",
            "verify-tag",
            "fmt-merge-msg",
            "pull",
            "web--browse",
            "for-each-ref",
            "push",
            "whatchanged",
            "format-patch",
            "quiltimport",
            "worktree",
            "fsck",
            "read-tree",
            "write-tree",
            "fsck-objects",
            "rebase",
        ]
        # get alias
        try:
            config = os.path.expanduser("~/.gitconfig")
            if os.path.exists(config):
                start = False
                for line in open(config):
                    if line.strip() == "[alias]":
                        start = True
                    elif line.startswith("["):
                        start = False
                    elif line.strip().startswith("#"):
                        pass
                    else:
                        if "=" in line:
                            GIT_CMDS.append(line.split("=")[0].strip())
        except OSError:
            pass

        GIT_CMDS.sort(key=cmpkey(lambda x, y: len(x) - len(y)))
        WordCompleter.__init__(self, GIT_CMDS)


class SvnCmdCompleter(WordCompleter):
    def __init__(self):
        SVN_CMDS = [
            "add",
            "auth",
            "blame",
            "praise",
            "annotate",
            "ann",
            "cat",
            "changelist",
            "cl",
            "checkout",
            "co",
            "cleanup",
            "commit",
            "ci",
            "copy",
            "cp",
            "delete",
            "del",
            "remove",
            "rm",
            "diff",
            "di",
            "export",
            "help",
            "?",
            "h",
            "import",
            "info",
            "list",
            "ls",
            "lock",
            "log",
            "merge",
            "mergeinfo",
            "mkdir",
            "move",
            "mv",
            "rename",
            "ren",
            "patch",
            "propdel",
            "pdel",
            "pd",
            "propedit",
            "pedit",
            "pe",
            "propget",
            "pget",
            "pg",
            "proplist",
            "plist",
            "pl",
            "propset",
            "pset",
            "ps",
            "relocate",
            "resolve",
            "resolved",
            "revert",
            "status",
            "stat",
            "st",
            "switch",
            "sw",
            "unlock",
            "update",
            "up",
            "upgrade",
        ]
        SVN_CMDS.sort(key=cmpkey(lambda x, y: len(x) - len(y)))
        WordCompleter.__init__(self, SVN_CMDS)


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
    def __init__(self,
                 only_directories=False,
                 get_paths=None,
                 file_filter=None,
                 min_input_len=0,
                 expanduser=False):
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
                directories = [
                    os.path.dirname(os.path.join(p, text))
                    for p in self.get_paths()
                ]
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
                        if filename.lower().startswith(
                                prefix.lower()):  # ignore case
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
        self.pathcompleter = PathCompleter(only_directories=False,
                                           expanduser=True)
        self.wordcompleter = WordCompleter(CMDEXE_INT_CMDS +
                                           list(_InternalCmds.keys()),
                                           ignore_case=True)

    def get_completions(self, document, complete_event):
        text_prefix = document.text_before_cursor

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
                git(\.exe)?
                (\s+h|\s+help)?
                \s+
                (?P<git_command>[^\s]+)
                \s+
                (
                    (?P<filename>[^\s]+) |
                    "(?P<double_quoted_filename>[^\s]+)"
                )

            |
                svn(\.exe)?
                \s+
                (?P<svn_command>[^\s]+)
                \s+
                (
                    (?P<filename>[^\s]+) |
                    "(?P<double_quoted_filename>[^\s]+)"
                )

            |
                start
                \s+
                ("[^"]+"\s+)?
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


            |
                ;? # a semicolon get a start command
                # First we have an executable.
                (
                    (?P<executable>[^\s]+) |
                    "(?P<double_quoted_executable>[^\s]+)"
                )

                # Ignore texts between
                .*

                \s+

                # Filename as parameters.
                (
                    (?P<filename>[^\s]+) |
                    "(?P<double_quoted_filename>[^\s]+)"
                )
            """,
            escape_funcs={
                'double_quoted_filename':
                (lambda string: string.replace('"', '\\"')),
                'double_quoted_executable':
                (lambda string: string.replace('"', '\\"')),
            },
            unescape_funcs={
                # XXX: not enterily correct.
                'double_quoted_filename':
                (lambda string: string.replace('\\"', '"')),
                'double_quoted_executable':
                (lambda string: string.replace('\\"', '"')),
            })

        # Create GrammarCompleter
        super(CmdExCompleter, self).__init__(
            g, {
                'executable':
                ExecutableCompleter(),
                'double_quoted_executable':
                ExecutableCompleter(),
                'filename':
                PathCompleter(only_directories=False, expanduser=True),
                'double_quoted_filename':
                PathCompleter(only_directories=False, expanduser=True),
                'git_command':
                GitCmdCompeter(),
                'svn_command':
                SvnCmdCompleter(),
            })


def ch_title(title=None):
    if title:
        ctypes.windll.kernel32.SetConsoleTitleW(str(title))
    else:
        cwd = os.getcwd()
        cwds = cwd.split("\\")
        cwds.reverse()
        ctypes.windll.kernel32.SetConsoleTitleW("/".join(cwds) + " - CMDEX")


def dump_banner():
    print("""cmdex.py %s  An enhanced console
    """ % __version__)


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
        print(cwd.replace("\\", "/"))
        return
    param = expand_env(params[1].strip())
    if param == "-":
        _ch_dir(_last_cwd)
    elif param in ["/", "\\"]:
        _ch_dir(cwd.split(':')[0] + ":/")
    else:
        if not os.path.isdir(param):
            print("Cannot find directory: '%s'" % param)
        else:
            _ch_dir(os.path.abspath(param))


def process_set(cmd):
    "set environment variables"
    params = re.split(r"\s+", cmd, 1)
    if len(params) == 1 or params[1] == "":
        # dump_env
        keys = sorted(os.environ.keys())
        for key in keys:
            print(key, "=", os.environ[key])
    else:
        param = params[1].strip()
        if "=" in param:
            k, v = param.split("=", 1)
            os.environ[k.strip()] = expand_env(v.strip())
        else:
            count = 0
            keys = list(os.environ.keys())
            for key in keys:
                if key.upper().startswith(param.upper()):
                    print(key, "=", os.environ[key])
                    count += 1
            if not count:
                print("Environment variable '%s' is not defined." % param)


def process_pwd(cmd):
    print(os.getcwd())


_InternalCmds = {
    "q": process_exit,
    "exit": process_exit,
    "quit": process_exit,
    "cd": process_cd,
    "set": process_set,
    "env": process_set,
    "pwd": process_pwd,
    # "hist": process_history,
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
        cmdf = 'py.exe "%s"' % cmdf
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
    print("Illegal char '%s'" % t.value[0])
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


SUMMARY_STYLE = Style.from_dict({
    "pygments.normal": "#00FF00",
    "pygments.alerm": "#FF0000",
})


def dump_summary(retcode, start, end):
    tokens = [(Token.NORMAL, "\n" + "=" * 80 + "\n[Return "),
              (Token.NORMAL if retcode == 0 else Token.ALERM, "%d" % retcode),
              (Token.NORMAL, "] [Start %s] [End %s] [Elapsed %.3f sec]\n" %
               (time.strftime("%H:%M:%S", time.localtime(start)) +
                ".%d" % int(1000 * (start - int(start))),
                time.strftime("%H:%M:%S", time.localtime(end)) +
                ".%d" % int(1000 * (end - int(end))), end - start))]
    print_formatted_text(PygmentsTokens(tokens), style=SUMMARY_STYLE)


def get_prompt_args():
    kb = KeyBindings()

    @kb.add("c-v")
    def _(event):
        txt = get_clipboard_text()
        if txt:
            event.current_buffer.insert_text(txt.replace('\r', ''))

    args = {
        "style":
        Style.from_dict({
            "host": "#00FF00",
            "path": "#8080C0",
            "tip": "#FF0000",
        }),
        "message":
        lambda: [
            ("class:host", "%s@%s: " %
             (os.getenv("USERNAME", ""), os.getenv("COMPUTERNAME", ""))),
            ("class:path", "%s\n" % os.getcwd().replace("\\", "/")),
            ("class:tip", "$ "),
        ],
        "complete_in_thread":
        True,
        "lexer":
        PygmentsLexer(BatchLexer),
        "completer":
        CmdExCompleter(),
        "history":
        FileHistory(os.environ["USERPROFILE"] + "\\.cmdex.hist"),
        "auto_suggest":
        AutoSuggestFromHistory(),
        "enable_open_in_editor":
        True,
        "complete_style":
        CompleteStyle.MULTI_COLUMN,
        "key_bindings":
        kb,
    }
    return args


def main():
    init()
    args = get_prompt_args()
    session = PromptSession(**args)
    while True:
        try:
            try:
                cmd = session.prompt().strip()
            except KeyboardInterrupt:
                print()
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
            print(type(e).__name__, ":", str(e))


if __name__ == "__main__":
    if sys.platform.startswith("linux"):
        print("Linux is not supported yet.")
        sys.exit(1)
    main()
