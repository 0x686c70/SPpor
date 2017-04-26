# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


# class JsonWithEncodingPipeline(object):
#     # 自定义json文件的导出
#     def __init__(self):
#         self.file = codecs.open('article.json', 'w', encoding='utf-8')
#
#     def process_item(self, item, spider):
#         lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
#         self.file.write(lines)
#         return item
#
#     def spider_closed(self, spider):
#         self.file.close()

# 自定义mysql插入
# class MysqlPipeline(object):
#     def __init__(self):
#         self.conn = MySQLdb.connect(host='192.168.45.129',
#                                     user='root',
#                                     password='root',
#                                     db='article_spider',
#                                     charset='utf8',
#                                     use_unicode=True,
#                                     )
#         self.cursor = self.conn.cursor()
#
#     def process_item(self, item, spider):
#         insert_sql = """
#           INSERT INTO jobbole_article(title,url,create_date,fav_nums)
#           VALUES(%s, %s, %s, %s)
#         """
#         self.cursor.execute(insert_sql, (item['title'], item['url'], item['create_date'], item['fav_nums']))
#         self.conn.commit()


# scrapy异步插入
class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted奖mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的Item构建不同sql语句插入数据库

        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


# scrapy内置json接口
class JsonExporterPipeline(object):
    # 调用scrapy提供的json导出器导出json文件
    def __init__(self):
        self.file = open('article_exporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# 图片处理类
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item
