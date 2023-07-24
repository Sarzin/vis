from rest_framework.serializers import ModelSerializer
from performanceManagement.models import *
from reports.models import *


class IndicatorsListSerializer(ModelSerializer):
    class Meta:
        model = Indicators
        fields = '__all__'


class ItemsEvaluationListSerializer(ModelSerializer):
    class Meta:
        model = Items_evaluation
        fields = '__all__'


class AxesListSerializer(ModelSerializer):
    class Meta:
        model = Axes
        fields = '__all__'


class FeedBackListSerializer(ModelSerializer):
    class Meta:
        model = Feedback_sessions
        fields = '__all__'


class FeedBackListBeEvalSerializer(ModelSerializer):
    class Meta:
        model = Feedback_sessions
        exclude = ('description_hidden',)


class EvaluationListSerializer(ModelSerializer):
    class Meta:
        model = Indicators
        fields = '__all__'


class IndicatorsRegisterSerializer(ModelSerializer):
    class Meta:
        model = Indicators
        fields = '__all__'


class ReportEvalSerializer(ModelSerializer):
    class Meta:
        model = Eval_Report
        fields = '__all__'
