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

    @retry(Exception, tries=3, delay=1)
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

    @retry(Exception, tries=1, delay=1)
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
            raise Exception('商品没有data信息：{}'.format(pcode))

        body['schemaCode'] = response['data']['basicInfo']['categoryId']
        body['brandId'] = response['data']['basicInfo']['brandId']

        # 获取属性key(attributeId:1686) 所在的对象
        item = get_target_item(response['data']['prodPropInfo'], attrkey, attrvalue)
        if not item:
            body['remark'] = '商品属性中没有=>{}:{}'.format(attrkey, attrvalue)
        else:
            if not item['values']:
                body['remark'] = '商品属性中，{}:{}，对应值为空'.format(attrkey, attrvalue)
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


if __name__ == '__main__':
    response = json.loads('''{
    "code": 0,
    "message": "成功",
    "key": "success",
    "data": {
        "basicInfo": {
            "saasTenantCode": "TopSports",
            "id": "5fd3747ea8c220000126f5b2",
            "shopCode": "26785",
            "operationCode": null,
            "platformCode": null,
            "isValid": null,
            "isDelete": false,
            "createdTime": "2020-12-11T13:30:38.576+0000",
            "updatedTime": "2020-12-11T13:30:38.903+0000",
            "createdBy": null,
            "updatedBy": null,
            "spuId": "TS030202_1211_year_2017nian_3828",
            "name": "商品名称_TS030202_1211_year_2017nian_3828",
            "colorCode": null,
            "status": 0,
            "errorMsg": null,
            "quantity": null,
            "cc": [
                "TS030202_1211_year_2017nian_3828"
            ],
            "brandId": 10004124,
            "categoryId": 391185,
            "productDescription": "商品名称_TS030202_1211_year_2017nian_3828",
            "productPushTime": null,
            "pdpSyncTime": null,
            "pictureSyncTime": null,
            "pdpSyncStatus": 0,
            "pictureSyncStatus": 0,
            "skuSyncWarning": 0,
            "productResource": 2,
            "originalSpuId": null,
            "productType": 0,
            "isFragile": null,
            "isLarge": null,
            "isPrecious": null,
            "brands": [
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10000223",
                    "brand_name": "阿迪达斯",
                    "brand_name_eng": "adidas"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10000630",
                    "brand_name": "耐克",
                    "brand_name_eng": "Nike"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10000677",
                    "brand_name": "锐步",
                    "brand_name_eng": "Reebok"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10004124",
                    "brand_name": "",
                    "brand_name_eng": "ASICS"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10007186",
                    "brand_name": "",
                    "brand_name_eng": "ONITSUKA TIGER"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10006920",
                    "brand_name": "范斯",
                    "brand_name_eng": "VANS"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10000329",
                    "brand_name": "彪马",
                    "brand_name_eng": "PUMA"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10000513",
                    "brand_name": "匡威",
                    "brand_name_eng": "converse"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10012283",
                    "brand_name": "",
                    "brand_name_eng": "The North Face"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10004819",
                    "brand_name": "添柏岚",
                    "brand_name_eng": "TIMBERLAND"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10000406",
                    "brand_name": "",
                    "brand_name_eng": "Columbia"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10005107",
                    "brand_name": "",
                    "brand_name_eng": "UGG"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10012552",
                    "brand_name": "",
                    "brand_name_eng": "Jordan"
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10000685",
                    "brand_name": "阿迪达斯三叶草",
                    "brand_name_eng": ""
                },
                {
                    "vendor_id": 26785,
                    "vendor_name": "滔搏企业发展（上海）有限公司",
                    "brand_id": "10039256",
                    "brand_name": "",
                    "brand_name_eng": "ADIDAS NEO"
                }
            ],
            "categoryName": "儿童凉鞋",
            "productTypeName": "普通商品"
        },
        "skuInfo": {
            "salePropNames": [
                "颜色",
                "尺码"
            ],
            "salePropIds": [
                134,
                453
            ],
            "skus": [
                {
                    "saasTenantCode": "TopSports",
                    "id": "5fd3747ea8c220000126f5af",
                    "shopCode": "26785",
                    "operationCode": null,
                    "platformCode": null,
                    "isValid": null,
                    "isDelete": false,
                    "createdTime": "2020-12-11T13:30:38.588+0000",
                    "updatedTime": "2020-12-11T13:30:38.588+0000",
                    "createdBy": null,
                    "updatedBy": null,
                    "spuId": "TS030202_1211_year_2017nian_3828",
                    "name": null,
                    "description": null,
                    "skuId": "332a67650d1edb65e2bcf8719c6789",
                    "status": null,
                    "quantity": null,
                    "price": null,
                    "cc": "TS030202_1211_year_2017nian_3828",
                    "groupSn": "TS030202_1211_year_2017nian_3828",
                    "barcode": "B1_TS030202_1211_year_2017nian_3828",
                    "marketPrice": 88.0,
                    "sellPrice": 88.0,
                    "isSyncSku": 0,
                    "errorMsg": null,
                    "propValueAlias": [
                        "粉红色",
                        "38"
                    ]
                },
                {
                    "saasTenantCode": "TopSports",
                    "id": "5fd3747ea8c220000126f5b7",
                    "shopCode": "26785",
                    "operationCode": null,
                    "platformCode": null,
                    "isValid": null,
                    "isDelete": false,
                    "createdTime": "2020-12-11T13:30:38.915+0000",
                    "updatedTime": "2020-12-11T13:30:38.915+0000",
                    "createdBy": null,
                    "updatedBy": null,
                    "spuId": "TS030202_1211_year_2017nian_3828",
                    "name": null,
                    "description": null,
                    "skuId": "182257c898a579ba13d458f91c0ceff4",
                    "status": null,
                    "quantity": null,
                    "price": null,
                    "cc": "TS030202_1211_year_2017nian_3828",
                    "groupSn": "TS030202_1211_year_2017nian_3828",
                    "barcode": "B2_TS030202_1211_year_2017nian_3828",
                    "marketPrice": 89.0,
                    "sellPrice": 89.0,
                    "isSyncSku": 0,
                    "errorMsg": null,
                    "propValueAlias": [
                        "粉红色",
                        "39"
                    ]
                }
            ]
        },
        "prodPropInfo": [
            {
                "attributeId": 2266,
                "attributeName": "适用性别",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 52,
                "required": true,
                "multi": true,
                "options": [
                    {
                        "attributeId": 2266,
                        "optionId": 31614,
                        "name": "男童",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 4,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 2266,
                        "optionId": 31615,
                        "name": "女童",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 5,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    }
                ],
                "values": []
            },
            {
                "attributeId": 43,
                "attributeName": "闭合方式",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 20,
                "required": true,
                "multi": false,
                "options": [
                    {
                        "attributeId": 43,
                        "optionId": 153,
                        "name": "套脚",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 1,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "set foot"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 43,
                        "optionId": 154,
                        "name": "系带",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 2,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "lase"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 43,
                        "optionId": 155,
                        "name": "魔术贴",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 3,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "velcro"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 43,
                        "optionId": 156,
                        "name": "搭扣",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 4,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "hasp"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 43,
                        "optionId": 157,
                        "name": "拉链",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 5,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "zipper"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 43,
                        "optionId": 158,
                        "name": "松紧带",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 6,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "elastic"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 43,
                        "optionId": 294,
                        "name": "抽带搭扣",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 8,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "sling back with hasp"
                        },
                        "externaldata": ""
                    }
                ],
                "values": []
            },
            {
                "attributeId": 595,
                "attributeName": "功能",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 52,
                "required": true,
                "multi": true,
                "options": [
                    {
                        "attributeId": 595,
                        "optionId": 12612,
                        "name": "防水",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 34,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 12613,
                        "name": "保暖",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 35,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 12626,
                        "name": "荧光",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 49,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 12636,
                        "name": "防臭",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 59,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 13534,
                        "name": "防滑",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 78,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 18034,
                        "name": "速干",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 271,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 18036,
                        "name": "透气",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 273,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 18288,
                        "name": "耐磨",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 283,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 18467,
                        "name": "减震",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 285,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 18468,
                        "name": "包裹性",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 286,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 18471,
                        "name": "轻便",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 289,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 18472,
                        "name": "抗冲击",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 290,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 18473,
                        "name": "增高",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 291,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 18479,
                        "name": "吸汗",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 297,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 28375,
                        "name": "矫正",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 452,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 595,
                        "optionId": 44063,
                        "name": "支撑稳定",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 767,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    }
                ],
                "values": []
            },
            {
                "attributeId": 47,
                "attributeName": "适用场景",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 1060,
                "required": false,
                "multi": true,
                "options": [
                    {
                        "attributeId": 47,
                        "optionId": 206,
                        "name": "宴会",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 4,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "party"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 47,
                        "optionId": 2956,
                        "name": "户外",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 15,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "ourdoor"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 47,
                        "optionId": 2960,
                        "name": "运动",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 19,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "sports"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 47,
                        "optionId": 11621,
                        "name": "旅行",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 21,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 47,
                        "optionId": 11740,
                        "name": "其他",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 28,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 47,
                        "optionId": 20477,
                        "name": "居家",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 66,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 47,
                        "optionId": 20574,
                        "name": "沙池沙滩",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 80,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 47,
                        "optionId": 20639,
                        "name": "日常",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 96,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 47,
                        "optionId": 20641,
                        "name": "涉水",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 98,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 47,
                        "optionId": 27513,
                        "name": "校园",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 110,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    }
                ],
                "values": []
            },
            {
                "attributeId": 980,
                "attributeName": "类型",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 1076,
                "required": true,
                "multi": true,
                "options": [
                    {
                        "attributeId": 980,
                        "optionId": 18342,
                        "name": "洞洞鞋",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 453,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 980,
                        "optionId": 20700,
                        "name": "沙滩鞋",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 1373,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 980,
                        "optionId": 19343,
                        "name": "鱼嘴鞋",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 1921,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 980,
                        "optionId": 42818,
                        "name": "果冻鞋",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 2196,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 980,
                        "optionId": 42843,
                        "name": "亲子鞋",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 2221,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 980,
                        "optionId": 42869,
                        "name": "全凉鞋",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 2247,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 980,
                        "optionId": 11921,
                        "name": "其他",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 2337,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    }
                ],
                "values": []
            },
            {
                "attributeId": 42,
                "attributeName": "鞋头款式",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 1028,
                "required": false,
                "multi": false,
                "options": [
                    {
                        "attributeId": 42,
                        "optionId": 5402,
                        "name": "夹趾",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 1,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "thong"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 42,
                        "optionId": 5403,
                        "name": "套趾",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 2,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "toe covered"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 42,
                        "optionId": 5404,
                        "name": "露趾",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 3,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "open toe"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 42,
                        "optionId": 149,
                        "name": "尖头",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 4,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "pointed toes"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 42,
                        "optionId": 150,
                        "name": "方头",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 5,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "square toe"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 42,
                        "optionId": 151,
                        "name": "圆头",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 6,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "round toe"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 42,
                        "optionId": 152,
                        "name": "扁头",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 7,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "oblate toe"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 42,
                        "optionId": 11056,
                        "name": "其他",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 8,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 42,
                        "optionId": 20646,
                        "name": "鱼嘴",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 9,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    }
                ],
                "values": []
            },
            {
                "attributeId": 118,
                "attributeName": "适用人群",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 52,
                "required": true,
                "multi": true,
                "options": [
                    {
                        "attributeId": 118,
                        "optionId": 3674,
                        "name": "亲子",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 6,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "mothers and children"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 118,
                        "optionId": 11836,
                        "name": "婴童",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 10,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 118,
                        "optionId": 39637,
                        "name": "幼童",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 11,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 118,
                        "optionId": 39642,
                        "name": "中大童",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 14,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 118,
                        "optionId": 16384,
                        "name": "青少年",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 18,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    }
                ],
                "values": []
            },
            {
                "attributeId": 209,
                "attributeName": "适用年龄",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 52,
                "required": true,
                "multi": true,
                "options": [
                    {
                        "attributeId": 209,
                        "optionId": 21446,
                        "name": "0-6个月",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 3,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 209,
                        "optionId": 21652,
                        "name": "6-12个月",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 6,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 209,
                        "optionId": 21441,
                        "name": "1-3岁",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 11,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 209,
                        "optionId": 2060,
                        "name": "3-6岁",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 12,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "3-6 years old"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 209,
                        "optionId": 2061,
                        "name": "6-12岁",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 13,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "6-12 years old"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 209,
                        "optionId": 2950,
                        "name": "12岁以上",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 26,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "Over 12-year-old"
                        },
                        "externaldata": ""
                    }
                ],
                "values": []
            },
            {
                "attributeId": 51,
                "attributeName": "跟高",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 20,
                "required": true,
                "multi": false,
                "options": [
                    {
                        "attributeId": 51,
                        "optionId": 226,
                        "name": "平跟",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 1,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "low-cutter"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 51,
                        "optionId": 227,
                        "name": "低跟",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 2,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "Low"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 51,
                        "optionId": 228,
                        "name": "中跟",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 3,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "Medium high"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 51,
                        "optionId": 229,
                        "name": "高跟",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 4,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "high"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 51,
                        "optionId": 237,
                        "name": "超高跟",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 7,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "super high"
                        },
                        "externaldata": ""
                    }
                ],
                "values": []
            },
            {
                "attributeId": 578,
                "attributeName": "选购热点",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 36,
                "required": false,
                "multi": true,
                "options": [
                    {
                        "attributeId": 578,
                        "optionId": 30506,
                        "name": "专柜同款",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 335,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 578,
                        "optionId": 30507,
                        "name": "明星同款",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 336,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 578,
                        "optionId": 32173,
                        "name": "特价款",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 345,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 578,
                        "optionId": 32174,
                        "name": "唯品专供款",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 346,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 578,
                        "optionId": 32175,
                        "name": "限量款",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 347,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 578,
                        "optionId": 32176,
                        "name": "线上专供款",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 348,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 578,
                        "optionId": 32178,
                        "name": "联名款",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 350,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 578,
                        "optionId": 32179,
                        "name": "主推款",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 351,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    }
                ],
                "values": [
                    {
                        "optionId": 32178,
                        "name": "联名款",
                        "alias": null
                    }
                ]
            },
            {
                "attributeId": 974,
                "attributeName": "面材质",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 52,
                "required": true,
                "multi": true,
                "options": [
                    {
                        "attributeId": 974,
                        "optionId": 11723,
                        "name": "牛皮",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 1,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 11605,
                        "name": "羊皮",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 5,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 11591,
                        "name": "猪皮",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 6,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 11594,
                        "name": "PU",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 8,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 28380,
                        "name": "棉布",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 21,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 11607,
                        "name": "牛仔布",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 22,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 11595,
                        "name": "帆布",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 23,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 14643,
                        "name": "毛线",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 26,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 11659,
                        "name": "毛绒",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 27,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 11990,
                        "name": "皮革",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 28,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 42617,
                        "name": "网布/网面",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 29,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 12022,
                        "name": "聚酯纤维",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 30,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 14634,
                        "name": "绒布",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 32,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 13808,
                        "name": "麻",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 33,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 50070,
                        "name": "飞织",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 38,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 28381,
                        "name": "EVA",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 42,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 11726,
                        "name": "塑料",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 44,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 11610,
                        "name": "其他",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 45,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 974,
                        "optionId": 33767,
                        "name": "合成革",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 632,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    }
                ],
                "values": []
            },
            {
                "attributeId": 1686,
                "attributeName": "上市时间",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 4,
                "required": false,
                "multi": false,
                "options": [
                    {
                        "attributeId": 1686,
                        "optionId": 19077,
                        "name": "2017",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 8,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 1686,
                        "optionId": 39631,
                        "name": "2018",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 46,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 1686,
                        "optionId": 39632,
                        "name": "2019",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 47,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    },
                    {
                        "attributeId": 1686,
                        "optionId": 39633,
                        "name": "2020",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 48,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": null,
                        "externaldata": ""
                    }
                ],
                "values": [
                    {
                        "optionId": 19077,
                        "name": "2017",
                        "alias": null
                    }
                ]
            },
            {
                "attributeId": 73,
                "attributeName": "适用季节",
                "attributeType": 0,
                "dataType": 2,
                "unit": "",
                "flags": 52,
                "required": true,
                "multi": true,
                "options": [
                    {
                        "attributeId": 73,
                        "optionId": 451,
                        "name": "春",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 1,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "spring"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 73,
                        "optionId": 452,
                        "name": "夏",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 2,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "summer"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 73,
                        "optionId": 453,
                        "name": "秋",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 3,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "autumn"
                        },
                        "externaldata": ""
                    },
                    {
                        "attributeId": 73,
                        "optionId": 454,
                        "name": "冬",
                        "description": null,
                        "hierarchyGroup": "",
                        "sort": 4,
                        "parentOptionId": 0,
                        "isVirtual": null,
                        "realOptions": null,
                        "foreignName": {
                            "en": "winter"
                        },
                        "externaldata": ""
                    }
                ],
                "values": []
            }
        ],
        "sizeTableInfo": {
            "sizeData": {},
            "sizeType": null,
            "templateType": 53
        }
    },
    "success": true
}''')

    print(type(response))

    targetlist = response['data']['prodPropInfo']

    item = get_target_item(targetlist, 'attributeId', '1686')
    print(item)
