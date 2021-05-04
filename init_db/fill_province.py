# 用来填充 城市所属省份的
import json

import pandas as pd
import requests

from init_db.mysql_coon import mysql_conn

gaode = pd.read_excel("AMap_adcode_citycode_20210406.xlsx")


def find_province_by_city_code(city_code):
    city_code = str(city_code)
    for index, row in gaode.iterrows():
        name = row[0]
        code = row[1]

        if str(code) == city_code:
            return name
    return ""


def get_province_by_gaode(address):
    response = requests.get(
        f'https://restapi.amap.com/v3/geocode/geo?address={address}&output=json&key=4719e1d3f1bb1a6c237cd0659e0265bc'
    )
    dict_reponse = json.loads(response.text)
    province_name = ""
    if "geocodes" in dict_reponse:
        try:
            province_name = dict_reponse['geocodes'][0]['province']
        except Exception as e:
            print(e)

    return province_name


def get_location_by_gaode(address):
    response = requests.get(
        f'https://restapi.amap.com/v3/geocode/geo?address={address}&output=json&key=4719e1d3f1bb1a6c237cd0659e0265bc'
    )
    dict_reponse = json.loads(response.text)
    lat_lng_location = ""
    if "geocodes" in dict_reponse:
        try:
            lat_lng_location = dict_reponse['geocodes'][0]['location']
        except Exception as e:
            print(e)

    return lat_lng_location


def fill_province_main():
    cur = mysql_conn.cursor()  # 这一段是填充省份的
    select_city_name_sql = '''select name from City ;'''
    cur.execute(select_city_name_sql)
    citys = cur.fetchall()
    citys = [i[0] for i in citys]

    province_name = ''
    for city in citys:
        province_name = get_province_by_gaode(city)
        if not province_name:
            continue
        else:
            update_sql_pattern = '''update City set belong_province='{province_name}' where name = '{city}' '''.format(
                province_name=province_name,
                city=city
            )
            cur.execute(update_sql_pattern)
            print(city)
            print(cur.fetchall())
            mysql_conn.commit()

    print(province_name)
    print(citys)
    cur.close()
    print('创建数据库 py3_tstgr 成功！')


def fill_lat_lng_location():
    cur = mysql_conn.cursor()  # 这一段是填充省份的
    select_city_name_sql = '''select name from City ;'''
    cur.execute(select_city_name_sql)
    citys = cur.fetchall()
    citys = [i[0] for i in citys]

    location = ''
    for city in citys:
        location = get_location_by_gaode(city)
        if not location:
            continue
        else:
            update_sql_pattern = '''update City set location='{location}' where name = '{city}' '''.format(
                location=location,
                city=city
            )
            cur.execute(update_sql_pattern)
            print(city)
            print(cur.fetchall())
            mysql_conn.commit()

    print(location)
    print(citys)
    cur.close()
    print('创建数据库 py3_tstgr 成功！')


if __name__ == '__main__':
    fill_lat_lng_location()  # 填充location
    # 查找，插入
