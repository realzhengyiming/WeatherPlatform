# -*- coding: utf-8 -*-

from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from weather_show_app import views

app_name = "weather_show_app"  # 这儿需要设置这个来分辨不同的app

urlpatterns = [
    path("index/", views.index, name="index"),
]
