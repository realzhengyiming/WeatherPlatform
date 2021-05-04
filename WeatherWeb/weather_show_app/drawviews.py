import datetime
import json
import time

import numpy as np
import pandas as pd
from django.core.cache import cache  # 导入缓存对象,redis存储
from django.db import connection
from django.db.models import Count  # 直接使用models中的统计类来进行统计查询操作
from django.http import HttpResponse
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Line, Geo, Map, Radar
from pyecharts.globals import ThemeType, ChartType
from rest_framework.views import APIView

from .constant import ALL_DIRECTION_MAPPING_DICT
from .models import DateWeather, City


def fetchall_sql(sql) -> dict:  # 这儿唯一有一个就是显示页面的
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()
        return row


def fetchall_sql_dict(sql) -> [dict]:  # 这儿唯一有一个就是显示页面的
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]  # 提取出column_name
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error


# 数据概略处的图 最近7天爬虫数据爬取
def bar_base() -> Bar:
    nowdate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    count_total_city = DateWeather.objects.filter(date=nowdate).values("city").annotate(
        count=Count("city")).order_by("-count")
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.WONDERLAND))
            .add_xaxis([city['city'] for city in count_total_city])
            .add_yaxis("房源数量", [city['count'] for city in count_total_city])
            .set_global_opts(title_opts=opts.TitleOpts(title="今天城市房源数量", subtitle="如图"),
                             xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                             )
            .set_global_opts(
            datazoom_opts={'max_': 2, 'orient': "horizontal", 'range_start': 10, 'range_end': 20, 'type_': "inside"})
            .dump_options_with_quotes()
    )
    return c


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(bar_base()))  # 这儿这个是返回json数据用来装到bar中的


class PieView(APIView):  # 房型饼图
    def get(self, request, *args, **kwargs):
        result = fetchall_sql(
            '''select state,count(state) counter from 
            (select distinct id ,state from DateWeather  group by id,state )
             hello group by state order by counter''')
        c = (
            Pie()
                .add("", [z for z in zip([i[0] for i in result], [i[1] for i in result])])
                .set_global_opts(title_opts=opts.TitleOpts(title="天气类型"),
                                 legend_opts=opts.LegendOpts(pos_left="15%",
                                                             type_='scroll', is_show=False),
                                 )
                .set_series_opts(label_opts=opts.LabelOpts(
                formatter="{b}: {c} | {d}%",
            ))
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


class timeLineView(APIView):  # todo 改成了7天内，全国各地多条曲线，每个曲线是一种天气状态的数量。 应该选择原本是line 的图来直接修改好一些，不然自己容易有些乱
    def get(self, request, *args, **kwargs):
        # week_name_list = getLatestSevenDay()  # 获得最近七天的日期 时间列折线图
        # 七天前的那个日期
        today = datetime.datetime.now()
        # // 计算偏移量
        offset = datetime.timedelta(days=-6)
        # // 获取想要的日期的时间
        re_date = (today + offset).strftime('%Y-%m-%d')
        house_sevenday = DateWeather.objects.filter(date__gte=re_date).values("date"). \
            annotate(count=Count("date")).order_by("date")

        week_name_list = [day['date'] for day in house_sevenday]
        date_count = [day['count'] for day in house_sevenday]
        c = (
            Line(init_opts=opts.InitOpts(width="1600px", height="800px"))
                .add_xaxis(xaxis_data=week_name_list)
                .add_yaxis(
                series_name="抓取的数量",
                # y_axis=high_temperature,
                y_axis=date_count,
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="最大值"),
                        opts.MarkPointItem(type_="min", name="最小值"),
                    ]
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="average", name="平均值")]
                ),
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(title="最近七天抓取情况", subtitle=""),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            )
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))

class drawMap(APIView):
    def get(self, request, *args, **kwargs):
        result = cache.get('weather_city', None)  # 使用缓存，可以共享真好。
        if result is None:  # 如果无，则向数据库查询数据
            print("读取缓存中的城市")
            result = fetchall_sql(
                """select name, count(name) as counter
                    from (
                             select belong_province as name
                             from DateWeather
                                      left join City on DateWeather.city_id = City.id
                                      where name!=''
                    )  as t where name<>'' group by name;""")
        else:
            pass

        province_names = [i[0].replace("市", "")
                              .replace("省", "")
                              .replace("回族自治区", "")
                              .replace("壮族自治区", "")
                              .replace("维吾尔自治区", "")
                              .replace("自治区", "")
                              .replace('特别行政区', '')
                          for i in result]
        province_names_number = [i[1] for i in result]
        max_total_size = max(province_names_number)
        zip_data = [list(z) for z in zip(province_names, province_names_number)]
        c = (
            Map()
                .add(series_name="天气数据省份分布", data_pair=zip_data, maptype="china", zoom=1, center=[105, 38])
                .set_global_opts(
                title_opts=opts.TitleOpts(title="天气数据省份分布"),
                visualmap_opts=opts.VisualMapOpts(max_=max_total_size, is_piecewise=False)
            )
                .dump_options_with_quotes()
        )

        return JsonResponse(json.loads(c))


class get_today_aqi_bar(APIView):  # 按月份分，或者按年分
    def get(self, request, *args, **kwargs):
        city_id = request.GET.get("city_id")
        today_date = datetime.date.today()
        select_date = request.GET.get("select_date", today_date)

        if not city_id:
            city_id = City.objects.get(name="茂名").id
        result = fetchall_sql_dict(
            f'''select * from HourWeather where weather_id = (
            select id from DateWeather where city_id=(
            select id from City where id='{city_id}') 
            and date='{select_date}') 
            and belong_to_date ='{select_date}' order by hour ;
            ''')
        temp_df = pd.DataFrame(result)

        # 都使用df来进行处理和显示
        count = 0
        for i in list(temp_df.AQI.values):
            if i != 0:
                break
            else:
                count += 1
        if count >= 24:  # 如果24小时的都为0
            pass
        else:
            temp_df = temp_df.replace(0, np.nan)
        temp_df['AQI'].fillna((temp_df['AQI'].mean()), inplace=True)
        print(temp_df)
        hour_list = ['0点', "1点", "2点", "3点", "4点", '5点', '6点', '7点', '8点', '9点', '10点', '11点', '12点',
                     '13点', '14点', '15点', '16点', '17点', '18点', '19点', '20点', '21点', '22点', '23点']
        c = (
            Bar()
                .add_xaxis(hour_list)
                .add_yaxis("AQI", [int(i) for i in list(temp_df.AQI.values)])
                .set_global_opts(title_opts=opts.TitleOpts(title="24小时空气质量"),
                                 datazoom_opts=opts.DataZoomOpts(),
                                 xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                                 )

                .set_global_opts(datazoom_opts={'orient': "horizontal", 'range_start': 1, 'range_end': 8,
                                                'type_': "inside"})
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


class get_today_average_humity(APIView):  # 按月份分，或者按年分
    def get(self, request, *args, **kwargs):
        print("水球图")
        city_id = request.GET.get("city_id")
        today_date = datetime.date.today()
        select_date = request.GET.get("select_date", today_date)

        if not city_id:
            city_id = City.objects.get(name="茂名").id
        result = fetchall_sql_dict(
            f'''select * from HourWeather where weather_id = (
            select id from DateWeather where city_id=(
            select id from City where id='{city_id}') 
            and date='{select_date}') 
            and belong_to_date ='{select_date}' order by hour ;
            ''')
        temp_df = pd.DataFrame(result)
        # 都使用df来进行处理和显示
        temp_df = temp_df.replace(0, np.nan)
        temp_df['relative_humidity'].fillna((temp_df['relative_humidity'].mean()), inplace=True)
        relative_humidity = round(temp_df['relative_humidity'].mean() * 0.01, 2)
        from pyecharts import options as opts
        from pyecharts.charts import Liquid

        c = (
            Liquid()
                .add("lq", [relative_humidity, 0.6, 0.7], is_outline_show=False)
                .set_global_opts(title_opts=opts.TitleOpts(title="24小时平均湿度"))
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


class wind_graph(APIView):
    def get(self, request, *args, **kwargs):
        city_id = request.GET.get("city_id")
        today_date = datetime.date.today()
        select_date = request.GET.get("select_date", today_date)

        if not city_id:
            city_id = City.objects.get(name="茂名").id
        result = fetchall_sql_dict(
            f'''select * from HourWeather where weather_id = (
            select id from DateWeather where city_id=(
            select id from City where id='{city_id}') 
            and date='{select_date}') 
            and belong_to_date ='{select_date}' order by hour ;
            ''')
        temp_df = pd.DataFrame(result)

        # 都使用df来进行处理和显示
        today_24hour_winds = temp_df[['wind_power', "wind_direction", "hour"]]
        today_24hour_winds['hour'] = today_24hour_winds['hour'].apply(int)

        rader = Radar(init_opts=opts.InitOpts(width="1280px", height="720px")).add_schema(
            schema=[
                opts.RadarIndicatorItem(name="北风", max_=10),
                opts.RadarIndicatorItem(name="东北风", max_=10),
                opts.RadarIndicatorItem(name="东风", max_=10),
                opts.RadarIndicatorItem(name="东南风", max_=10),
                opts.RadarIndicatorItem(name="南风", max_=10),
                opts.RadarIndicatorItem(name="西南风", max_=10),
                opts.RadarIndicatorItem(name="西风", max_=10),
                opts.RadarIndicatorItem(name="西北风", max_=10),
            ],
            splitarea_opt=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        )
        for index, row in today_24hour_winds.iterrows():
            wind_power, wind_direction, hour = list(row)
            temp_hour_wind = [0 for i in range(8)]
            temp_hour_wind[ALL_DIRECTION_MAPPING_DICT[wind_direction]] = wind_power
            rader.add(series_name=f"{hour + 1}时", data=[temp_hour_wind])
        c = (rader.set_series_opts(label_opts=opts.LabelOpts(is_show=True))
             .set_global_opts(
            legend_opts=opts.LegendOpts())
             .dump_options_with_quotes())
        return JsonResponse(json.loads(c))


class today_temperature_detail_line(APIView):
    def get(self, request, *args, **kwargs):
        city_id = request.GET.get("city_id")
        now_date = datetime.datetime.now().date()
        select_date = request.GET.get("select_date", now_date)

        if not city_id:
            city_id = City.objects.get(name="茂名").id

        print(f"温度获得的城市id {city_id}")
        result = fetchall_sql_dict(
            f'''select * from HourWeather where weather_id = (
            select id from DateWeather where city_id={city_id}
            and date='{select_date}' ) 
            and belong_to_date ='{select_date}' order by hour ;
            ''')  # 用line？  # 按24小时进行排序才可以

        temp_df = pd.DataFrame(result)
        week_name_list = ['0点', "1点", "2点", "3点", "4点", '5点', '6点', '7点', '8点', '9点', '10点', '11点', '12点',
                          '13点', '14点', '15点', '16点', '17点', '18点', '19点', '20点', '21点', '22点', '23点']
        high_temperature = [i for i in list(temp_df.temperature)]  # 改成按当天的 按 1～23 ，
        # low_temperature =  [i for i in list(temp_df.relative_humidity)]

        c = (
            Line(init_opts=opts.InitOpts(width="1600px", height="800px"))  # 为什么没反应
                .add_xaxis(xaxis_data=week_name_list)
                .add_yaxis(
                series_name="最高气温",
                y_axis=high_temperature,
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="最大值"),
                        opts.MarkPointItem(type_="min", name="最小值"),
                    ]
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="average", name="平均值")]
                ),
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(title="当天24小时温度情况", subtitle="每小时温度"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            )
                .dump_options_with_quotes()
        )

        return JsonResponse(json.loads(c))
