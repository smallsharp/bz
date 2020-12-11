import asyncio
import requests
import time
from multiprocessing.dummy import Pool

now = lambda: time.time()


def do_some_work(x):
    print('Waiting: ', x)
    r = requests.get('http://www.baidu.com?key={}'.format(x))
    return 'reposne code is {}'.format(r.status_code)


start = now()

pool = Pool(6)
results = pool.map(do_some_work, range(1000))
pool.close()
pool.join()
# print(results)

print('TIME: ', now() - start)
