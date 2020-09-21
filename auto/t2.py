import os

ADB_HOME = os.path.abspath("D:\Env\ADB")
#
# ADB_DEVICES = os.path.abspath(os.path.join(ADB_HOME, "adb devices"))
#
#
# print(os.system(ADB_DEVICES))


from appium import webdriver

import uiautomator2 as u2

d = u2.connect('127.0.0.1:62001')
print(d.info)

# d.app_start("com.tencent.wework")
# d.app_start("com.android.settings")
app = d.session("com.android.settings")

app.click(300,1300)
from time import sleep
sleep(1)
# d.press("back")
app.press("back")


import sys

# os.chdir("D:\Env\ADB")

# sys.path.append(ADB_HOME)
# sys.path.insert(0, r"D:\Env\ADB")
# print(sys.path)

# print(os.system("adb shell input keyevent KEYCODE_HOME"))
