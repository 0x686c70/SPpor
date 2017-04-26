# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
from scrapy.loader import ItemLoader
from items import ZhihuAnswerItem, ZhihuQuestionItem
from tools.yundama_request import YDMHttp
try:
    import urlparse as parse
except:
    from urllib import parse


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']

    # question的第一页answer的请求url
    start_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?include=data[*].is_normal,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,mark_infos,created_time,updated_time,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].author.badge[?(type=best_answerer)].topics&offset={1}&limit={2}&sort_by=default'

    header = {
        'HOST': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

    # custom_settings = {
    #     "COOKIES_ENABLED": False
    # }

    crawl_count = 0

    def parse(self, response):
        """
        提取出html页面中的所有URL并跟中URL进一步爬取
        如果提取的url中格式为/question/xxx 就下载后直接进入解析函数
        """
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        for url in all_urls:
            match_obj = re.match('(.*zhihu.com/question/(\d+))(/|$).*', url)
            if match_obj and self.crawl_count <= 10:
                self.crawl_count += 1
                # 如果提取到 question页面则提交解析
                requset_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(requset_url, headers=self.header, meta={'question_id': question_id},
                                     callback=self.parse_question)
                break
            else:
                pass
                # 不是question页面继续请求
                # yield scrapy.Request(url, headers=self.header, callback=self.parse)
        pass

    def parse_question(self, response):
        # 处理question页面，从页面中提取出具体的quesiton item

        if 'QuestionHeader-title' in response.text:
            # 新版本
            question_id = int(response.meta.get('question_id', ''))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_value('zhihu_id', question_id)
            item_loader.add_css('title', 'h1.QuestionHeader-title::text')
            item_loader.add_css('content', '.QuestionHeader-detail')
            item_loader.add_value('url', response.url)
            item_loader.add_css('answer_nums', '.List-headerText span::text')
            item_loader.add_css('comment_nums', '.QuestionHeader-actions button::text')
            item_loader.add_css('watch_user_nums', '.NumberBoard-value::text')
            item_loader.add_css('topics', '.QuestionHeader-topics .Popover div::text')

            question_item = item_loader.load_item()

        else:
            # 旧版本
            question_id = int(response.meta.get('question_id', ''))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_value('zhihu_id', question_id)
            item_loader.add_xpath("title", "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_css("answer_nums", "#zh-question-answer-num::text")
            item_loader.add_css("comment_nums", "#zh-question-meta-wrap a[name='addcomment']::text")
            # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_nums", "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")

            question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 0, 20), headers=self.header, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        answer_json = json.loads(response.text)
        is_end = answer_json['paging']['is_end']
        next_url = answer_json['paging']['next']

        # 提取answer的具体字段
        for answer in answer_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answer_item['content'] = answer['content'] if 'content' in answer else None
            answer_item['praise_nums'] = answer['voteup_count']
            answer_item['comment_nums'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.datetime.now()
            yield answer_item
        if not is_end:
            yield scrapy.Request(next_url, headers=self.header, callback=self.parse_answer)

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.header, callback=self.login)]

    def login(self, response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf = ''
        if match_obj:
            xsrf = match_obj.group(1)

        if xsrf:
            post_url = 'https://www.zhihu.com/login/email'
            post_data = {
                '_xsrf': xsrf,
                'email': '846146039@qq.com',
                'password': '667519zxc',
                'captcha': ''
                }

            import time
            t = str(int(time.time()*1000))
            captcha_url = 'https://www.zhihu.com/captcha.gif?r={0}&type=login'.format(t)
            yield scrapy.Request(captcha_url, headers=self.header, meta={'post_data': post_data},
                                 callback=self.login_after_captcha)

    def login_after_captcha(self, response):
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
            f.close()
        im = open('captcha.jpg', 'rb')
        im_read = im.read()
        im.close()
		
		# 集成云打码输入验证码
        # 用户名
        username = 'da_ge_da1'
        # 密码
        password = 'da_ge_da'
        # 软件ＩＤ，开发者分成必要参数。登录开发者后台【我的软件】获得！
        appid = 3129
        # 软件密钥，开发者分成必要参数。登录开发者后台【我的软件】获得！
        appkey = '40d5ad41c047179fc797631e3b9c3025'
        # 验证码类型，# 例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。在此查询所有类型 http://www.yundama.com/price.html
        codetype = 5000
        # 超时时间，秒
        timeout = 60
        yundama_requests = YDMHttp(username, password, appid, appkey)

        # 手动输入验证码
        # from PIL import Image
        # try:
        #     im = Image.open('captcha.jpg')
        #     im.show()
        #     im.close()
        # except:
        #     pass

        captcha = yundama_requests.decode(im_read, codetype, timeout)

        post_data = response.meta.get('post_data')
        post_url = 'https://www.zhihu.com/login/email'
        post_data['captcha'] = captcha
        return [scrapy.FormRequest(
                url=post_url,
                formdata=post_data,
                headers=self.header,
                callback=self.check_login
                )]

    def check_login(self, response):
        # 验证服务器的返回数据判断是否成功
        text_json = json.loads(response.text)
        if 'msg' in text_json and text_json['msg'] == '登录成功':
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.header)
