import scrapy

from weather_cralwer.weather_cralwer.db_util import mysql_conn_instance  # todo 修好这个东西 找不到爬虫的问题


class ChinaWeatherSpider(scrapy.Spider):
    name = 'today_weather'
    allowed_domains = ['weather.com.cn']
    # start_urls = ['http://www.weather.com.cn/weather1d/101280601.shtml']
    head_url = "http://www.weather.com.cn/weather1d/{city_code}.shtml"

    def start_requests(self):
        all_city_list = mysql_conn_instance.query("select * from city ;")

        # all_city_list = [{"name": "北京", "pinyin": "beijing", "code": '101010100'}]
        for city_dict in all_city_list[:2]:
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
        result = response.xpath("//script/text()")
        # 抓取当天的天气
        print(result)
        print()
