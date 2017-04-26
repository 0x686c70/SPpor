# -*- coding:utf-8 -*-
__author__ = 'WdAxz'
__date__ = '2017-04-17 20:56'
import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(
    host='192.168.45.129',
    user='root',
    passwd='root',
    db='article_spider',
    charset='utf8'
)
cursor = conn.cursor()


def crawl_ips():
    # 爬取西刺的免费IP

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    for i in range(1560):
        re = requests.get('http://www.xicidaili.com/nn/{0}'.format(i), headers=header)

        selector = Selector(text=re.text)
        all_trs = selector.css('#ip_list tr')

        ip_list =[]
        for tr in all_trs[1:]:
            speed_str = tr.css('.bar::attr(title)').extract()[0]
            if speed_str:
                speed = float(speed_str.split('秒')[0])

            all_text = tr.css('td::text').extract()

            ip = all_text[0]
            port = all_text[1]
            proxy_type = all_text[5]
            print('Now Fetch ip:{0}:{1}'.format(ip, port))

            ip_list.append((ip, port, proxy_type, speed))

            for ip_info in ip_list:
                cursor.execute(
                    "insert proxy_ip(ip,port,speed,proxy_type) VALUES('{0}', '{1}', {2}, '{3}') \
                    ON DUPLICATE KEY UPDATE speed=VALUES(speed)".format(
                        ip_info[0], ip_info[1], ip_info[3], ip_info[2]
                    )
                )
                conn.commit()


class GetIP(object):

    # 从数据库删除无效IP
    def delete_ip(self, ip):
        delete_sql = """
            DELETE FROM proxy_ip WHERE ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        # 判断ip是否可用
        http_url = 'http://www.baidu.com'
        proxy_url = 'http://{0}:{1}'.format(ip, port)
        s_proxy_url = 'https://{0}:{1}'.format(ip, port)
        try:
            proxy_dict = {
                'http': proxy_url,
                'https': s_proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code <= 300:
                print('available ip and port')
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        # 从数据库中随机获取可用的IP
        random_sql = """
            SELECT ip, port FROM proxy_ip
            ORDER BY RAND()
            LIMIT 1
        """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            judge_result = self.judge_ip(ip, port)
            if judge_result:
                # if ip_info[3] == 'HTTP':
                return 'http://{0}:{1}'.format(ip, port)
                break
                # else:
                #     return 'https://{0}:{1}'.format(ip, port)
            else:
                return self.get_random_ip()


if __name__ == '__main__':
    # get_ip = GetIP()
    # get_ip.get_random_ip()
    crawl_ips()
