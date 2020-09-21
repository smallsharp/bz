# coding=utf-8
from common.tool import GeneralTool
from datetime import datetime


def main():
    # 1
    uri = "mongodb://u_mid_platform_publish_sit:root1234@kh-public-uat-mongo-db01.cloud.bz:27017,kh-public-uat-mongo-db02.cloud.bz:27017,kh-public-uat-mongo-db03.cloud.bz:27017/db_mid_platform_publish_sit?authSource=db_mid_platform_publish_sit&replicaSet=rs-public-uat"
    dbname = "db_mid_platform_publish_sit"
    colname = "RESOURCE_anf"
    mycol = GeneralTool.get_collection(uri, dbname, colname, authuser="u_mid_platform_publish_sit", authpwd="root1234")

    # 4. insert data
    for i in range(80000):
        fileCode = f'{862400000 + i}'
        mydict = {
            "fileCode": fileCode,
            "url": "http://pic40.nipic.com/20140403/8614226_162017444195_2.jpg",
            "name": "{}.png".format(fileCode),
            "path": "/dam/pic/",
            "type": 1,
            "meta": {
                "size": "8511089",
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
            "opDomain": "anf",
            "operatorName": "likai",
            "orderField": 1,
            "operatorId": "9527",
            "propertyTemplateId": "5e96ae2a7336496ecc31abbf",
            "logicDelete": 0,
            "tenantCode": "baozun",
            "createTime": datetime.now(),
            "updateTime": datetime.now(),
            "labels": [
                "618", "测试"
            ]
        }
        # # 4. insert data
        x = mycol.insert_one(mydict)  # print(x.inserted_id)
        # print(x)
        print('正在进行操作-{}'.format(i))


# def insert(pic:dict):
#     pass



if __name__ == '__main__':
    main()
