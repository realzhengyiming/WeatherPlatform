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

from weather_show_app.models import City,DateWeather

register = template.Library()


@register.inclusion_tag('weather_show_app/select.html')
def get_all_city():
    result = City.objects.all()
    return {'allcity': result, }


@register.inclusion_tag('weather_show_app/select_cityName.html')
def get_all_cityName():
    result = City.objects.all()
    return {'allcity': result, }