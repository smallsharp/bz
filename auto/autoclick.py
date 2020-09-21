# coding=utf-8
import uiautomator2 as u2
import requests, schedule, sys
from time import sleep


def punch_in():
    # 连接设备
    d = u2.connect('127.0.0.1:62001')
    # print(d.info)
    print(d.app_info("com.tencent.wework"))

    d.app_start("com.tencent.wework")  # 启动应用
    d.xpath("工作台").click(timeout=20)  # 点击
    d.xpath("eHR Portal").click()
    d.xpath("考勤打卡").click()
    d.xpath("考勤打卡").click(timeout=20)
    if d.xpath("打卡成功").wait():
        sys.exit()


def main():
    # schedule.every().day.at('18:03').do(punch_in)
    schedule.every(10).seconds.do(punch_in)
    while True:
        schedule.run_pending()
        sleep(5)
        print('running')


if __name__ == '__main__':
    main()
