import time
import requests
from retry import retry
from pim.check import model
import urllib3
import json

urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()


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


class PimService():

    def __init__(self, domain, headers):
        self.domain = domain
        self.headers = headers

    def create_product(self, body):
        url = "https://{}/pim-workbench-bff/pim-core/product/save".format(self.domain)
        response = requests.request("POST", url, headers=self.headers, json=body, verify=False)
        if response.status_code != 200:
            raise Exception('PIM 创建商品异常:{}'.format(response.status_code))
        if str((res := response.json())['code']) != '0':
            raise Exception('PIM 创建商品请求业务异常:{}'.format(res['code']))

    @retry(Exception, tries=2, delay=1)
    def release_product(self, product_code):
        url = "https://{}/pim-workbench-bff/pim-core/product/releaseLatestVersion".format(self.domain)
        body = {"operatorId": "jm006826", "productCode": product_code}
        response = requests.request("POST", url, headers=self.headers, json=body, verify=False)
        if response.status_code != 200:
            raise Exception('PIM 发布商品状态码异常:{}'.format(response.status_code))
        if str((res := response.json())['code']) != '0':
            raise Exception('PIM 发布商品请求业务异常:{}'.format(res['code']))

    def delete_pim_product(self, productCode):
        url = "http://{}/pim-workbench-bff/pim-core/product/delete".format(self.domain)
        body = {
            "catalog": "REEBOK",
            "operatorId": "jm006826",
            "productCodes": [
                productCode
            ]
        }
        response = requests.request("POST", url, headers=self.headers, json=body)
        if response.status_code != 200:
            raise Exception('pim 删除商品时状态码异常:{}'.format(response.status_code))
        if str((res := response.json())['code']) != '0':
            raise Exception('pim 删除商品时请求业务异常:{}'.format(res['code']))


class RossService():

    def __init__(self, domain, headers):
        self.domain = domain
        self.headers = headers

    @retry(Exception, tries=1, delay=0.5)
    def get_product_id_tm(self, productNo, categoryId):
        # https://ross-api-uat.baozun.com/pim-service/api/products/list
        url = "https://{}/pim-service/api/products/list".format(self.domain)
        body = {"currentPage": "1", "pageSize": 20, "articleNo": productNo, "categories": categoryId}
        response = requests.request("POST", url, json=body, headers=self.headers, verify=False)

        if response.status_code != 200:
            raise Exception('商品PID状态码异常:{}'.format(response.status_code))
        if str((res := response.json())['code']) != '0':
            raise Exception('商品PID请求业务异常:{}'.format(res['code']))
        if not res['data']['docs']:
            raise Exception('商品PID获取失败')
        else:
            return res['data']['docs'][0]['_id']

    @retry(Exception, tries=1, delay=1)
    def get_product_tm(self, id, target_key):
        body = {
            "schemaCode": None,
            "brandId": None,
            "vcode": None,  # value code
            "value": None,  # value name
            "remark": ''
        }
        url = "https://{}/tmall/j/api/v1/product/getProductForEdit?id={}".format(self.domain, id)
        response = requests.request("GET", url, headers=self.headers, verify=False)
        if response.status_code != 200:
            raise Exception('商品详情状态码异常:{}'.format(response.status_code))
        if (response := response.json())['code'] != 0:
            raise Exception('商品详情业务异常:{}'.format(response['code']))
        if not response.get('data'):
            raise Exception('商品详情没有data信息：{}'.format(id))

        body['brandId'] = response['data']['prop_20000']

        # targetkey 所在的对象
        item = response['data'].get(target_key)
        if not item:
            body['remark'] = '商品属性中，没有:{}'.format(target_key)
        else:
            if not item.get('value'):  # 这个属性对应的 value(vcode)为空的情况
                body['remark'] = '商品属性中，{}对应的值为空'.format(target_key)
            else:
                body['vcode'] = item['value']  # 天猫的value 是code值，displayName是显示的值
                # 判断这个值 有没有可选项，有的话取出value 对应的displayName,  没有就还是默认的None
                if item.get('options'):
                    body['value'] = ''.join([i['displayName'] for i in item['options'] if i['value'] == item['value']])
        return body

    @retry(Exception, tries=5, delay=1)
    def get_product_vip(self, pcode, attrkey='attributeId', attrvalue='', position='SPU'):
        # 需要返回的数据格式
        body = {
            "schemaCode": None,
            "brandId": None,
            "vcode": None,
            "value": None,  # 值
            "remark": ''
        }
        url = 'https://{}/vip/sd/api/vip/product/query/detail/{}?spuId={}'.format(self.domain, pcode, pcode)
        response = requests.request("GET", url, headers=self.headers, verify=False)
        # print(f'请求URL:{url}')
        if response.status_code != 200:
            raise Exception('商品详情ERROR:{},{}'.format(pcode, response.status_code))
        if (response := response.json())['code'] != 0:
            raise Exception('商品详情业务异常:{}'.format(pcode, response))
        if not response.get('data'):
            raise Exception('商品家商品没有data信息：{}'.format(pcode))

        body['schemaCode'] = response['data']['basicInfo']['categoryId']
        body['brandId'] = response['data']['basicInfo']['brandId']

        # 获取属性key(attributeId:1686) 所在的对象
        item = get_target_item(response['data']['prodPropInfo'], attrkey, attrvalue)
        if not item:
            body['remark'] = '商品属性列表中没有找到=>{}:{}'.format(attrkey, attrvalue)
        else:
            if not item['values']:
                body['vcode'] = None
                body['remark'] = '商品属性列表中，{}:{}，对应值为空'.format(attrkey, attrvalue)
            else:
                body['vcode'] = item['values'][0]['optionId']
                body['value'] = item['values'][0]['name']  # 值

        return body

    @retry(Exception, tries=10, delay=1)
    def get_jd_pid(self, articleNo, domain, headers):
        # print('开始查询商品家ID:{}'.format(articleNo))
        url = "https://{}/jd/api/v1/ware/wareList?exactMatch=true&criteria={\"itemNum\":{}}&pageSize=20&pageNo=1".format(
            self.domain, articleNo)
        response = requests.request("GET", url, headers=self.headers, verify=False)

        if response.status_code != 200:
            raise Exception('商品家 查询商品ID状态码异常:{}'.format(response.status_code))
        if str((res := response.json())['code']) != '0':
            raise Exception('商品家 查询商品ID请求业务异常:{}'.format(res['code']))
        if not res['data']['docs']:
            raise Exception('商品家 查询商品ID失败，code:{}，articleNo={}'.format(res['code'], articleNo))
        else:
            return res['data']['docs'][0]['_id']

    @retry(Exception, tries=10, delay=1)
    def get_jd_value(self, pcode, attrKey='attrId', attrValue='', position='SPU', skuKey='pimSkuId'):
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
        url = "https://{}/jd/jd/api/v1/product/getInfoToUpdate?productId={}".format(self.domain, pcode)
        response = requests.request("GET", url, headers=self.headers, verify=False)
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
                sku_obj = get_target_item(response['data']['sku'], skuKey, 'K1_{}'.format(pcode))
                if not sku_obj:
                    remark = f'商品中没有sku信息：K1_{pcode}'
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

    def delete_ross_product(self, pid):
        url = "https://{}/api/products".format(self.domain)
        payload = [pid]
        response = requests.request("DELETE", url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            raise Exception('商品家 删除商品时状态码异常:{}'.format(response.status_code))
        if (res := response.json())['code'] != 0:
            raise Exception('商品家 删除商品时请求业务异常:{}'.format(res['code']))


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
