# 怎么弄出一个统一的接口呢，或者就弄一个统一的打包装饰器

import json

from django.http import HttpResponse
from rest_framework.views import APIView

from analysis.graph_view import bar_base, GeoMap


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


# 下面开始是各个api 视图
class BarView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(bar_base()))  # 这是一个接口，是需要写url映射滴，那怎么办呢


class GeoView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(GeoMap()))  # 这是一个接口，是需要写url映射滴，那怎么办呢
