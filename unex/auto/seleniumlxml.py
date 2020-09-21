from selenium import webdriver
from time import sleep
from lxml import etree

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("window-size=1980,1080")

driver = webdriver.Chrome(options=options)

driver.get("https://news.163.com/domestic/")

html = etree.HTML(driver.page_source)

print(type(html))

news_list = html.xpath('//div[contains(@class,"data_row")]')

print(len(news_list))

for news in news_list:
    print(news.xpath('./a/img/@src')[0], news.xpath('./a/img/@alt')[0])
driver.quit()
