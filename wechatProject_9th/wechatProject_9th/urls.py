"""
URL configuration for wechatProject_9th project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app01 import views
from app01.views import UserView, LoginView, RecordView, RecordDetailView, RecordYearView, CategoryView, \
    RecordSearchView, WechatView

# 路由URL
urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
    path('api/user/', UserView.as_view()),
    path('api/login/', LoginView.as_view()),
    path('api/records/<str:category>/', RecordView.as_view()),
    path('api/record/<int:record_id>/', RecordDetailView.as_view()),
    # 如果不按类别查询，则category=1/2....（即category_id）
    # 如果category=range，则按日期范围查询，加一个num1用于范围查询，其他时刻num1=""
    # 缺少查询条件
    # path('api/record/<str:condition>/<str:num>/<str:num1>/<str:category>', RecordYearView.as_view()),
    # 查出所有的category
    path('api/category', CategoryView.as_view()),
    path('api/recordSearch/',RecordSearchView.as_view()),

    path('api/getWechatId/',WechatView.as_view()),
    path('api/userWechat/',WechatView.as_view())

]
