from multiprocessing import Pool


def f(x):
    # print(x * 2)
    return x * 2


if __name__ == '__main__':
    import time

    print('start')
    start = time.time()
    with Pool() as p:
        p.map(f, (i for i in range(1, 1000000)))

    end = time.time()
    print(end - start)
