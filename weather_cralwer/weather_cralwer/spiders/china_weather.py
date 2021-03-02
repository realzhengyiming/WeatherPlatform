import scrapy


class ChinaWeatherSpider(scrapy.Spider):
    name = 'china_weather'
    allowed_domains = ['weather.com.cn']
    start_urls = ['http://www.weather.com.cn/weather1d/101280601.shtml']

    def parse(self, response):
        # 抓取当天的天气
        pass
