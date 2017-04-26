# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from items import LagouJobItemloader, LagouJobItem
from utils.common import get_md5, get_common_range
from datetime import datetime


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']
    count = 0

    # rule的  process_links  参数传进的函数可用以控制爬取数量
    rules = (
        Rule(LinkExtractor(allow=r'zhaopin/.*'), follow=True),
        Rule(LinkExtractor(allow=r'gongsi/j\d+.*'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    # def parse_start_url(self, response):
    #     return []
    #
    # def process_results(self, response, results):
    #     if self.count <= 10:
    #         self.count += 1
    #         return results
    #     else:
    #         pass

    def parse_job(self, response):
        # 解析拉钩网职位
        salary = response.css('.job_request .salary::text').extract()
        work_years = response.xpath('//*[@class="job_request"]/p/span[3]/text()').extract()
        if get_common_range(salary):
            if len(get_common_range(salary)) == 1:
                salary_min = get_common_range(salary)[0]
                salary_max = 99
            else:
                salary_min = get_common_range(salary)[0]
                salary_max = get_common_range(salary)[1]
        else:
            salary_min = 0
            salary_max = 0

        if get_common_range(work_years):
            if len(get_common_range(work_years)) == 1:
                work_years_min = get_common_range(work_years)[0]
                work_years_max = 99
            else:
                work_years_min = get_common_range(work_years)[0]
                work_years_max = get_common_range(work_years)[1]
        else:
            work_years_min = 0
            work_years_max = 0

        item_loader = LagouJobItemloader(item=LagouJobItem(), response=response)
        item_loader.add_value('salary_min', salary_min)
        item_loader.add_value('salary_max', salary_max)
        item_loader.add_value('work_years_min', work_years_min)
        item_loader.add_value('work_years_max', work_years_max)
        item_loader.add_css('title', '.job-name::attr(title)')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        # item_loader.add_css('salary_min', '.job_request .salary::text')
        # item_loader.add_css('salary_max', '.job_request .salary::text')
        # item_loader.add_css('salary', '.job_request .salary::text')
        item_loader.add_xpath('job_city', '//*[@class="job_request"]/p/span[2]/text()')
        # item_loader.add_xpath('work_years_min', '//*[@class="job_request"]/p/span[3]/text()')
        # item_loader.add_xpath('work_years_max', '//*[@class="job_request"]/p/span[3]/text()')
        # item_loader.add_xpath('work_years', '//*[@class="job_request"]/p/span[3]/text()')
        item_loader.add_xpath('degree_demand', '//*[@class="job_request"]/p/span[4]/text()')
        item_loader.add_xpath('job_type', '//*[@class="job_request"]/p/span[5]/text()')
        item_loader.add_css('tags', '.position-label li::text')
        item_loader.add_css('publish_time', '.publish_time::text')
        item_loader.add_css('job_advantage', '.job-advantage p::text')
        item_loader.add_css('job_desc', '.job_bt div')
        item_loader.add_css('job_addr', '.work_addr')
        item_loader.add_css('company_name', '#job_company dt a img::attr(alt)')
        item_loader.add_css('company_url', '#job_company dt a::attr(href)')
        item_loader.add_value('crawl_time', datetime.now())

        job_item = item_loader.load_item()

        return job_item
