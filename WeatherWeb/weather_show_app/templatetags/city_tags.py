# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     city_tags   
   Description :  
   Author :        zhengyimiing 
   date：          2020/4/28 
-------------------------------------------------
   Change Activity:
                   2020/4/28  
-------------------------------------------------
"""

__author__ = 'zhengyimiing'

import datetime

from django import template

from weather_show_app.models import City, DateWeather

register = template.Library()


@register.inclusion_tag('weather_show_app/select.html')
def get_all_city():
    result = City.objects.all()
    return {'allcity': result, }


@register.inclusion_tag('weather_show_app/select_cityName.html')
def get_all_cityName():
    result = City.objects.all()
    return {'allcity': result, }


@register.filter(name='get_city_today_weather')
def get_city_today_weather(city_id):
    city = City.objects.get(id=city_id)
    now_date = datetime.datetime.now().date()
    today_weather = DateWeather.objects.get(city_id=city.id, date=now_date)
    return today_weather


@register.filter(name='get_max_temperature')
def get_max_temperature(today_weather):
    return today_weather.max_temperature


@register.filter(name='get_min_temperature')
def get_min_temperature(today_weather):
    return today_weather.min_temperature


@register.filter(name='get_state')
def get_state(today_weather):
    return today_weather.state
