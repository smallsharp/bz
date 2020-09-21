from configparser import RawConfigParser

conf = RawConfigParser()
conf.optionxform = str
conf.read('config.ini', encoding='utf-8-sig')

headers_dsg = dict(conf.items('headers_dsg'))
headers_pim = dict(conf.items('headers_pim'))

# HOST
url_pim = conf.get('Host', 'pim')
url_design = conf.get('Host', 'design')

# 渠道
channel = conf.get('Common', 'channel')
brand = conf.get('Common', 'brand')

# postion
# brand = conf.get('Postion', 'brand')

if channel == 'TM':
    fieldmap = dict(conf.items('TMFieldMapping'))
else:
    fieldmap = dict(conf.items('JDFieldMapping'))


def get_product(pcode, schemaCode, channel, brand='Reebok'):
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
                "variantCode": "sku1_{}".format(pcode),
                "properties": {
                    "customColor": {
                        "customColorID": "customColorID1",
                        "customColorName": "customColorName1"
                    },
                    "barcode": "bar1_{}".format(pcode),
                    "color": "",
                    "customSize": "size1",
                    "saleLocation": "",
                    "platformCode": "pf1_{}".format(pcode),
                    "skuTagPrice": "",
                    "skuCode": ""
                }
            },
            {
                "schemaCode": schemaCode,
                "variantCode": "sku2_{}".format(pcode),
                "properties": {
                    "customColor": {
                        "customColorID": "customColorID2",
                        "customColorName": "customColorName2"
                    },
                    "barcode": "bar2_{}".format(pcode),
                    "color": "",
                    "customSize": "size2",
                    "saleLocation": "",
                    "platformCode": "pf2_{}".format(pcode),
                    "skuTagPrice": "",
                    "skuCode": ""
                }
            }
        ],
        "web": True,
        "labels": [],
        "removeLabels": []
    }


def gen_pending_item(schema, row, vcode, target_vcode=None, target_value=None, target_schema=None):
    '''
    有缺失字段
    :param schema:
    :param row:
    :param vcode: 天猫字段
    :param target_vcode: 天猫属性值key
    :param kwargs:
    :return:
    '''
    return {
        "origin": {
            'schemaCode': schema,
            'key': row[fieldmap.get('pimkey')],
            'vcode': vcode,
            'type': row[fieldmap.get('pimkey_type')],
            'multiple': row[fieldmap.get('multiple')],
            'position': row.get(fieldmap.get('position')),  # None if not supported
        },
        'target': {
            'schemaCode': target_schema,
            'key': row[fieldmap.get('target_key')],  # 京东字段
            'type': row[fieldmap.get('target_type')],  # 京东字段类型
            'vcode': target_vcode,  # 京东属性值key
            'value': target_value  # 京东属性值value
        }
    }
