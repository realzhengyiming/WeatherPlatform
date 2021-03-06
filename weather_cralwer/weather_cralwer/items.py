# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy import Item, Field


class WeatherItem(Item):
    humidity = Field()  # 湿度
    AQI = Field()  # 空气质量
    state = Field()  # 晴朗，多云，大风，台风，暴雨，暴雪，～之类的
    date = Field()
    update_date = Field()

    max_temperature = Field()  # 最高温和最低温
    mini_temperature = Field()

    wind_direction = Field()
    wind_power = Field()

    city = Field()
    extend_detail = Field()  # 这个是json的东西,dumps 放置七天的天气的东西
