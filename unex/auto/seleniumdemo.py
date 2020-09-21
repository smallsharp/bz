from selenium import webdriver
from time import sleep
from lxml import etree

driver = webdriver.Chrome()

driver.get("https://news.163.com/domestic/")

# ��ȡ���������б�
news_list = driver.find_elements_by_xpath('//div[contains(@class,"data_row")]')

print(len(news_list))

for news in news_list:
    img = news.find_element_by_xpath('./a/img')
    src = img.get_attribute('src')
    # title = img.get_attribute('alt')
    title = news.find_element_by_xpath('./div//a').text
    print(src,title)

driver.quit()
