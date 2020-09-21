from gevent import monkey;

monkey.patch_all()
import gevent
import time
from DBUtils.PooledDB import PooledDB


def data_handler(s, e):
    sum = 0
    numlist = []
    for i in range(s, e):
        # print(i)
        sum = sum + i
        numlist.append(i)


if __name__ == '__main__':
    start_time = time.time()

    gevent.joinall([
        gevent.spawn(data_handler, 1, 20000),
        gevent.spawn(data_handler, 20001, 50000),
        gevent.spawn(data_handler, 50001, 80000),
        gevent.spawn(data_handler, 80001, 100001),
    ])
    stop_time = time.time()
    print('本次耗时 %s' % (stop_time - start_time))
