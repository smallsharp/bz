import pymysql
import threading
import re
import time
from queue import Queue
from DBUtils.PooledDB import PooledDB


class ThreadInsert(object):

    def __init__(self):
        start_time = time.time()
        self.pool = self.mysql_connection()
        self.data = self.getData()
        self.mysql_delete()
        self.task()
        print("========= 数据插入,共耗时:{}'s =========".format(round(time.time() - start_time, 3)))

    # 数据库连接
    def mysql_connection(self):
        print('connect')
        # maxconnections = 15  # 最大连接数
        # pool = PooledDB(
        #     pymysql,
        #     maxconnections,
        #     host='localhost',
        #     user='root',
        #     port=3306,
        #     passwd='root',
        #     db='db1',
        #     use_unicode=True)
        # return pool

    # 从本地的文件中读取数据
    def getData(self):
        st = time.time()
        with open("D:\\logs\\user2.txt", "rb") as f:
            data = []
            for line in f:
                line = re.sub("\s", "", str(line, encoding="utf-8"))
                line = tuple(line[1:-1].split("\"\""))
                data.append(line)
        n = 1000  # 按每1000行数据为最小单位拆分成嵌套列表，可以根据实际情况拆分
        result = [data[i:i + n] for i in range(0, len(data), n)]
        print("共获取{}组数据,每组{}个元素.==>> 耗时:{}'s".format(len(result), n, round(time.time() - st, 3)))
        return result

    # 数据库回滚
    def mysql_delete(self):
        st = time.time()
        con = self.pool.connection()
        cur = con.cursor()
        sql = "TRUNCATE TABLE user5"
        cur.execute(sql)
        con.commit()
        cur.close()
        con.close()
        print("清空原数据.==>> 耗时:{}'s".format(round(time.time() - st, 3)))

    # 数据插入
    def mysql_insert(self, *args):
        con = self.pool.connection()
        cur = con.cursor()
        sql = "INSERT INTO user5(uid, uname, email) VALUES(%s, %s, %s)"
        try:
            cur.executemany(sql, *args)
            con.commit()
        except Exception as e:
            con.rollback()  # 事务回滚
            print('SQL执行有误,原因:', e)
        finally:
            cur.close()
            con.close()

    # 开启多线程任务
    def task(self):
        # 设定最大队列数和线程数
        q = Queue(maxsize=10)
        st = time.time()
        while self.data:
            content = self.data.pop()
            t = threading.Thread(target=self.mysql_insert, args=(content,))
            q.put(t)
            if (q.full() == True) or (len(self.data)) == 0:
                thread_list = []
                while q.empty() == False:
                    t = q.get()
                    thread_list.append(t)
                    t.start()
                for t in thread_list:
                    t.join()
        print("数据插入完成.==>> 耗时:{}'s".format(round(time.time() - st, 3)))


if __name__ == '__main__':
    ThreadInsert()
