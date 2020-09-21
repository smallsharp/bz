import requests
import json


def agg():
    url = "http://pim-center-sit.cloud.bz/pim-query/product/findProductList"

    payload = {
        "searchType": "COMMON_MASTER",
        "searchParam": {
            "iStart": 0,
            "iRowSize": 100,
            "schemaCode": ""
        }
    }
    headers = {
        'tenantCode': 'baozun',
        'catalog': 'user',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    productlist = response.json()['data']['dataList']
    print(json.dumps(productlist))
    path_dict = dict()
    for data in productlist:
        schemaCode = data['schemaCode']
        path_dict.update({schemaCode: None})

    print(path_dict, len(path_dict))  # 先拿到key

    for key in path_dict:
        codelist = []
        for i in productlist:
            if key == i['schemaCode']:
                codelist.append(i['productCode'])
        path_dict.update({key: codelist})

    print(path_dict)


def main():
    agg()


if __name__ == '__main__':
    main()
