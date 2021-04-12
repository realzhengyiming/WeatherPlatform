import datetime
import json
import time
from typing import List

import scrapy

from weather_cralwer.weather_cralwer.clean_util import temperature_process, aqi_process
from weather_cralwer.weather_cralwer.db_util import mysql_conn_instance  # todo 修好这个东西 找不到爬虫的问题
from weather_cralwer.weather_cralwer.items import DateWeatherItem, HourWeatherItem


class ChinaOneWeatherSpider(scrapy.Spider):
    name = 'baidu'
    allowed_domains = ['*']

    start_urls = [
        "http://weathernew.pae.baidu.com/weathernew/pc?query=%E6%83%A0%E5%B7%9E%E5%A4%A9%E6%B0%94&srcid=4982&city_name=%E6%B7%B1%E5%9C%B3&province_name=%E5%B9%BF%E4%B8%9C"
]
    custom_settings = {

        'DOWNLOADER_MIDDLEWARES': {
            'weather_cralwer.weather_cralwer.middlewares.ChangeUserAgentMiddleware': 1,
        },
        'DOWNLOAD_DELAY': 1,
        'ITEM_PIPELINES': {
            'weather_cralwer.weather_cralwer.pipelines.DateWeatherPipeline': 2,
        },
        # "DOWNLOAD_DELAY": 0.5,

    }

    def __init__(self, city_id=None, *args, **kwargs):
        super(ChinaOneWeatherSpider, self).__init__(*args, **kwargs)
        self.city_id = city_id

    def parse_24hour_data(self, script_string: str):
        script_string = script_string[script_string.index('=') + 1:-2]  # 移除改var data=将其变为json数据
        waather_json = json.loads(script_string)
        today_hour_weather = waather_json['od']['od2']  # 找到当天的数据
        today_24hours_weather = []  # 存放当天的数据
        count = 0
        nowdate = time.strftime('%Y-%m-%d', time.localtime(time.time()))  # todo 这儿是做什么的呢。这儿是修改成多表查询，然后才是显示对图进行分析工作。

        # now_date = datetime.datetime.now().strftime("%Y-%m-")
        for i in today_hour_weather:
            if count <= 23:
                hour_weather = HourWeatherItem()
                hour_weather['hour'] = i['od21']  # 添加时间
                hour_weather['temperature'] = i['od22']  # 添加当前时刻温度
                hour_weather['wind_direction'] = i['od24']  # 添加当前时刻风力方向
                hour_weather['wind_power'] = i['od25']  # 添加当前时刻风级
                hour_weather["precipitation"] = i['od26']  # 添加当前时刻降水量
                hour_weather["relative_humidity"] = i['od27']  # 添加当前时刻相对湿度
                hour_weather["AQI"] = aqi_process(i['od28'])  # 添加当前时刻控制质量
                hour_weather["belong_to_date"] = nowdate  # 添加当前时刻控制质量

                today_24hours_weather.append(hour_weather)
            count = count + 1

        return today_24hours_weather

    def parse_7days_data(self, html: str, city_name: str) -> List[DateWeatherItem]:

        now_date = datetime.datetime.now().strftime('%Y-%m-')

        html = html.replace("\n", "")
        html = html[html.find("=") + 1:]
        html_json = json.loads(html)
        week_date_weather = html_json.get("7d")
        week_date_weather_list = []
        for day in week_date_weather:
            day_short_info_item = DateWeatherItem()
            temp_temperature_list = [t.split(",")[3] for t in day]
            min_temperature = min(temp_temperature_list)
            max_temperature = max(temp_temperature_list)
            temp_day = day[0].split(",")
            day_short_info_item['date'] = now_date + temp_day[0].split("日")[0]  # 获得 日期的号
            day_short_info_item['state'] = temp_day[2]
            day_short_info_item['humidity'] = 0.0
            day_short_info_item['city_name'] = city_name  # 这个是城市名，还需要改成真正的城市对象才可以
            day_short_info_item['max_temperature'] = temperature_process(max_temperature)
            day_short_info_item['min_temperature'] = temperature_process(min_temperature)
            day_short_info_item['wind_direction'] = temp_day[4]
            day_short_info_item['wind_power'] = temp_day[5]

            week_date_weather_list.append(day_short_info_item)  # 里面这个是item

        return week_date_weather_list

    def parse(self, response):
        # print(response.text)
        """处理得到有用信息保存数据文件"""
        status = response.xpath('//div[@class="zhishu-box"]//text()').get_all()  # hour3data;  observe24h_data
        print("----------")
        print(status)

