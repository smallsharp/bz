from multiprocessing.dummy import Pool

import time


def download(item):
    print("正在下载:{}".format(item))
    return item


if __name__ == "__main__":
    start = time.time()
    id_list = range(0, 20000)
    # 实例化线程池
    pool = Pool(4)

    # Apply `func` to each element in `iterable`, collecting the results in a list that is returned.
    result = pool.map(download, id_list)
    pool.close()
    pool.join()
    end = time.time()
    print(result)
    print("共耗时：", end - start)
