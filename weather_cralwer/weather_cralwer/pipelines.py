from twisted.enterprise import adbapi
from pymysql import cursors

from weather_cralwer.weather_cralwer.db_util import mysql_conn_instance
from weather_cralwer.weather_cralwer.items import WeatherItem
from weather_show_app.models import City  # 改成才可以，什么鬼》》。。 todo

class MysqlPipline:

    @staticmethod
    def get_insert_weather_sql(item):
        columns_list = ",".join([x for x in item.keys()])
        value_list = ",".join([f'"{x}"' for x in item.values()])
        wind_sql = f"insert into Weather ({columns_list}) values ({value_list})"
        return wind_sql

    def process_item(self, item, spider):
        if isinstance(item, WeatherItem):
            wind_sql = self.get_insert_weather_sql(item)
            mysql_conn_instance.query(wind_sql)



if __name__ == '__main__':
    any = {"name": "zhengyiming", "gender": "man"}
    columns = ",".join([x for x in any.keys()])
    values = ",".join([f'"{x}"' for x in any.values()])
    sql = f"insert into test_table ({columns}) values ({values})"
    print(sql)
