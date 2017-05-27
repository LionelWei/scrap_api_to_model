# -*- coding: utf-8 -*-
from __future__ import print_function  # (at top of module)
import sys
import re
import os
from jsmin import jsmin
from bs4 import BeautifulSoup
from utils import capitalize_only as cap

input_html = ''


JSON_OUTPUT_DIR = '../data/'

JSON_MODEL_INPUT_KEYWORD = "bizParams"
JSON_MODEL_OUTPUT_KEYWORD = "success"

# 找到"data"字段的所有内容
JSON_OUT_REGEX = r'"data":(.*})}'

# 找到"bizParams"字段的所有内容
# 只匹配到第一个'}', 如果bizParams里有嵌套的model, 可能会有问题
JSON_IN_REGEX = r'"bizParams":(.*?}),'

URI_PARA_REGEX = r'<p>(.*)</p>'


def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    _name = parse_name(soup)
    _input, _output = parse_input_output(soup)
    return _name, _input, _output


def parse_name(soup):
    _uri = ''
    found = False
    tds = soup.findAll('td', attrs={'class': 'confluenceTd'})
    for td in tds:
        if found:
            break
        ps = td.findAll('p')
        for p in ps:
            str_p = str(p)
            uri_regs = re.findall(URI_PARA_REGEX, str_p)
            if uri_regs and len(uri_regs) > 0:
                result = str(re.findall(URI_PARA_REGEX, str_p)[0])
                if result.count("/") >= 2:
                    _uri = result
                    found = True
                    break
    arr = _uri.split("/")
    if len(arr[-1]) > 10:
        return cap(arr[-1])
    else:
        return cap(arr[-1]) + cap(arr[-2])


def parse_input_output(soup):
    json_model_input = ''
    json_model_output = ''
    code_content = soup.findAll('script', attrs={'class': 'theme: Confluence; brush: java; gutter: false'})
    for value in code_content:
        value_str = str(value)
        decoded_content = jsmin(html_decode(value_str))
        if JSON_MODEL_INPUT_KEYWORD in decoded_content:
            json_model_input = decoded_content
            json_model_input = re.findall(JSON_IN_REGEX, json_model_input)[0]
        elif JSON_MODEL_OUTPUT_KEYWORD in decoded_content:
            json_model_output = decoded_content
            json_model_output = re.findall(JSON_OUT_REGEX, json_model_output)[0]
    return json_model_input, json_model_output


def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    html_codes = (
        ("'", '&#39;'),
        ('"', '&quot;'),
        ('>', '&gt;'),
        ('<', '&lt;'),
        ('&', '&amp;')
    )
    for code in html_codes:
        s = s.replace(code[1], code[0])
    return s


def export_json_model(html_content):
    output_dir = JSON_OUTPUT_DIR
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    json_name, json_input, json_output = parse_html(html_content)

    print("name: " + json_name)
    print("input: \n" + json_input)
    print("====\n\n")
    print("output: \n" + json_output)

    file_name_input = output_dir + json_name + "Input.json"
    file_name_output = output_dir + json_name + "Output.json"
    file_input = open(file_name_input, 'w')
    file_input.write(json_input)
    file_output = open(file_name_output, 'w')
    file_output.write(json_output)


if __name__ == '__main__':
    f = open('../test/test1.html', 'r')
    input_html = f.read()
    export_json_model(input_html)
