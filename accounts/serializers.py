from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.serializers import ModelSerializer
from accounts.models import *
from rest_framework import serializers
from accounts import views
import datetime


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        season_isEvalTime = views.get_season_isEvalTime()
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['assessor'] = user.assessor
        token['is_eval_time'] = season_isEvalTime['is_eval_time']
        token['season'] = season_isEvalTime['season']
        token['season_eval'] = season_isEvalTime['season_eval']
        token['year'] = season_isEvalTime['year']
        token['id'] = user.id
        token['full_name'] = user.get_full_name()
        token['picture'] = user.picture.url
        # token['unit'] = user.unit['name']
        user.last_login = datetime.datetime.now()
        user.save()
        return token


# for check the access token data you can decode it in https://token.dev/

################################# start Account #########################

class PostCreateSerializerAccount(ModelSerializer):
    class Meta:
        model = Account
        fields = ('email', 'password',)


class PostListSerializerAccount(ModelSerializer):
    class Meta:
        model = Account
        exclude = ('password', 'last_login', 'join_date')


################################# end Account #########################

class StaffAssessor_Serializer(ModelSerializer):
    class Meta:
        model = staff_assessor
        fields = ('staff',)


class CreateEvaluatedUser(ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class AddNewUnit(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('name',)


class ListUnitSerializer(ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'


class ChangePasswordSerializer(serializers.Serializer):
    model = Account

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
