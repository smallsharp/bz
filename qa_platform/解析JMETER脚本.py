from qa_platform import template
from lxml import etree
import json
import requests
import copy


class QAPlatform():

    def __init__(self, filename=None, login_script_id=None):
        self.filename = filename
        self.moduleId = 522
        self.login_script_id = login_script_id  # 5117
        self.headers = {
            'Cookie': 'JSESSIONID=6BAF73B2CDB13CCA2759DFB095E80A37'
        }
        self.model_controllers = []

        self.remove_prefix = ['/pim-workbench-bff', '/pim-core', '/pim-query']

    def parser_jmx(self):

        html = etree.parse(self.filename)
        # 提取所有 已启用的事务控制器标签
        controllers = html.xpath(
            '//ThreadGroup[@enabled="true"]/following-sibling::hashTree[1]/TransactionController[@enabled="true"]')
        print(f'已启用的事务控制器数量:{len(controllers)}')

        for controller in controllers:
            model_controller = copy.deepcopy(template.model_controller)
            model_controller['moduleId'] = self.moduleId
            model_controller['name'] = controller.get('testname')
            model_controller['description'] = controller.get('testname')

            # 每个事务对应 qa平台一个用例（一个事务包含多个httpsampler）
            httpsamplers = controller.xpath('following-sibling::hashTree[1]/HTTPSamplerProxy[@enabled="true"]')
            print(f'当前用例：{controller.get("testname")}')

            for httpsampler in httpsamplers:
                # 获取每个步骤的详情
                step = self.get_step_info(httpsampler)
                model_controller['stepList'].append(step)
                print('-' * 32)
            if self.login_script_id and len(httpsamplers) > 0:
                step = copy.deepcopy(template.step)
                step['refScriptId'] = self.login_script_id
                step['type'] = 'SCRIPT'
                step['description'] = '登录'
                step['scriptId'] = 0
                step['refScriptOutput'] = [
                    {
                        "name": "token",
                        "description": "",
                        "isRequired": None,
                        "type": "NORMAL",
                        "value": None
                    },
                    {
                        "name": "session",
                        "description": "",
                        "isRequired": None,
                        "type": "NORMAL",
                        "value": None
                    }
                ]

                step['refScriptInput'] = [
                    {
                        "name": "token",
                        "description": "",
                        "isRequired": None,
                        "type": "NORMAL",
                        "value": "token"
                    },
                    {
                        "name": "session",
                        "description": "",
                        "isRequired": None,
                        "type": "NORMAL",
                        "value": "session"
                    }
                ]
                model_controller['stepList'].insert(0, step)
            print(model_controller)
            self.model_controllers.append(model_controller)

    def get_assertion_list(self, httpsampler):
        # 1. json断言
        json_assertions = httpsampler.xpath('./following-sibling::hashTree[1]/JSONPathAssertion[@enabled="true"]')
        print(f'当前请求的断言数量:{len(json_assertions)}')

        assertion_list = list()
        for assert_ in json_assertions:
            JSON_PATH = assert_.find('./stringProp[@name=\"JSON_PATH\"]').text
            EXPECTED_VALUE = assert_.find('./stringProp[@name=\"EXPECTED_VALUE\"]').text
            JSON_VALIDATION = assert_.find('./boolProp[@name=\"JSONVALIDATION\"]').text

            ## 是否需要断言值，是则断言EXPECTED_VALUE,赋值value, 否则只断言JSON_PATH，赋值（.*）
            if JSON_VALIDATION != 'true':
                EXPECTED_VALUE = '(.*)'

            # EXPECT_NULL = assertion.find('./boolProp[@name=\"EXPECT_NULL\"]').text
            # INVERT = assertion.find('./boolProp[@name=\"INVERT\"]').text
            # ISREGEX = assertion.find('./boolProp[@name=\"ISREGEX\"]').text
            assertion = copy.deepcopy(template.assertion)
            assertion['value'] = EXPECTED_VALUE
            assertion['path'] = JSON_PATH
            assertion['description'] = assert_.get('testname')
            assertion_list.append(assertion)
            print(assert_.get('testname'), json.dumps(assertion, ensure_ascii=False))

        # 2. json 提取器
        json_extractors = httpsampler.xpath('./following-sibling::hashTree[1]/JSONPostProcessor[@enabled="true"]')
        print(f'当前请求的json提取器数量:{len(json_extractors)}')
        for index, extractor in enumerate(json_extractors):
            JSON_PATH = extractor.find('./stringProp[@name=\"JSONPostProcessor.jsonPathExprs\"]').text
            export = extractor.find('./stringProp[@name=\"JSONPostProcessor.referenceNames\"]').text
            assertion = copy.deepcopy(template.assertion)  # assertion = dict.copy(template.assertion)
            assertion['value'] = '(.*)'
            assertion['path'] = JSON_PATH
            assertion['description'] = JSON_PATH
            assertion['export'] = export
            assertion_list.append(assertion)
            # print(f'index:{index + 1},json_path:{json_path}')

        # print(json.dumps(assertion_list))
        return assertion_list

    def get_step_info(self, httpsampler):
        '''
        :param httpsampler: 是一个完整的http请求
        :param remove_prefix: 接口path中需要去掉的前缀
        :return: step
        '''
        stepname = httpsampler.get('testname')
        print('step:{}'.format(stepname))
        # path = httpsampler.xpath('./stringProp[@name=\"HTTPSampler.path\"]')[0].text
        path = httpsampler.find('./stringProp[@name=\"HTTPSampler.path\"]').text
        method = httpsampler.find('./stringProp[@name=\"HTTPSampler.method\"]').text
        domain = httpsampler.find('./stringProp[@name=\"HTTPSampler.domain\"]').text
        port = httpsampler.find('./stringProp[@name=\"HTTPSampler.port\"]').text
        body = httpsampler.find('.//stringProp[@name=\"Argument.value\"]').text

        for prefix in self.remove_prefix:
            if str(path).startswith(prefix):
                path = str(path).replace(prefix, '')
                break

        # 获取当前请求的 json断言 和 json其提取数据
        assertionList = self.get_assertion_list(httpsampler)
        step = copy.deepcopy(template.step)
        step['description'] = stepname
        step['requestAssertion'] = assertionList
        step['requestCustomContent'] = body
        step['requestApiId'] = self.get_api_id(path=path)  # tobe continue  get_api_id
        return step

    def get_api_id(self, path, groupId=44):
        '''
        通过接口path获取接口id, 从 groupId=44接口返回的数据进行检索
        '''
        url = "http://qa.baozun.com/api2/get_api_list_by_ids?groupIds={}".format(groupId)
        payload = {}

        try:
            response = requests.request("GET", url, headers=self.headers, data=payload)
        except Exception as e:
            raise Exception('请求失败')
        if response.status_code != 200:
            raise Exception('qa平台中接口请求出现异常,status_code:{}'.format(response.status_code))

        targetrows = [item for item in response.json()['data'] if item.get('path') == path]

        if len(targetrows) > 0:
            return targetrows[0]['id']
        else:
            raise Exception('没有匹配到apiId，使用path：{}'.format(path))

    def save_script(self, body):
        url = "http://qa.baozun.com/api2/save_script"
        response = requests.request("POST", url, headers=self.headers, json=body)
        print(response.json())

    def run(self):
        self.parser_jmx()
        print('解析完成')

        # for body in self.model_controllers:
        #     self.save_script(body)


if __name__ == '__main__':
    qa = QAPlatform(filename='test.jmx')
    qa.run()
