import datetime
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # 用来分页饿
from django.db import connection
from django.db.models import Count  # 直接使用models中的统计类来进行统计查询操作
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.views import APIView

from .forms import LoginForm, RegistrationForm
from .kmeans_process import get_similarity_city_controller
from .models import City, DateWeather, Favourite


def index(request):
    return render(request, 'weather_show_app/index_charts.html')


@login_required(login_url='/weather/loginpage/')  # 默认主页
def detailView(request):  # 详情页
    house_id = request.GET.get("house_id")
    houseList = City.objects.filter(Q(house_id=house_id)).order_by("-house_date")
    labels = houseList[0].house_labels.all()
    # print(labels)
    facility = houseList[0].house_facility.all()
    return render(request, "weather_show_app/index_chartspage_detail.html",
                  context={"house": houseList,
                           "house_id": house_id,
                           "labels": labels,
                           "facility": facility,
                           "app_name": "房源详情"
                           })


def testindex(request):  # 测试页
    # todo 提取不重复的日期的东西，然后进行年月日绘制图片进行查看可视化，同比环比，这个也是可以的
    result = fetchall_sql_dict("SELECT distinct(id),house_firstOnSale FROM `hotelapp_house` ")
    # print(result)
    # 然后转换成pandas进行一系列的筛选等
    # qs_dataframe = read_frame(qs=result)
    # print(qs_dataframe)

    import pandas as pd

    df = pd.DataFrame(result)
    # print(df)
    # 按月份
    df.index = pd.to_datetime(df.house_firstOnSale)
    return render(request, 'weather_show_app/test.html', context={"article": result})


# @login_required(login_url='/loginpage/')  # 详情页
def detaillist(request):  # 数据列表页分页
    today = datetime.datetime.now().date()
    date_weathers = DateWeather.objects.filter(date=today).order_by("-id").order_by("city_id")
    paginator = Paginator(date_weathers, 20)  # 2个一页的意思
    page = request.GET.get("page")
    try:
        current_page = paginator.page(page)
        date_weathers = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        date_weathers = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        date_weathers = current_page.object_list
    return render(request, "weather_show_app/index_chartspage_detaillist.html",
                  context={"app_name": "详细数据", "date_weathers": date_weathers, "page": current_page})
    # 这两个是必须要带上的属性


def fetchall_sql(sql) -> tuple:  # 这儿唯一有一个就是显示页面的
    # latest_question_list = KeyWordItem # 换成直接使用sql来进行工作
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()
        # columns = [col[0] for col in cursor.description]  # 提取出column_name
        # return [dict(zip(columns, row)) for row in cursor.fetchall()][0]
        return row


def fetchall_sql_dict(sql) -> [dict]:  # 这儿唯一有一个就是显示页面的
    # latest_question_list = KeyWordItem # 换成直接使用sql来进行工作
    print("check sql")
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        # row = cursor.fetchall()
        columns = [col[0] for col in cursor.description]  # 提取出column_name
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


# @login_required(login_url='/loginpage/')  # 默认主页，主页不用登录，但是收藏夹需要登录
def index(request):  # 这儿唯一有一个就是显示页面的
    if request.GET.get("success_info"):
        success_info = request.GET.get("success_info")
    # 总共的城市的数量
    count_city = City.objects.all().aggregate(count=Count("name", distinct=True))  # todo 花里胡哨的样式晚点再慢慢调整
    count_today = DateWeather.objects.all().aggregate(count=Count("id"))
    context = {
        'app_name': "天气分析",
        'count_today': count_today,  # None,  # count_today,
        'count_today_city': count_city,  # None,  # count_today_city,  # 今天总共爬了多少个城市
        'count_total_city': None,  # count_total_city,
        'success_info': None  # success_info

    }
    return render(request, 'weather_show_app/index_chartspage.html', context)


def loginPage(request):  # 登陆界面的,这个是自定义的
    if request.method == "GET":
        success_info = None
        if request.session.get("success_info"):
            success_info = request.session.get("success_info")
            print("正在输出")
            print(request.session.get("success_info"))
            del request.session['success_info']  # 用完就删掉
            print("删除后")
            print(request.session.get("success_info"))
        login_form = LoginForm()
        return render(request, 'weather_show_app/loginPage.html',
                      context={'form': login_form, 'success_info': success_info})
    if request.method == "POST":
        login_form = LoginForm(request.POST)  # 这个
        if login_form.is_valid():
            cd = login_form.cleaned_data  # 转化成字段来方便提取
            user = authenticate(username=cd['username'], password=cd['password'])
            if user:
                login(request, user)
                # return HttpResponse("Wellcome!")
                return redirect('/')
            else:
                return render(request, 'weather_show_app/loginPage.html',
                              context={'form': login_form, "error": "账号或者密码错误！"})
        else:
            error = "请检查输入的账号和密码是否正确"
            login_form = LoginForm()
            return render(request, 'weather_show_app/loginPage.html', context={'form': login_form, "error": error})


def register(request):  # 注册用户User
    if request.method == "POST":
        user_form = RegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data["password"])
            # new_user.
            new_user.save()
            # 这儿放登陆注册的
            # loginForm = LoginForm()
            request.session['success_info'] = 'register_success'
            return redirect('/loginpage')  # todo 用命名空间的方式来进行操作
        else:
            return render(request, "weather_show_app/register.html", {"form": user_form,
                                                                      "error_message": "提交的账号密码不合法"})  # 这个是get的方式进来
    else:
        user_form = RegistrationForm()
        return render(request, "weather_show_app/register.html", {"form": user_form})  # 这个是get的方式进来


def userLogout(request):  # 登出
    logout(request)
    return redirect("/loginpage/")


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


def today_weather_page(request):

    city_id = request.GET.get("city_id", 174)  # 174 是茂名
    city_name = request.GET.get("city_name", None)  # 174 是茂名
    city = City.objects.filter(name=city_name)
    if not city:
        now_city = City.objects.get(id=city_id)
    else:
        now_city = city[0]

    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    select_date = request.GET.get("select_date", now_date)

    all_citys = City.objects.filter(is_city=True)
    today_weather = DateWeather.objects.get(city_id=now_city.id, date=select_date)
    future_date = (datetime.date.today() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    past_dates = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')

    future_weathers = DateWeather.objects.filter(date__range=(now_date, future_date), city_id=city_id)
    past_weathers = DateWeather.objects.filter(date__range=(past_dates, yesterday), city_id=city_id).order_by("-date")
    past_weather_dates = [weather.date for weather in past_weathers]

    result = get_similarity_city_controller(city_id)

    return render(request, 'weather_show_app/index_chartspage_today_detail.html',
                  context={"app_name": "指定城市当天天气情况",
                           'all_citys': all_citys,
                           'test_vars': result,
                           "select_date": select_date,
                           "city_id": city_id, "now_city": now_city, "today_weather": today_weather,
                           "future_weathers": future_weathers, "past_dates": past_weather_dates})


@login_required(login_url='/loginpage/')  # 默认主页
def consumerPage(request):
    return render(request, 'weather_show_app/index_chartspage_consumer.html', context={"app_name": "房客专区"})


# 详细的页面
@login_required(login_url='/loginpage/')  # 默认主页
def timePage(request):
    return render(request, 'weather_show_app/index_chartspage_time.html', context={"app_name": "房源发布时间分析"})


# 详细的页面
@login_required(login_url='/loginpage/')  # 默认主页
def pricePage(request):
    return render(request, 'weather_show_app/index_chartspage_price.html', context={"app_name": "房源价格分析"})


# 详细的页面
@login_required(login_url='/loginpage/')  # 默认主页
def favcountPage(request):
    return render(request, 'weather_show_app/index_chartspage_price.html', context={"app_name": "热门房源分析"})


# 搜索的页面
@login_required(login_url='/loginpage/')  # 默认主页
def searchPage(request):
    return render(request, 'weather_show_app/index_chartspage_search.html', context={"app_name": "查找房源"})


# 房源面积的页面
@login_required(login_url='/loginpage/')  # 默认主页
def assessPage(request):
    return render(request, 'weather_show_app/index_chartspage_assess.html', context={"app_name": "房源价格评估"})


# 房源面积的页面
@login_required(login_url='/loginpage/')  # 默认主页
def area(request):
    return render(request, 'weather_show_app/index_chartspage_area.html', context={"app_name": "房源面积分析"})


# 房源面积的页面
@login_required(login_url='/loginpage/')  # 默认主页
def predictPage(request):
    return render(request, 'weather_show_app/index_chartspage_predict.html', context={"app_name": "房源价格预估"})


# 详细的页面
# @login_required(login_url='/loginpage/')  # 默认主页
def trainPage(request):
    return render(request, 'weather_show_app/test.html', context={"app_name": "test"})


def genFavtag(city_object: City, date_weather: DateWeather):  # 输入一个fav对象，生成一个house tag  # todo 收藏夹功能
    tag = f'''<tr id='tr-{city_object.id}'>
                <td>{city_object.id}</td>

            <td>{city_object.name}</td>
            <td>{date_weather.state}</td>
            <td>{date_weather.min_temperature}℃~~{date_weather.max_temperature}℃~</td>
            <td><a target="_blank" href="/host/?city_id={city_object.id}">{city_object.name}</a></td>
              <td>
                  <button  onclick="delete_btn({city_object.id})"  
                        id="{city_object.name}"  name="del_button"
                          class="mdui-color-theme-accent mdui-btn mdui-btn-icon mdui-ripple mdui-ripple-white">
                  <i class="mdui-icon material-icons">delete_forever</i></button></td>
          </tr>'''
    return tag


# 加入收藏和删除收藏的功能
class favouriteHandler(APIView):  # 使用不同的试图来进行封装
    def get(self, request, *args, **kwargs):
        # print("get 进来了")
        method = self.request.query_params.get('method', None)
        if method is not None:
            username = self.request.query_params.get("username", None)
            if not username:
                return json_response({"result": "请您先登录呢😯", 'tag': ""})
            city_id = self.request.query_params.get("city_id", 0)
            if method == "add":
                if username != 0 and city_id != 0:
                    import traceback
                    user = User.objects.filter(username=username).first()  #
                    city = City.objects.filter(id=city_id).first()  # 找到这个房子
                    date_weather = DateWeather.objects.filter(city_id=city.id,
                                                              date=datetime.datetime.now().date()).first()
                    if user is not None and city is not None:
                        try:
                            f1 = Favourite.objects.get(user=user)  # 找到一个收藏夹对象
                            # 这儿可能重复
                            for i in list(f1.city.all()):
                                if str(i.id) == city_id:
                                    return json_response({"result": "已在收藏夹 √   😀", 'tag': ""})
                            f1.city.add(city)
                            f1.save()  # 增加收藏
                            return json_response({"result": "加入收藏 √   👌", 'tag': genFavtag(city, date_weather)})
                        except Favourite.DoesNotExist:  # 创建
                            # 没有收藏时候
                            print(traceback.print_exc())
                            try:
                                f1 = Favourite.objects.create(user=user)
                                f1.city.add(city)
                                f1.save()
                                return json_response({"result": "加入收藏 √   👌", 'tag': genFavtag(city, date_weather)})
                            except Exception as e:
                                print(e)
                                print(traceback.print_exc())
                                print("请检查")
                        except Exception as e:
                            print(e)
                return json_response({"result": "出现问题", 'tag': ""})
            if method == "del":
                user = User.objects.filter(username=username).first()  #
                city = City.objects.filter(id=city_id).first()  # 找到这个房子
                if user is not None and city is not None:
                    try:
                        f1 = Favourite.objects.get(user=user)  # 找到一个收藏夹对象
                        f1.city.remove(city)
                        f1.save()  # 增加收藏
                        return json_response({"result": "删除成功 √  👌"})
                    except Favourite.DoesNotExist:  # 创建
                        print("没有收藏夹")
                else:
                    return json_response({"result": "未找到此城市！！！"})
        else:
            return json_response({"result": "未找到参数"})

    def post(self, request, *args, **kwargs):
        return json_response({"result": "请通过get"})


# 这个组件是组装搜索结果的
def maketable(result):
    head = '''
    <table class="mdui-table">
    <thead>
      <tr>
          <th>价格(￥)</th>
        <th>房源名</th>
        <th>地理位置</th>

        <th>喜欢数</th>
          <th>预览</th>
      </tr>
    </thead>
    <tbody>
    '''
    temp = ""
    for object in result:
        temp += f'''
     <tr>
         <td>{object['house_discountprice']}</td>
        <td ><a href="/weather_show_app/detail/?house_id={object['house_id']}" target="_blank" >{object['house_title']}</a></td>
        <th>{object['house_location_text']}</th>

        <td>{object['house_favcount']}</td>
        <td style="width:300px;height:auto;"><img class="mdui-img-fluid" src="{object['house_img']}"  /></td>
     </tr>
    '''
    tail = '''</tbody></table>'''
    return head + temp + tail
