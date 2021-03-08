import json

import scrapy
from bs4 import BeautifulSoup

from weather_cralwer.weather_cralwer.db_util import mysql_conn_instance  # todo 修好这个东西 找不到爬虫的问题
from weather_cralwer.weather_cralwer.items import WeatherItem


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
            'weather_cralwer.weather_cralwer.pipelines.MysqlPipline': 2,
        }

    }

    def start_requests(self):
        all_city_list = mysql_conn_instance.query("select * from city ;")

        # all_city_list = [{"name": "北京", "pinyin": "beijing", "code": '101010100'}]
        for city_dict in all_city_list[:2]:
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

        pass

    def parse(self, response):
        """处理得到有用信息保存数据文件"""
        all_script_text = response.xpath("//script/text()").getall()  # hour3data;  observe24h_data
        observe24h, hour3data = None, None
        for one in all_script_text:
            if one.find("var observe24h_data") != -1:
                observe24h = one
            elif one.find("var hour3data") != -1:
                hour3data = one

        script_string = observe24h
        script_string = script_string[script_string.index('=') + 1:-2]  # 移除改var data=将其变为json数据
        waather_json = json.loads(script_string)
        today_hour_weather = waather_json['od']['od2']  # 找到当天的数据
        today_weather_data = []  # 存放当天的数据
        weather_item = WeatherItem()
        count = 0
        for i in today_hour_weather:
            day_hour_list = []
            if count <= 23:
                day_hour_list.append(i['od21'])  # 添加时间
                day_hour_list.append(i['od22'])  # 添加当前时刻温度
                day_hour_list.append(i['od24'])  # 添加当前时刻风力方向
                day_hour_list.append(i['od25'])  # 添加当前时刻风级
                day_hour_list.append(i['od26'])  # 添加当前时刻降水量
                day_hour_list.append(i['od27'])  # 添加当前时刻相对湿度
                day_hour_list.append(i['od28'])  # 添加当前时刻控制质量
                today_weather_data.append(day_hour_list)
            count = count + 1

        # today data
        weather_item['extend_detail'] = today_hour_weather

        # 下面爬取7天的数据
        # ul = data.find('ul')  # 找到所有的ul标签
        # li = ul.find_all('li')  # 找到左右的li标签
        # i = 0  # 控制爬取的天数

        # 直接抓取所有的数据  TODO ，收藏夹增加城市收藏;
        # TODO (2-7 00:40 还有一个问题就是那个 7天的列表怎么获得呢？

        all_li = response.xpath("//div[@id='7d']/ul/li").getall()
        # return today_weather_data, week_weather_data

        yield weather_item

    # def parse(self, response):
    #     pass
