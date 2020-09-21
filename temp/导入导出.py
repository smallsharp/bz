import requests
import json
import csv


def get_product_info():
    url = "http://pim-center-sit.cloud.bz/pim-workbench-bff/product/findProductInfo"

    payload = {
        "productReqList": [
            {
                "code": "P630_1005"
            }
        ]
    }
    headers = {
        'tenantCode': 'baozun',
        'catalog': 'user',
        'token': '1822561',
        'Cookie': 'SESSION=MGUwYjRjYmEtYjM5Ny00OWE1LTg5ZTEtNzI5N2Y0NTMzNTNm',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    return response


def get_value(propertyType, obj: dict, propertyCode: None, hasnestedProperties: False, multiple: False):
    value = None
    if propertyType in ["NUMBER", "SELECT"]:
        value = obj['value']
    elif propertyType == 'String':
        value = obj['value']['default']
    elif propertyType == 'ATTR_GROUP' and not multiple:
        nestedProperties = obj['nestedProperties']
        valuedict = dict(obj['value'])
        for np in nestedProperties:
            value = get_value(np['propertyType'], np)
            # tempcode = {}
            tmpcode = np['propertyCode']
            tmpname = np['propertyName']
            propertyCode = f'{propertyCode}.{tmpcode}'
            propertyName = f'{propertyName}.{tmpname}'
            propertyCode = obj['propertyCode']
            propertyName = obj['propertyName']

    return value


def tmp():
    print(json.dumps(properties, ensure_ascii=False))
    headers = list()

    sexrow = {
        "productCode": '商品编码',
        "schemaNamePath": "类目路径名称",
    }
    row = {
        "productCode": 'P630_1001',
        "schemaNamePath": "c110110",
    }
    for sp in properties:
        propertyType = sp["propertyType"]

        # 属性名称 和 属性编码
        propertyName = sp['propertyName']
        propertyCode = sp["propertyCode"]
        multiple = sp['multiple']

        if propertyType != 'ATTR_GROUP':
            headers.append(propertyCode)  # 更新header

        value = None
        if propertyType in ["NUMBER", "SELECT"]:
            value = sp['value']
        elif propertyType == 'String':
            value = sp['value']['default']
        elif propertyType == 'ATTR_GROUP' and not multiple:
            nestedProperties = sp['nestedProperties']
            tempdict = {}
            namedict = {}
            valuedict = dict(sp['value'])
            for np in nestedProperties:
                # tempcode = {}
                tmpcode = np['propertyCode']
                tmpname = np['propertyName']
                propertyCode = f'{propertyCode}.{tmpcode}'
                propertyName = f'{propertyName}.{tmpname}'
                tempdict.update({propertyCode: propertyName})
                # namedict.update({propertyCode: propertyName})
                valuedict.update({propertyCode: valuedict.get(tmpcode)})
                headers.append(propertyCode)
                propertyCode = sp['propertyCode']
                propertyName = sp['propertyName']

        sexrow.update(tempdict)  # 更新第二行文字说明
        row.update(valuedict)

    print(headers)

    fieldnames = ['productCode', 'schemaNamePath']
    fieldnames.extend(headers)

    fw = open('../files/c4.csv', 'w', encoding='utf8', newline='')

    # 使用这个风格mydialect
    # d_writer = csv.DictWriter(fw, fieldnames=fieldnames, dialect='mydialect')
    d_writer = csv.DictWriter(fw, fieldnames=fieldnames)

    d_writer.writeheader()  # writer header
    d_writer.writerow(sexrow)  # write desc
    d_writer.writerow(row)


if __name__ == '__main__':
    # response = get_product_info()
    # properties = response.json()['data']['schemaProperties']
    # print(properties)
    #
    # property_list = list()
    # for sp in properties:
    #     propertyType = sp["propertyType"]
    #     # 属性名称 和 属性编码
    #     propertyName = sp['propertyName']
    #     propertyCode = sp["propertyCode"]
    #     multiple = sp['multiple']
    #     if propertyType != 'ATTR_GROUP':
    #         property_list.append(propertyCode)
    #     else:
    #         nestedProperties = sp['nestedProperties']
    #         print(propertyCode, propertyName, len(nestedProperties))
    #         nestplist = list()
    #         for n in nestedProperties:
    #             nestplist.append(f"{propertyCode}.{n['propertyCode']}")
    #         property_list.extend(nestplist)
    #
    # print(property_list)
    # print(len(property_list))
    str1 = 'productCode	schemaNamePath	productNo	title	productName	careNotice.careWash	careNotice.careBleach	careNotice.careIron	careNotice.careDry	careNotice.careOther	productDescription	sellingPoints	price	productImage.image	productImage.imageType	productImage.imageTypeExtend	productImage.productColor	isGift	isExpirationProduct	isERPCreate	isSnProduct	originalLocation.country	originalLocation.province	originalLocation.city	originalLocation.area	originalLocation.areaExtend	brand	mutiProperty	channelCode	obj.relation-one	obj.relation-many	obj.desc	obj.num	obj.num-multi	obj.select-one	obj.select-many	obj.date-many	launchInfo.launchTime	launchInfo.year	launchInfo.month	launchInfo.season	material.name	material.desc	material.desc_list	material.richtext	material.desc-enum-mulitple	material.date	material.date-many	material.relation-one	material.relation-many	richtext	relation	relation-multiple	num_mutilple	datetime-many	自定义属性K1'

    list1 = str1.split()
    list2 = ['originalLocation.country', 'originalLocation.province', 'originalLocation.city', 'originalLocation.area',
             'originalLocation.areaExtend', 'isSnProduct', 'title', 'launchInfo.launchTime', 'launchInfo.year',
             'launchInfo.month', 'launchInfo.season', 'productName', 'relation', 'isExpirationProduct',
             'productImage.image', 'productImage.imageType', 'productImage.imageTypeExtend',
             'productImage.productColor', 'material.name', 'material.desc', 'material.desc_list', 'material.richtext',
             'material.desc-enum-mulitple', 'material.date', 'material.date-many', 'material.relation-one',
             'material.relation-many', 'careNotice.careWash', 'careNotice.careBleach', 'careNotice.careIron',
             'careNotice.careDry', 'careNotice.careOther', 'price', 'obj.relation-one', 'obj.relation-many', 'obj.desc',
             'obj.num', 'obj.num-multi', 'obj.select-one', 'obj.select-many', 'obj.date-many', 'mutiProperty', 'isGift',
             'num_mutilple', 'richtext', 'sellingPoints', 'brand', 'productNo', 'productDescription',
             'relation-multiple', 'channelCode']
    list2.extend(['productCode', 'schemaNamePath'])

    print(list1)
    print(len(list1),len(list2))

    print(set(list1).difference(set(list2)))

    # for i in list1:
    #     for j in list2:
    #         if j == i:
    #             list1.remove(i)

    print(list1)
