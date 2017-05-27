# -*- coding: utf-8 -*-
from __future__ import print_function  # (at top of module)
import sys
import re
import os
from jsmin import jsmin
from bs4 import BeautifulSoup
from wiki_login import login

WIKI_API_MAIN = "http://wiki.tuniu.org"
WIKI_SHOW_CHILDREN_SUFFIX = "&showChildren=true"
WIKI_API_ROOT_PAGE = WIKI_API_MAIN + "/pages/viewpage.action?pageId=71367772" + WIKI_SHOW_CHILDREN_SUFFIX
HREF_REGEX = r'href="(.*)"'
URI_OUTPUT_DIR = '../data/'

uri_set = set()

suffix_len = len(WIKI_SHOW_CHILDREN_SUFFIX)


# 爬到所有有接口数据的html页面, 保存到文件里
def dfs_html(browser, uri):
    response = browser.open(uri)
    html_content = response.read()
    response.close()
    soup = BeautifulSoup(html_content, 'html.parser')
    spans = soup.findAll('span', attrs={'class': 'child-display'})
    if not spans:
        real_data_link = uri[0:-suffix_len]
        print(real_data_link)
        uri_set.add(real_data_link)
        return
    for span in spans:
        hrefs = span.findAll('a')
        if not hrefs:
            break
        for href in hrefs:
            dir_link = WIKI_API_MAIN + re.findall(HREF_REGEX, str(href))[0] + WIKI_SHOW_CHILDREN_SUFFIX
            dfs_html(browser, dir_link)


if __name__ == '__main__':
    br = login()
    dfs_html(br, WIKI_API_ROOT_PAGE)
    output_dir = URI_OUTPUT_DIR
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    uri_file = output_dir + 'api_uri.txt'
    file_uri = open(uri_file, 'w')
    for uri in uri_set:
        file_uri.write(uri + '\n')
