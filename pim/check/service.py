import time
import requests
from retry import retry
from pim.check import const
import urllib3

urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()


# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
# context.verify_mode = ssl.CERT_NONE

def generate_product_code(schemaCode, key, seed):
    t = time.strftime("%m%d", time.localtime())
    return f'{schemaCode}_{t}_{key}|{seed}'


def create_product(template_product: dict):
    url = "https://{}/pim-workbench-bff/pim-core/product/save".format(const.URL_PIM)
    response = requests.request("POST", url, headers=const.HEADERS_PIM, json=template_product, verify=False)
    if response.status_code != 200:
        raise Exception('PIM 创建商品异常:{}'.format(response.status_code))
    if str((res := response.json())['code']) != '0':
        raise Exception('PIM 创建商品请求业务异常:{}'.format(res['code']))


@retry(Exception, tries=20, delay=1)
def release_product(product_code):
    url = "https://{}/pim-workbench-bff/pim-core/product/releaseLatestVersion".format(const.URL_PIM)
    body = {"operatorId": "jm006826", "productCode": product_code}
    response = requests.request("POST", url, headers=const.HEADERS_PIM, json=body, verify=False)
    if response.status_code != 200:
        raise Exception('PIM 发布商品状态码异常:{}'.format(response.status_code))
    if str((res := response.json())['code']) != '0':
        raise Exception('PIM 发布商品请求业务异常:{}'.format(res['code']))


@retry(Exception, tries=20, delay=1)
def get_tm_pid(articleNo):
    # print('开始查询商品家ID:{}'.format(articleNo))
    url = "https://{}/api/products?articleNo={}&exactMatch=1&pageSize=20&currentPage=1".format(const.URL_ROSS,
                                                                                               articleNo)
    response = requests.request("GET", url, headers=const.HEADERS_ROSS, verify=False)

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
        const.URL_ROSS, articleNo)
    response = requests.request("GET", url, headers=const.HEADERS_ROSS, verify=False)

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
    url = "https://{}/j/api/v1/product/getProductForEdit?id={}".format(const.URL_ROSS, id)

    response = requests.request("GET", url, headers=const.HEADERS_ROSS, verify=False)
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
    ##todo  需要修改
    '''
    remark = ''
    url = "https://{}/jd/jd/api/v1/product/getInfoToUpdate?productId={}".format(const.URL_ROSS, pcode)
    response = requests.request("GET", url, headers=const.HEADERS_ROSS, verify=False)
    if response.status_code != 200:
        raise Exception('商品家 查询商品详情请求出现错误:{}'.format(response.status_code))
    if (response := response.json())['code'] != 0:
        raise Exception('商品家 查询商品详情请求业务异常:{}'.format(response))
    else:
        # print(f'商品家详情：{json.dumps(response, ensure_ascii=False)}')
        if not response.get('data'):
            remark = '商品家没有查到此商品'

        if position == 'SPU':
            item = get_target_item(response['data']['multiCateProps'], attrKey, attrValue)
            if not item:
                remark = '商品中没有属性：attrKey,attrValue=>{}:{}'.format(attrKey, attrValue)
        else:
            sku_obj = get_target_item(response['data']['sku'], skuKey, skuValue1)
            if not sku_obj:
                remark = '商品中没有sku信息：{}'.format(skuValue1)
            else:
                item = get_target_item(sku_obj['saleAttrs'], attrKey, attrValue)
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


@retry(Exception, tries=5, delay=1)
def get_vip_value(pcode, attrkey='attributeId', attrvalue='', position='SPU'):
    # 需要返回的数据格式
    vbody = {
        "schemaCode": None,
        "brandId": None,
        "actual_vcode": None,
        "actual_value": None,  # 值
        "remark": ''
    }
    url = 'https://{}/vip/sd/api/vip/product/query/detail/{}?spuId={}'.format(const.URL_ROSS, pcode, pcode)
    response = requests.request("GET", url, headers=const.HEADERS_ROSS, verify=False)
    # print(f'请求URL:{url}')
    if response.status_code != 200:
        raise Exception('商品详情ERROR:{},{}'.format(pcode, response.status_code))
    if (response := response.json())['code'] != 0:
        raise Exception('商品详情业务异常:{}'.format(pcode, response))
    if not response.get('data'):
        raise Exception('商品家商品没有data信息：{}'.format(pcode))

    vbody['schemaCode'] = response['data']['basicInfo']['categoryId']
    vbody['brandId'] = response['data']['basicInfo']['brandId']

    # 获取属性key(attributeId:1686) 所在的对象
    item = get_target_item(response['data']['prodPropInfo'], attrkey, attrvalue)
    if not item:
        vbody['remark'] = '商品属性列表中没有找到=>{}:{}'.format(attrkey, attrvalue)
    else:
        if not item['values']:
            vbody['actual_vcode'] = None
            vbody['remark'] = '商品属性列表中，{}:{}，对应值为空'.format(attrkey, attrvalue)
        else:
            vbody['actual_vcode'] = item['values'][0]['optionId']
            vbody['actual_value'] = item['values'][0]['name']  # 值

    return vbody


def delete_ross_product(pid):
    url = "https://{}/api/products".format(const.URL_ROSS)
    payload = [pid]
    response = requests.request("DELETE", url, headers=const.HEADERS_ROSS, json=payload, verify=False)
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


def get_target_item(targetlist, key, value):
    '''
    过滤出list中,key:value 完全匹配的那一项
    :param targetlist:
    :param key:
    :param value:
    :return:
    '''
    for item in targetlist:
        if key not in item.keys():
            return None
        for k in item.keys():
            if k == key and str(item.get(k)) == str(value):
                return item

    # return [item for item in targetlist if key in item.keys() and item[key] == str(value)]


class CustomDict(dict):
    """
    Makes a  dictionary behave like an object,with attribute-style access.
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value
