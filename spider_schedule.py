# 写一个简单的定时任务，让爬虫自动启动吧

from scrapy.cmdline import execute
import schedule
import time
import datetime


def spider_schedule_job():
    # 启动爬虫呢
    print(f"爬虫已启动，启动时间{datetime.datetime.now()}")
    execute("scrapy crawl today_weather".split())


if __name__ == '__main__':
    SCHEDULE_TIME = "00:10"
    schedule.every().day.at(SCHEDULE_TIME).do(spider_schedule_job)
    print(f"开始执行，现在时间是 {datetime.datetime.now()}")
    while True:
        schedule.run_pending()
        time.sleep(1)
