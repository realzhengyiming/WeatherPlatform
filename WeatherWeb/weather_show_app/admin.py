from django.contrib import admin

from weather_show_app.models import City
from weather_show_app.models import DateWeather
from weather_show_app.models import Favourite


class ExtendCity(admin.ModelAdmin):
    search_fields = ("name", "pinyin", "code")  # 搜索字段
    list_display = ('id', 'name', 'pinyin', 'code',)


class ExtendDateWeather(admin.ModelAdmin):
    search_fields = ("date",)  # 搜索字段
    list_display = (
        "id", 'city', "state", "date",
        "max_temperature", "min_temperature",
        "update_date", "humidity", "wind_power", "wind_direction")

    def detail_weather(self, obj):  # 好方便啊
        num = len(obj.city.all())
        return str(num)


class ExtendFav(admin.ModelAdmin):
    list_display = (
        "user",
        'fav_city_number',
    )

    def fav_city_number(self, obj):  # 好方便啊
        num = len(obj.city.all())
        return str(num)

    def fav_city_list(self, obj):
        string = ";".join(obj.city.all())
        return string


admin.site.register(DateWeather, ExtendDateWeather)
admin.site.register(City, ExtendCity)
admin.site.register(Favourite, ExtendFav)
