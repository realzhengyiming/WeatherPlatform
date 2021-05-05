# 写一个简单的定时任务，让爬虫自动启动吧
from os import system
import schedule
import time
import datetime
import subprocess
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

def execute_spider():
    execute('scrapy crawl today_weather'.split(" "))

if __name__ == '__main__':
    # SCHEDULE_TIME = "10:14"
    # schedule.every().day.at(SCHEDULE_TIME).do(spider_schedule_job)
    # print(f"开始执行，现在时间是 {datetime.datetime.now()}")
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    spider_schedule_job()
