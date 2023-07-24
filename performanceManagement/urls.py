from django.conf.urls import url
from performanceManagement.views import *

app_name = 'performanceManagement'

urlpatterns = [
    url('list-Indicators/', IndicatorsListAPIView.as_view(), name='IndicatorsListAPIView'),
    url('list-items-evaluation/', ItemsEvaluationList.as_view(), name='list-items-evaluation'),
    url('list-axes/', AxesList.as_view(), name='axes_list'),

    url('getIndicatorsForAccount/', getIndicatorsForAccount.as_view(), name="getIndicatorsForAccount"),
    url('eval-a-user/', EvalAccaount.as_view(), name='eval a user'),
    url('show-report-eval/', getReportEval.as_view(), name='show-report-eval'),
    # url('registerIndicatorsForAccount/', RegisterIndicatorsForAccount.as_view(), name='registerIndicatorsForAccount'),
    # url('registerAIndicators', RegisterAIndicators.as_view(), name='RegisterAIndicators')
]
