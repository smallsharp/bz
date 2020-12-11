import asyncio
import requests
import time

now = lambda: time.time()


async def do_some_work(x):
    print('Waiting: ', x)
    r = requests.get('http://www.baidu.com?key={}'.format(x))
    return 'reposne code is {}'.format(r.status_code)


tasks = []
for i in range(1, 1000):
    coroutine = do_some_work(i)
    tasks.append(asyncio.ensure_future(coroutine))

start = now()

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*tasks))

for task in tasks:
    print('Task ret: ', task.result())

print('TIME: ', now() - start)
