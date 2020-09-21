# coding=utf-8
import requests
from retrying import retry
from lxml import etree


class Qiubai_spider():
    def __init__(self):
        self.url = "http://www.qiushibaike.com/8hr/page/{}/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1 Trident/5.0;"
        }

    @retry(stop_max_attempt_number=5)  # 调用retry，当assert出错时候，重复请求5次
    def parse_url(self, url):
        response = requests.get(url, timeout=10, headers=self.headers)  # 请求url
        assert response.status_code == 200  # 当响应码不是200时候，做断言报错处理
        print(url)
        return etree.HTML(response.text)  # 返回etree之后的html

    def parse_content(self, html):
        item_temp = html.xpath("//div[@class='article block untagged mb15']")
        print(len(item_temp))
        for item in item_temp:
            # 获取用户头像地址
            avatar = item.xpath("./div[1]/a[1]/img/@src")[0] if len(item.xpath("./div[1]/a[1]/img/@src")) > 0 else None
            # 为头像地址添加前缀
            if avatar is not None and not avatar.startswith("http:"):
                avatar = "http:" + avatar
            print(avatar)
            name = item.xpath("./div[1]/a[2]/h2/text()")[0]  # 获取用户名
            print(name)
            content = item.xpath("./a[@class='contentHerf']/div/span/text()")[0]  # 获取内容
            print(content)
            star_number = item.xpath("./div[@class='stats']/span[1]/i/text()")[0]  # 获取点赞数
            print(star_number)
            comment_number = item.xpath("./div[@class='stats']/span[2]/a/i/text()")[0]  # 获取评论数
            print(comment_number)
            print("*" * 100)

    def run(self):
        '''函数的主要逻辑实现
        '''
        url = self.url.format(1)  # 获取到url
        html = self.parse_url(url)  # 请求url
        self.parse_content(html)  # 解析页面内容并把内容存入内容队列


if __name__ == "__main__":
    qiubai = Qiubai_spider()
    qiubai.run()
