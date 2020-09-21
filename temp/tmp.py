sku = {
    'propeties': {
        'sku': 'k001',
        'custom': {
            'colorId': 111,
            'colorName': 'xxx',
            'obj': {
                'id': 333
            }
        }
    }
}


def set_value(propertiesObj, key, value):
    # prop = propertiesObj['propeties']
    for word in key.split('.'):
        obj = propertiesObj.get(word)
        if isinstance(obj, (str, int, float)):
            propertiesObj[word] = value
        else:
            propertiesObj = obj

        # print(propertiesObj)

    print(sku)


if __name__ == '__main__':
    key = 'custom.colorId'
    set_value(sku['propeties'], key, 66655.55)
