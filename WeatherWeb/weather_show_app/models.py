from django.contrib.auth.models import User
from django.db import models


class DateWeather(models.Model):  # 天气概括表
    class Meta:
        db_table = 'DateWeather'
        unique_together = (("date", "city"),)

    humidity = models.FloatField()  # 湿度
    state = models.TextField()  # 晴朗，多云，大风，台风，暴雨，暴雪，～之类的
    date = models.DateField()
    update_date = models.DateField(auto_now=True)

    max_temperature = models.FloatField()  # 最高温和最低温
    min_temperature = models.FloatField()

    wind_power = models.TextField(blank=True, default="")  # 风力
    wind_direction = models.TextField(blank=True)  # 风向

    city = models.ForeignKey("City", related_name="City", on_delete=models.CASCADE)  # 这个是删除操作
    # extend_detail = models.TextField(blank=True)  # 这个是json的东西


class WeatherDetail(models.Model):
    class Meta:
        db_table = 'WeatherDetail'

    Weather = models.ForeignKey("DateWeather", on_delete=models.CASCADE, related_name='DateWeather')

    hour = models.IntegerField()
    temperature = models.FloatField()  # 最高温和最低温
    wind_power = models.FloatField(blank=True, default=0.0)  # 风力
    wind_direction = models.TextField(blank=True)  # 风向
    precipitation = models.FloatField()
    relative_humidity = models.IntegerField()
    AQI = models.IntegerField(blank=True, default=0)  # 空气质量


class City(models.Model):
    class Meta:
        db_table = 'City'

    name = models.CharField(max_length=50, unique=True)  # 城市名字
    pinyin = models.CharField(max_length=100, blank=True)  # 减少冗余的代价是时间代价
    code = models.CharField(max_length=20, blank=True)

    # 对应中国天气网的url code http://www.weather.com.cn/weather/101080101.shtml

    def __str__(self):
        return f"{self.name}"


class Favourite(models.Model):  # 收藏夹
    class Meta:
        db_table = 'Favourite'

    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    city = models.ManyToManyField('City', related_name="fav_city")

    # def __str__(self):
    #     return str(self.city.name)
