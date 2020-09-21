# mongo 配置
integration = {
    'sit': {
        "uri": "mongodb://u_mid_platform_integration_sit:root1234@kh-public-uat-mongo-db01.cloud.bz:27017,kh-public-uat-mongo-db02.cloud.bz:27017,kh-public-uat-mongo-db03.cloud.bz:27017/db_mid_platform_integration_sit?authSource=db_mid_platform_integration_sit&replicaSet=rs-public-uat",
        "db": "db_mid_platform_integration_sit",
        "authuser": "u_mid_platform_integration_sit",
        "authpwd": "root1234"
    }

}

from configparser import RawConfigParser

conf = RawConfigParser()
conf.read('config.ini', encoding='utf-8-sig')

headers_dsg = dict(conf.items('headers_dsg'))
headers_pim = dict(conf.items('headers_pim'))

# HOST
url_pim = conf.get('Host', 'pim')
url_design = conf.get('Host', 'design')

channel = conf.get('Common', 'channel')

if channel == 'TM':
    fieldmap = dict(conf.items('TMFieldMapping'))
else:
    fieldmap = dict(conf.items('JDFieldMapping'))


def get_model_source():
    '''
    源数据模板
    '''
    return {
        "LOCAL_RP": "1199",
        "HARD_LAUNCH": "Y",
        "BARCODE": "4062052169568",
        "SEASON_OF_TM": "19Q4",
        "EAST_LAUNCH": "2019-11-01 00:00:00",
        "DIVISION": "FTW",
        "SPORTS_CATEGORY": "RUNNING",
        "YEAR": "2019",
        "COLOR": "white/light pink/black",
        "CATEGORY": "CLASSIC",
        "GENDER": "UNISEx",
        "MODEL_NAME": "REEBOK ROYAL ULTRA",
        "PRODUCT_GROUP": "SHOES",
        "SIZE": "7.5",
        "DESC_IN_CHINESE": "INSTAPUMP FURY",
        "KEY_CONCEPT": "ITS A MENS WORLD",
        "LAUNCH_MONTH": "Nov",
        "LOCAL_PRODUCT_TYPE": "SHOES",
        "SEASON": "FW",
        "PRODUCT_TYPE": "",
        "AGE_GROUP": "ADULTS",
        "ARTICLE_NO": "FU7743",
        "MODEL_NO": "JQ050",
        "PRICE_POINT": ">1000",
        "COLOR_IN_CHINESE": "白/浅粉/黑色"
    }


def get_product(productCode: str, schemaCode):
    return {
        "operatorId": "jm006826",
        "master": {
            "productCode": productCode,
            "fragments": [],
            "schemaCode": schemaCode,
            "properties": {
                "productNo": productCode,
                "title": "标题:{}".format(productCode),
                "productName": "名称:".format(productCode),
                "productDescription": "商品描述:{}".format(productCode),
                "sellingPoints": "商品卖点:{}".format(productCode),
                "isGift": "false",
                "isExpirationProduct": "true",
                "isERPCreate": "false",
                "isSnProduct": "true",
                "brand": "Reebok",
                "channelCode": "TM",
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
                "price": "",
                "careNotice": {
                    "careWash": "水洗需知:{}".format(productCode),
                    "careBleach": "漂洗须知:{}".format(productCode),
                    "careIron": "熨烫须知:{}".format(productCode),
                    "careDry": "晾干须知:{}".format(productCode),
                    "careOther": "备注:{}".format(productCode)
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
                    "areaExtend": "区域拓展:{}".format(productCode)
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
                "variantCode": "sku_{}".format(productCode),
                "properties": {
                    "customColor": {
                        "customColorID": "色号{}".format(productCode),
                        "customColorName": "色名{}".format(productCode)
                    },
                    "barcode": "bar_{}".format(productCode),
                    "color": "",
                    "saleLocation": "",
                    "platformCode": "pf_{}".format(productCode),
                    "skuTagPrice": "",
                    "skuCode": ""
                }
            }
        ],
        "web": True,
        "labels": [],
        "removeLabels": []
    }


def get_source_row(schemaCode, row, vcode, target_vcode=None):
    '''
    有缺失字段
    :param schemaCode:
    :param row:
    :param vcode: 天猫字段
    :param target_vcode: 天猫属性值key
    :param kwargs:
    :return:
    '''

    # return {
    #     'schemaCode': schemaCode,
    #     'key': row['属性键值'],
    #     'type': row['属性类型'],
    #     'multiple': row['是否支持多选'],
    #     'positon': row['属性位置'],
    #     'key_tm': row['天猫字段'],
    #     'type_tm': row['天猫字段类型'],  # 需要对比的
    #     'vcode': vcode,  # 属性值键值  pim 的属性值code
    #     'vcode_tm': target_vcode
    # }
    return {
        'schemaCode': schemaCode,
        'key': row[fieldmap.get('pimkey')],
        'type': row[fieldmap.get('pimkey_type')],
        'multiple': row[fieldmap.get('multiple')],
        'positon': row[fieldmap.get('position')],
        'key_tm': row[fieldmap.get('target_key')],
        'type_tm': row[fieldmap.get('target_type')],  # 需要对比的
        'vcode': vcode,  # 属性值键值  pim 的属性值code
        'vcode_tm': target_vcode
    }
