import django
from twisted.enterprise import adbapi
from pymysql import cursors

from weather_cralwer.weather_cralwer.db_util import mysql_conn_instance
from weather_cralwer.weather_cralwer.items import DateWeather, WeatherDetail, CityItem, FavouriteItem, DateWeatherItem
from weather_show_app.models import City  # 改成才可以，什么鬼》》。。 todo


# class MysqlPipline:
#
#     @staticmethod
#     def get_insert_weather_sql(item):
#         columns_list = ",".join([x for x in item.keys()])
#         value_list = ",".join([f'"{x}"' for x in item.values()])
#         wind_sql = f"insert into Weather ({columns_list}) values ({value_list})"
#         return wind_sql
#
#     def process_item(self, item, spider):
#         if isinstance(item, DateWeather):
#             wind_sql = self.get_insert_weather_sql(item)
#             mysql_conn_instance.query(wind_sql)


class DateWeatherPipeline:
    def process_item(self, item, spider):
        if isinstance(item, DateWeatherItem):
            # 先保存多的数量的对象，然后在把多的数量的对象存进来保存少的对象
            city_name = item["city_name"]
            date = item['date']
            city_list = City.objects.filter(name=city_name)

            if not city_list:
                spider.logger.info(f"city {city_name} 找不到！")
                return item
            else:
                city = city_list[0]
                item["city"] = city

            try:
                item.save(commit=True)  # 保存后就有id了吗
            except django.db.utils.IntegrityError:
                spider.logger.info("已经有了这天的数据")

            if "extend_detail" in item.keys() and not not item['extend_detail']:  # 如果有细节，把24小时细节补上
                today_24hours_weather_list = item['extend_detail']
                today_weather_object_list = DateWeather.objects.filter(date=date)
                if not today_weather_object_list:
                    spider.logger.info(f"{city} {date} 的天气找不到！")
                    return item
                else:
                    today_weather = today_weather_object_list[0]
                    for hour_weather in today_24hours_weather_list:
                        hour_weather['Weather'] = today_weather
                        hour_weather.save(commit=True)

# if __name__ == '__main__':
#     any = {"name": "zhengyiming", "gender": "man"}
#     columns = ",".join([x for x in any.keys()])
#     values = ",".join([f'"{x}"' for x in any.values()])
#     sql = f"insert into test_table ({columns}) values ({values})"
#     print(sql)
