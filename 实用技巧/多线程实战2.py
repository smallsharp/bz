import pymysql
import requests, time
from concurrent.futures import ProcessPoolExecutor


def data_handler(urls):
    sum = 0
    numlist = []
    for i in range(urls[0], urls[1]):
        # print(i)
        sum = sum + i
        numlist.append(i)
    # conn = pymysql.connect(host='localhost', user='root', password='root', database='db1', charset='utf8')
    # cursor = conn.cursor()
    # for i in range(urls[0], urls[1]):
    #     sql = 'insert into user3(uid,uname,email) values(%s,%s,concat(%s,"hello","@qq.com"));'
    #     res = cursor.execute(sql, [i, "root", i])
    #     conn.commit()
    # cursor.close()
    # conn.close()


def run():
    urls = [(1, 20000), (20001, 50000), (50001, 80000), (80001, 100000)]
    with ProcessPoolExecutor() as excute:
        ##ProcessPoolExecutor 提供的map函数，可以直接接受可迭代的参数，并且结果可以直接for循环取出
        excute.map(data_handler, urls)


if __name__ == '__main__':
    start_time = time.time()
    run()
    stop_time = time.time()
    print('插入1万条数据耗时 %s' % (stop_time - start_time))
