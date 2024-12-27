from rest_framework import serializers,exceptions
from app01 import models
from ext.hook import HookSerializer


class UserModelSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(write_only=True)

    class Meta:
        model = models.User
        fields = ["id", "username", "password", "confirm_password","token","openid","wechatName","wechatAvatarUrl"]
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only":True}
        }

    def validate_confirm_password(self, value):
        # value=confirm_password
        # self.inital_data：fields的全部字段值
        password = self.initial_data.get("password")
        if password != value:
            raise exceptions.ValidationError("密码不一致！")
        return value

    def get_openid(self,obj):
        if(obj.openid!=None and obj.openid!=''):
            #已绑定微信
            return "true"
        else:
            # 未绑定微信
            return "false"

class LoginSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["id", "username", "password"]


class RecordSerializers(HookSerializer,serializers.ModelSerializer):
    # type = serializers.CharField(source="get_type_display")
    # category = serializers.CharField(source="category.category_name")
    # category = serializers.SerializerMethodField()
    # username = serializers.CharField(source="user.username")

    class Meta:
        model = models.Record
        # fields = ["type", "ctime", "money", "note", "category", "username"]
        fields = ["id","type", "ctime", "money", "note", "category", "user"]

    def nget_type(self,obj):
        return obj.get_type_display()

    def nget_category(self, obj):
        return {"id": obj.category.id, "name": obj.category.category_name}

    def nget_user(self,obj):
        return obj.user.username


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ["id","category_name"]

class RecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Record
        fields =["sum"]