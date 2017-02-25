#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys

import re
import argparse
from subprocess import call


def parse_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--format",
        "-f",
        choices=[
            "pdf",
            "html",
            "docx"],
        default="html",
        help="转换到文件格式")
    parser.add_argument(
        "--toc",
        "-t",
        action="store_true",
        help="在正文前包含目录（对docx无效）")
    parser.add_argument(
        "--number",
        "-n",
        action="store_true",
        help="在标题前显示编号（对docx无效）")
    parser.add_argument(
        "--indent",
        "-i",
        action='store_true',
        help='在段落前缩进两个字符（建议中文文档设置，对docx无效）')
    parser.add_argument(
        '--breakfirst',
        '-F',
        action='store_true',
        help='标题页单独占一页（只对pdf有效）')
    parser.add_argument(
        '--breakchapter',
        '-C',
        action='store_true',
        help='每一章单独从新页开始（只对pdf有效）')
    parser.add_argument(
        '--filter', '-l', default="", help='指定一个命令来过滤生成的html，从STDIN读入，从STDOUT输出（对html与pdf有效）'
    )
    parser.add_argument(
        '--template', '-T', default="", help="指定一个模板文件（对html与pdf应该是一个html模板，对docx应该是一个docx模板）"
    )
    parser.add_argument(
        '--variable', '-V', action = "append", help="指定传给pandoc的变量，见pandoc的帮助"
        )
    parser.add_argument(
        '--outfile',
        '-o',
        action='store',
        default=None,
        help='设置输出文件名，默认使用源文件名（包括路径）加相应后缀')
    parser.add_argument("mdfile", nargs=1, help="Markdown文件")

    return parser.parse_args(sys.argv[1:])


def get_base_dir():
    return os.path.dirname(os.path.abspath(sys.argv[0])) + "\.."


def filter_html(cmd, fname):
    with open(fname, encoding="utf-8") as f:
        content = f.read()
    from subprocess import Popen, PIPE
    p = Popen(cmd, shell=1, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    outdata, errdata = p.communicate(content)
    if p.returncode:
        sys.stderr.write(errdata)
        return p.returncode
    else:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(outdata)
        return 0


def gen_html(ns):
    mdfile = ns.mdfile[0]
    cmds = [r"pandoc",
            "-t",
            "html",
            "-s",
            "-S",
            ]
    if ns.template:
        cmds.append("--template=" + ns.template)
    else:
        cmds.append("--template=" + os.path.join(os.path.dirname(__file__), "pandoc_default.html"))

    if ns.toc:
        cmds.append("--toc")
    if ns.number:
        cmds.append("-N")
    if ns.indent:
        cmds += ["-V", "indent=1"]
    if ns.variable:
        for v in ns.variable:
            cmds += ["-V", v]
    if not ns.outfile:
        ns.outfile = mdfile + ".html"
    cmds += ["-o", ns.outfile, mdfile]
    ret = call(cmds, shell=1)
    if ret:
        return ret
    if ns.filter:
        return filter_html(ns.filter, ns.outfile)
    else:
        return 0


def filter_html_for_pdf(fname):
    reg_ref = re.compile(
        r'<a href="#(fn\d+)" class="footnoteRef" id="fnref\d+"><sup>\d+</sup></a>')
    reg_fn = re.compile(
        r'<li id="(fn\d+)"><p>([^<]*)<a href="#fnref\d+">[^<]*</a></p></li>')
    fn_dict = {}
    contents = []
    with open(fname, encoding="utf-8") as f:
        for line in f:
            contents.append(line)
            mobj = reg_fn.search(line)
            if mobj:
                fn_dict[mobj.group(1)] = mobj.group(2)

    def repl_ref(mobj):
        return b'<span class="fn">' + fn_dict[mobj.group(1)] + b'</span>'
    with open(fname, "w", encoding="utf-8") as f:
        for line in contents:
            if line == b'<div class="footnotes">\n':
                f.write(b"</div>\n</body>\n</html>\n")
                break
            f.write(reg_ref.sub(repl_ref, line))


def gen_pdf(ns):
    # pandoc
    mdfile = ns.mdfile[0]
    cmds = [r"pandoc",
            "-t",
            "html",
            "-s",
            "-S",
            ]
    if ns.template:
        cmds.append("--template=" + ns.template)
    else:
        cmds.append("--template=" + os.path.join(os.path.dirname(__file__), "pandoc_prince.html"))

    if ns.toc:
        cmds.append("--toc")
    if ns.number:
        cmds.append("-N")
    if ns.indent:
        cmds += ["-V", "indent=1"]
    if ns.breakfirst:
        cmds += ["-V", "breakfirst=1"]
    if ns.breakchapter:
        cmds += ["-V", "breakchapter=1"]
    if ns.variable:
        for v in ns.variable:
            cmds += ["-V", v]
    if not ns.outfile:
        ns.outfile = mdfile + ".pdf"
    tempfile = mdfile + ".tmp"
    cmds += ["-o", tempfile, mdfile]
    ret = call(cmds, shell=1)
    if ret:
        return ret

    filter_html_for_pdf(tempfile)
    if ns.filter:
        ret = filter_html(ns.filter, tempfile)
        if ret:
            return ret
    # prince
    cmds = ["prince", tempfile, "-o", ns.outfile]
    ret = call(cmds, shell=1)
    if os.path.isfile(tempfile):
        os.remove(tempfile)
    return ret


def gen_docx(ns):
    mdfile = ns.mdfile[0]
    cmds = ["pandoc",
            "-t",
            "docx",
            "-s",
            "-S",
            ]
    if ns.variable:
        for v in ns.variable:
            cmds += ["-V", v]
    if ns.template:
        cmds.append("--reference-docx=" + ns.template)
    else:
        cmds.append("--reference-docx=" + os.path.join(os.path.dirname(__file__), "pandoc_refer.docx"))
    if not ns.outfile:
        ns.outfile = mdfile + ".docx"
    cmds += ["-o", ns.outfile, mdfile]
    return call(cmds, shell=1)


def main():
    ns = parse_cmdline()
    if ns.format == "html":
        ret = gen_html(ns)
    elif ns.format == "pdf":
        ret = gen_pdf(ns)
    elif ns.format == "docx":
        ret = gen_docx(ns)
    else:
        print("format error")
        ret = 4
    sys.exit(ret)

if __name__ == "__main__":
    main()
