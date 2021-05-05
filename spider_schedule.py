# 写一个简单的定时任务，让爬虫自动启动吧
import datetime
import subprocess
import time

import schedule
from scrapy.cmdline import execute


def spider_schedule_job():
    # 启动爬虫呢
    print(f"爬虫已启动，启动时间{datetime.datetime.now()}")
    # execute("scrapy crawl today_weather".split())  # 这样好像是不行的
    cmdline = '''
    cd /root/new_tmp_job/WeatherPlatform && conda activate weather && scrapy crawl today_weather
    '''
    cmdline = "date"
    result = subprocess.Popen(cmdline)
    # system(cmdline)
    print(result)


def execute_spider():  # shell执行的时候提前 使用指定路径下（虚拟环境下的python）
    execute('scrapy crawl today_weather'.split(" "))


if __name__ == '__main__':
    SCHEDULE_TIME = "01:00"  # 每天这个时候爬虫进行更新
    schedule.every().day.at(SCHEDULE_TIME).do(execute_spider)
    print(f"开始执行，现在时间是 {datetime.datetime.now()}")
    while True:
        schedule.run_pending()
        time.sleep(1)
    # execute_spider()
