import random
import time

label = time.strftime('%m%d', time.localtime())


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


def gen_ts_body(pcode, schemaCode, skus=[], **kwargs):
    # 数据从PIM 模型中拿的
    brands = ['AD01', 'AO01', 'AS01', 'PU01', 'OT01', 'CV01', 'RB01', 'TB01', 'VN01', 'AC01']
    colors = ['白色', '肤色', '橙色', '个性花色（格子、条纹、印花、绣花等）', '黑/灰', '红色', '酒红色', '蓝色', '浅绿色', '深灰色', '透明', '紫罗兰', '丛林迷彩',
              '更多颜色', '黑/蓝', '花色', '桔色', '绿', '浅色', '深卡其布色', '香槟色', '紫色', '通用迷彩', '黑/荧光绿', '淡紫色', '海洋迷彩', '黑白灰迷彩',
              '灰/绿松石', '军绿色', '米色', '乳白色', '深色', '炫彩色', '粉', '黑', '黑色', '灰色', '咖啡/橙', '其他', '沙漠迷彩', '深紫色', '银色', '碎花',
              '卡其', '栗子色', '酒红', '栗色', '栗色/豹纹', '巧克力色', '棕色', '粉色', '粉红色', '深红色', '金色', '浅灰色', '深蓝色', '蓝', '紫', '沙色',
              '豹纹', '玫瑰粉']

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
                "brand": b if (b := kwargs.get('brand')) else random.choice(brands),
                "colorNo": random.choice(colors),
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
                "barcode": "B1_{}".format(pcode),
                "size": "XL",
                "SKU-marketValue": "98",
                "SKU-costPrice": "78",
                "customSize": "38" if '鞋' in kwargs.get('schemaPath') else 'XL',
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
                "customSize": "39" if '鞋' in kwargs.get('schemaPath') else 'XXL',
                "MDM-brand": "",
                "MDM-goods": "",
                "supplierBarcode": ""
            }
        }],
        "web": True,
        "labels": ["likai", "script", label],
        "removeLabels": []
    }


def get_item_model():
    '''
    task 标准化数据格式
    '''
    return {
        'origin': {
            'schemaCode': '',
            'schemaPath': '',
            'key': '',  # like color is attr
            'vcode': '',  # like red is value code of attr while "红色" is name
            'type': '',
            'position': '',  # None if not supported
            'brand': ''
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


class Report(object):
    '''测试报告'''

    def __init__(self, task_item=None):
        self.item = task_item
        if self.item:
            self.generate_report()

    def generate_report(self):
        if str(self.item['target']['vcode']) == str(self.item['actual']['vcode']):
            self.item['report']['vcode'] = 'success'
        if str(self.item['target']['schemaCode']) == str(self.item['actual']['schemaCode']):
            self.item['report']['schemaCode'] = 'success'

    @staticmethod
    def headers():
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
        for d in self.item.keys():
            for v in self.item[d].values():
                values.append(v)
        return values
