from django.conf.urls import url

from . import views, graph_api_view

# 上面是api 的映射，下面是页面的url的映射，采用前后端分离的操作进行开发。
urlpatterns = [
                  url(r'^bar/$', graph_api_view.BarView.as_view(), name='demo'),
                  url(r'^geo/$', graph_api_view.GeoView.as_view(), name="geo"),
              ] + [
                  url(r'^index/$', views.IndexView, name='demo'),
              ]
