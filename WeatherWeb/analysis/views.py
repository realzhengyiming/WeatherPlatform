from django.shortcuts import render

# geo graph
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.datasets import register_url


# 做这个前后端分离的步骤是：
# 1. 思考，选好大概要用什么可视化的图
# 2. 然后是查看官方文档，复制下源代码
# 2.1 首先是按照官方的。把 对象创建好，比如bar(),然后统一用jsonResponse 装好。
# 2.2 然后是创建好url的映射这个接口的路径和name
# 2。3 然后前端使用ajax进行加载。这个加载可以从老的代码那儿抽取出来。


# class IndexView(APIView):
#     def get(self, request, *args, **kwargs):
# return HttpResponse(content=open("analysis/test.html").read())

def IndexView(request):  # 测试页
    return render(request, 'analysis/test.html')

