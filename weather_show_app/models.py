from django.db import models


class Weather(models.Model):  # 天气的表
    class Meta:
        db_table = 'Weather'

    humidity = models.FloatField()  # 湿度
    AQI = models.IntegerField(blank=True)  # 空气质量
    state = models.TextField()  # 晴朗，多云，大风，台风，暴雨，暴雪，～之类的
    date = models.DateField()
    update_date = models.DateField(auto_now=True)

    max_temperature = models.FloatField()  # 最高温和最低温
    mini_temperature = models.FloatField()

    wind_power = models.FloatField(blank=True,default=0.0)  # 风力
    wind_direction = models.TextField(blank=True)  # 风向

    city = models.CharField(max_length=40)
    extend_detail = models.TextField()  # 这个是json的东西


class City(models.Model):
    class Meta:
        db_table = 'City'

    name = models.CharField(max_length=50, unique=True)  # 城市名字
    pinyin = models.CharField(max_length=100, blank=True)  # 减少冗余的代价是时间代价
    code = models.CharField(max_length=20, blank=True)

    # 对应中国天气网的url code http://www.weather.com.cn/weather/101080101.shtml

    def __str__(self):
        return f"{self.name} - {self.pinyin} {self.code}"


class Favourite(models.Model):  # 收藏夹
    fav_city = models.OneToOneField(City, unique=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.fav_city.city_name)
