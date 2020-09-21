# coding=utf8
from urllib import request

# 1.下载网页内容，文件名baidu.html
# request.urlretrieve('http://www.baidu.com','baidu.html')

# 2.下载图片到本地，文件名luban.jpg
# request.urlretrieve('https://uxresources.baozun.com/prod/88000028/20200225/F8B94EB6026D348DE2BA4BE66C2223F1.jpg',
#                     'luban.jpg')

import requests
import json

url = "https://api.victoriassecret.cn/vsmall/product/list/searchProductByConditionStyle.do"

data = {"data": {"conditionList": [{"key": "type", "value": ["0"], "valueType": "basic"},
                                   {"key": "saleStatus", "value": [1], "valueType": "basic"},
                                   {"key": "parentCategoryCode", "value": ["18060200006508"], "valueType": "list"},
                                   {"key": "attributeValueCode", "value": ["9d58a6cc-efcd-464d-8a49-56da67001fd8"],
                                    "valueType": "list"}], "itemFilterList": [],
                 "itemSortList": [{"frontName": "综合排序", "name": "sort", "sort": 1}], "keyword": "",
                 "notIncludeSpuCodeList": [], "withPromotionFlag": "0"}, "page": 1, "size": 36, "channelCode": 100,
        "storeCode": 1804277398}

res = requests.post(url, json=data)

print(res.text)

resjson = json.loads(res.text)

productList = resjson['data']['productList']

images = []
for product in productList:
    itemImageList = product['itemImageList']
    for image in itemImageList:
        picUrl = image['picUrl']
        # request.urlretrieve(picUrl)
        images.append(picUrl)

print(len(images))

for url in images:
    res = request.urlretrieve(url, filename=str(url).split("/")[-1])
    print(res)
