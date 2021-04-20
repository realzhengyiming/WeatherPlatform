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

from weather_show_app.constant import walk_out_guide_dict
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


# 出行指南
@register.filter(name='state_to_outdoor_guide')
def state_to_outdoor_guide(state):
    if not state:
        return "无推荐"
    return walk_out_guide_dict[state]


# 穿衣指数
@register.filter(name='wear_clothing_guide')
def wear_clothing_guide(today_weather):
    mean_temperature = (today_weather.min_temperature + today_weather.max_temperature) / 2
    if mean_temperature <= 0:
        return "棉衣、冬大衣、皮夹克、厚呢外套、呢帽、手套、羽绒服、裘皮大衣"
    elif 0 < mean_temperature <= 5:
        return '厚呢外套、呢帽、手套、羽绒服、皮袄'
    elif 5 < mean_temperature <= 10:
        return "棉衣、冬大衣"
    elif 10 < mean_temperature <= 20:
        return "风衣、大衣"
    elif 20 < mean_temperature <= 25:
        return '棉麻面料的衬衫、薄长裙、薄T恤'
    elif 25 < mean_temperature < 30:
        return '轻棉织物制作的短衣、短裙、薄短裙、短裤'
    else:
        return "没有推荐"


# 穿衣指数
@register.filter(name='clean_mydate')
def clean_mydate(date_str):
    date_str = str(date_str)
    date_str = date_str.replace("年", "-").replace("月", "-").replace("日", "-")
    return date_str
