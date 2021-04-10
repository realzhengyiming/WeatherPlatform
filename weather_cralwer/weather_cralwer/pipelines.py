import django

from weather_cralwer.weather_cralwer.items import DateWeather, DateWeatherItem
from weather_show_app.models import City, HourWeather  # 改成才可以，什么鬼》》。。 todo


class DateWeatherPipeline:
    def insert_hour_weather(self, spider, item,weather):  # check hour weather exist
        belong_to_date = item['belong_to_date']
        hour = item['hour']

        try:
            hour_weather = HourWeather.objects.filter(Weather=weather ,hour=hour, belong_to_date=belong_to_date)
            if len(hour_weather) == 0:  # todo 这儿还是有问题的好
                item.save(commit=True)
                spider.logger.info(f"保存成功:{item}")
                # hour_weather = hour_weather[0]
                # hour_weather.save(commit=True)
            else:
                spider.logger.info(f"{hour_weather}已经存在")
        except Exception as e:
            spider.logger.info(e)

    def update_date_weather(self, spider, item):
        date = item['date']
        city_name = item['city_name']
        # 查询到城市id
        city_result = City.objects.filter(name=city_name)
        if not city_result:
            spider.logger.error("不存在这个城市!")
            return item
        else:
            city = city_result[0]
            data_weather = DateWeather.objects.get(city=city.id, date=date)
            if 'dressing_index' in item.keys():
                data_weather.dressing_index = item['dressing_index']
                data_weather.save()

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

            city_id = city.id

            try:
                item.save(commit=True)  # 保存后就有id了吗
            except django.db.utils.IntegrityError:
                self.update_date_weather(spider, item)
                spider.logger.info(f"更新成功！{item}")

            if "extend_detail" in item.keys() and not not item['extend_detail']:  # 如果有细节，把24小时细节补上
                today_24hours_weather_list = item['extend_detail']
                today_weather_object_list = DateWeather.objects.filter(date=date, city_id=city_id)
                if not today_weather_object_list:
                    spider.logger.info(f"{city} {date} 的天气找不到！")
                    return item
                else:
                    today_weather = today_weather_object_list[0]
                    for hour_weather in today_24hours_weather_list:
                        hour_weather['Weather'] = today_weather
                        self.insert_hour_weather(spider, hour_weather,today_weather)
# if __name__ == '__main__':
#     any = {"name": "zhengyiming", "gender": "man"}
#     columns = ",".join([x for x in any.keys()])
#     values = ",".join([f'"{x}"' for x in any.values()])
#     sql = f"insert into test_table ({columns}) values ({values})"
#     print(sql)
