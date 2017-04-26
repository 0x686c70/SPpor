# -*- coding:utf-8 -*-
"""通用方法模块"""

import hashlib
import re

def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_nums(text):
    # 从字符串中提取数字
    match_re = re.match(r'.*?(\d+).*', text)
    if match_re:
        nums = match_re.group(1)
    else:
        nums = 0
    return nums


def get_common_range(value):
    match_salary = re.match('.*?(\d+).*?(\d+).*', value[0])
    if match_salary:
        s_min = int(match_salary.group(1))
        s_max = int(match_salary.group(2))
    else:
        return False
    return [s_min, s_max]

# 测试
if __name__ == '__main__':
    # print(get_md5('https://jobbole.com/'.encode('utf8')))
    print(get_common_range(['经验3-5年 /']))
    print(get_common_range(['经验不限']))
    print(get_common_range(['12k-30k '])[1])
    # if get_common_range(['经验不限']):
    #     print('ok')
    # else:
    #     s = 0
    #     print(s)
