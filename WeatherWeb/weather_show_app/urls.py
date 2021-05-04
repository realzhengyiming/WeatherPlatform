# -*- coding: utf-8 -*-

from django.contrib.auth import views as auth_views
from django.urls import path

from weather_show_app import views, drawviews

app_name = "weather_show_app"  # 这儿需要设置这个来分辨不同的app

urlpatterns = [  # todo 记得要删除这些坏东西/
    path("index/", views.index, name="index"),
    path("", views.index, name='index'),
    path("loginpage/", views.loginPage, name="user_login"),
    path('logout/', views.userLogout, name="user_logout"),
    path("register/", views.register, name="user_register"),
    path("psssword-change/",
         auth_views.PasswordChangeView.as_view(template_name='weather_show_app/password_change_form.html',
                                               success_url='/index/'), name='password_change'),

    path('password-change-done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name="/registration/password-change-done.html"), name="password_change_done"),

    path("detail/", views.detailView, name="detail"),
    path("detaillist/", views.detaillist, name="detaillist"),
    path("today_weather/", views.today_weather_page, name="today_weather"),
    path("favourite/", views.favouriteHandler.as_view(), name="Favourite"),

    # 可视化的接口
    path('bar/', drawviews.ChartView.as_view(), name='bar'),
    path("pie/", drawviews.PieView.as_view(), name="pie"),
    path('timeline/', drawviews.timeLineView.as_view(), name="timeline"),
    path("drawmap/", drawviews.drawMap.as_view(), name="drawMap"),
    path("get_today_aqi_line/", drawviews.get_today_aqi_bar.as_view(), name="get_today_aqi_line"),
    path("get_relative_humidity/", drawviews.get_today_average_humity.as_view(), name="draw_relative_humidity"),
    path("get_hostReplay/", drawviews.wind_graph.as_view(), name="get_hostReplay"),
    path("today_temperature_line/", drawviews.today_temperature_detail_line.as_view(), name="today_temperature_line"),
    # 这个改成了当踢的天气折线图

]
