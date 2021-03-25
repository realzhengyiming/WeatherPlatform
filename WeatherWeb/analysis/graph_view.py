from random import randrange

from pyecharts import options as opts
from pyecharts.charts import Bar, Geo
from pyecharts.datasets import register_url


def bar_base() -> Bar:
    c = (
        Bar()
            .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
            .add_yaxis("商家A", [randrange(0, 100) for _ in range(6)])
            .add_yaxis("商家B", [randrange(0, 100) for _ in range(6)])
            .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"))
            .dump_options_with_quotes()
    )
    return c


def GeoMap() -> Geo:
    try:
        register_url("https://echarts-maps.github.io/echarts-countries-js/")
    except Exception:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        register_url("https://echarts-maps.github.io/echarts-countries-js/")

    geo = (
        Geo()
            .add_schema(maptype="瑞士")

            .set_global_opts(title_opts=opts.TitleOpts(title="瑞士"))
            .dump_options_with_quotes()

        # .render("geo_chart_countries_js.html")
    )
    return geo
