# -*- coding: utf-8 -*-
from __future__ import print_function  # (at top of module)
from jsmin import jsmin
import json
import sys
import re
import os
from utils import capitalize_only as cap
from wiki_login import login
from html_parser import export_json_model

URI_PATH = '../data/api_uri.txt'
JSON_DIR = '../data/json/'
ANDROID_DIR = 'android/'
OUTPUT_DIR_PREFIX = '../output/' + ANDROID_DIR

WIKI_TEST_PAGE = "http://wiki.tuniu.org/pages/viewpage.action?pageId=75006118"

# 配置
# 包名
DEFAULT_PACKAGE = 'com.blackfish.app'
PACKAGE_PREFIX = 'package '
PACKAGE_SUFFIX = ';\n\n'
# 成员可见性, 默认为public
MEMBER_PUBLIC = 'public'
# 缩进, 默认四个空格
INDENT = '    '
# 文件后缀名
JAVA_SUFFIX = '.java'
# 行位分隔符
LINE_SEP = ';\n'
IMPORT_STRING = 'import java.lang.String;\n'
IMPORT_LIST = 'import java.util.List;\n'
CLASS_PREFIX_FORMER = '\npublic class '
CLASS_PREFIX_LATTER = ' {\n'
CLASS_SUFFIX = '}'

# 需要用到的import
imports_with_sep = ''
imports_set = set()


def generate_java(input_json_file, output_class=''):
    global imports_with_sep, imports_set
    imports_with_sep = ''
    imports_set = set()
    json_file = open(input_json_file, 'r')
    json_min = jsmin(json_file.read())
    json_file_model = json.loads(json_min)
    json_file.close()
    model_content = parse_model(json_file_model)
    file_content = PACKAGE_PREFIX + DEFAULT_PACKAGE + PACKAGE_SUFFIX + imports_with_sep + CLASS_PREFIX_FORMER + \
                   output_class + CLASS_PREFIX_LATTER + model_content + CLASS_SUFFIX
    output_dir = '/'.join(DEFAULT_PACKAGE.split('.')) + '/'
    output_dir = OUTPUT_DIR_PREFIX + output_dir
    output_file_path = output_dir + output_class + JAVA_SUFFIX
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = open(output_file_path, 'w')
    output_file.write(file_content)
    output_file.close()
    print(output_class + JAVA_SUFFIX + '已生成')


def parse_model(json_model, prefix_indent=''):
    java_model = ''
    inner_java_model = []
    if type(json_model) is dict:
        for key, value in dict.iteritems(json_model):
            type_value = get_value_type(key, value)
            java_model += prefix_indent + INDENT + MEMBER_PUBLIC + ' ' + type_value + ' ' + key + LINE_SEP
            if type(value) is dict:
                cur_intent = prefix_indent + INDENT
                inner_content = parse_model(json_model[key], cur_intent)
                inner_java_model.append(assemble_inner_java(inner_content, type_value, cur_intent))
            elif type(value) is list:
                if json_model[key] and len(json_model[key]) > 0:
                    cur_intent = prefix_indent + INDENT
                    inner_content = parse_model(json_model[key][0], cur_intent)
                    inner_java_model.append(assemble_inner_java(inner_content, type_value, cur_intent))
            # print('key: %s, value: %s ' % (key, value))
    flat_inner_content = ''
    for value in inner_java_model:
        flat_inner_content += value
    return java_model + flat_inner_content


def assemble_inner_java(java_model='', class_name='', indent=''):
    static_class_prefix_former = '\n' + indent + 'public static class '
    static_class_suffix = indent + '}\n'
    return static_class_prefix_former + class_name + CLASS_PREFIX_LATTER + java_model + static_class_suffix


def get_value_type(key, value):
    type_value = type(value)
    type_value_string = ''
    value_import = ''
    if type_value is dict:
        type_value_string = cap(key) + 'Bean'
    elif type_value is list:
        value_import = IMPORT_LIST
        if not value:
            type_value_string = 'List<Object>'
        else:
            list_type_tuple = get_value_type(key, value[0])
            type_value_string = 'List<' + list_type_tuple + '>'
    elif type_value is unicode:
        type_value_string = 'String'
        value_import = IMPORT_STRING
    elif type_value is int:
        type_value_string = 'int'
    elif type_value is float:
        type_value_string = 'double'
    elif type_value is bool:
        type_value_string = 'boolean'
    else:
        type_value_string = 'Object'
    check_import(value_import)
    return type_value_string


def check_import(type_import):
    global imports_with_sep
    if type_import not in imports_set:
        imports_with_sep += type_import
        imports_set.add(type_import)


def check_args():
    argv_count = len(sys.argv)
    if argv_count < 2:
        show_help()
        exit()


def show_help():
    print('请输入JSON文件名')


if __name__ == '__main__':
    br = login()
    file_uri = open(URI_PATH, 'r')
    uris = file_uri.read().split("\n") # create a list containing all lines

    for uri in uris:
        try:
            response = br.open(uri)
            export_json_model(response.read())
            response.close()
            for parent, dirs, files in os.walk(JSON_DIR):
                for single_file in files:
                    print("filename is:" + single_file)
                    output_file_name = cap(single_file.partition('.')[0])
                    generate_java(JSON_DIR + single_file, output_file_name)
        except:
            print('exception: ' + uri)