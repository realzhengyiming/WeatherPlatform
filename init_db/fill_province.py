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


if __name__ == '__main__':

    cur = mysql_conn.cursor()
    select_city_name_sql = '''select name from City ;'''
    cur.execute(select_city_name_sql)
    citys = cur.fetchall()
    citys = [i[0] for i in citys]

    province_name = ''
    for city in citys:
        # city_name = row[0]
        # city_code = row[1]
        province_name = get_province_by_gaode(city)
        # if city_name.find(city) != -1:
        #     city_code = str(city_code)[:2] + "0000"
        #     province_name = find_province_by_city_code(city_code)
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
            # cur.commit()
            mysql_conn.commit()

    print(province_name)

    # 这儿执行的是 插入数据库的东西
    # for city in citys:
    #
    # update_sql_pattern = '''update City set belong_province={province} where name = {city_name}'''
    #     cur.execute()
    #     cur.commit()

    print(citys)
    cur.close()
    print('创建数据库 py3_tstgr 成功！')

    # 查找，插入
# 4719e1d3f1bb1a6c237cd0659e0265bc  appkey
