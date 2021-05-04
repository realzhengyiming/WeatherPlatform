# 这个是进行无监督聚类处理的东西
import datetime

import pandas as pd
from sklearn.cluster import KMeans

from weather_show_app.models import City, DateWeather


def one_hot_col_process(df, col_name):  # 对分类变量做one-hot处理
    one_hot_cols = pd.get_dummies(df[col_name])
    df = df.join(one_hot_cols)
    df = df.drop(col_name, axis=1)
    return df


# 这儿进行 数据清洗操作
def get_similarity_city(df_one_hot_processed):
    '''
    这儿输出的df 是经过了把city_id替换成city_name，
    并且经过了one-hot 对城市列表处理的聚类后的 date_weather的df
    '''
    temp_df = df_one_hot_processed[CITY_TYPES]  # 截取只有city one-hot的列（27开始是城市列）
    temp_df_col = list(temp_df.columns)

    # 按行读，如果找到所在行为1 的就取columns名字
    not_zero = []
    for index, row in temp_df.iterrows():
        for row_index, value in enumerate(row):
            if value == 1 or value == "1":
                col_name = temp_df_col[row_index]
                not_zero.append(col_name)
    return not_zero  # 相似的城市列表返回回来了


# 初始化，先读取出来
SQL_PATTERN = "select * from City;"
HOUR_WEATHER_SQL = '''select * from  HourWeather ;'''
DATE_WEATHER_SQL = '''select * from DateWeather where date='2021-05-03' and city_id in (
    select id from City where is_city=true)'''

all_citys = City.objects.all()
city_table = pd.DataFrame.from_records(all_citys.values())

some_citys = City.objects.filter(is_city=True).order_by("-id")
all_date_weathers = DateWeather.objects.filter(date=datetime.datetime.today(), city__in=some_citys)
date_weather_table = pd.DataFrame.from_records(all_date_weathers.values())

# 合并多个表，然后做分析处理
city_table = city_table.rename(columns={"id": "city_id"})
date_weather_with_city_name = pd.merge(date_weather_table, city_table,
                                       how='left',
                                       on='city_id')

# 提前配置好的常量
NEED_TRAIN_COLS = ['state', 'max_temperature',
                   'min_temperature', 'wind_power', 'wind_direction',
                   'name']

WEATHER_TYPES = list(date_weather_with_city_name['state'].unique())
CITY_TYPES = list(date_weather_with_city_name['name'].unique())
NEED_ONE_HOT_COLS = ['state', 'wind_power', 'wind_direction', 'name']

df = date_weather_with_city_name[NEED_TRAIN_COLS]

# 把df分类变量处理成one hot
for col_name in NEED_ONE_HOT_COLS:
    df = one_hot_col_process(df, col_name)
# 现在是处理后的样子了

kmeans_model = KMeans(n_clusters=10, init='k-means++', random_state=11)
fit_clf = kmeans_model.fit(df)


# 这儿开始是将传过来的df处理成 待查询预测的分类
def get_similarity_city_controller(city_id):
    today_city_weather_result = DateWeather.objects.filter(city_id=city_id, date=datetime.datetime.today())
    today_city_weather = pd.DataFrame.from_records(today_city_weather_result.values())

    today_city_weather = pd.merge(today_city_weather, city_table, how='left', on='city_id')
    today_city_weather = today_city_weather[NEED_TRAIN_COLS]
    today_city_weather_cleaned = today_city_weather

    for col_name in NEED_ONE_HOT_COLS:
        today_city_weather_cleaned = one_hot_col_process(today_city_weather_cleaned, col_name)  # 不行，应该直接从训练好的地方来进行查询

    full_columns = list(df.columns)
    empty_df = pd.DataFrame(columns=full_columns)
    need_predict_df = pd.concat([empty_df, today_city_weather_cleaned], axis=0).fillna(0)

    # 也要经过相同的处理
    result = fit_clf.predict(need_predict_df)
    # 获得每一类的相似的城市
    classes = list(set(list(result)))[0]
    res_df = df[(fit_clf.labels_ == classes)]  # 同一类的df集合（已经是one——hot后的了
    return get_similarity_city(res_df)
