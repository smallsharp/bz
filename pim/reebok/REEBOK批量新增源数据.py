import time
import time
from datetime import datetime
from multiprocessing.dummy import Pool
from pymongo.errors import DuplicateKeyError
from common.tool import GeneralTool
import re


def insert(model: dict):
    print("正在操作：{}".format(model.get("externalCode")))
    try:
        mycol.insert_one(model)  # print(x.inserted_id)
    except DuplicateKeyError:
        pass
        # conditon = {"externalCode": model.get("externalCode")}
        # mycol.update_one(conditon, {'$set', model})  # 整个model更新
    except Exception as e:
        raise Exception("数据新增异常：", model.get("externalCode"), e)


def get_sourcelist():
    data_csv = GeneralTool.get_csv_data('../../files/Reebok-主档数据.csv')
    sourcelist = list()
    for data in data_csv:
        now = datetime.utcnow()
        reebok_model = {
            "externalCode": data['BARCODE'],
            "sourceType": "reebok-erp",
            "sourceData": data,
            "isStore": False,
            "operatorId": "jm006826",
            "createTime": now,
            "updateTime": now,
            "logicDelete": 0
        }
        sourcelist.append(reebok_model)
    return sourcelist


if __name__ == '__main__':
    start = time.time()

    uri = """mongodb://u_mid_platform_integration_sit:root1234@kh-public-uat-mongo-db01.cloud.bz:27017,kh-public-uat-mongo-db02.cloud.bz:27017,kh-public-uat-mongo-db03.cloud.bz:27017/db_mid_platform_integration_sit?authSource=db_mid_platform_integration_sit&replicaSet=rs-public-uat"""
    mycol = GeneralTool.get_collection(uri, 'db_mid_platform_integration_sit', 'P_SOURCE_REEBOK',
                                       authuser='u_mid_platform_integration_sit', authpwd='root1234')
    sourcelist = get_sourcelist()

    pool = Pool(4)  # 实例化线程池
    pool.map(insert, sourcelist)  # 开启线程池，get_down函数，list为可迭代对象
    pool.close()
    pool.join()
    end = time.time()
    print("共耗时：{}秒".format(round(end - start)))
