import json

import requests

url = "http://gateway-sandbox.baozun.com/pim/inventory/querySkuInventoryList"

payload = "{\n    \"pSize\": 1000,\n    \"pNum\": 1,\n    \"tenantCode\": 88000063\n}"
headers = {
  'Content-Type': 'application/json',
  'client-id': 'DEV201805001',
  'client-secret': 'PLmpfFsKv6mF6G3QVR9izWk82nxmelEm',
  'Host': 'gateway-sandbox.baozun.com',
  'accept-encoding': 'gzip'
}

response = requests.request("POST", url, headers=headers, data = payload)

resjson = json.loads(response.content.decode('utf-8'))
fw = open('skuCode.txt', 'w')

for item in resjson.get('content'):
    fw.write(item.get('skuCode')+'\n')
    # print(item.get('skuCode'))

fw.close()

# print(response.content.decode('utf-8'))
