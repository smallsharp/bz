def encode(s):
    return ' '.join([bin(ord(c)).replace('0b', '') for c in s])


def decode(s):
    return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])


# print(encode('x'))
# print(ord('x'))  # 120
# print(ord('A'))  # 120
# print(ord('B'))  # 120
# print(bin(120))

import time
from datetime import datetime

print(int(time.time() * 1000))

print()
