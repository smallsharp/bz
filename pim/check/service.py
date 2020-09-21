import time
import requests
from retry import retry
from pim.check import const
import urllib3

urllib3.disable_warnings()


def generate_product_code(schemaCode, key, seed):
    t = time.strftime("%m%d", time.localtime())
    return f'{schemaCode}_{t}_{key}|{seed}'


def create_product(template_product: dict):
    url = "http://{}/pim-workbench-bff/pim-core/product/save".format(const.url_pim)
    response = requests.request("POST", url, headers=const.headers_pim, json=template_product)
    if response.status_code != 200:
        raise Exception('PIM 创建商品异常:{}'.format(response.status_code))
    if str((res := response.json())['code']) != '0':
        raise Exception('PIM 创建商品请求业务异常:{}'.format(res['code']))


@retry(Exception, tries=20, delay=1)
def release_product(product_code):
    url = "http://{}/pim-workbench-bff/pim-core/product/releaseLatestVersion".format(const.url_pim)
    body = {"operatorId": "jm006826", "productCode": product_code}
    response = requests.request("POST", url, headers=const.headers_pim, json=body)
    if response.status_code != 200:
        raise Exception('PIM 发布商品状态码异常:{}'.format(response.status_code))
    if str((res := response.json())['code']) != '0':
        raise Exception('PIM 发布商品请求业务异常:{}'.format(res['code']))


@retry(Exception, tries=20, delay=1)
def get_tm_pid(articleNo):
    # print('开始查询商品家ID:{}'.format(articleNo))
    url = "https://{}/api/products?articleNo={}&exactMatch=1&pageSize=20&currentPage=1".format(const.url_design,
                                                                                               articleNo)
    response = requests.request("GET", url, headers=const.headers_dsg, verify=False)

    if response.status_code != 200:
        raise Exception('商品家 查询商品ID状态码异常:{}'.format(response.status_code))
    if str((res := response.json())['code']) != '0':
        raise Exception('商品家 查询商品ID请求业务异常:{}'.format(res['code']))
    if not res['data']['docs']:
        raise Exception('商品家 查询商品ID失败，code:{}，articleNo={}'.format(res['code'], articleNo))
    else:
        return res['data']['docs'][0]['_id']


@retry(Exception, tries=20, delay=1)
def get_jd_pid(articleNo):
    # print('开始查询商品家ID:{}'.format(articleNo))
    url = "https://{}/jd/api/v1/ware/wareList?exactMatch=true&criteria={\"itemNum\":{}}&pageSize=20&pageNo=1".format(
        const.url_design, articleNo)
    response = requests.request("GET", url, headers=const.headers_dsg, verify=False)

    if response.status_code != 200:
        raise Exception('商品家 查询商品ID状态码异常:{}'.format(response.status_code))
    if str((res := response.json())['code']) != '0':
        raise Exception('商品家 查询商品ID请求业务异常:{}'.format(res['code']))
    if not res['data']['docs']:
        raise Exception('商品家 查询商品ID失败，code:{}，articleNo={}'.format(res['code'], articleNo))
    else:
        return res['data']['docs'][0]['_id']


@retry(Exception, tries=20, delay=1)
def get_tm_value(id, key_tm):
    # key_type = ['singleCheck','multiCheck','input'] 取值方式是一样的，暂时用不到该字段
    url = "https://{}/j/api/v1/product/getProductForEdit?id={}".format(const.url_design, id)

    response = requests.request("GET", url, headers=const.headers_dsg, verify=False)
    # print('>>>>商品家商品详情：{}'.format(response.text))
    if response.status_code != 200:
        raise Exception('商品家 查询商品详情状态码异常:{}'.format(response.status_code))
    if (res := response.json())['code'] != 0:
        raise Exception('商品家 查询商品详情请求业务异常:{}'.format(res['code']))
    else:
        if (km := res['data'].get(key_tm)):
            return km.get('value'), km.get('type')  # ["7850140","137928"]
        return None, None


import json


@retry(Exception, tries=20, delay=1)
def get_jd_value(pcode, attrKey='attrId', attrValue='', position='SPU', skuKey='pimSkuId', skuValue1='', skuValue2=''):
    '''
    :param pcode: 货号
    :param attrKey: 属性key
    :param attrValue: 属性value
    :param position: 属性的位置
    :param skuKey: sku属性的key
    :param skuValue1: sku属性的value
    :param skuValue2
    '''
    url = "https://{}/jd/api/v1/product/getInfoToUpdate?productId={}".format(const.url_design, pcode)
    response = requests.request("GET", url, headers=const.headers_dsg, verify=False)
    if response.status_code != 200:
        raise Exception('商品家 查询商品详情状态码异常:{}'.format(response.status_code))
    if (res := response.json())['code'] != 0:
        raise Exception('商品家 查询商品详情请求业务异常:{}'.format(res['code']))
    else:
        if position == 'SPU':
            item = get_item_from_list(res['data']['multiCateProps'], attrKey, attrValue)
            # json.dumps(item, ensure_ascii=False)
        else:
            skuitem = get_item_from_list(res['data']['sku'], skuKey, skuValue1)
            item = get_item_from_list(skuitem['saleAttrs'], attrKey, attrValue)
        return {
            "schemaCode": res['data']['categoryId'],
            "brandId": res['data']['brandId'],
            "target_vcode": item['attrValues'] if item else None,  # 832670
            # "target_name": item['name'] if item else None  # 运动鞋科技
        }


def delete_design_product(pid):
    url = "https://{}/api/products".format(const.url_design)
    payload = [pid]
    response = requests.request("DELETE", url, headers=const.headers_dsg, json=payload, verify=False)
    if response.status_code != 200:
        raise Exception('商品家 删除商品时状态码异常:{}'.format(response.status_code))
    if (res := response.json())['code'] != 0:
        raise Exception('商品家 删除商品时请求业务异常:{}'.format(res['code']))


def delete_pim_product(productCode):
    url = "http://{}/pim-workbench-bff/pim-core/product/delete".format(const.url_pim)
    body = {
        "catalog": "REEBOK",
        "operatorId": "jm006826",
        "productCodes": [
            productCode
        ]
    }
    response = requests.request("POST", url, headers=const.headers_pim, json=body)
    if response.status_code != 200:
        raise Exception('pim 删除商品时状态码异常:{}'.format(response.status_code))
    if str((res := response.json())['code']) != '0':
        raise Exception('pim 删除商品时请求业务异常:{}'.format(res['code']))


def get_item_from_list(targetlist, key, value):
    for item in targetlist:
        if key not in item.keys():
            return 'no'
        for k in item.keys():
            if k == key and str(item.get(k)) == str(value):
                return item

# if __name__ == '__main__':
#     print(get_jd_value('LEB60_PIM', 'attrId', 100141))
