from django.urls import path
from dashboard.views import AssessorEventArgumentCharts, AssessorData, AssessorAverageEvalFBeginning, \
    AssessorAverageEvalCurrent, BeEvalData, BeEvalEventArgumentCharts, BeEvalAverageEvalFBeginning, \
    BeEvalAverageEvalCurrent, BeEvalUserReportTable, AssessorUserReportTable

urlpatterns = [
    path('assessor/data', AssessorData.as_view(), name='AssessorData'),
    path('assessor/event-argument-chart', AssessorEventArgumentCharts.as_view(), name='AssessorEventArgumentCharts'),
    path('assessor/average-eval-from-begin', AssessorAverageEvalFBeginning.as_view(),
         name='AssessorAverageEvalFBeginning'),
    path('assessor/average-eval-current-year', AssessorAverageEvalCurrent.as_view(), name='AssessorAverageEvalCurrent'),
    path('assessor/user-report-table', AssessorUserReportTable.as_view(), name='evaluation-for-feedbackSessions'),
    ############# be eval #############
    path('be-eval/data', BeEvalData.as_view(), name='BeEvalData'),
    path('be-eval/event-argument-chart', BeEvalEventArgumentCharts.as_view(), name='BeEvalEventArgumentCharts'),
    path('be-eval/average-eval-from-begin', BeEvalAverageEvalFBeginning.as_view(), name='BeEvalAverageEvalFBeginning'),
    path('be-eval/average-eval-current-year', BeEvalAverageEvalCurrent.as_view(), name='BeEvalAverageEvalCurrent'),
    path('be-eval/user-report-table', BeEvalUserReportTable.as_view(), name='evaluation-for-feedbackSessions'),
]
