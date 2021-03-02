from django.shortcuts import render


def index(request):
    return render(request, 'weather_show_app/test.html', context={"article": ""})
