# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re
import scrapy
import datetime
from scrapy.loader import ItemLoader
from settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from utils.common import extract_nums
from w3lib.html import remove_tags


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, '%Y/%m/%d')
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    match_re = re.match(r'.*?(\d+).*', value)
    if match_re:
        nums = match_re.group(1)
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    # 去掉tag中提取的 评论
    if '评论' in value:
        return ''
    else:
        return value


def return_value(value):
    return value


class ArticleItemloader(ItemLoader):
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(lambda x: x+'-jobbole')
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(',')
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
          INSERT INTO jobbole_article(title,url,url_object_id,create_date,front_image_url,front_image_path,comment_nums,
          fav_nums,praise_nums,tags,content)
          VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          ON DUPLICATE KEY UPDATE fav_nums=VALUES(fav_nums),
           comment_nums=VALUES(comment_nums), praise_nums=VALUES(praise_nums)
        """
        params = (self['title'], self['url'], self['url_object_id'], self['create_date']
                  , self['front_image_url'][0], self['front_image_path'], self['comment_nums']
                  , self['fav_nums'], self['praise_nums'], self['tags'], self['content'],
                  )

        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    # 知乎问题item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    watch_user_nums = scrapy.Field()
    click_nums = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表达sql语句
        insert_sql = """
            INSERT INTO zhihu_question(zhihu_id,topics,url,title,content,comment_nums,answer_nums,
          watch_user_nums,click_nums,crawl_time)
          VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          ON DUPLICATE KEY UPDATE content=VALUES(content),
           answer_nums=VALUES(answer_nums), comment_nums=VALUES(comment_nums), watch_user_nums=VALUES(watch_user_nums),
           click_nums=VALUES(click_nums)
        """
        zhihu_id = self['zhihu_id'][0]
        topics = ','.join(self['topics'])
        url = ''.join(self['url'])
        title = ''.join(self['title'])
        content = ''.join(self['content'])
        comment_nums = extract_nums(''.join(self['comment_nums']))
        answer_nums = extract_nums(''.join(self['answer_nums']))
        if len(self['watch_user_nums']) == 2:
            watch_user_nums = int(self['watch_user_nums'][0])
            click_nums = int(self['watch_user_nums'][1])
        else:
            watch_user_nums = int(self['watch_user_nums'][0])
            click_nums = 0
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title
                  , content, comment_nums, answer_nums
                  , watch_user_nums, click_nums, crawl_time,
                  )

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表达sql语句
        insert_sql = """
            INSERT INTO zhihu_answer(zhihu_id,url,question_id,author_id,content,praise_nums,comment_nums,
          create_time,update_time,crawl_time)
          VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          ON DUPLICATE KEY UPDATE content=VALUES(content),
           comment_nums=VALUES(comment_nums), praise_nums=VALUES(praise_nums), update_time=VALUES(update_time)
        """

        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)
        params = (self['zhihu_id'], self['url'], self['question_id'], self['author_id'], self['content']
                  , self['praise_nums'], self['comment_nums'], create_time
                  , update_time, self['crawl_time'].strftime(SQL_DATETIME_FORMAT),
                  )

        return insert_sql, params


def remove_splash(value):
    return value.replace('/', '').rstrip()


def handle_jobaddr(value):
    addr_list = value.split('\n')
    addr_list = [item.strip() for item in addr_list if item.strip() != '查看地图']
    return ''.join(addr_list)


class LagouJobItemloader(ItemLoader):
    # 自定义输出itemloader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    # salary = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    # work_years = scrapy.Field()
    work_years_min = scrapy.Field()
    work_years_max = scrapy.Field()
    degree_demand = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    publish_time = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(','),
    )
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表达sql语句
        insert_sql = """
            INSERT INTO lagou_job(title,url,url_object_id,salary_min,salary_max,job_city,work_years_min,
          work_years_max,degree_demand,job_type,publish_time ,tags ,job_advantage ,job_desc ,job_addr,
          company_url, company_name , crawl_time
          )
          VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          ON DUPLICATE KEY UPDATE job_desc=VALUES(job_desc),
           publish_time=VALUES(publish_time), salary_min=VALUES(salary_min), salary_max=VALUES(salary_max),
           tags=VALUES(tags)
        """
        # 18各字段
        params = (self['title'], self['url'], self['url_object_id'], self['salary_min'], self['salary_max']
                  , self['job_city'], self['work_years_min'], self['work_years_max'], self['degree_demand'],
                  self['job_type'], self['publish_time'], self['tags'], self['job_advantage'],
                  self['job_desc'], self['job_addr'], self['company_url']
                  , self['company_name'], self['crawl_time'].strftime(SQL_DATETIME_FORMAT),
                  )

        return insert_sql, params
