import requests

# 登录cookie
headers = {
    'Cookie': 'experimentation_subject_id=IjI5ZDk1YWJlLTU1NDEtNDQ1ZC04MDc5LTMyNWExOGNhZDJmOCI%3D--b7693d682e63dc76c311ca307b7644a467b90fda; _ga=GA1.2.337985542.1590731198; JSESSIONID=3BF7C5E44FE1CB3F74BC644EDA191140; ross_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ3ZXdvcmstam0wMDY4MjYiLCJpc3MiOiJST1NTIiwiYWNsIjpbImFjdGl2aXR5IiwiY29tbW9uIiwiZGVzaWduIiwic3BlZWRyYXciLCJwb3J0YWwiLCJ3b3JrYmVuY2giXSwiZW52Ijoic2l0IiwiZXhwIjoxNTkxNjg4NDE1LCJ1c2VyIjp7InVzZXJDb2RlIjoid2V3b3JrLWptMDA2ODI2IiwidWFjVXNlckNvZGUiOiJqbTAwNjgyNiIsInVzZXJuYW1lIjoi5p2O5YevIiwiZW1wSUQiOiJqbTAwNjgyNiIsImRlcElEIjo0MjY5NTMsImVtYWlsIjoia2FpLmxpQGJhb3p1bi5jb20iLCJtb2JpbGUiOiIxODUyMTAzNTEzMyIsImhlYWRJbWdVcmwiOiJodHRwOi8vcC5xbG9nby5jbi9iaXptYWlsL0hWM2ZXaWJzbUV0a0pIUkRoTElpYVhzdXFoQVdkWkdYUjVwdVZza2tmOVo3RUYyQTVnaHZpY3dZdy8wIiwiZ2VuZGVyIjowfSwiaWF0IjoxNTkxNjgxMjE1fQ.EmT712c0w4OEGlxj0BebAKdpoCbXPYAjZZzcXoUWCVw_d4C_6BIDvFy1Jibgc4SEg364YAi24yeS_rgj8ZZLv8ZnH2Rw-x8P7nUzNxW0CTBqMFbMgQhTk4UTYREmMnmE4Lb1Y31E3fI40uWW1EBS9trV_DUhWDkWrE7luILKc48; ross_token_design_sit=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhcHAiOiJkZXNpZ24iLCJzdWIiOiJ3ZXdvcmstam0wMDY4MjYiLCJzaG9wIjozNCwiaXNzIjoiUk9TUyIsImFjbCI6WyJhY3Rpdml0eSIsImNvbW1vbiIsImRlc2lnbiIsInNwZWVkcmF3IiwicG9ydGFsIiwid29ya2JlbmNoIl0sImVudiI6InNpdCIsImV4cCI6MTU5MTY5MzI5NSwidXNlciI6eyJ1c2VyQ29kZSI6Indld29yay1qbTAwNjgyNiIsInVhY1VzZXJDb2RlIjoiam0wMDY4MjYiLCJ1c2VybmFtZSI6IuadjuWHryIsImVtcElEIjoiam0wMDY4MjYiLCJkZXBJRCI6NDI2OTUzLCJlbWFpbCI6ImthaS5saUBiYW96dW4uY29tIiwibW9iaWxlIjoiMTg1MjEwMzUxMzMiLCJoZWFkSW1nVXJsIjoiaHR0cDovL3AucWxvZ28uY24vYml6bWFpbC9IVjNmV2lic21FdGtKSFJEaExJaWFYc3VxaEFXZFpHWFI1cHVWc2trZjlaN0VGMkE1Z2h2aWN3WXcvMCIsImdlbmRlciI6MH0sImlhdCI6MTU5MTY4NjA5NX0.aQj51WygLn3GLE9Ni6LBwrUWYuF8BWbcBT75hDbIl3lbZh2L1Q213Otj1VJXdlvP0etReSYvJHXK4TFnQBQfBmYUJWQ_kEgvxNlI0-r4WWcL2hFpFLv6fxJw86oHSBrb5h0jqH_WpdafnDx8XFVOKKkKda9V94pNpNF98CjNV4U; ross_token_workbench_sit=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ3ZXdvcmstam0wMDY4MjYiLCJpc3MiOiJST1NTIiwiYWNsIjpbImFjdGl2aXR5IiwiY29tbW9uIiwiZGVzaWduIiwic3BlZWRyYXciLCJwb3J0YWwiLCJ3b3JrYmVuY2giXSwiZW52Ijoic2l0IiwiZXhwIjoxNTkxNjkzODM2LCJ1c2VyIjp7InVzZXJDb2RlIjoid2V3b3JrLWptMDA2ODI2IiwidWFjVXNlckNvZGUiOiJqbTAwNjgyNiIsInVzZXJuYW1lIjoi5p2O5YevIiwiZW1wSUQiOiJqbTAwNjgyNiIsImRlcElEIjo0MjY5NTMsImVtYWlsIjoia2FpLmxpQGJhb3p1bi5jb20iLCJtb2JpbGUiOiIxODUyMTAzNTEzMyIsImhlYWRJbWdVcmwiOiJodHRwOi8vcC5xbG9nby5jbi9iaXptYWlsL0hWM2ZXaWJzbUV0a0pIUkRoTElpYVhzdXFoQVdkWkdYUjVwdVZza2tmOVo3RUYyQTVnaHZpY3dZdy8wIiwiZ2VuZGVyIjowfSwiaWF0IjoxNTkxNjg2NjM2fQ.Dd-zsEyAP13EkrGBQDdDKVlvFOAz-9R4tnsu7flMCmRm7FInlhJmHsczR4gqTQNlI81SUIZZtUTDl-42uq7TBK0Z-MDQMwvSgsWBp2mT7pVqBIkYBngTrm7J8LIXxRhCL91mdEqXBVCWcv0yC_YpmfAo6vTIuZHGg_JeQjhDTq4'
}

def list_apis():
    url = 'http://qa.baozun.com/api2/get_api_list_by_ids?groupIds=44&productIds=279'

    rep = requests.get(url, headers=headers)
    if rep.status_code != 200:
        raise Exception('接口请求异常')
    return [item['id'] for item in rep.json().get('data')]


def api_detail(apiId: str):
    url = 'http://qa.baozun.com/api2/get_api_info?apiId={}'.format(apiId)
    rep = requests.get(url, headers=headers)
    if rep.status_code != 200:
        raise Exception('接口请求异常')
    return rep.json().get('data')


def save_api(body: dict):
    url = 'http://qa.baozun.com/api2/save_api'
    rep = requests.post(url, json=body, headers=headers)
    if rep.status_code != 200:
        raise Exception('接口请求异常')
    assert rep.json().get('success')


def main():
    for apiId in list_apis():
        body = api_detail(apiId)
        # 更新请求参数
        for config in body['configInfo']:
            config[
                'header'] = 'Connection: keep-alive\nContent-type: application/json\ntenantCode: baozun\nopDomain:${opDomain}'
        save_api(body)


if __name__ == '__main__':
    main()
