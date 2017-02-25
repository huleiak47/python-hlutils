#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import sys
import locale
from hlutils import consolecolor as cc

SYSENC = locale.getdefaultlocale()[1]

def debug():
    xml = open("word.xml").read()
    print(get_text(xml))
    print(get_elements_by_path(xml, "custom-translation/content"))
    #print_translations(xml, False, False)
def get_elements_by_path(xml, elem):
    if type(xml) == type(''):
        xml = [xml]
    if type(elem) == type(''):
        elem = elem.split('/')
    if (len(xml) == 0):
        return []
    elif (len(elem) == 0):
        return xml
    elif (len(elem) == 1):
        result = []
        for item in xml:
            result += get_elements(item, elem[0])
        return result
    else:
        subitems = []
        for item in xml:
            subitems += get_elements(item, elem[0])
        return get_elements_by_path(subitems, elem[1:])
textre = re.compile(r"\!\[CDATA\[(.*?)\]\]", re.DOTALL)
def get_text(xml):
    match = re.search(textre, xml)
    if not match:
        return xml.decode("utf-8").encode(SYSENC)
    return match.group(1).decode("utf-8").encode(SYSENC)
def get_elements(xml, elem):
    p = re.compile("<" + elem + ">" + "(.*?)</" + elem + ">", re.DOTALL)
    it = p.finditer(xml)
    result = []
    for m in it:
        result.append(m.group(1))
    return result

def crawl_xml(queryword):
    return urllib.request.urlopen("http://dict.yodao.com/search?keyfrom=dict.python&q=" + urllib.parse.quote_plus(queryword.decode(SYSENC).encode("utf-8")) + "&xmlDetail=true&doctype=xml").read()

def print_translations(xml, with_color, detailed):
        #print xml
    original_query = get_elements(xml, "original-query")
    queryword = get_text(original_query[0])
    custom_translations = get_elements(xml, "custom-translation")
    cc.output(queryword, cc.YELLOW); print("")
    translated = False

    for cus in custom_translations:
        source = get_elements_by_path(cus, "source/name")

        cc.output("Translations from " + source[0].decode("utf-8").encode(SYSENC), cc.RED);print("")
        contents = get_elements_by_path(cus, "translation/content")
        if with_color:
            for content in contents[0:5]:
                cc.output(get_text(content), cc.GREEN);print("")
        else:
            for content in contents[0:5]:
                print(get_text(content))
        translated = True

    yodao_translations = get_elements(xml, "yodao-web-dict")
    printed = False
    for trans in yodao_translations:
        webtrans = get_elements(trans, "web-translation")
        for web in webtrans[0:5]:
            if not printed:
                cc.output("Translations from yodao:", cc.RED);print("")
                printed = True
            keys = get_elements(web, "key")
            values = get_elements_by_path(web, "trans/value")
            summaries = get_elements_by_path(web, "trans/summary")
            key = keys[0].strip()
            value = values[0].strip()
            if with_color:
                cc.output(get_text(key) + ":\t", cc.YELLOW)
                cc.output(get_text(value), cc.GREEN);print("")
            else:
                print(get_text(value))

def usage():
    print("usage: yd.py word_to_translate")

def main():
    argv = sys.argv[1:]
    if len(argv) <= 0:
        usage()
        #debug()
        sys.exit(1)
    xml = crawl_xml(" ".join(argv))
    print_translations(xml, True, False)

if __name__ == "__main__":
    main()
