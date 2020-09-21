from qa_platform import template
from lxml import etree
import json
import requests
import copy


def get_assertion_list(httpsampler):
    assertion_list = list()
    # 1. json断言
    json_assertions = httpsampler.xpath('./following-sibling::hashTree[1]/JSONPathAssertion')
    print(f'当前请求的断言数量:{len(json_assertions)}')

    for ast in json_assertions:
        json_path = ast.find('./stringProp[@name=\"JSON_PATH\"]').text
        EXPECTED_VALUE = ast.find('./stringProp[@name=\"EXPECTED_VALUE\"]').text
        # JSON_VALIDATION = assertion.find('./boolProp[@name=\"JSONVALIDATION\"]').text
        # EXPECT_NULL = assertion.find('./boolProp[@name=\"EXPECT_NULL\"]').text
        # INVERT = assertion.find('./boolProp[@name=\"INVERT\"]').text
        # ISREGEX = assertion.find('./boolProp[@name=\"ISREGEX\"]').text
        assertion = copy.deepcopy(template.assertion)
        assertion['value'] = EXPECTED_VALUE
        assertion['path'] = json_path
        assertion['description'] = ast.get('testname')
        assertion_list.append(assertion)

    # 2. json 提取器
    json_extractors = httpsampler.xpath('./following-sibling::hashTree/JSONPostProcessor')
    print(f'当前请求的json提取器数量:{len(json_extractors)}')
    for index, extractor in enumerate(json_extractors):
        json_path = extractor.find('./stringProp[@name=\"JSONPostProcessor.jsonPathExprs\"]').text
        export = extractor.find('./stringProp[@name=\"JSONPostProcessor.referenceNames\"]').text
        assertion = copy.deepcopy(template.assertion)  # assertion = dict.copy(template.assertion)
        assertion['value'] = '(.*)'
        assertion['path'] = json_path
        assertion['description'] = json_path
        assertion['export'] = export
        assertion_list.append(assertion)

        # print(f'index:{index + 1},json_path:{json_path}')

    # print(json.dumps(assertion_list))
    return assertion_list


def get_step_info(httpsampler, remove_prefix='/pim-workbench-bff'):
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

    if str(path).startswith(remove_prefix):
        path = str(path).replace(remove_prefix, '')

    # 获取当前请求的 json断言 和 json其提取数据
    assertionList = get_assertion_list(httpsampler)
    step = copy.deepcopy(template.step)
    step['description'] = stepname
    step['requestAssertion'] = assertionList
    step['requestCustomContent'] = body
    step['requestApiId'] = get_api_id(path=path)  # tobe continue  get_api_id
    return step


def get_api_id(path, groupId=44):
    '''
    通过接口path获取接口id, 从 groupId=44接口返回的数据进行检索
    '''
    url = "http://qa.baozun.com/api2/get_api_list_by_ids?groupIds={}".format(groupId)
    payload = {}
    headers = {
        'Cookie': 'ross_token_workbench_sit=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ3ZXdvcmstam0wMDY4MjYiLCJpc3MiOiJST1NTIiwiYWNsIjpbImFjdGl2aXR5IiwiY29tbW9uIiwiZGVzaWduIiwic3BlZWRyYXciLCJwb3J0YWwiLCJ3b3JrYmVuY2giXSwiZW52Ijoic2l0IiwiZXhwIjoxNTk3NjY2Njg5LCJ1c2VyIjp7InVzZXJDb2RlIjoid2V3b3JrLWptMDA2ODI2IiwidWFjVXNlckNvZGUiOiJqbTAwNjgyNiIsInVzZXJuYW1lIjoi5p2O5YevIiwiZW1wSUQiOiJqbTAwNjgyNiIsImRlcElEIjo0MjY5NTMsImVtYWlsIjoia2FpLmxpQGJhb3p1bi5jb20iLCJtb2JpbGUiOiIxODUyMTAzNTEzMyIsImhlYWRJbWdVcmwiOiJodHRwOi8vcC5xbG9nby5jbi9iaXptYWlsL0hWM2ZXaWJzbUV0a0pIUkRoTElpYVhzdXFoQVdkWkdYUjVwdVZza2tmOVo3RUYyQTVnaHZpY3dZdy8wIiwiZ2VuZGVyIjowfSwiaWF0IjoxNTk3NjU5NDg5LCJ0ZW5hbnQiOiJiYW96dW4ifQ.TrIbEaqJ_u99sPVDJMqNoWmkSyBo8Fby4stkPWQKTPhpNkOsWdq_W97laObB4kRm7I_6ia_am-ffz1U_32dISapCdyIOuPdAngGQsMCgkpnD38fK0msPrEKM7wibKeqUz8XS705BD895OoMe_vmVaiVhOTpvI6hwpB6-_4BWZXg; ross_token_workbench_uat=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ3ZXdvcmstam0wMDY4MjYiLCJpc3MiOiJST1NTIiwiYWNsIjpbImFjdGl2aXR5IiwiY29tbW9uIiwiZGVzaWduIiwic3BlZWRyYXciLCJwb3J0YWwiLCJ3b3JrYmVuY2giXSwiZW52IjoidWF0IiwiZXhwIjoxNTk3NzM3OTAxLCJ1c2VyIjp7InVzZXJDb2RlIjoid2V3b3JrLWptMDA2ODI2IiwidWFjVXNlckNvZGUiOiJqbTAwNjgyNiIsInVzZXJuYW1lIjoi5p2O5YevIiwiZW1wSUQiOiJqbTAwNjgyNiIsImRlcElEIjo0NzQwNzcsImVtYWlsIjoia2FpLmxpQGJhb3p1bi5jb20iLCJtb2JpbGUiOiIxODUyMTAzNTEzMyIsImhlYWRJbWdVcmwiOiJodHRwOi8vcC5xbG9nby5jbi9iaXptYWlsL0hWM2ZXaWJzbUV0a0pIUkRoTElpYVhzdXFoQVdkWkdYUjVwdVZza2tmOVo3RUYyQTVnaHZpY3dZdy8wIiwiZ2VuZGVyIjowfSwiaWF0IjoxNTk3NzMwNzAxLCJ0ZW5hbnQiOiJiYW96dW4ifQ.k3UgLo5L16jTqXegLVVHBI1NartKdZ5NlUU4_1mA7vsauHSAai9XRnYFMFWr48b_lLwsL5neFyaSOfyyMzK-z9ovQwVXddbiymdBYnnLsqGNIKG6nL6gJtCTn76EH1m7tgCwabb1H3zdlszLLotZSMz8Z6agx9GvATQRQdD4xOo; ross_token_workbench_prod=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ3ZXdvcmstam0wMDY4MjYiLCJpc3MiOiJST1NTIiwiYWNsIjpbImFjdGl2aXR5IiwiY29tbW9uIiwiZGVzaWduIiwic3BlZWRyYXciLCJwb3J0YWwiLCJ3b3JrYmVuY2giXSwiZW52IjoicHJvZCIsImV4cCI6MTU5NzkxNjIyOSwidXNlciI6eyJ1c2VyQ29kZSI6Indld29yay1qbTAwNjgyNiIsInVhY1VzZXJDb2RlIjoiam0wMDY4MjYiLCJ1c2VybmFtZSI6IuadjuWHryIsImVtcElEIjoiam0wMDY4MjYiLCJkZXBJRCI6Mzg4LCJlbWFpbCI6ImthaS5saUBiYW96dW4uY29tIiwibW9iaWxlIjoiMTg1MjEwMzUxMzMiLCJoZWFkSW1nVXJsIjoiaHR0cDovL3AucWxvZ28uY24vYml6bWFpbC9IVjNmV2lic21FdGtKSFJEaExJaWFYc3VxaEFXZFpHWFI1cHVWc2trZjlaN0VGMkE1Z2h2aWN3WXcvMCIsImdlbmRlciI6MH0sImlhdCI6MTU5NzkwOTAyOSwidGVuYW50IjoiYmFvenVuIn0.UdEa1e45RMLu9Ca6NC-GSxnetgLaNdaMIZJjxDiLueL9-JC2EI6trjftGHz6EwhJWWlzjhsRP1UmdmQWCSE43IeoQwZ7LFDZ9G4bwZeathK3ESaEilBxgeeVYgcU96uc6qyVTiKIAYMGlm0W-JTQWAKmHaUhr8DZsJzLrG5bk6M; JSESSIONID=64435FACC4076A90C48FF6B3F22253F3'
    }

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
    except Exception as e:
        raise Exception('请求失败')
    if response.status_code != 200:
        raise Exception('qa平台中接口请求出现异常,status_code:{}'.format(response.status_code))

    targetrows = [item for item in response.json()['data'] if item.get('path') == path]

    if len(targetrows) > 0:
        return targetrows[0]['id']
    else:
        raise Exception('没有匹配到apiId，使用path：{}'.format(path))


def bulid_controller():
    pass


def save_script(body):
    url = "http://qa.baozun.com/api2/save_script"

    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'ross_token_workbench_sit=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ3ZXdvcmstam0wMDY4MjYiLCJpc3MiOiJST1NTIiwiYWNsIjpbImFjdGl2aXR5IiwiY29tbW9uIiwiZGVzaWduIiwic3BlZWRyYXciLCJwb3J0YWwiLCJ3b3JrYmVuY2giXSwiZW52Ijoic2l0IiwiZXhwIjoxNTk3NjY2Njg5LCJ1c2VyIjp7InVzZXJDb2RlIjoid2V3b3JrLWptMDA2ODI2IiwidWFjVXNlckNvZGUiOiJqbTAwNjgyNiIsInVzZXJuYW1lIjoi5p2O5YevIiwiZW1wSUQiOiJqbTAwNjgyNiIsImRlcElEIjo0MjY5NTMsImVtYWlsIjoia2FpLmxpQGJhb3p1bi5jb20iLCJtb2JpbGUiOiIxODUyMTAzNTEzMyIsImhlYWRJbWdVcmwiOiJodHRwOi8vcC5xbG9nby5jbi9iaXptYWlsL0hWM2ZXaWJzbUV0a0pIUkRoTElpYVhzdXFoQVdkWkdYUjVwdVZza2tmOVo3RUYyQTVnaHZpY3dZdy8wIiwiZ2VuZGVyIjowfSwiaWF0IjoxNTk3NjU5NDg5LCJ0ZW5hbnQiOiJiYW96dW4ifQ.TrIbEaqJ_u99sPVDJMqNoWmkSyBo8Fby4stkPWQKTPhpNkOsWdq_W97laObB4kRm7I_6ia_am-ffz1U_32dISapCdyIOuPdAngGQsMCgkpnD38fK0msPrEKM7wibKeqUz8XS705BD895OoMe_vmVaiVhOTpvI6hwpB6-_4BWZXg; ross_token_workbench_uat=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ3ZXdvcmstam0wMDY4MjYiLCJpc3MiOiJST1NTIiwiYWNsIjpbImFjdGl2aXR5IiwiY29tbW9uIiwiZGVzaWduIiwic3BlZWRyYXciLCJwb3J0YWwiLCJ3b3JrYmVuY2giXSwiZW52IjoidWF0IiwiZXhwIjoxNTk3NzM3OTAxLCJ1c2VyIjp7InVzZXJDb2RlIjoid2V3b3JrLWptMDA2ODI2IiwidWFjVXNlckNvZGUiOiJqbTAwNjgyNiIsInVzZXJuYW1lIjoi5p2O5YevIiwiZW1wSUQiOiJqbTAwNjgyNiIsImRlcElEIjo0NzQwNzcsImVtYWlsIjoia2FpLmxpQGJhb3p1bi5jb20iLCJtb2JpbGUiOiIxODUyMTAzNTEzMyIsImhlYWRJbWdVcmwiOiJodHRwOi8vcC5xbG9nby5jbi9iaXptYWlsL0hWM2ZXaWJzbUV0a0pIUkRoTElpYVhzdXFoQVdkWkdYUjVwdVZza2tmOVo3RUYyQTVnaHZpY3dZdy8wIiwiZ2VuZGVyIjowfSwiaWF0IjoxNTk3NzMwNzAxLCJ0ZW5hbnQiOiJiYW96dW4ifQ.k3UgLo5L16jTqXegLVVHBI1NartKdZ5NlUU4_1mA7vsauHSAai9XRnYFMFWr48b_lLwsL5neFyaSOfyyMzK-z9ovQwVXddbiymdBYnnLsqGNIKG6nL6gJtCTn76EH1m7tgCwabb1H3zdlszLLotZSMz8Z6agx9GvATQRQdD4xOo; ross_token_workbench_prod=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ3ZXdvcmstam0wMDY4MjYiLCJpc3MiOiJST1NTIiwiYWNsIjpbImFjdGl2aXR5IiwiY29tbW9uIiwiZGVzaWduIiwic3BlZWRyYXciLCJwb3J0YWwiLCJ3b3JrYmVuY2giXSwiZW52IjoicHJvZCIsImV4cCI6MTU5NzkxNjIyOSwidXNlciI6eyJ1c2VyQ29kZSI6Indld29yay1qbTAwNjgyNiIsInVhY1VzZXJDb2RlIjoiam0wMDY4MjYiLCJ1c2VybmFtZSI6IuadjuWHryIsImVtcElEIjoiam0wMDY4MjYiLCJkZXBJRCI6Mzg4LCJlbWFpbCI6ImthaS5saUBiYW96dW4uY29tIiwibW9iaWxlIjoiMTg1MjEwMzUxMzMiLCJoZWFkSW1nVXJsIjoiaHR0cDovL3AucWxvZ28uY24vYml6bWFpbC9IVjNmV2lic21FdGtKSFJEaExJaWFYc3VxaEFXZFpHWFI1cHVWc2trZjlaN0VGMkE1Z2h2aWN3WXcvMCIsImdlbmRlciI6MH0sImlhdCI6MTU5NzkwOTAyOSwidGVuYW50IjoiYmFvenVuIn0.UdEa1e45RMLu9Ca6NC-GSxnetgLaNdaMIZJjxDiLueL9-JC2EI6trjftGHz6EwhJWWlzjhsRP1UmdmQWCSE43IeoQwZ7LFDZ9G4bwZeathK3ESaEilBxgeeVYgcU96uc6qyVTiKIAYMGlm0W-JTQWAKmHaUhr8DZsJzLrG5bk6M; JSESSIONID=64435FACC4076A90C48FF6B3F22253F3'
    }

    response = requests.request("POST", url, headers=headers, json=body)

    print(response.json())


def parser_jmx(jmxfile, moduleId=522, loginscriptId=5117):
    html = etree.parse(jmxfile)
    # 提取所有 启用的事务控制器标签
    controllers = html.xpath('//TransactionController[@enabled="true"]')
    # print(f'事务控制器的数量:{len(controllers)}')
    model_controllers = []

    customargs = html.xpath('//ThreadGroup/following-sibling::hashTree[1]/Arguments')
    print(len(customargs))
    for arg in customargs:
        print(arg.get('testname'))


    return
    for controller in controllers:
        model_controller = copy.deepcopy(template.model_controller)
        model_controller['moduleId'] = moduleId
        model_controller['name'] = controller.get('testname')
        model_controller['description'] = controller.get('testname')

        # 每个事务对应 qa平台一个用例（包含多个step）
        httpsamplers = controller.xpath('following-sibling::hashTree[1]/HTTPSamplerProxy[@enabled="true"]')
        print(f'当前用例：{controller.get("testname")}')

        for http in httpsamplers:
            step = get_step_info(http, remove_prefix='/pim-workbench-bff')
            model_controller['stepList'].append(step)
            print('-' * 32)
        if loginscriptId and len(httpsamplers) > 0:
            step = copy.deepcopy(template.step)
            step['refScriptId'] = loginscriptId
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
        model_controllers.append(model_controller)
    return model_controllers


def main():
    model_controllers = parser_jmx('测试专用.jmx')
    # print(json.dumps(model_controllers, ensure_ascii=False))
    # print('解析完成')

    # for body in model_controllers:
    #     save_script(body)
    #     break


if __name__ == '__main__':
    main()
