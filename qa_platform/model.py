class assertionModel(dict):

    def __init__(self, JSON_PATH, EXPECTED_VALUE, type='JSON', JSON_VALIDATION=False, EXPECT_NULL=False, INVERT=False,
                 ISREGEX=True):
        self.type = type
        self.json_path = JSON_PATH
        self.expected_value = EXPECTED_VALUE

    def __str__(self):
        # return {"json_path": self.json_path, "expected_value": self.expected_value}
        return f'JSON_PATH={self.json_path},EXPECTED_VALUE={self.expected_value}'


from dataclasses import dataclass, field


def request_qa(url, body, headers):
    pass


class RequestModel():
    def __init__(self):
        pass


model_step = {
    "id": None,
    "parentId": None,
    "scriptId": 4848,
    "description": "属性模板查询",
    "detail": None,
    "waitTime": None,
    "type": "REQUEST",
    "refProductId": None,
    "refScriptId": None,
    "refScriptDisabledStep": [],
    "refScriptInput": [],
    "refScriptOutput": [],
    "requestApiId": 4428,
    "customEncryptionKey": "",
    "customSignatureKey": "",
    "customMqTag": None,
    "customMqMsgType": None,
    "requestHeader": None,
    "uploadFile": None,
    "requestBodyType": "CUSTOM",
    "requestDatasetId": None,
    "requestCustomUrl": "",
    "requestCustomContent": None,
    "requestFormDataContent": [],
    "beanshellScript": "",
    "ifCondition": None,
    "foreachVar": None,
    "foreachType": None,
    "foreach1": None,
    "foreach2": None,
    "requestAssertion": [],
    "ord": 1,
    "createTime": "2020-08-04 18:45:33",
    "lastModify": "2020-08-04 18:45:33",
    "mysqlConfig": {
        "sql": ""
    },
    "mysqlResult": None,
    "stepList": []
}
