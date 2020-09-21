# coding=utf-8
import time
from datetime import datetime
from multiprocessing.dummy import Pool
from common.tool import GeneralTool

# from multiprocessing import Pool

mycol = None


def main():
    # 1
    # uri = "mongodb://u_mid_platform_publish_sit:root1234@kh-public-uat-mongo-db01.cloud.bz:27017,kh-public-uat-mongo-db02.cloud.bz:27017,kh-public-uat-mongo-db03.cloud.bz:27017/db_mid_platform_publish_sit?authSource=db_mid_platform_publish_sit&replicaSet=rs-public-uat"
    uri = "mongodb://u_mid_platform_publish_uat:db_mid_platform_publish_uat1234@kh-public-uat-mongo-db01.cloud.bz:27017,kh-public-uat-mongo-db02.cloud.bz:27017,kh-public-uat-mongo-db03.cloud.bz:27017/db_mid_platform_publish_uat?replicaSet=rs-public-uat&authSource=db_mid_platform_publish_uat"
    dbname = "db_mid_platform_publish_uat"
    colname = "RESOURCE_NIKEPIM"
    global mycol
    mycol = GeneralTool.get_collection(uri, dbname, colname, authuser="u_mid_platform_publish_uat",
                                       authpwd="db_mid_platform_publish_uat1234")
    sourcelist = list()
    for i in range(20000):
        fileCode = f'{863000000 + i}'
        now = datetime.utcnow()
        mydict = {
            "fileCode": fileCode,
            "url": "http://pic40.nipic.com/20140403/8614226_162017444195_2.jpg",
            "name": "{}.png".format(fileCode),
            "path": "/dam/pic/",
            "type": 1,
            "meta": {
                "size": "830",
                "name": "{}.png".format(fileCode),
                "fullName": "{}.png".format(fileCode),
                "extName": ".png",
                "fileType": "png",
                "htmlMediaType": "image"
            },
            "properties": [
                {
                    "key": "year",
                    "value": "2020年"
                },
                {
                    "key": "artNo",
                    "value": fileCode
                },
                {
                    "key": "sku",
                    "value": fileCode
                }
            ],
            "opDomain": "NIKEPIM",
            "operatorName": "likai",
            "orderField": 1,
            "operatorId": "9527",
            "propertyTemplateId": "5e96ae2a7336496ecc31abbf",
            "logicDelete": 0,
            "tenantCode": "NIKE",
            "createTime": now,
            "updateTime": now,
            "labels": [
                "630", "1111"
            ]
        }
        sourcelist.append(mydict)

    start = time.time()
    pool = Pool(4)  # 实例化线程池
    pool.map(insert, sourcelist)  # 开启线程池，get_down函数，list为可迭代对象
    pool.close()
    pool.join()
    end = time.time()
    print("共耗时：", end - start)


def insert(picdict: dict):
    print("正在操作：{}".format(picdict.get("fileCode")))
    try:
        mycol.insert_one(picdict)  # print(x.inserted_id)
    except Exception as e:
        raise Exception("数据新增异常：", picdict.get("fileCode"), e)


if __name__ == '__main__':
    main()
