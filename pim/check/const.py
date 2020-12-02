from configparser import RawConfigParser

conf = RawConfigParser()
conf.optionxform = str
conf.read('topsports.ini', encoding='utf-8-sig')

HEADERS_ROSS = dict(conf.items('headers_ross'))
HEADERS_PIM = dict(conf.items('headers_pim'))

# attr position
SUB_POSITION = dict(conf.items('Position'))

# HOST
URL_PIM = conf.get('Host', 'pim')
URL_ROSS = conf.get('Host', 'ross')

# 渠道
CHANNEL = conf.get('Common', 'channel')
# BRAND = conf.get('Common', 'brand')

# 判断用哪个渠道配置文件 映射字段
if CHANNEL == 'TM':
    fieldmap = dict(conf.items('TMFieldMapping'))
elif CHANNEL == 'JD':
    fieldmap = dict(conf.items('JDFieldMapping'))
else:
    fieldmap = dict(conf.items('VIPFieldMapping'))

# pim title
TITLE_PIM_KEY = fieldmap['attr']
TITLE_PIM_KEY_TYPE = fieldmap['attrType']
TITLE_PIM_VCODE = fieldmap['valueId']
TITLE_SCHEMACODE = fieldmap['schemaCode']
TITLE_SCHEMA_PATH = fieldmap['schemaPath']

PIM_MULTIPLE = fieldmap.get('multiple')
PIM_POSITION = fieldmap.get('position')

# target title
TITLE_TARGET_KEY = fieldmap['targetAttr']
TITLE_TARGET_TYPE = fieldmap['targetAttrType']
TITLE_TARGET_VCODE = fieldmap['targetValueId']
TITLE_TARGET_VALUE = fieldmap['targetValue']
TITLE_TARGET_SCHEMACODE = fieldmap.get('targetSchemaCode')


def gen_bz_body(pcode, schemaCode, channel, skus=[], brand='Reebok'):
    return {
        "operatorId": "jm006826",
        "master": {
            "productCode": pcode,
            "fragments": [],
            "schemaCode": schemaCode,
            "properties": {
                "productNo": pcode,
                "title": "(auto标题):{}".format(pcode),
                "productName": "(auto名称):{}".format(pcode),
                "productDescription": "(auto商品描述):{}".format(pcode),
                "sellingPoints": "(auto商品卖点):{}".format(pcode),
                "isExpirationProduct": "true",
                "isERPCreate": "false",
                "isSnProduct": "true",
                "brand": brand,
                "channelCode": channel,
                "gender": "",
                "upperHeight": "",
                "outsoleMaterial": "",
                "function": "",
                "upperMaterial": "",
                "applicableSite": "",
                "isFlaw": "",
                "sneakerTechnology": "",
                "std_size_group": "",
                "sportSeries": "",
                "isSameShoppingMall": "",
                "price": "5207",
                "careNotice": {
                    "careWash": "(水洗需知):{}".format(pcode),
                    "careBleach": "(漂洗须知):{}".format(pcode),
                    "careIron": "(熨烫须知):{}".format(pcode),
                    "careDry": "(晾干须知):{}".format(pcode),
                    "careOther": "(备注):{}".format(pcode)
                },
                "productImage": [
                    {
                        "image": "",
                        "imageType": "",
                        "imageTypeExtend": "",
                        "productColor": ""
                    }
                ],
                "originalLocation": {
                    "country": "1",
                    "province": "110000000000",
                    "city": "110100000000",
                    "area": "110101000000",
                    "areaExtend": "区域拓展:{}".format(pcode)
                },
                "launchInfo": {
                    "launchTime": "2020-08-31",
                    "year": 2020,
                    "month": 8,
                    "season": "autumn"
                }
            }
        },
        "variants": [
            {
                "schemaCode": schemaCode,
                "variantCode": skus[0],
                "properties": {
                    "customColor": {
                        "customColorID": "customColorID1",
                        "customColorName": "customColorName1"
                    },
                    "barcode": "bar1_{}".format(pcode),
                    "color": "",
                    "customSize": "size1",
                    "saleLocation": "",
                    "platformCode": "p1_{}".format(pcode),
                    "skuTagPrice": "",
                    "skuCode": ""
                }
            },
            {
                "schemaCode": schemaCode,
                "variantCode": skus[1],
                "properties": {
                    "customColor": {
                        "customColorID": "customColorID2",
                        "customColorName": "customColorName2"
                    },
                    "barcode": "bar2_{}".format(pcode),
                    "color": "",
                    "customSize": "size2",
                    "saleLocation": "",
                    "platformCode": "p2_{}".format(pcode),
                    "skuTagPrice": "",
                    "skuCode": ""
                }
            }
        ],
        "web": True,
        "labels": [],
        "removeLabels": []
    }


def gen_ts_body(pcode, schemaCode, schemaPath, skus=[]):
    return {
        "operatorId": "topsports_uat",
        "master": {
            "productCode": pcode,
            "fragments": [],
            "schemaCode": schemaCode,
            "properties": {
                "productStyle": "",
                "launchTime": "2020nianxiaji",
                "itemName": "商品名称_{}".format(pcode),
                "suitableSeason": "20Q1",
                "costPrice": 111,
                "gender": "zhongxing",
                "year": "2020nian",
                "brand": "AO01",
                "colorNo": "酒红色",
                "colorSYS": "红色",
                "style": "baida",
                "seriesTypeName": "",
                "supportType": "",
                "salesPrice": 222,
                "productNo": pcode,
                "seasonName": "",
                "categoryName": "",
                "re-Launch": "True",
                "marketValue": 333,
                "launchMonth": "2020nian9yue",
                "shoppingHot": "lianmingkuan",
                "effectiveSize": "",
                "detailStyle": "",
                "liningMaterial": "rongbu",
                "plateType": "",
                "sportEvent": "banxie/xiuxian",
                "placketType": "",
                "model": "",
                "mainFunction": "透气",
                "collarType": "ketuoxiemao",
                "fabricMaterial": "",
                "fashionElement": "LOGObu",
                "clothStyle": "",
                "casualClothesCategory": "",
                "sleeveType": "",
                "sportStyle": "",
                "sleeveLength": ""
            }
        },
        "variants": [{
            "schemaCode": schemaCode,
            "variantCode": skus[0],
            "properties": {
                "SKU-salesPrice": "88",
                "barcode": "B2_{}".format(pcode),
                "size": "XL",
                "SKU-marketValue": "98",
                "SKU-costPrice": "78",
                "customSize": "38" if '鞋' in schemaPath else 'XL',
                "MDM-brand": "",
                "MDM-goods": "",
                "supplierBarcode": ""
            }
        }, {
            "schemaCode": schemaCode,
            "variantCode": skus[1],
            "properties": {
                "SKU-salesPrice": "89",
                "barcode": "B2_{}".format(pcode),
                "size": "XXL",
                "SKU-marketValue": "99",
                "SKU-costPrice": "79",
                "customSize": "39" if '鞋' in schemaPath else 'XXL',
                "MDM-brand": "",
                "MDM-goods": "",
                "supplierBarcode": ""
            }
        }],
        "web": True,
        "labels": ["likai", "script"],
        "removeLabels": []
    }


def get_item_model():
    '''
    task 标准化数据格式
    '''

    return {
        "origin": {
            'schemaCode': "",
            'schemaPath': "",
            'key': "",  # like color is attr
            'vcode': "",  # like red is value code of attr while "红色" is name
            'type': "",
            'multiple': "",
            'position': "",  # None if not supported
        },
        'target': {
            'schemaCode': "",
            'key': "",
            'type': '',
            'vcode': '',
            'value': ''
        },
        'actual': {
            'schemaCode': None,
            'type': None,  # 京东字段类型
            'vcode': None,  # value code of attr
            'value': None,  # value name of attr
            'remark': None,
            'productCode': None
        },
        'report': {
            'schemaCode': 'failed',
            'vcode': 'failed'
        }
    }


class Task():

    def __init__(self, row: dict):
        self.row = row
        self.item = get_item_model()
        self.__get_task_item()

    def __get_task_item(self):
        # origin 赋值
        self.item['origin']['schemaCode'] = self.row.get(TITLE_SCHEMACODE)
        self.item['origin']['schemaPath'] = self.row.get(TITLE_SCHEMA_PATH)
        self.item['origin']['key'] = self.row.get(TITLE_PIM_KEY)
        self.item['origin']['vcode'] = self.row.get(TITLE_PIM_VCODE)
        # self.item['origin']['type'] = self.row.get(TITLE_PIM_KEY_TYPE)
        # self.item['origin']['multiple'] = self.row.get(PIM_MULTIPLE)
        # self.item['origin']['position'] = self.row.get(PIM_POSITION)

        # target 赋值
        self.item['target']['schemaCode'] = self.row.get(TITLE_TARGET_SCHEMACODE)
        self.item['target']['key'] = self.row.get(TITLE_TARGET_KEY)
        self.item['target']['type'] = self.row.get(TITLE_TARGET_TYPE)
        self.item['target']['vcode'] = self.row.get(TITLE_TARGET_VCODE)
        self.item['target']['value'] = self.row.get(TITLE_TARGET_VALUE)

        # return self.item


class Report(object):
    '''测试报告'''

    def __init__(self, task_item=None):
        self.task_item = task_item
        if self.task_item:
            self.generate_report()

    def generate_report(self):
        if str(self.task_item['target']['vcode']) == str(self.task_item['actual']['vcode']):
            self.task_item['report']['vcode'] = 'success'
        if str(self.task_item['target']['schemaCode']) == str(self.task_item['actual']['schemaCode']):
            self.task_item['report']['schemaCode'] = 'success'

    @classmethod
    def headers(cls):
        '''
        报告的头
        '''
        title = []
        for d in get_item_model().keys():
            for k in get_item_model()[d].keys():
                title.append(f'{d}_{k}')
        return title

    def values(self):
        '''
        报告的内容
        '''
        values = []
        for d in self.task_item.keys():
            for v in self.task_item[d].values():
                values.append(v)
        return values
