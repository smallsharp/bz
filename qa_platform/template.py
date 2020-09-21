'''
qa-platform 模板数据
'''

# 断言的模板
assertion = {
    "type": "JSON",
    "value": '',
    "header": None,
    "path": '',
    "reg": None,
    "var": None,
    "export": None,
    "exportDescription": None,
    "isExportAsArray": None,
    "isContinue": True,
    "description": ''
}

# step
step = {
    "id": None,
    "parentId": None,
    "scriptId": 0,  # default 0 when insert
    "description": '这里是步骤的描述',
    "detail": None,
    "waitTime": None,
    "type": "REQUEST",
    "refProductId": None,
    "refScriptId": None,
    "refScriptDisabledStep": [],
    "refScriptInput": [],
    "refScriptOutput": [],
    "requestApiId": 0,  # 绑定的api ,需要查出来
    "customEncryptionKey": "",
    "customSignatureKey": "",
    "customMqTag": None,
    "customMqMsgType": None,
    "requestHeader": None,
    "uploadFile": None,
    "requestBodyType": "CUSTOM",
    "requestDatasetId": None,
    "requestCustomUrl": "",
    "requestCustomContent": None,  # 请求参数体
    "requestFormDataContent": [],
    "beanshellScript": "",
    "ifCondition": None,
    "foreachVar": None,
    "foreachType": None,
    "foreach1": None,
    "foreach2": None,
    "requestAssertion": [],  # 断言数据
    "ord": None,
    "mysqlConfig": {
        "sql": ""
    },
    "mysqlResult": None,
    "stepList": []
}

# model_controller

model_controller = {
    "id": 0,
    "moduleId": None,  # pim-product 522
    "name": '',  # 用例名称
    "description": '',  # 用例描述
    "isPublic": False,
    "isDraft": False,
    "isCrossSystem": False,
    "inputVar": [],
    "inputValue": [],
    "outputVar": [],
    "stepList": [],  # 步骤
    "creator": "jm006826",
    "creatorCn": "李凯",
    "createTime": None,
    "lastModify": None,
    "variableDef": [],
    "variableSet": [{
        "id": 0,
        "name": "DEFAULT",
        "description": "默认数据集"
    }],
    "variableValue": [],
    "tag": []
}
