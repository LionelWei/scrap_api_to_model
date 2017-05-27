# -*- coding: utf-8 -*-
from __future__ import print_function  # (at top of module)
import sys
import re
import os
import mechanize
from os.path import expanduser

reload(sys)
sys.setdefaultencoding('utf-8')

HOME_DIR = expanduser("~")
WIKI_LOGIN_URL = "http://wiki.tuniu.org/login.action?os_destination=%2Fhomepage.action"
USER_NAME = 'os_username'
PASSWORD = 'os_password'

WIKI_HOME_PAGE = "http://wiki.tuniu.org/pages/viewpage.action?pageId=71367772"


def get_username_pwd():
    f = open(HOME_DIR + '/.tnwikipwd', 'r')
    content = f.read()
    arr = content.split(",")
    if not arr[0] or not arr[1]:
        raise Exception('invalid username or password')
    return arr[0], arr[1]


def login():
    """
    表单数据:
    <get http://wiki.tuniu.org/dosearchsite.action application/x-www-form-urlencoded
  <TextControl(queryString=)>
  <SubmitControl(<None>=搜索) (readonly)>>
<loginform POST http://wiki.tuniu.org/dologin.action application/x-www-form-urlencoded
  <TextControl(os_username=)>
  <PasswordControl(os_password=)>
  <CheckboxControl(os_cookie=[true])>
  <SubmitControl(login=登录) (readonly)>
  <HiddenControl(os_destination=/homepage.action) (readonly)>>
    """
    user_pwd_tuple = get_username_pwd()
    br = mechanize.Browser()
    br.open(WIKI_LOGIN_URL)
    for form in br.forms():
        print(form)
    br.select_form(nr=1)
    br['os_username'] = user_pwd_tuple[0]
    br['os_password'] = user_pwd_tuple[1]
    br.submit()
    return br


if __name__ == '__main__':
    login()
