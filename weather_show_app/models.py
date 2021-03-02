from django.db import models


class Wind(models.Model):  # 风
    class Meta:
        db_table = 'Wind'

    wind_power = models.FloatField()  # 风力
    wind_direction = models.TextField()  # 风向


class Weather(models.Model):  # 天气的表
    class Meta:
        db_table = 'Weather'

    humidity = models.FloatField()  # 湿度
    state = models.TextField()  # 晴朗，多云，大风，台风，暴雨，暴雪，～之类的
    date = models.DateField()
    update_date = models.DateField(auto_now=True)

    max_temperature = models.FloatField()  # 最高温和最低温
    mini_temperature = models.FloatField()

    wind = models.OneToOneField(Wind, on_delete=models.CASCADE)
    city = models.CharField(max_length=40)
    extend_detail = models.TextField()  # 这个是json的东西


class City(models.Model):
    class Meta:
        db_table = 'City'

    city_name = models.CharField(max_length=50, unique=True)  # 城市名字
    city_pinyin = models.CharField(max_length=50, unique=True)  # 减少冗余的代价是时间代价
    city_code = models.CharField(max_length=20)

    # 对应中国天气网的url code http://www.weather.com.cn/weather/101080101.shtml

    def __str__(self):
        return f"{self.city_name} - {self.city_pinyin} {self.city_code}"
