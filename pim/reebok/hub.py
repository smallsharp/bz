import requests
from common.tool import CommonTool
from pim.reebok.rule import rulelist


class Convert():
    source_demo = {
        "BARCODE": 'BARCODE',
        "MODEL_NO": "MODEL_NO",
        "ARTICLE_NO": "ARTICLE_NO",
        "MARKETING_DIVISION": "CLASSIC",
        "DESC_IN_CHINESE": "经典鞋",
        "MODEL_NAME": 'MODEL_NAME',
        "LOCAL_RP": "569",
        "COLOR": "CHALK/COLL NAVY/RED/WHT",
        "SIZE": "4",
        "YEAR": "2019",
        "SEASON_OF_TM": "19Q3",
        "CATEGORY": 'CATEGORY',
        "COMPOSITION_IN_CHINESE": "COMPOSITION_IN_CHINESE",
        "EAST_LAUNCH": "2019-6-1 0:00",
        "GENDER": 'GENDER',
        "HARD_LAUNCH": "HARD_LAUNCH",
        "DIVISION": "DIVISION",
        "KEY_CONCEPT": "SLICE",
        "SPORTS_CATEGORY": "TENNIS",
        "LOCAL_PRODUCT_TYPE": 'LOCAL_PRODUCT_TYPE',
        "PRODUCT_GROUP": "SHOES",
        "AGE_GROUP": "ADULTS",
        "PRODUCT_TYPE": "SHOES - MID (NON-FOOTBALL)	",
        "LAUNCH_MONTH": "Jun",
        "ECOM_PP": "ECOM_PP",
        "POP": "POP",
        "SEASON": "FW",
        "COMPOSITION": "COMPOSITION",
        "CAMPAIGN_NAME": "CAMPAIGN_NAME",
        "PRICE_POINT": "500-600",
        "COLOR_IN_CHINESE": "粉白/学院藏青蓝/亮粉红荧光/白色",
        "SUB_CATEGORY_I": "CLASSIC"
    }

    @classmethod
    def hub_convert(cls, source):
        headers = {
            'tenantCode': 'baozun',
            'catalog': 'REEBOK',
            'ruleCode': '44681425-1b0d-4b25-bba5-e53b8d9b23b1',
            'token': '43y256b',
            'Cookie': 'SESSION=NWYwYjEyOGQtNzhkMS00YWE1LWJhYjAtN2VlOWE1MDg4NDY1',
            'Content-Type': 'application/json'
        }

        body = {
            "BARCODE": source["BARCODE"],
            "MODEL_NO": source["MODEL_NO"],
            "ARTICLE_NO": source["ARTICLE_NO"],
            "MARKETING_DIVISION": "CLASSIC",
            "DESC_IN_CHINESE": "这里是个描述",
            "MODEL_NAME": source['MODEL_NAME'],
            "LOCAL_RP": "569",
            "COLOR": "CHALK/COLL NAVY/RED/WHT",
            "SIZE": "4",
            "YEAR": "2019",
            "SEASON_OF_TM": "19Q3",
            "CATEGORY": source['CATEGORY'],
            "COMPOSITION_IN_CHINESE": "",
            "EAST_LAUNCH": "2019-6-1 0:00",
            "GENDER": source['GENDER'],
            "HARD_LAUNCH": "",
            "DIVISION": source.get("DIVISION"),
            "KEY_CONCEPT": "SLICE",
            "SPORTS_CATEGORY": "TENNIS",
            "LOCAL_PRODUCT_TYPE": source.get('LOCAL_PRODUCT_TYPE'),
            "PRODUCT_GROUP": "SHOES",
            "AGE_GROUP": "ADULTS",
            "PRODUCT_TYPE": "SHOES - LOW (NON FOOTBALL)",
            "LAUNCH_MONTH": "Jun",
            "ECOM_PP": "",
            "POP": "",
            "SEASON": "FW",
            "COMPOSITION": "",
            "CAMPAIGN_NAME": "",
            "PRICE_POINT": "500-600",
            "COLOR_IN_CHINESE": "粉白/学院藏青蓝/亮粉红荧光/白色",
            "SUB_CATEGORY_I": "CLASSIC"
        }
        url = "http://mid-platform-publish-platform-service-sit.cloud.bz/publish-platform/convertJs/hub-convert"
        # print(f'正在处理：{source["BARCODE"]}')
        try:
            res = requests.request("POST", url, json=source, headers=headers)
            return res.json()
        except Exception as e:
            print(f'请求失败：{source["externalCode"]}')

    @classmethod
    def get_actual_schemacode(cls, response):
        master = response['data']['master']
        return master.get('schemaCode')

    @classmethod
    def get_value_from_response(cls, response, key, positon='master'):
        maps = response['data'][positon]['properties']
        return maps.get(key)

    @classmethod
    def get_expect_title(cls, source: dict):
        # 固定规则：Reebok锐步官方 + GENDER
        prefix = 'Reebok锐步官方'
        article_no = source.get('ARTICLE_NO')
        model_name = source.get('MODEL_NAME')
        category = source.get('CATEGORY')
        local_product_type = source.get('LOCAL_PRODUCT_TYPE')

        # 公共的部分 prefix + gender
        title_gender = CommonTool.get_value_from_dict('title_gender', source.get('GENDER'), rulelist)
        title = f'{prefix} {title_gender}' if title_gender else prefix

        # FTW Reebok锐步官方 + GENDER + title_modelname1 + title_product_type + title_modelname4 + ARTICLE_NO
        if source.get('DIVISION') == 'FTW':
            # 【规则2】FTW类 modelName的转换逻辑，如MODEL_NAME的值不在下表中，则无需转换
            modelname1 = CommonTool.get_value_from_dict('title_modelname1', model_name, rulelist)
            title = f'{title} {modelname1}' if modelname1 else f'{title} {model_name}'  # RUNNER 4.0

            # 【规则3】PRODUCT_TYPE的转换逻辑，PRODUCT_TYPE不在下表中就中文名称就转换为空
            title_product_type = CommonTool.get_value_from_dict('title_product_type', source['PRODUCT_TYPE'], rulelist)
            title = f'{title} {title_product_type}' if title_product_type else f'{title} '  # 中帮

            # 【规则4】鞋类商品名称的转换逻辑( 包含关键词)，不在下表的转换中的，统一转化为【休闲鞋】
            modelname4 = CommonTool.get_matchvalue_from_dict('title_modelname4', model_name, rulelist)  # 休闲鞋
            title = f'{title}{modelname4}' if modelname4 else f'{title}休闲鞋'  # 健步鞋
            title = f'{title} {article_no}' if {article_no} else title  # FS1626

        elif source.get('DIVISION') == 'APP':
            # 【规则5】APP类 modelName的转换逻辑，如MODEL_NAME的值不在下表中，则无需转换
            modelname5 = CommonTool.get_value_from_dict('title_modelname5', model_name, rulelist)
            title = f'{title} {modelname5}' if modelname5 else f"{title} {model_name}"
            # 【规则6】服装配饰对应名称转换规则
            title_app = CommonTool.get_value_from_dict('title_app', f"{category}_{local_product_type}", rulelist)
            title = f'{title} {title_app}' if title_app else title
            title = f'{title} {article_no}' if article_no else title
        else:
            # Prefix + Gender + MODEL_NAME(直接取值) + 规则6（CATEGORY+LOCAL_PRODUCT_TYPE)	+ ARTICLE_NO（直接取值）
            title = f'{title} {model_name}' if model_name else title
            title_app = CommonTool.get_value_from_dict('title_app', f"{category}_{local_product_type}", rulelist)
            # 【规则6】服装配饰对应名称转换规则
            title = f'{title} {title_app}' if title_app else title
            if not title_app:
                print(f"{source['BARCODE']},CATEGORY&LOCAL_PRODUCT_TYPE:{category} {local_product_type}")

            title = f'{title} {article_no}' if article_no else title

        return title


if __name__ == '__main__':
    source = {
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

    # v1 = Convert.get_expect_title(source)
    # print(v1)

    v2 = CommonTool.get_matchvalue_from_dict('title_modelname4', 'Back to Trail', rulelist)

    print(v2)
