# -*- coding:utf-8 -*-
"""测试知乎登录模块，spider本体中未使用"""
import re
import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib


session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")

try:
    session.cookies.load(ignore_discard=True)
except:
    print('cookies未能加载')

agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
header = {
    'HOST': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com',
    'User-Agent': agent
}


def is_login():
    # 通过个人中心页面判断是否为登录状态
    inbox_url = 'https://www.zhihu.com/inbox'
    response = session.get(inbox_url, headers=header, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True


def get_xsrf():
    response = session.get('https://www.zhihu.com', headers=header)
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text, re.DOTALL)
    if match_obj:
        return match_obj.group(1)
    else:
        return ''


def get_index():
    response = session.get('https://www.zhihu.com', headers=header)
    with open('index_page.html', 'wb') as f:
        f.write(response.text.encode('utf-8'))
    print('ok')


def get_captcha():
    import time
    t = str(int(time.time()*1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r={0}&type=login'.format(t)
    t = session.get(captcha_url, headers=header)
    with open('captcha.jpg', 'wb') as f:
        f.write(t.content)
        f.close()
	# 手动输入验证码
    from PIL import Image
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        pass

    captcha = input('输入验证码\n>')
    return captcha


def zhihu_login(account, password):
    # 知乎登陆
    if re.match(r"^1\d{10}", account):
        print('手机号码登录')
        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = {
            '_xsrf': get_xsrf(),
            'phone_num': account,
            'password': password,
            'captcha': get_captcha()
        }
    else:
        if '@' in account:
            print('邮箱登陆')
            post_url = 'https://www.zhihu.com/login/email'
            post_data = {
                '_xsrf': get_xsrf(),
                'email': account,
                'password': password,
                'captcha': get_captcha()
            }
    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()

zhihu_login('your_account', 'your_password')
get_index()
is_login()
# get_captcha()
