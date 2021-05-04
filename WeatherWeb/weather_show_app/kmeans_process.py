# 这个是进行聚类处理的东西
import pymysql
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import KMeans



def GetQueryByDF(sql):  # 执行sql，然后返回df
    connect_info = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8' \
        .format("root", "123456", "127.0.0.1", "3306", "scrapy_django")  # 这个是对应的数据库
    engine = create_engine(connect_info)
    df = pd.read_sql(sql, engine)
    return df

def one_hot_col_process(df, col_name):  # 对分类变量做one-hot处理
    one_hot_cols = pd.get_dummies(df[col_name])
    df = df.join(one_hot_cols)
    df = df.drop(col_name, axis=1)
    return df

# 这儿进行 数据清洗操作
def get_similarity_city(df):
    temp_df = df.iloc[:,27:]  # 截取只有city one-hot的列（27开始是城市列）
    temp_df_col = list(temp_df.columns)

    # 按行读，如果找到为1 的就取columns名字
    not_zero = []
    for index,row in temp_df.iterrows():
        for row_index,value in enumerate(row):
            if value==1 or value=="1":
                col_name = temp_df_col[row_index]
                not_zero.append(col_name)
    return not_zero  # 相似的城市列表返回回来了

# 初始化，先读取出来
SQL_PATTERN = "select * from City;"
HOUR_WEATHER_SQL = '''select * from  HourWeather ;'''
DATE_WEATHER_SQL = '''select * from DateWeather where date='2021-05-03' and city_id in (
    select id from City where is_city=true)'''

city_table = GetQueryByDF(SQL_PATTERN)
hour_weather_table = GetQueryByDF(HOUR_WEATHER_SQL)
date_weather_table = GetQueryByDF(DATE_WEATHER_SQL)

# 合并多个表，然后做分析处理
city_table = city_table.rename(columns={"id": "city_id"})
dff = pd.merge(date_weather_table, city_table,
               how='left',
               on='city_id')
df = dff[['state', 'max_temperature',
          'min_temperature', 'wind_power', 'wind_direction',
          'name']]
