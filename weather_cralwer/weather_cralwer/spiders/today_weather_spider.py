import datetime
import json
import time
from typing import List

import scrapy

from weather_cralwer.weather_cralwer.clean_util import temperature_process, aqi_process
from weather_cralwer.weather_cralwer.db_util import mysql_conn_instance  # todo 修好这个东西 找不到爬虫的问题
from weather_cralwer.weather_cralwer.items import DateWeatherItem, HourWeatherItem


class ChinaWeatherSpider(scrapy.Spider):
    name = 'today_weather'
    allowed_domains = ['weather.com.cn']

    head_url = "http://www.weather.com.cn/weather1d/{city_code}.shtml"

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

    def start_requests(self):
        all_city_list = mysql_conn_instance.query("select * from City order by  is_city desc,id;")

        # all_city_list = [{"name": "北京", "pinyin": "beijing", "code": '101010100'}]
        for city_dict in all_city_list:

            if "pinyin" in city_dict:
                city_code = city_dict['code']
                city_name = city_dict['name']
                city_pinyin = city_dict['pinyin']
                url = "http://www.weather.com.cn/weather1d/{city_code}.shtml".format(city_code=city_code)
                yield scrapy.Request(url=url, callback=self.parse,
                                     meta={"city_name": city_name,
                                           "city_pinyin": city_pinyin,
                                           "city_code": city_code})
            else:
                self.logger.info("非国内的跳过")

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
        future_date = (datetime.date.today() + datetime.timedelta(days=6)).strftime("%Y-%m-")  # 如果发现6天后是换月了

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

            fetch_day = temp_day[0].split("日")[0]
            date_pattern = future_date if int(fetch_day) <= 7 else now_date
            day_short_info_item['date'] = date_pattern + fetch_day  # 获得 日期的号 如果是月底那还是可以找到
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
        """处理得到有用信息保存数据文件"""
        all_script_text = response.xpath("//script/text()").getall()  # hour3data;  observe24h_data
        dressing_index = response.xpath('//*[@id="chuanyi"]/a/span/text()').extract_first()
        dressing_index_desc = response.xpath('//*[@id="chuanyi"]/a/p/text()').extract_first()  # 穿衣指数描述

        observe24h, hour3data = None, None
        for one in all_script_text:
            if one.find("var observe24h_data") != -1:
                observe24h = one  # 24小时天气数据
            elif one.find("var hour3data") != -1:
                hour3data = one  # 这个是7天天气概括数据

        today_24hours_weather = self.parse_24hour_data(observe24h)
        # 下面爬取7天的数据
        # hour3data

        city_name = response.meta.get("city_name")
        seven_days_weather_list = self.parse_7days_data(hour3data, city_name)
        today_weather = seven_days_weather_list[0]
        # 只能获得当天的穿衣指数，其他天得其他时候进行抓取。
        today_weather['dressing_index'] = '' if not dressing_index else dressing_index  # 穿衣指数
        today_weather['dressing_index_desc'] = "" if not dressing_index_desc else dressing_index_desc

        today_weather['extend_detail'] = today_24hours_weather

        # return today_weather_data, week_weather_data
        for day_weather_item in seven_days_weather_list:
            yield day_weather_item
