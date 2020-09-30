from configparser import RawConfigParser

conf = RawConfigParser()
conf.optionxform = str
conf.read('config_g2000.ini', encoding='utf-8-sig')

HEADERS_DSG = dict(conf.items('headers_dsg'))
HEADERS_PIM = dict(conf.items('headers_pim'))

# attr position
SUB_POSITION = dict(conf.items('position'))

# HOST
URL_PIM = conf.get('Host', 'pim')
URL_DESIGN = conf.get('Host', 'design')

# 渠道
CHANNEL = conf.get('Common', 'channel')
BRAND = conf.get('Common', 'brand')

# postion
# brand = conf.get('Postion', 'brand')

if CHANNEL == 'TM':
    fieldmap = dict(conf.items('TMFieldMapping'))
else:
    fieldmap = dict(conf.items('JDFieldMapping'))

TITLE_PIM_KEY = fieldmap['pimkey']
TITLE_PIM_KEY_TYPE = fieldmap['pimkey_type']
TITLE_PIM_VCODE = fieldmap['pim_vcode']
TITLE_SCHEMA_CODE = fieldmap['schemaCode']
PIM_MULTIPLE = fieldmap['multiple']
PIM_POSITION = fieldmap['position']
PIM_INPUT = fieldmap['pimkey_input']
PIM_SINGLE_CHECK = fieldmap['pimkey_single_check']
PIM_MULTI_CHECK = fieldmap['pimkey_multi_check']

# target title
TITLE_TARGET_KEY = fieldmap['target_key']
TITLE_TARGET_TYPE = fieldmap['target_type']
TITLE_TARGET_VCODE = fieldmap['target_vcode']
TITLE_TARGET_VALUE = fieldmap['target_value']
TITLE_TARGET_SCHEMA_CODE = fieldmap['target_schemaCode']
TARGET_SINGLE_CHECK = fieldmap['targetkey_single_check']
TARGET_MULTI_CHECK = fieldmap['targetkey_multi_check']
TARGET_INPUT = fieldmap['targetkey_input']


def gen_product_body(pcode, schemaCode, channel, skus=[], brand='Reebok'):
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


class Task():

    def __init__(self, schema, row: dict, vcode, target_vcode=None, target_value=None, target_schema=None):
        self.item = {
            "origin": {
                'schemaCode': schema,
                'key': row[TITLE_PIM_KEY],
                'vcode': vcode,
                'type': row[TITLE_PIM_KEY_TYPE],
                'multiple': row[PIM_MULTIPLE],
                'position': row.get(PIM_POSITION),  # None if not supported
            },
            'target': {
                'schemaCode': target_schema,
                'key': row[TITLE_TARGET_KEY],  # 京东字段
                'type': row[TITLE_TARGET_TYPE],  # 京东字段类型
                'vcode': target_vcode,  # 京东属性值key
                'value': target_value  # 京东属性值value
            }
        }

    def run(self):
        pass
