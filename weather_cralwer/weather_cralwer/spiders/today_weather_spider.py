import scrapy

from weather_cralwer.weather_cralwer.util import mysql_conn_instance


class ChinaWeatherSpider(scrapy.Spider):
    name = 'today_weather'
    allowed_domains = ['weather.com.cn']
    # start_urls = ['http://www.weather.com.cn/weather1d/101280601.shtml']
    head_url = "http://www.weather.com.cn/weather1d/{city_code}.shtml"

    def start_requests(self):
        all_city_list = mysql_conn_instance.query("select * from city ;")
        for city_dict in all_city_list:
            if "pinyin" in city_dict:
                city_code = city_dict['code']
                city_name = city_dict['name']
                city_pinyin = city_dict['pinyin']
                url = "http://www.weather.com.cn/weather1d/{city_code}.shtml".format(city_code=city_code)
                yield scrapy.Request(url=url, callback=self.parse, meta={"city_name": city_name,
                                                                         "city_pinyin": city_pinyin,
                                                                         "city_code": city_code})
            else:
                self.logger.info("非国内的跳过")

        pass

    def parse(self, response):
        # 抓取当天的天气
        pass
