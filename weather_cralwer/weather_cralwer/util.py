# read_all_city_and_city_code from databases;
# 导入pymysql模块
from typing import List

import pymysql

from WeatherWeb.settings import DATABASES
import pymysql
from dbutils.pooled_db import PooledDB


class MysqlSimipleConn:

    def __init__(self):
        # pymysql 连接池 从django settings读取数据库配置，共用
        mysql_config = DATABASES["default"]
        self.pool = PooledDB(pymysql, 5, host=mysql_config['HOST'],
                             user=mysql_config['USER'],
                             passwd=mysql_config['PASSWORD'],
                             db=mysql_config['NAME'],
                             port=int(mysql_config['PORT']),
                             charset=mysql_config["OPTIONS"]['charset'])

    def query(self, sql: str) -> List:
        conn = self.pool.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql)
        result = []
        if sql.find('select') != -1 or sql.find("SELECT") != -1:
            result = cursor.fetchall()
        return result


mysql_conn_instance = MysqlSimipleConn()
if __name__ == '__main__':
    result = mysql_conn_instance.query("select * from city ;")
    print(result)
