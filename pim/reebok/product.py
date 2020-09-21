import requests, time
from common.tool import GeneralTool, CommonTool
from multiprocessing.dummy import Pool
from pim.reebok.const import integration
from pim.reebok.rule import rulelist


class Prodcut():
    headers = {
        'tenantCode': 'baozun',
        'catalog': 'REEBOK',
        'token': '18u255w',
        'Cookie': 'SESSION=MjBkZTJmODUtMjVmZS00NmE0LThkNzItY2FhMjI5NWNjMzFj',
        'Content-Type': 'application/json'
    }

    @classmethod
    def find_product_info(cls, product_code):
        url = "http://pim-center-sit.cloud.bz/pim-workbench-bff/product/findProductInfo"
        payload = {
            "productReqList": [
                {
                    "code": product_code
                }
            ]
        }
        try:
            response = requests.request("POST", url, headers=cls.headers, json=payload)
            return response.json()
        except Exception as e:
            print("Request Exception:{},detail:{}".format(product_code, e))
            return None

    @classmethod
    def get_schemacode(cls, product_info):
        if not product_info:
            return None
        return product_info['data']['schemaCode']

    @classmethod
    def handle_source(self, row):

        # 1.使用源数据进行入库
        response = Prodcut.conver2common(row)
        if not response:
            print(f'请单独排查，入库失败了：{row["externalCode"]}')
            return
        source = row['sourceData']  # sourceData
        DIVISION = source.get('DIVISION')  # DIVISION
        MODEL_NAME = source['MODEL_NAME']
        MODEL_NO = source['MODEL_NO']

        # 2.查询商品详情
        productinfo = Prodcut.find_product_info(MODEL_NO)
        if not productinfo:
            print(f'请单独排查，查询商品失败了：{MODEL_NO}')
            return
        act_schemacode = Prodcut.get_schemacode(productinfo)

        # 3. 对比类目-鞋类
        if DIVISION == 'FTW':
            exp_schemacode = CommonTool.get_matchvalue_from_dict('schema_ftw', MODEL_NAME, rulelist)
            if not exp_schemacode:
                exp_schemacode = 's1011705'  # 如果关键字没有匹配到，则使用这个
        else:
            key = f"{source['CATEGORY']}_{source['LOCAL_PRODUCT_TYPE']}"
            exp_schemacode = CommonTool.get_value_from_dict('schema_other', key, rulelist)

        # 生成报告
        return Prodcut.generate_error_report(exp_schemacode, act_schemacode, source=source)

    @staticmethod
    def conver2common(row):
        url = "http://pim-center-sit.cloud.bz/pim-workbench-bff/integration-platform/product/source/convertToCommon"
        body = {
            "operatorId": "jm006826",
            "externalCodes":
                [{"sourceType": row['sourceType'], "externalCode": row['externalCode']}]
        }
        # if not row['sourceData']['MODEL_NO']:
        #     print(f'model_no is null:{row["externalCode"]}')
        #     return row['externalCode']
        try:
            res = requests.request("POST", url, headers=Prodcut.headers, json=body)
            # print(f'正在转换：{row["externalCode"]},结果：{res.status_code}')
            if len(res.json()['data']['success']) > 0:
                return True
            # print(f'入库失败了：{row["externalCode"]}')
        except Exception as e:
            print(f'入库请求失败了：{row["externalCode"]},===>>>:{e}')

    @classmethod
    def get_value_from_master(cls, property_code, product_info, is_custom_propery=False):
        if not is_custom_propery:
            schemaProperties = product_info['data']['schemaProperties']
            # propertyCode = 'title'
            for property in schemaProperties:
                if property['propertyCode'] == property_code:
                    value = property.get('value') if isinstance(property.get('value'), str) else property.get(
                        'value').get('default')
                    return value
            return None
        else:
            customProperties = product_info['data']['customProperties']
            for property in customProperties:
                if property['propertyCode'] == property_code:
                    return property.get('value')
            return None

    @classmethod
    def get_value_from_variant(cls, variantCode, propertyCode, product_info):
        # value = None
        skuList = product_info['data']['skuList']
        for sku in skuList:
            if sku['variantCode'] != variantCode:
                continue
            else:
                for property in sku['schemaProperties']:
                    if property['propertyCode'] == propertyCode:
                        value = property.get('value') if isinstance(property.get('value'), str) else property.get(
                            'value').get('default')
                        return value

    @classmethod
    def generate_error_report(cls, expectvalue, acutalvalue, **kwargs):
        success = expectvalue == acutalvalue

        MODEL_NO = kwargs['source']['MODEL_NO']
        BARCODE = kwargs['source']['BARCODE']
        DIVISION = kwargs['source']['DIVISION']

        if kwargs['source']['DIVISION'] == 'FTW':
            keyword = kwargs['source']['MODEL_NAME']
        else:
            keyword = f"{kwargs['source']['CATEGORY']} {kwargs['source']['LOCAL_PRODUCT_TYPE']}"

        if not success:
            return MODEL_NO, BARCODE, DIVISION, keyword, expectvalue, acutalvalue

    @classmethod
    def get_expect_schemacode(cls, DIVISION, shoelist=None, otherlist=None, **kwargs):
        if DIVISION == 'FTW':
            # 通过源数据的 MODEL_NAME+DESC_IN_CHINESE 拼接，然后从Excel中读取到的schemacode
            keyword = kwargs['source']['MODEL_NAME']
            # expect_schemacode = cls.get_schemacode_by_keyword(keyword, shoelist, DIVISION=DIVISION)
            for item in shoelist:
                if keyword == item['keyword']:
                    return item['schemacode']
        else:
            # 通过源数据的 CATEGORY+LOCAL_PRODUCT_TYPE 拼接，然后从Excel中读取到的schemacode
            keyword = f"{kwargs['source']['CATEGORY']} {kwargs['source']['LOCAL_PRODUCT_TYPE']}"
            # [{'keyword': 'CLASSIC BAG', 'schema_code': 's1011107'}]
            # expect_schemacode = cls.get_schemacode_by_keyword(keyword, otherlist, DIVISION=DIVISION)
            for item in otherlist:
                if keyword.find(item['keyword']) != -1:
                    return item['schemacode']

    @classmethod
    def get_expect_title(cls, DIVISION, **kwargs):
        if DIVISION == 'FTW':
            # 通过源数据的 MODEL_NAME+DESC_IN_CHINESE 拼接，然后从Excel中读取到的schemacode
            keyword = f"{kwargs['MODEL_NAME']} {kwargs['DESC_IN_CHINESE']}"
            title = cls.get_schemacode_by_keyword(keyword)
        else:
            # 通过源数据的 CATEGORY+LOCAL_PRODUCT_TYPE 拼接，然后从Excel中读取到的schemacode
            keyword = f"{kwargs['CATEGORY']} {kwargs['LOCAL_PRODUCT_TYPE']}"
            # [{'keyword': 'CLASSIC BAG', 'schema_code': 's1011107'}]
            title = cls.get_schemacode_by_keyword(keyword)
        return title


if __name__ == '__main__':
    print('start')
    collection = GeneralTool.get_collection(integration['sit']['uri'], integration['sit']['db'],
                                            'P_SOURCE_REEBOK')
    condition = {"sourceType": "reebok-erp", "sourceData.MODEL_NO": {"$ne": ""}}
    allrows = collection.find(condition)
    allrows = list(allrows)
    print(len(allrows))
    start = time.time()
    pool = Pool(4)  # 实例化线程池
    pool.map(Prodcut.conver2common, allrows)  # 开启线程池，get_down函数，list为可迭代对象
    pool.close()
    pool.join()
    end = time.time()
    print('end')
    print("共耗时：", end - start)
