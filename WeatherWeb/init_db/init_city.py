from referer.backup.mysql_coon import mysql_conn
from referer.backup.new_city_code import city_and_code
from xpinyin import Pinyin


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


if __name__ == '__main__':  # 写入城市代码和拼音
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
