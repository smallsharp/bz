# -*- coding:utf-8 -*-
import time
from pymysql import *


# 装饰器，计算插入10000条数据需要的时间
def timer(func):
    def decor(*args):
        start_time = time.time()
        func(*args)
        end_time = time.time()
        d_time = end_time - start_time
        print("这次插入10000条数据耗时 : ", d_time)

    return decor


@timer
def add_test_users():
    sum = 0
    numlist = []
    for i in range(1000000):
        sum = sum + i
        numlist.append(i)
    # conn = connect(host='localhost', user='root', password='root', database='db1', charset='utf8')
    # cs = conn.cursor()
    # for num in range(0, 10000):
    #     try:
    #         sql = "insert into user1(uid,uname,email) values(%s,%s,%s);"
    #         params = (num, "zcy", "543325130@qq.com")
    #         cs.execute(sql, params)
    #     except Exception as e:
    #         return
    # conn.commit()
    # cs.close()
    # conn.close()
    print(sum)


if __name__ == '__main__':
    add_test_users()
