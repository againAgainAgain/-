from django.shortcuts import render,HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from ext.auth import RecordAuthentication


# Create your views here.
def index(request):
    return HttpResponse('欢迎使用')


from rest_framework.viewsets import ModelViewSet
from .models import User, Record, Category
from .serializers import UserModelSerializer, LoginSerializers, RecordSerializers, CategorySerializers
import uuid

# Create your views here.
# class UserViewSet(ModelViewSet):
#     queryset = User.objects.all()       # queryset 指明该视图集在查询数据时使用的查询集
#     serializer_class = UserModelSerializer # 指明该视图在进行序列化或反序列化时使用的序列化器


class UserView(APIView):
    """获取全部用户、用户注册"""
    def get(self, request):
        """获取全部用户"""
        users = User.objects.all()
        # 将数据从数据库取出序列化后传给前端
        user_serializer=UserModelSerializer(users, many=True)
        return Response({
            'status': '200',
            'msg': 'ok',
            'results': user_serializer.data
        })

    def post(self,request):
        """新建用户"""
        # 获取到前端的数据先校验
        user = UserModelSerializer(data=request.data)
        # {"username":"5","password":"6"}
        # User.objects.create(user)

        #print(user.is_valid())
        #print(user.data) # JSON格式：{'username': '5', 'password': '6'}

        if user.is_valid():
            user.validated_data.pop("confirm_password")
            user.save()
            return Response({
                'status': '200',
                'msg': '注册成功！'
            })

        return Response({
            'status': '500',
            'msg': user.errors
        })


class LoginView(APIView):
    """登录、修改密码"""
    authentication_classes = [RecordAuthentication, ]

    def post(self, request):
        ser = LoginSerializers(data=request.data)
        if not ser.is_valid():
            return Response({
                'status': '500',
                'msg': ser.errors
            })
        user = User.objects.filter(**ser.validated_data).first()
        if not user:
            return Response({
                'status': '500',
                'msg': "用户名或密码错误"
            })
        token = str(uuid.uuid4())
        user.token=token
        user.save()

        if(user.openid!=None and user.openid!=''):
            # 已绑定微信
            openid="true"
            # 根据openid获取用户的微信头像和名字

        else:
            openid="false"
        return Response({
            'status': '200',
            'msg': '登录成功！',
            # 'data': {
            #     'userInfo': user
            # }
            'user': {
                'id': user.id,
                'username': user.username,
                'token': user.token,
                'openid':openid,
                'nickName':user.wechatName,
                'avatarUrl':user.wechatAvatarUrl
            }
        })

    def put(self,request):
        # 密码修改（需登录）
        # 没使用confirm_new_password二次确认密码
        # # 查看用户是否登录，但不用登录也可以修改密码
        # if not request.user:
        #     return Response({
        #         'status': '500',
        #         'msg': '认证失败'
        #     })
        print(request.data)     # {'username': 'test', 'password': '111', 'new_password': '121', 'confirm_new_password': '121'}
        # 验证用户书写格式是否正确
        ser = LoginSerializers(data=request.data)
        if not ser.is_valid():
            return Response({
                'status': '500',
                'msg': ser.errors
            })
        # 验证用户旧密码是否正确
        user = User.objects.filter(**ser.validated_data).first()
        if not user:
            return Response({
                'status': '500',
                'msg': "用户名或密码错误"
            })
        new_password=request.data.get('new_password')
        user.password=new_password
        user.save()
        return Response({
            'status': '200',
            'msg': '修改成功！'
        })


class RecordView(APIView):
    """查看所有记录、新增记录（没写完）！！！"""
    authentication_classes = [RecordAuthentication, ]

    def get(self, request,category):
        """获取所有收支记录"""
        # 查看用户是否登录
        if not request.user:
            return Response({
                'status': '500',
                'msg': '认证失败'
            })
        # 获取数据库中该用户的所有手机记录
        userid = request.user.id
        print(request.user.id)
        records = Record.objects.filter(user=userid).order_by("-ctime") # 并按时间降序排列
        if(category!="all"):
            records=records.filter(category__category_name=category)

        for record in records:
            if(record.type==1):
                record.money="+"+str(record.money)
            else:
                record.money="-"+str(record.money)
        ser = RecordSerializers(instance=records, many=True)
        return Response({
            'status': '200',
            'msg': 'ok',
            'results': ser.data
        })

    def post(self, request,category):
        """新增收支记录"""
        userid = request.user.id
        print(request.data.get('record'))
        # 获取到前端的数据先校验
        record = RecordSerializers(data=request.data.get('record'))

        if record.is_valid():
            record.save()
            return Response({
                'status': '200',
                'msg': '新增成功！',
                'results': record.data
            })

        return Response({
            'status': '500',
            'msg': record.errors
        })



class RecordDetailView(APIView):
    """单条记录的修改、删除"""
    authentication_classes = [RecordAuthentication, ]

    def put(self, request, record_id):
        """添加/修改备注"""
        if not request.user:
            return Response({
                'status': '500',
                'msg': '认证失败'
            })

        userid = request.user.id
        record = Record.objects.filter(id=record_id).first()
        if not record:
            return Response({
                'status': '500',
                'msg': '没有该记录，请刷新'
            })
        note=request.data.get("note")
        record.note=note
        record.save()

        return Response({
            'status': '200',
            'msg': '修改成功！'
        })

    def delete(self, request, record_id):
        """删除"""
        if not request.user:
            return Response({
                'status': '500',
                'msg': '认证失败'
            })
        Record.objects.filter(id=record_id).delete()
        return Response({
            'status': '200',
            'msg': '删除成功！'
        })

class RecordYearView(APIView):
    authentication_classes = [RecordAuthentication, ]

    def get(self, request, condition, num, num1, category):
        """按年/月/日查询，类别。要修改，按范围查询写到一起了，但写到一起后按范围查询就不能同时按类别查询了"""
        """20231103修改，添加num1用于范围查询，其他时刻num1="" """
        if not request.user:
            return Response({
                'status': '500',
                'msg': '认证失败'
            })
        userid=request.user.id
        if(condition == "year"):
            records = Record.objects.filter(user=userid).filter(ctime__year=int(num))
            print(records)
        elif(condition == "month"):
            records = Record.objects.filter(user=userid).filter(ctime__month=int(num))
        elif (condition == "day"):
            records = Record.objects.filter(user=userid).filter(ctime__day=int(num))
        elif(condition=="range"):
            records=Record.objects.filter(user=userid).filter(ctime__range=(num,num1))

        # if(condition!="range" and category!="all"):
        if (category != "all"):
            records = records.filter(category=category)

        ser = RecordSerializers(instance=records, many=True)
        return Response({
            'status': '200',
            'msg': '查询成功！',
            'results': ser.data
        })


class CategoryView(APIView):
    """获取所有的类别"""
    authentication_classes = [RecordAuthentication, ]

    def get(self, request):
        categorys=Category.objects.all()
        ser = CategorySerializers(instance=categorys, many=True)
        return Response({
            'status': '200',
            'msg': '查询成功！',
            'results': ser.data
        })

class RecordSearchView(APIView):
    authentication_classes = [RecordAuthentication, ]

    def get(self, request):
        if not request.user:
            return Response({
                'status': '500',
                'msg': '认证失败'
            })
        userid=request.user.id
        print(request.query_params)

        year=request.query_params.get("year")
        month = request.query_params.get("month")
        week = request.query_params.get("week")
        day = request.query_params.get("day")
        date_start = request.query_params.get("date_start")
        date_end = request.query_params.get("date_end")
        category = request.query_params.get("category")
        moneycome = request.query_params.get("moneycome")
        moneygo = request.query_params.get("moneygo")

        # 先查询出该用户的所有收支记录
        records = Record.objects.filter(user=userid)
        if (category != 'all'):
            # 按类别查询
            records = records.filter(category=category)
        if (moneycome == 'true' and moneygo == 'false'):
            # 只查收入
            records = records.filter(type=1)
        elif (moneycome == 'false' and moneygo == 'true'):
            # 只查支出
            records = records.filter(type=2)

        if(year!='' and month!=''):
            # 先按年月查询
            records = records.filter(ctime__year=int(year)).filter(ctime__month=int(month))
            if(day!=''):
                # 按年月日查询
                records = records.filter(ctime__day=int(day))
            elif (week != ''):
                # 按周查询（范围查询）
                # week=0,1,2,3,4代表第一周(1-7)，第二周(8-14)，第三周(15-21)，第四周(22-28)，第五周(29-31)
                num = int(week) * 7 + 1
                num1 = (int(week) + 1) * 7
                # import Date
                num=year+'-'+month+'-'+str(num)
                num1=year+'-'+month+'-'+str(num1)
                # records = records.filter(ctime__week_day=2)表示查询星期二
                records = records.filter(ctime__range=(num, num1))  # num、num1为2023-10-01格式

        elif(date_start!='' and date_end!=''):
            #范围查询
            records = records.filter(ctime__range=(date_start, date_end))

        from django.db.models import Avg, Count, Max, Min, Sum,F
        # records = records.annotate(totalMoney=Sum('money'))
        # print('total',records.first().totalMoney)
        # 先按类别排放
        # records=records.order_by('category')

        # 输出record表的外键'category'在其表中的category_name字段值
        # print(records.select_related("category")[0].category.category_name)

        results=[]  # 前端饼图需要[{"name":xxx,"value"=xxx},{}]格式
        # 假设经过筛选后的视图为records
        # 那么下列的语句转换为sql语句为：select sum(money) from records
        sum=records.aggregate(sumMoney=Sum('money'))
        print("sum",sum)            # 筛选出的数据的总额，为{'sumMoney': Decimal('2251.00')}格式

        # select category as name,sum(money) as value from records group by category
        # annote(name=F("category"))：把属性名category重命名为name
        # results=records.annotate(name=F("category__category_name")).values("category_id",'name').annotate(value=Sum('money'))
        results = records.annotate(name=F("category__category_name")).values('name').annotate(
            value=Sum('money'))
        print("results",results)    # 筛选出饼图所需要的数据，为<QuerySet [{'name': 2, 'value': Decimal('6.00')}, {'name': 1, 'value': Decimal('2245.00')}]>格式

        # 还要把外键category变为category_name
        # select category as name,sum(money) as value from records,category where records.category_id=category.id group by category

        # 将数据按类别筛选出来，然后放进dict中
        recordsByCategory={}
        # recordsDetail=[]
        for result in results:
            category_name=result['name']
            recordsDetail=records.filter(category__category_name=category_name)
            ser = RecordSerializers(instance=recordsDetail, many=True)
            recordsByCategory[category_name]=ser.data

        print("recordsByCategory")
        print(recordsByCategory) # {'餐饮': <QuerySet [<Record: Record object (5)>, <Record: Record object (14)>]>, '交通': <QuerySet [<Record: Record object (13)>]>}

        returns={"sum":sum,"pie":results,"recordsDetail":recordsByCategory}
        print("returns",returns)
        # first=records.first()
        # category=first.category #
        # sum_c=first.money       # 每个分类的总金额
        # i = 1
        # totalMoney =
        # while(i < len(records)):
        #
        # for record in records:
        #     totalMoney+=record.money
        #     sum_c
        # print('totalMoney',totalMoney)
        ser = RecordSerializers(instance=records, many=True)
        return Response({
            'status': '200',
            'msg': '查询成功！',
            'results': returns
        })

class WechatView(APIView):
    authentication_classes = [RecordAuthentication, ]

    def get(self, request):
        code = request.query_params.get("code")
        print("code " + code)
        url = "https://api.weixin.qq.com/sns/jscode2session"
        url += "?appid=wx070c6bfef3f5cd73"  # 自己的appid
        url += "&secret=e4516f67084b6f43d1432d14c06d6a52"  # 自己的appSecret
        url += "&js_code=" + code
        url += "&grant_type=authorization_code"
        url += "&connect_redirect=1"

        import requests, json
        r = requests.get(url)  # 向微信发送请求，获得微信用户的openid
        key = json.loads(r.text)  # 转成json格式
        openid = key.get("openid")  # openid是该用户在该小程序中的唯一标识
        print("openid " + openid)

        if not request.user:
            # 选择微信登录
            # 根据openid到user表中查出该用户，如果没有，为其创建一个用户
            user=User.objects.filter(openid=openid).first()
            token = str(uuid.uuid4())
            if(user):
                # 存在该用户
                user.token=token
                user.save()
                user_serializer = UserModelSerializer(user)

            else:
                # 没有此用户
                user.username="momo"
                user.password="123456"
                user.openid=openid

                user.token = token
                user.save()
                user_serializer = UserModelSerializer(user)

            return Response({
                'status': '200',
                'msg': '登录成功！',
                'results': user_serializer.data
            })
            # return Response({
            #     'status': '500',
            #     'msg': '认证失败'
            # })

        else:
            # 登录状态绑定微信
            userid=request.user.id


            user=User.objects.filter(id=userid).first()
            user.openid=openid
            user.save()

            return Response({
                'status': '200',
                'msg': '绑定成功！',
                'results': {
                    'BindWechat':'true'
                }
            })

    def post(self,request):
        print("userWechat")
        wechatName=request.data.get("wexinName")
        wechatAvatarUrl=request.data.get("wexinAvatarUrl")
        print(wechatName)
        print(wechatAvatarUrl)

        if not request.user:
            return Response({
                'status': '500',
                'msg': '认证失败'
            })

        user=User.objects.filter(id=request.user.id).first()
        user.wechatName=wechatName
        user.wechatAvatarUrl=wechatAvatarUrl
        user.save()

        return Response({
            'status': '200',
            'msg': '登录成功！',
            'results': "user_serializer.data"
        })



