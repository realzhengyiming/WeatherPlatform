# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy import Item, Field

from scrapy_djangoitem import DjangoItem
from weather_show_app.models import DateWeather, WeatherDetail, Favourite, City


class DateWeatherItem(DjangoItem):
    django_model = DateWeather
    city_name = Field()  # 这个是临时增加的，用来存城市名字，后面再填充到model中去
    extend_detail = Field()  # 这个是json的东西


class WeatherDetailItem(DjangoItem):
    django_model = WeatherDetail


class FavouriteItem(DjangoItem):
    django_model = Favourite


class CityItem(DjangoItem):
    django_model = City


