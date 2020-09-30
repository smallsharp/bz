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
    url = "http://{}/pim-workbench-bff/pim-core/product/save".format(const.URL_PIM)
    response = requests.request("POST", url, headers=const.HEADERS_PIM, json=template_product)
    if response.status_code != 200:
        raise Exception('PIM 创建商品异常:{}'.format(response.status_code))
    if str((res := response.json())['code']) != '0':
        raise Exception('PIM 创建商品请求业务异常:{}'.format(res['code']))


@retry(Exception, tries=20, delay=1)
def release_product(product_code):
    url = "http://{}/pim-workbench-bff/pim-core/product/releaseLatestVersion".format(const.URL_PIM)
    body = {"operatorId": "jm006826", "productCode": product_code}
    response = requests.request("POST", url, headers=const.HEADERS_PIM, json=body)
    if response.status_code != 200:
        raise Exception('PIM 发布商品状态码异常:{}'.format(response.status_code))
    if str((res := response.json())['code']) != '0':
        raise Exception('PIM 发布商品请求业务异常:{}'.format(res['code']))


@retry(Exception, tries=20, delay=1)
def get_tm_pid(articleNo):
    # print('开始查询商品家ID:{}'.format(articleNo))
    url = "https://{}/api/products?articleNo={}&exactMatch=1&pageSize=20&currentPage=1".format(const.URL_DESIGN,
                                                                                               articleNo)
    response = requests.request("GET", url, headers=const.HEADERS_DSG, verify=False)

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
        const.URL_DESIGN, articleNo)
    response = requests.request("GET", url, headers=const.HEADERS_DSG, verify=False)

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
    url = "https://{}/j/api/v1/product/getProductForEdit?id={}".format(const.URL_DESIGN, id)

    response = requests.request("GET", url, headers=const.HEADERS_DSG, verify=False)
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


@retry(Exception, tries=10, delay=1)
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
    remark = ''
    url = "https://{}/jd/jd/api/v1/product/getInfoToUpdate?productId={}".format(const.URL_DESIGN, pcode)
    response = requests.request("GET", url, headers=const.HEADERS_DSG, verify=False)
    if response.status_code != 200:
        raise Exception('商品家 查询商品详情请求出现错误:{}'.format(response.status_code))
    if (response := response.json())['code'] != 0:
        raise Exception('商品家 查询商品详情请求业务异常:{}'.format(response))
    else:
        print(f'商品家详情：{json.dumps(response, ensure_ascii=False)}')
        if not response.get('data'):
            remark = '商品家没有查到此商品'

        if position == 'SPU':
            item = get_item_from_list(response['data']['multiCateProps'], attrKey, attrValue)
            if not item:
                remark = '商品中没有属性：attrKey,attrValue=>{}:{}'.format(attrKey, attrValue)
        else:
            sku_obj = get_item_from_list(response['data']['sku'], skuKey, skuValue1)
            if not sku_obj:
                remark = '商品中没有sku信息：{}'.format(skuValue1)
            else:
                item = get_item_from_list(sku_obj['saleAttrs'], attrKey, attrValue)
                print(f'商品家item：{json.dumps(item, ensure_ascii=False)}')
                if not item:
                    remark = '商品sku中，没有查到attrKey,attrValue=>{}:{}'.format(attrKey, attrValue)
        return {
            "schemaCode": response['data']['categoryId'],
            "brandId": response['data']['brandId'],
            "target_vcode": item['attrValues'] if item else None,  # 832670
            "target_valias": item.get('attrValueAlias'),  # 832670
            "remark": remark
        }


def delete_design_product(pid):
    url = "https://{}/api/products".format(const.URL_DESIGN)
    payload = [pid]
    response = requests.request("DELETE", url, headers=const.HEADERS_DSG, json=payload, verify=False)
    if response.status_code != 200:
        raise Exception('商品家 删除商品时状态码异常:{}'.format(response.status_code))
    if (res := response.json())['code'] != 0:
        raise Exception('商品家 删除商品时请求业务异常:{}'.format(res['code']))


def delete_pim_product(productCode):
    url = "http://{}/pim-workbench-bff/pim-core/product/delete".format(const.URL_PIM)
    body = {
        "catalog": "REEBOK",
        "operatorId": "jm006826",
        "productCodes": [
            productCode
        ]
    }
    response = requests.request("POST", url, headers=const.HEADERS_PIM, json=body)
    if response.status_code != 200:
        raise Exception('pim 删除商品时状态码异常:{}'.format(response.status_code))
    if str((res := response.json())['code']) != '0':
        raise Exception('pim 删除商品时请求业务异常:{}'.format(res['code']))


def get_item_from_list(targetlist, key, value):
    for item in targetlist:
        if key not in item.keys():
            return None
        for k in item.keys():
            if k == key and str(item.get(k)) == str(value):
                return item

# if __name__ == '__main__':
#     print(get_jd_value('LEB60_PIM', 'attrId', 100141))
