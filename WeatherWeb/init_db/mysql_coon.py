import pymysql

config = {
    "host": "127.0.0.1",  # 地址
    "port": 3306,  # 端口
    "user": "root",  # 用户名
    "password": "123456",  # 密码
    "database": "scrapy_django",  # 数据库名;如果通过Python操作MySQL,要指定需要操作的数据库
    "charset": "utf8mb4"
}


mysql_conn = pymysql.connect(**config)
