import httpx
import asyncio
import time
from common.tool import GeneralTool


async def request(client, body):
    url = "http://pim-center-sit.cloud.bz/pim-workbench-bff/integration-platform/product/source/convertToCommon"
    resp = await client.post(url=url, json=body)
    result = resp.json()
    print(result)


async def main():
    async with httpx.AsyncClient() as client:
        start = time.time()
        task_list = []
        client.headers = {
            'tenantCode': 'baozun',
            'catalog': 'REEBOK',
            'Cookie': 'SESSION=YzNhZTQwYzUtMTkxZS00YTdiLWJjMmUtNjk5YmZjMTVjNTQz; SESSION=ZmY2N2Y0YTMtOGMwYy00OTBkLWFkNTMtYjhkZjk4NjVhNDkw',
            'token': '18p2570',
            'Content-Type': 'application/json'
        }
        uri = """mongodb://u_mid_platform_integration_sit:root1234@kh-public-uat-mongo-db01.cloud.bz:27017,kh-public-uat-mongo-db02.cloud.bz:27017,kh-public-uat-mongo-db03.cloud.bz:27017/db_mid_platform_integration_sit?authSource=db_mid_platform_integration_sit&replicaSet=rs-public-uat"""

        collection = GeneralTool.get_collection(uri, 'db_mid_platform_integration_sit', 'P_SOURCE_REEBOK',
                                                authuser='u_mid_platform_integration_sit', authpwd='root1234')
        condition = {"sourceType": "reebok-erp"}
        allrows = collection.find(condition)
        allrows = list(allrows)

        for index, item in enumerate(allrows):
            print(index)
            req = request(client, body={"operatorId": "jm006826",
                                        "externalCodes": [
                                            {"sourceType": 'reebok-erp',
                                             "externalCode": item['externalCode']}]})
            task = asyncio.create_task(req)
            task_list.append(task)
        await asyncio.gather(*task_list)
        end = time.time()
    print(f'耗时：{end - start}')


asyncio.run(main())
