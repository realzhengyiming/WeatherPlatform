# read_all_city_and_city_code from databases;
# 导入pymysql模块
from typing import List

import pymysql

from WeatherWeb.WeatherWeb.settings import DATABASES
import pymysql
from dbutils.pooled_db import PooledDB
import logging

logger = logging.getLogger(__name__)


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

        result = []
        try:
            cursor.execute(sql)
            if sql.find('select') != -1 or sql.find("SELECT") != -1:
                result = cursor.fetchall()
            elif sql.find("insert") != -1 or sql.find("INSERT") != -1:
                conn.commit()  # 提交的插入才有效果
        except Exception as e:
            conn.rollback()  # 失败后就不插入
            logger.error(f"{e} : {sql}")
        return result


mysql_conn_instance = MysqlSimipleConn()
if __name__ == '__main__':
    # result = mysql_conn_instance.query("select * from city ;")
    # print(result)

    # 测试插入
    sql = "insert into test_table (id,name) values ('1','nihao')"
    result = mysql_conn_instance.query(sql)
    result = mysql_conn_instance.query("select * from test_table ;")
    print(result)
