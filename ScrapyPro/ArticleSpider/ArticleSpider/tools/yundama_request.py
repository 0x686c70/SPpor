# -*- coding: utf-8 -*-
__author__ = 'WdAxz'
__date__ = '2017-04-18 11:33'

import json
import requests
import time


def open_a_image(file_name):
    with open(file_name, 'rb') as f:
        f_data = f.read()
    return f_data


class YDMHttp(object):
    apiurl = 'http://api.yundama.com/api.php'
    username = ''
    password = ''
    appid = ''
    appkey = ''

    def __init__(self, username, password, appid, appkey):
        self.username = username
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey

    def balance(self):
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response_data = requests.post(self.apiurl, data=data)
        ret_data = json.loads(response_data.text)
        if ret_data["ret"] == 0:
            print("获取剩余积分", ret_data["balance"])
            return ret_data["balance"]
        else:
            return None

    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response_data = requests.post(self.apiurl, data=data)
        ret_data = json.loads(response_data.text)
        if ret_data["ret"] == 0:
            print("登录成功", ret_data["uid"])
            return ret_data["uid"]
        else:
            return None

    def decode(self, file_obj, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        # files = {'file': open(filename, 'rb')}
        response_data = requests.post(self.apiurl, files={'file': file_obj}, data=data)
        ret_data = json.loads(response_data.text)
        cid = ret_data['cid']
        if cid >= 0:
			# 循环请求获取返回值才能获取到，可sleep延时后获取，否则很消耗积分
            for i in range(timeout):
                get_text_data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout), 'cid': str(cid)}
                get_text_response = requests.post(self.apiurl, files={'file': file_obj}, data=get_text_data)
                get_t_ret_data = json.loads(get_text_response.text)
                if get_t_ret_data != '' and get_t_ret_data['text'] != '':
                    print("识别成功", get_t_ret_data["text"])
                    return get_t_ret_data["text"]
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''


if __name__ == "__main__":
    # 用户名
    username = 'your_ac'
    # 密码
    password = 'your_pw'
    # 软件ＩＤ，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appid = 3129
    # 软件密钥，开发者分成必要参数。登录开发者后台【我的软件】获得！
    appkey = 'your_key'
    # 图片文件
    filename = 'pin9.png'
    # 验证码类型，# 例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。在此查询所有类型 http://www.yundama.com/price.html
    codetype = 5000
    # 超时时间，秒
    timeout = 60
    # 检查
    if (username == 'username'):
        print('请设置好相关参数再测试')
    else:
        # 初始化
        yundama = YDMHttp(username, password, appid, appkey)

        # 登陆云打码
        uid = yundama.login()
        print('uid: %s' % uid)

        # 查询余额
        balance = yundama.balance()
        print('balance: %s' % balance)

        # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
        text = yundama.decode(filename, codetype, timeout)
        print(text)
 