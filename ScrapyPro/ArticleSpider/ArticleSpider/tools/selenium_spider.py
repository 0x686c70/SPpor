# -*- coding:utf-8 -*-
__author__ = 'WdAxz'
__date__ = '2017-04-18 19:17'

from selenium import webdriver
from scrapy.selector import Selector


# browser.get('https://www.zhihu.com/#signin')
#
# browser.find_element_by_css_selector('.view-signin input[name="account"]').send_keys("846146039@qq.com")
# browser.find_element_by_css_selector('.view-signin input[name="password"]').send_keys('667519zxc')
# browser.find_element_by_css_selector('.view-signin button.sign-button').click()

# selenium完成微博自动登录
# import time
# time.sleep(5)
# browser.find_element_by_css_selector('#loginname').send_keys('15878750876')
# browser.find_element_by_css_selector('.info_list.password input[name="password"]').send_keys('LH8.8zxc')
# browser.find_element_by_css_selector('.info_list.login_btn a[node-type="submitBtn"]').click()
# for i in range(3):
#     browser.execute_script('window.scrollTo(0, document.body.scrollHeight); var lengthOfPage=document.body.scrollHeight; return lengthOfPage;')
#     time.sleep(3)
# t_selector = Selector(text=browser.page_source)
# print(t_selector.css('.tm-promo-price .tm-price::text').extract())
# browser.quit()

# DISABLE LOAD IMAGES FOR Chrome 不加载图片
# chrome_opt = webdriver.ChromeOptions()
# prefs = {'profile.managed_default_content_settings.images': 2}
# chrome_opt.add_experimental_option('prefs', prefs)
# E:/PythonEnvs/selenium_chrome_driver/chromedriver.exe

# browser = webdriver.PhantomJS(executable_path='E:/PhantomJS/phantomjs-2.1.1-windows/bin/phantomjs.exe')

# For Firefox不加载图片
# firefox_profile = webdriver.FirefoxProfile()
# firefox_profile.set_preference('permissions.default.image', 2)
# browser = webdriver.Firefox(executable_path='E:/PythonEnvs/firefox_driver/geckodriver.exe'
#                             , firefox_profile=firefox_profile)
#
# browser.get('https://item.taobao.com/item.htm?spm=a219r.lm895.14.20.LtgxhE&id=522142735808&ns=1&abbucket=13')
# print(browser.page_source)
# browser.quit()
