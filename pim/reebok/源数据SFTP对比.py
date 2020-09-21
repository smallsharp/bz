from common.tool import GeneralTool
from pim.reebok.const import integration
import json


def compare_dict(dict1, dict2):
    # diff keys
    if dict1.keys() ^ dict2.keys():
        print('不同的key：', dict1.keys() ^ dict2.keys())
        print('前有后无的key：', dict1.keys() - dict2.keys())
        print('前有后无的key：', dict2.keys() - dict1.keys())

    # same key  diff value
    samekey = dict1.keys() & dict2.keys()
    diff_vals = [{k: (dict1[k], dict2[k])} for k in samekey if str(dict1[k]).strip() != str(dict2[k]).strip()]
    if diff_vals:
        print(f'异常的数据：{barcode},{json.dumps(diff_vals, ensure_ascii=False)}')


if __name__ == '__main__':
    # sit mongo db
    # uri = """mongodb://u_mid_platform_integration_sit:root1234@kh-public-uat-mongo-db01.cloud.bz:27017,kh-public-uat-mongo-db02.cloud.bz:27017,kh-public-uat-mongo-db03.cloud.bz:27017/db_mid_platform_integration_sit?authSource=db_mid_platform_integration_sit&replicaSet=rs-public-uat"""
    query = {"catalog": "REEBOK", "sourceType": "reebok-erp"}
    collection = GeneralTool.get_collection(integration['sit']['uri'], integration['sit']['db'], 'p_source')

    datas_mongo = collection.find(query).sort('_id', -1)
    datas_csv = GeneralTool.get_csv_data('BARCODE_ARTICLE_20200805020001.csv', delimiter=',', encoding='gbk')

    print("mongo数据条数：{},csv数据条数：{}".format(len(datas_mongo := list(datas_mongo)), len(datas_csv := list(datas_csv))))

    for c in datas_csv:
        barcode = c['BARCODE']
        condition = {"catalog": "REEBOK", "externalCode": barcode}
        m = collection.find_one(condition)
        s = m['sourceData']

        # diff keys
        if s.keys() ^ c.keys():
            print('不同的key：', s.keys() ^ c.keys())
            print('前有后无的key：', s.keys() - c.keys())
            print('前有后无的key：', c.keys() - s.keys())

        # same key  diff value
        samekey = s.keys() & c.keys()
        diff_vals = [{k: (s[k], c[k])} for k in samekey if str(s[k]).strip() != str(c[k]).strip()]
        if diff_vals:
            print(f'异常的数据：{barcode},{json.dumps(diff_vals, ensure_ascii=False)}')
