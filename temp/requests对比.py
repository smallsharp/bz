import requests
import time


def request():
    url = "http://pim-center-sit.cloud.bz/pim-query/product-rule/findProductRuleAlgorithmList"

    payload = "{\r\n    \"tenantCode\":\"baozun\"\r\n}"
    headers = {
        'tenantCode': 'baozun',
        'cataLog': 'user',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def main():
    start = time.time()
    for _ in range(1000):
        request()
    end = time.time()
    print(f'发送100次请求，耗时：{end - start}')

if __name__ == '__main__':
    main()
