from django.contrib import admin
from weather_show_app.models import Weather
from weather_show_app.models import Wind, City


class ExtendWind(admin.ModelAdmin):
    list_display = ('id', 'wind_power', 'wind_direction')
    search_fields = ('win_power', "wind_direction")


class ExtendCity(admin.ModelAdmin):
    search_fields = ("name", "pinyin", "code")  # 搜索字段
    list_display = ('id', 'name', 'pinyin', 'code',)


class ExtendWeather(admin.ModelAdmin):
    list_display = (
        "id", 'city', "state", "date",
        "max_temperature", "mini_temperature",
        "update_date", "humidity", "wind")

    def fav_house_number(self, obj):  # 好方便啊
        num = len(obj.fav_houses.all())
        return str(num)


admin.site.register(Weather, ExtendWeather)
admin.site.register(City, ExtendCity)
admin.site.register(Wind, ExtendWind)

