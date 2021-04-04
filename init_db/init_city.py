from xpinyin import Pinyin

from init_db.city_lists import CITY_LIST
from WeatherWeb.referer.backup.mysql_coon import mysql_conn
from WeatherWeb.referer.backup.new_city_code import city_and_code


def get_city_and_city_pinyin():
    city_list = []
    with open("city_pinyin_list.txt", "r", encoding="gbk") as file:
        for line in file.readlines():
            city, pinyin = line.split(" ")
            pinyin = pinyin.lower().rstrip()
            # print(city)
            # print(pinyin)
            city_list.append([city, pinyin])
    return city_list


def add_pinyin_to_new_city_code(city_list):
    for city, pinyin in city_list:
        for one_city in city_and_code:
            if one_city['name'] == city:
                one_city['pinyin'] = pinyin
    return city_and_code


def init_city_table_and_city_data():
    result = add_pinyin_to_new_city_code(get_city_and_city_pinyin())
    cursor = mysql_conn.cursor()
    p = Pinyin()
    print(result)
    for i in result:
        sql = ""
        if 'pinyin' in i:
            sql = f'insert into city (name,pinyin,code) value ("{i["name"]}","{i["pinyin"]}","{i["id"]}")'
        else:
            pinyin = p.get_pinyin(i["name"], "")
            sql = f'insert into city (name,pinyin,code) value ("{i["name"]}","{pinyin}","{i["id"]}")'
        try:
            cursor.execute(sql)
            mysql_conn.commit()

        except Exception as e:
            print(e)
            print(sql)

    mysql_conn.close()


def fill_city_type():  # is_direct_city
    cursor = mysql_conn.cursor()
    cursor.execute("select name from city;")
    read_all_city_name = cursor.fetchall()
    for city_name in read_all_city_name:

        for full_city_name in CITY_LIST:  # 有城市的城市列表
            if isinstance(city_name, tuple) and len(city_name) == 1:
                city_name = city_name[0]

            if full_city_name == city_name + "市":  # 对比，然后把地级市的城市列表填充好
                try:
                    fill_city_sql = '''update  City set direct_city_name = '{full_city_name}', is_city=1 where City.name='{city_name}' ; '''
                    sql = fill_city_sql.format(full_city_name=full_city_name, city_name=city_name)
                    print(sql)
                except Exception as e:
                    print(e)
                    print(f"城市全称叫做  -  {full_city_name} 城市简称叫做  -  {city_name}")
                    return
                try:
                    cursor.execute(sql)
                    mysql_conn.commit()

                except Exception as e:
                    print(e)
                    print(sql)

    mysql_conn.close()


if __name__ == '__main__':  # 写入城市代码和拼音
    init_city_table_and_city_data()
    fill_city_type()
