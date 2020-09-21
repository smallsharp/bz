#!/service.py/software/python-3.7/bin/python3
# -*- coding:utf-8 -*-

import os
import sys
import xml.dom.minidom
import datetime
import pandas

sys.path.append(".")
from .DBTool import DBTool

job_name = sys.argv[1]
product_code = sys.argv[2]
env = sys.argv[3]  # "sit"
profile_name = sys.argv[4]
# print(sys.argv)
# print(profile_name)

jtl_dir = "/service.py/software/jenkins/doc/workspace"  # /job_name/report.jtl
db_config = {
    'host': 'ylf-autotest-prod-mysql-db01.cloud.bz',
    'user': 'u_autotest',
    'password': 'root1234',
    'database': 'autotest',
    'charset': 'utf8',
    'autocommit': True,
}
# db_config = {
#    'host': '10.88.108.62',
#    'user': 'qatest',
#    'password': 'MyNewPass@123',
#    'database': 'autotest',
#    'charset': 'utf8',
#    'autocommit': True,
# }
request_table_columns = ['type', 'name', 'url', 'time', 't', 'ts', 'dt', 'success', 'request_header', 'request_body',
                         'cookie', 'request_method', 'response_code', 'response_msg', 'response_header',
                         'response_body', 'assertion_name', 'assertion_status', 'assertion_msg']

date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
xml_file = jtl_dir + "/" + job_name + "/" + profile_name + "/report.jtl"


class RequestParser:
    def __init__(self, element):
        self.testcase_name = None
        self.name = None
        self.url = None
        self.time = None
        self.t = None
        self.ts = None
        self.dt = None
        self.success = None
        self.request_header = None
        self.request_body = None
        self.cookie = None
        self.request_method = None
        self.response_code = None
        self.response_msg = None
        self.response_header = None
        self.response_body = None
        self.assertion_name = None
        self.assertion_status = None
        self.assertion_msg = None
        self._element = element
        self._run()

    def _run(self):
        self._get_common(self._element)
        self._get_url(self._element.getElementsByTagName("java.net.URL"))
        self._get_request_method(self._element.getElementsByTagName("method"))
        self._get_cookie(self._element.getElementsByTagName("cookies"))
        self._get_response_header(self._element.getElementsByTagName("responseHeader"))
        self._get_response_body(self._element.getElementsByTagName("responseData"))
        self._get_request_header(self._element.getElementsByTagName("requestHeader"))
        self._get_request_body(self._element.getElementsByTagName("queryString"))
        self._get_assertion(self._element.getElementsByTagName("assertionResult"))

    def _get_common(self, e):
        self.response_code = e.getAttribute('rc')
        self.response_msg = e.getAttribute('rm')
        self.testcase_name = e.getAttribute('tn')
        self.name = e.getAttribute('lb')
        self.t = e.getAttribute('t')
        self.success = True if e.getAttribute('s') == "true" else False
        self.ts = e.getAttribute('ts')
        self.dt = e.getAttribute('dt')

    def _get_url(self, es):
        try:
            if es is not None and es[0].childNodes[0] is not None:
                self.url = es[0].childNodes[0].data
        except Exception as e:
            pass

    def _get_cookie(self, es):
        try:
            if es is not None and es[0].childNodes[0] is not None:
                self.cookie = es[0].childNodes[0].data
        except Exception as e:
            pass

    def _get_request_method(self, es):
        try:
            if es is not None and es[0].childNodes[0] is not None:
                self.request_method = es[0].childNodes[0].data
        except Exception as e:
            pass

    def _get_response_header(self, es):
        try:
            if es is not None and es[0].childNodes[0] is not None:
                self.response_header = es[0].childNodes[0].data
        except Exception as e:
            pass

    def _get_response_body(self, es):
        try:
            if es is not None and es[0].childNodes[0] is not None:
                self.response_body = es[0].childNodes[0].data
        except Exception as e:
            pass

    def _get_request_header(self, es):
        try:
            if es is not None and es[0].childNodes[0] is not None:
                self.request_header = es[0].childNodes[0].data
        except Exception as e:
            pass

    def _get_request_body(self, es):
        try:
            if es is not None and es[0].childNodes[0] is not None:
                self.request_body = es[0].childNodes[0].data
        except Exception as e:
            pass

    def _get_assertion(self, es):
        try:
            if es is not None:
                if es[0].getElementsByTagName('name')[0] is not None:
                    self.assertion_name = es[0].getElementsByTagName('name')[0].childNodes[0].data
                    self.assertion_status = 'FAILED' if es[0].getElementsByTagName('failure')[0].childNodes[
                                                            0].data == 'true' else 'SUCCESS'
                    self.assertion_msg = es[0].getElementsByTagName('failureMessage')[0].childNodes[0].data
                    pass
        except Exception as e:
            pass

    def get_result(self):
        return {
            'testcase_name': self.testcase_name,
            'name': self.name,
            'url': self.url,
            'time': datetime.datetime.strftime(datetime.datetime.fromtimestamp(int(self.ts) / 1000),
                                               "%Y-%m-%d %H:%M:%S.%f"),  # self.time,
            't': self.t,
            'ts': self.ts,
            'dt': self.dt,
            'success': self.success,
            'request_header': self.request_header,
            'request_body': self.request_body,
            'cookie': self.cookie,
            'request_method': self.request_method,
            'response_header': self.response_header,
            'response_body': self.response_body,
            'response_code': self.response_code,
            'response_msg': self.response_msg,
            'assertion_name': self.assertion_name,
            'assertion_status': self.assertion_status,
            'assertion_msg': self.assertion_msg
        }


dbt = DBTool(db_config)
root = xml.dom.minidom.parse(xml_file)

# 生成list并转化为DF
rp_list = []
for i in root.getElementsByTagName("httpSample"):
    rp = RequestParser(i).get_result()
    rp_list.append(rp)
df_httpSample = pandas.DataFrame(rp_list)
df_httpSample['type'] = 'httpSample'

rp_list = []
for i in root.getElementsByTagName("sample"):
    rp = RequestParser(i).get_result()
    rp_list.append(rp)
df_sample = pandas.DataFrame(rp_list)
df_sample['type'] = 'sample'

df = pandas.concat([df_httpSample, df_sample])

flag = True
product_id = None
report_id = None

# 插入Report
r_module = dbt.s(**{'table': 'api_module', 'where': {'report_code': product_code}})
flag = True if len(r_module) > 0 else False

if flag:
    module_id = r_module[0]['id']
    report_id = dbt.i(**{
        'table': 'api_report',
        'value': {'module_id': module_id, 'date': date, 'env': env}
    })

# 插入Testcase
print(df.shape)
for testcase_name in df['testcase_name'].unique():
    df_request = df[df['testcase_name'] == testcase_name]
    testcase_id = dbt.i(**{'table': 'api_report_testcase', 'value': {'report_id': report_id, 'name': testcase_name}})
    for i, r in df_request.iterrows():
        # 插入Request
        dict_row = r.to_dict()
        value = {}
        for k in request_table_columns:
            value[k] = dict_row[k]
        value['testcase_id'] = testcase_id
        try:
            dbt.i(**{'table': 'api_report_testcase_request', 'value': value})
        except Exception as e:
            print("----------------")
            print(e)
            print(value)
            print("----------------")


